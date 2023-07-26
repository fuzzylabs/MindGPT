"""MindGPT Streamlit app."""
import argparse
import json
import os
from typing import Any, Dict, List, Optional, Union

import requests
import streamlit as st
from chromadb.api import API
from chromadb.api.types import EmbeddingFunction
from chromadb.utils import embedding_functions
from streamlit.logger import get_logger
from transformers import pipeline
from utils.chroma_store import ChromaStore

logger = get_logger("streamlit")

# Setup for chroma vector store
CHROMA_SERVER_HOST_NAME = "localhost"
CHROMA_SERVER_PORT = 8000
DEFAULT_EMBED_MODEL = "base"  # ["base", "large", "xl"]
N_CLOSEST_MATCHES = 3
EMBED_MODEL_MAP = {
    "xl": "hkunlp/instructor-xl",
    "large": "hkunlp/instructor-large",
    "base": "hkunlp/instructor-base",
}
COLLECTION_NAME_MAP = {"mind_data": "Mind", "nhs_data": "NHS"}

# Inference model configuration
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
    documents = "\n".join(result_dict["documents"][0])
    return documents


def _create_payload(prompt: str) -> Dict[str, List[Dict[str, Any]]]:
    """Create a payload from the user input to send to the LLM model.

    Args:
        prompt (str): A formatted user prompt to send to the model.

    Returns:
        Dict[str, List[Dict[str, Any]]]: the payload to send in the correct format.
    """
    return {
        "inputs": [
            {
                "name": "array_inputs",
                "shape": [-1],
                "datatype": "string",
                "data": str(prompt),
            }
        ]
    }


def _construct_prompt(question: str, context: str) -> str:
    """Construct a prompt from the user input to send to the LLM model.

    Args:
        question (str): user's question
        context (str): context relevant to the question

    Returns:
        str: constructed prompt
    """
    template = "Question: {question}\n\nContext: {context}\n\n"
    prompt = template.format(question=question, context=context)

    logger.info(f"Constructed LLM prompt: {prompt}")

    return prompt


def _get_llm_model(model_name: str) -> str:
    """_summary_.

    Args:
        model_name (str): _description_

    Returns:
        str: _description_
    """
    model_id = None
    if model_name == "flan-t5-small":
        model_id = "google/flan-t5-small"
    if model_name == "flan-t5-base":
        model_id = "google/flan-t5-base"
    if model_name == "flan-t5-large":
        model_id = "google/flan-t5-large"
    if model_name == "flan-t5-large":
        model_id = "google/flan-t5-large"
    if model_name == "fastchat":
        model_id = "lmsys/fastchat-t5-3b-v1.0"
    if model_name == "dolly-v2-3b":
        model_id = "databricks/dolly-v2-3b"
    return model_id


def _get_predictions(
    prediction_endpoint: str,
    prompt: str,
    model_name: str,
    max_length: int,
    temperature: float,
    load_8_bit: bool,
    local_llm_pipeline: bool = False,
) -> str:
    """Using the prediction endpoint and payload, make a prediction request to the deployed model.

    Args:
        prediction_endpoint (str): the url endpoint.
        prompt (str): the payload to send to the model.
        model_name (str): _description_
        max_length (int): _description_
        temperature (float): _description_
        load_8_bit (bool): _description_
        local_llm_pipeline (bool): Debugging: use local HF LLM pipeline

    Returns:
        str: the predictions from the model.
    """
    if not local_llm_pipeline:
        payload = _create_payload(prompt)
        response = requests.post(
            url=prediction_endpoint,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        data = json.loads(json.loads(response.text)["outputs"][0]["data"][0])
        return data["generated_text"]
    else:
        llm = pipeline(
            model=_get_llm_model(model_name),
            task="text2text-generation",
            model_kwargs={
                "device_map": "auto",
                "max_length": max_length,
                "load_in_8bit": load_8_bit,
                "temperature": temperature,
            },
        )
        data = llm(prompt)
        return data[0]["generated_text"]


def query_llm(
    prediction_endpoint: str,
    question: str,
    context: str,
    model_name: str,
    max_length: int,
    temperature: float,
    load_8_bit: bool,
    local_llm_pipeline: bool = False,
) -> str:
    """Query endpoint to fetch the summary.

    Args:
        prediction_endpoint (str): Prediction endpoint.
        messages (Dict[str, str]): Dict of message containing prompt and context.

    Returns:
        str: Summarised text.
    """
    with st.spinner("Loading response..."):
        prompt = _construct_prompt(question, context)
        summary_txt = _get_predictions(
            prediction_endpoint,
            prompt,
            model_name,
            max_length,
            temperature,
            load_8_bit,
            local_llm_pipeline,
        )
    return summary_txt


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


def main(args) -> None:
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

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        logger.info("Model parameters")
        logger.info(f"Model name: {args.model_name}")
        logger.info(f"Temperature: {args.temperature}")
        logger.info(f"Max length: {args.max_length}")
        logger.info(f"Load 8-bit: {args.load_8_bit}")

        if prompt := st.chat_input("Enter a question"):
            logger.info(f"Got user prompt: {prompt}")
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

                        logger.info(
                            f"Context from collection {collection}: {json.dumps(context)}"
                        )

                        # Query LLM by passing query and context
                        assistant_response = query_llm(
                            prediction_endpoint,
                            prompt,
                            context,
                            args.model_name,
                            args.max_length,
                            args.temperature,
                            args.load_8_bit,
                            args.local_llm_pipeline,
                        )

                        logger.info(
                            f"Got LLM response: {assistant_response} for source : {source}"
                        )

                        full_response += f"{source}: {assistant_response}  \n"

                    message_placeholder.markdown(full_response)

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="MindGPT",
        description="MindGPT streamlit app. Most of the CLI arguments are for debugging purposes.",
    )
    parser.add_argument(
        "--local-llm-pipeline",
        help="Load local LLM, instead of querying the remote deployed model.",
        action="store_true",
    )
    parser.add_argument(
        "--model-name",
        help="Name of LLM model to load",
        type=str,
        default="flan-t5-small",
        choices=[
            "googleflan-t5-small",
        ],
    )
    parser.add_argument(
        "--temperature", help="Temperature of LLM model", type=float, default=0
    )
    parser.add_argument(
        "--max_length", help="Max length of LLM model", type=int, default=128
    )
    parser.add_argument(
        "--load-8-bit", help="Boolean to load 8-bit model", action="store_true"
    )

    args = parser.parse_args()

    main(args)
