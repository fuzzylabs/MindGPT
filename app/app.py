"""MindGPT Streamlit app."""
# Fix for streamlit + chroma sqllite3 issue: https://discuss.streamlit.io/t/issues-with-chroma-and-sqlite/47950/5
# flake8: noqa
__import__("pysqlite3")
import sys

sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import json
import logging
from typing import Dict, Union

import streamlit as st

from configs.app_config import CONVERSATIONAL_MEMORY_SIZE
from configs.service_config import (
    CHROMA_SERVER_HOST_NAME,
    CHROMA_SERVER_PORT,
    COLLECTION_NAME_MAP,
    N_CLOSEST_MATCHES,
)

from ui_components import show_sidebar, create_feedback_components
from app_utils.monitoring import post_response_to_metric_service
from app_utils.chroma import connect_vector_store, query_vector_store
from app_utils.llm import build_memory_dict, query_llm
from app_utils.endpoints import get_metric_service_endpoint, get_prediction_endpoint


def setup() -> None:
    """This function set up the app page title, logging and page config."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )

    st.set_page_config(
        page_title="MindGPT",
        page_icon="🧠",
        layout="wide",
    )

    st.title("MindGPT 🧠")
    st.caption("_made by [Fuzzy Labs](https://www.fuzzylabs.ai/)_")
    st.caption(
        "MindGPT is not a digital counsellor and the answers provided may be inaccurate. If you or someone you know is in crisis or experiencing a mental health emergency, please contact your local emergency services or a helpline immediately such as https://www.mind.org.uk/need-urgent-help/using-this-tool/ . This chatbot is not designed to provide immediate crisis intervention or emergency assistance."
    )

    st.session_state.error_placeholder = st.empty()


def user_consent() -> None:
    """This function updates the session state based on the user's response to the disclaimer and data sharing consent."""
    if "accept" not in st.session_state:
        st.session_state.accept = False

    if "accepted_or_declined_data_sharing_consent" not in st.session_state:
        st.session_state.accepted_or_declined_data_sharing_consent = False

    if "data_sharing_consent" not in st.session_state:
        st.session_state.data_sharing_consent = False


def main() -> None:
    """Main streamlit app function."""
    setup()
    user_consent()
    show_sidebar()  # Show side bar base on the two session state variables, `accept` and `accepted_or_declined_data_sharing_consent`

    if (
        st.session_state.accept
        and st.session_state.accepted_or_declined_data_sharing_consent
    ):
        # Initialise chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Initialise conversational memory
        if "nhs_memory" not in st.session_state:
            st.session_state.nhs_memory = []
        else:
            nhs_memory = st.session_state.nhs_memory

        if "mind_memory" not in st.session_state:
            st.session_state.mind_memory = []
        else:
            mind_memory = st.session_state.mind_memory

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Enter a question"):
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Get seldon endpoint
            prediction_endpoint = get_prediction_endpoint()

            # Get the metric service endpoint
            metric_service_endpoint = get_metric_service_endpoint()

            # Get vector store client
            chroma_client = connect_vector_store(
                chroma_server_host=CHROMA_SERVER_HOST_NAME,
                chroma_server_port=CHROMA_SERVER_PORT,
            )

            if metric_service_endpoint is None:
                logging.warn("Metric service endpoint is None, monitoring is disabled.")

            if prediction_endpoint is None or chroma_client is None:
                st.session_state.error_placeholder.error(
                    "MindGPT is not currently reachable, please try again later.",
                    icon="🚨",
                )
            else:
                logging.info(st.session_state.prompt_template)
                with st.chat_message("assistant"):
                    full_response = "Here's what the NHS and Mind each have to say:\n\n"
                    message_placeholder = st.empty()

                    # Placeholder for the thumbs up and thumbs down button
                    feedback_placeholder = st.empty()

                    readability_scores: Dict[str, Dict[str, Union[str, float]]] = {}

                    # Placeholder for the thumbs up and thumbs down button
                    feedback_placeholder = st.empty()

                    for collection, source in COLLECTION_NAME_MAP.items():
                        # Query vector store
                        context = query_vector_store(
                            chroma_client=chroma_client,
                            query_text=prompt,
                            collection_name=collection,
                            n_results=N_CLOSEST_MATCHES,
                        )

                        # Create a dict of prompt and context
                        message = {"prompt_query": prompt, "context": context}

                        # Add history if neither memory is None
                        if nhs_memory and mind_memory:
                            message["history"] = (
                                mind_memory if collection == "mind_data" else nhs_memory
                            )

                        # Query LLM by passing query and context
                        assistant_response = query_llm(
                            prediction_endpoint=prediction_endpoint,
                            messages=message,
                            temperature=st.session_state.temperature,
                            max_length=st.session_state.max_length,
                        )

                        # Append the response to the appropriate memory and update session state
                        memory_dict = build_memory_dict(prompt, assistant_response)
                        if collection == "mind_data":
                            mind_memory.append(memory_dict)
                            st.session_state.mind_memory = mind_memory
                        else:
                            nhs_memory.append(memory_dict)
                            st.session_state.nhs_memory = nhs_memory

                        full_response += f"{source}: {assistant_response}  \n"

                        logging.info("MEMORY LOG")
                        logging.info(nhs_memory)
                        logging.info(mind_memory)

                        if metric_service_endpoint:
                            result = post_response_to_metric_service(
                                f"{metric_service_endpoint}/readability",
                                assistant_response,
                                source,
                            )
                            logging.info(result.text)
                            readability_scores[source] = {
                                "score": float(json.loads(result.text)["score"]),
                                "question": str(prompt),
                                "response": str(assistant_response),
                            }

                    # Remove first conversation in memory if either exceeds the size limit
                    if len(mind_memory) > CONVERSATIONAL_MEMORY_SIZE:
                        mind_memory.pop(0)
                    if len(nhs_memory) > CONVERSATIONAL_MEMORY_SIZE:
                        nhs_memory.pop(0)

                    message_placeholder.markdown(full_response)

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )

                    if metric_service_endpoint:
                        with feedback_placeholder.container():  # Show thumbs for every answers generated.
                            create_feedback_components(
                                metric_service_endpoint,
                                prompt,
                                full_response,
                                readability_scores,
                            )


if __name__ == "__main__":
    main()
