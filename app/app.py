"""MindGPT Streamlit app."""
# Fix for streamlit + chroma sqllite3 issue: https://discuss.streamlit.io/t/issues-with-chroma-and-sqlite/47950/5
# flake8: noqa
__import__("pysqlite3")
import sys

sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union, TypedDict

import requests
import streamlit as st
from chromadb.api import API
from chromadb.api.types import EmbeddingFunction
from chromadb.utils import embedding_functions
from requests.models import Response
from utils.chroma_store import ChromaStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


# Setup for chroma vector store
CHROMA_SERVER_HOST_NAME = "chroma-service.default"
CHROMA_SERVER_PORT = 8000
DEFAULT_EMBED_MODEL = "base"  # ["base", "large", "xl"]
N_CLOSEST_MATCHES = 3
EMBED_MODEL_MAP = {
    "xl": "hkunlp/instructor-xl",
    "large": "hkunlp/instructor-large",
    "base": "hkunlp/instructor-base",
}
COLLECTION_NAME_MAP = {"mind_data": "Mind", "nhs_data": "NHS"}

# Seldon configuration
SELDON_SERVICE_NAME = "llm-default-transformer"
SELDON_NAMESPACE = "matcha-seldon-workloads"
SELDON_PORT = 9000

# Metric service configuration
METRIC_SERVICE_NAME = "monitoring-service"
METRIC_SERVICE_NAMESPACE = "default"
METRIC_SERVICE_PORT = "5000"

# Paragraph from https://www.nhs.uk/mental-health/conditions/depression-in-adults/overview/
DEFAULT_CONTEXT = """Most people experience feelings of stress, anxiety or low mood during difficult times.
A low mood may improve after a short period of time, rather than being a sign of depression."""

