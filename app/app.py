"""MindGPT Streamlit app."""
import json
import os
import time
from typing import Any, Dict, List, Optional, Union

import requests
import streamlit as st
from chromadb.api import API
from chromadb.api.types import EmbeddingFunction
from chromadb.utils import embedding_functions
from utils.chroma_store import ChromaStore

# Setup for chroma vector store
CHROMA_SERVER_HOST_NAME = "server.default"
CHROMA_SERVER_PORT = 8000
DEFAULT_EMBED_MODEL = "base"  # ["base", "large", "xl"]
COLLECTION_NAMES = ["mind_data", "nhs_data"]
N_CLOSEST_MATCHES = 3
EMBED_MODEL_MAP = {
    "xl": "hkunlp/instructor-xl",
    "large": "hkunlp/instructor-large",
    "base": "hkunlp/instructor-base",
}

# Seldon configuration
SELDON_SERVICE_NAME = "llm-default-transformer"
SELDON_NAMESPACE = "matcha-seldon-workloads"
SELDON_PORT = 9000

# Paragraph from https://www.nhs.uk/mental-health/conditions/depression-in-adults/overview/
DEFAULT_CONTEXT = """Most people experience feelings of stress, anxiety or low mood during difficult times.
A low mood may improve after a short period of time, rather than being a sign of depression."""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


st.set_page_config(
    page_title="MindGPT",
    page_icon="🧠",
    layout="wide",
)

st.title("MindGPT 🧠")
st.caption("_made by [Fuzzy Labs](https://www.fuzzylabs.ai/)_")
st.caption(
    "MindGPT is not a digital counsellor and the answers provided may be innacurate. If you or someone you know is in crisis or experiencing a mental health emergency, please contact your local emergency services or a helpline immediately such as https://www.mind.org.uk/need-urgent-help/using-this-tool/ . This chatbot is not designed to provide immediate crisis intervention or emergency assistance."
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
    return embedding_functions.InstructorEmbeddingFunction(model_name=model_name)


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


def _create_payload(messages: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
    """Create a payload from the user input to send to the LLM model.

    Args:
        messages (Dict[str, str]): List of previous messages from both the AI and user.

    Returns:
        Dict[str, List[Dict[str, Any]]]: the payload to send in the correct format.
    """
    template = "Context: {context}\n\nQuestion: {question}\n\n"
    context = messages.get("context", DEFAULT_CONTEXT)
    input_text = template.format(question=messages["prompt_query"], context=context)

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


def _get_predictions(
    prediction_endpoint: str, payload: Dict[str, List[Dict[str, Any]]]
) -> str:
    """Using the prediction endpont and payload, make a prediction request to the deployed model.

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


def query_llm(prediction_endpoint: str, messages: Dict[str, str]) -> str:
    """Query endpoint to fetch the summary.

    Args:
        prediction_endpoint (str): Prediction endpoint.
        messages (Dict[str, str]): Dict of message containing prompt and context.

    Returns:
        str: Summarized text.
    """
    with st.spinner("Loading response..."):
        payload = _create_payload(messages)
        summary_txt = _get_predictions(prediction_endpoint, payload)
    return summary_txt


def show_disclaimer() -> bool:
    """Show disclamer on sidebar with streamlit.

    Returns:
        bool: True if disclamer accepted, False if not.
    """
    st.sidebar.title("Disclaimer")
    with open("app/disclaimer.txt") as f:
        disclaimer_text = f.read()
    st.sidebar.markdown(disclaimer_text)

    accept = st.sidebar.button("I Accept")

    return accept


def main() -> None:
    """Main streamlit app function."""
    if "accept" not in st.session_state:
        st.session_state.accept = False

    if not st.session_state.accept:
        accept = show_disclaimer()
        if accept:
            st.session_state.accept = True

    if st.session_state.accept:
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input("Enter a question")

        if prompt is not None:
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Get seldon endpoint
            prediction_endpoint = _get_prediction_endpoint()

            # Get vector store client
            chroma_client = connect_vector_store(
                chroma_server_host=CHROMA_SERVER_HOST_NAME,
                chroma_server_port=CHROMA_SERVER_PORT,
            )
            embed_function = _get_embedding_function(DEFAULT_EMBED_MODEL)

            if prediction_endpoint is None or chroma_client is None:
                st.session_state.error_placeholder.error(
                    "MindGPT is not currently reachable, please try again later.",
                    icon="🚨",
                )
            else:
                with st.chat_message("assistant"):
                    full_response = ""
                    message_placeholder = st.empty()

                    # Query vector store
                    context = query_vector_store(
                        chroma_client=chroma_client,
                        query_text=prompt,
                        collection_name=COLLECTION_NAMES[0],
                        n_results=N_CLOSEST_MATCHES,
                        embedding_function=embed_function,
                    )

                    # Create a dict of prompt and context
                    message = {"prompt_query": prompt, "context": context}

                    # Query LLM by passing query and context
                    assistant_response = query_llm(prediction_endpoint, message)

                    # Simulate stream of response with milliseconds delay
                    for chunk in assistant_response.split():
                        full_response += chunk + " "
                        time.sleep(0.1)
                        # Add a blinking cursor to simulate typing
                        message_placeholder.markdown(full_response + "▌")

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )


if __name__ == "__main__":
    main()