DEFAULT_QUERY_INSTRUCTION = (
    "Represent the question for retrieving supporting documents: "
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Prompt Templates
SIMPLE_TEMPLATE = "Context: {context}\n\nQuestion: {question}\n\n"

COMPLEX_TEMPLATE = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use three sentences maximum and keep the answer as concise as possible.
Always say "thanks for asking!" at the end of the answer.
{context}
Question: {question}
Helpful Answer:"""

ADVANCED_TEMPLATE = """You are a highly skilled AI trained in language comprehension and summarisation.
I would like you to read the following text and summarise it into a concise abstract paragraph. Use the following pieces of context to answer the question at the end.
Aim to retain the most important points, providing a coherent and readable summary that could help a person understand the main points of the discussion without needing to read the entire text.
Please avoid unnecessary details or tangential points.
{context}
Question: {question}
Helpful Answer:"""

CONVERSATIONAL_MEMORY_TEMPLATE = """Use the conversation history and context provided to inform your response.

Conversation history:
{history}

Context: {context}

Question: {question}
"""

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


@st.cache_data(show_spinner=False)
def _get_prediction_endpoint() -> Optional[str]:
    """Get the endpoint for the currently deployed LLM model.

    Returns:
        Optional[str]: the url endpoint if it exists and is valid, None otherwise.
    """
    return f"http://{SELDON_SERVICE_NAME}.{SELDON_NAMESPACE}:{SELDON_PORT}/v2/models/transformer/infer"


@st.cache_data(show_spinner=False)
def _get_metric_service_endpoint() -> str:
    """Get the endpoint for the currently deployed metric service.

    Returns:
        str: the url endpoint if it exists and is valid, None otherwise.
    """
    return f"http://{METRIC_SERVICE_NAME}.{METRIC_SERVICE_NAMESPACE}:{METRIC_SERVICE_PORT}/readability"


@st.cache_data(show_spinner=False)
def _get_embedding_function(embed_model_type: str) -> Union[EmbeddingFunction, None]:
    """Load embedding function to be used by Chroma vector store.

    Args:
        embed_model_type (str): String representation of the embedding model.

    Returns:
        Union[EmbeddingFunction, None]: Embedding function if it exists, None otherwise.
    """
    # Create a embedding function
    model_name = EMBED_MODEL_MAP.get(embed_model_type, None)
    if model_name is None:
        return None
    return embedding_functions.InstructorEmbeddingFunction(
        model_name=model_name, instruction=DEFAULT_QUERY_INSTRUCTION
    )


class MessagesType(TypedDict, total=False):
    """The class specifies constraints about which keys map to which types in the payload messages.

    This is required for mypy to understand the structure of the `messages` dictionary.

    Args:
        TypedDict (type): A class from the `typing` module to define types for specific dictionary keys.
        total (bool, optional): this signify that not all keys are mandatory in the dictionary.
    """

    history: List[Dict[str, str]]
    context: str
    prompt_query: str


def connect_vector_store(chroma_server_host: str, chroma_server_port: int) -> API:
    """Connect to Chroma vector store.

    Args:
        chroma_server_host (str): Chroma server host name
        chroma_server_port (int): Chroma server port

    Returns:
        API: Chroma client object.
    """
    try:
        # Connect to vector store
        chroma_client = ChromaStore(
            chroma_server_hostname=chroma_server_host,
            chroma_server_port=chroma_server_port,
        )
        return chroma_client
    except Exception:
        return None


def query_vector_store(
    chroma_client: API,
    query_text: str,
    collection_name: str,
    n_results: int,
    embedding_function: EmbeddingFunction,
) -> str:
    """Query vector store to fetch `n_results` closest documents.

    Args:
        chroma_client (API): Chroma vector store client.
        query_text (str): Query text.
        collection_name (str): Name of collection
        n_results (int): Number of closest documents to fetch
        embedding_function (EmbeddingFunction): Embedding function used while creating collection

    Returns:
        str: String containing the closest documents to the query.
    """
    result_dict = chroma_client.query_collection(
        collection_name=collection_name,
        query_texts=query_text,
        n_results=n_results,
        embedding_function=embedding_function,
    )
    documents = " ".join(result_dict["documents"][0])
    return documents


def _create_payload(messages: MessagesType) -> Dict[str, List[Dict[str, Any]]]:
    """Create a payload from the user input to send to the LLM model.

    Args:
        messages (Dict[str, Union[str, dict]]): List of previous messages from both the AI and user.

    Returns:
        Dict[str, List[Dict[str, Any]]]: the payload to send in the correct format.
    """
    context = messages.get("context", DEFAULT_CONTEXT)
    history: List[Dict[str, str]] = messages.get("history", [])

    if history:
        history_string = _build_conversation_history_template(history)

        input_text = CONVERSATIONAL_MEMORY_TEMPLATE.format(
            history=history_string, question=messages["prompt_query"], context=context
        )
    else:
        input_text = SIMPLE_TEMPLATE.format(
            question=messages["prompt_query"], context=context
        )

    logging.info(f"Prompt to LLM : {input_text}")

    return {
        "inputs": [
            {
                "name": "array_inputs",
                "shape": [-1],
                "datatype": "string",
                "data": str(input_text),
            }
        ]
    }


def _build_conversation_history_template(history_list: List[Dict[str, str]]) -> str:
    history_string = ""
    for history in history_list:
        user_input = history["user_input"]
        ai_response = history["ai_response"]

        history_string += f"User input: {user_input}\nAI response: {ai_response}"

    return history_string


def _get_predictions(
    prediction_endpoint: str, payload: Dict[str, List[Dict[str, Any]]]
) -> str:
    """Using the prediction endpoint and payload, make a prediction request to the deployed model.

    Args:
        prediction_endpoint (str): the url endpoint.
        payload (Dict[str, List[Dict[str, Any]]]): the payload to send to the model.

    Returns:
        str: the predictions from the model.
    """
    response = requests.post(
        url=prediction_endpoint,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )
    data = json.loads(json.loads(response.text)["outputs"][0]["data"][0])
    return data["generated_text"]


def query_llm(prediction_endpoint: str, messages: MessagesType) -> str:
    """Query endpoint to fetch the summary.

    Args:
        prediction_endpoint (str): Prediction endpoint.
        messages (MessagesType): Dict of message containing history, context and prompt.

    Returns:
        str: Summarised text.
    """
    with st.spinner("Loading response..."):
        payload = _create_payload(messages)
        summary_txt = _get_predictions(prediction_endpoint, payload)
    return summary_txt


def post_response_to_metric_service(
    metric_service_endpoint: str, response: str
) -> Response:
    """Send the LLM's response to the metric service for readability computation using a POST request.

    Args:
        metric_service_endpoint (str): the metric service endpoint where the readability is computed
        response (str): the response produced by the LLM

    Returns:
        Response: the post request response
    """
    response_dict = {"response": response}
    result = requests.post(url=metric_service_endpoint, json=response_dict)

    return result


def show_disclaimer() -> bool:
    """Show disclaimer on sidebar with streamlit.

    Returns:
        bool: True if disclaimer accepted, False if not.
    """
    st.sidebar.title("Disclaimer")
    with open("app/disclaimer.txt") as f:
        disclaimer_text = f.read()
    st.sidebar.markdown(disclaimer_text)

    accept = st.sidebar.button("I Accept")

    return accept


def build_memory_dict(question: str, response: str) -> Dict[str, str]:
    """Build the memory dictionary from user's question and the model's response.

    Args:
        question (str): the question asked by the user.
        response (str): the response by the model.

    Returns:
        Dict[str, str]: the memory dictionary.
    """
    return {"user_input": question, "ai_response": response}


def main() -> None:
    """Main streamlit app function."""
    if "accept" not in st.session_state:
        st.session_state.accept = False

    if not st.session_state.accept:
        accept = show_disclaimer()
        if accept:
            st.session_state.accept = True

    if st.session_state.accept:
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
            prediction_endpoint = _get_prediction_endpoint()

            # Get the metric service endpoint
            metric_service_endpoint = _get_metric_service_endpoint()

            # Get vector store client
            chroma_client = connect_vector_store(
                chroma_server_host=CHROMA_SERVER_HOST_NAME,
                chroma_server_port=CHROMA_SERVER_PORT,
            )
            embed_function = _get_embedding_function(DEFAULT_EMBED_MODEL)

            if metric_service_endpoint is None:
                logging.warn("Metric service endpoint is None, monitoring is disabled.")

            if prediction_endpoint is None or chroma_client is None:
                st.session_state.error_placeholder.error(
                    "MindGPT is not currently reachable, please try again later.",
                    icon="🚨",
                )
            else:
                with st.chat_message("assistant"):
                    full_response = ""
                    message_placeholder = st.empty()

                    full_response = "Here's what the NHS and Mind each have to say:\n\n"

                    for collection, source in COLLECTION_NAME_MAP.items():
                        # Query vector store
                        context = query_vector_store(
                            chroma_client=chroma_client,
                            query_text=prompt,
                            collection_name=collection,
                            n_results=N_CLOSEST_MATCHES,
                            embedding_function=embed_function,
                        )

                        # Create a dict of prompt and context
                        message = {"prompt_query": prompt, "context": context}

                        # Add history if neither memory is None
                        if nhs_memory and mind_memory:
                            if collection == "mind_data":
                                message["history"] = mind_memory
                            else:
                                message["history"] = nhs_memory

                        # Query LLM by passing query and context
                        assistant_response = query_llm(prediction_endpoint, message)

                        # Append the response to the appropriate memory
                        if collection == "mind_data":
                            mind_memory.append(
                                build_memory_dict(prompt, assistant_response)
                            )
                            st.session_state.mind_memory = mind_memory
                        else:
                            nhs_memory.append(
                                build_memory_dict(prompt, assistant_response)
                            )
                            st.session_state.nhs_memory = nhs_memory

                        full_response += f"{source}: {assistant_response}  \n"

                        logging.info("MEMORY LOG")
                        logging.info(nhs_memory)
                        logging.info(mind_memory)

                        if metric_service_endpoint:
                            result = post_response_to_metric_service(
                                metric_service_endpoint, assistant_response
                            )
                            logging.info(result.text)

                    message_placeholder.markdown(full_response)

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )


if __name__ == "__main__":
    main()
