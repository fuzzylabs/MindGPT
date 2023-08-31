"""Utility functions for interacting with Chroma store."""
from typing import List, Optional, Union

import streamlit as st
from chromadb.api.types import EmbeddingFunction
from chromadb.utils import embedding_functions
from configs.prompt_template import DEFAULT_QUERY_INSTRUCTION
from configs.service_config import DEFAULT_EMBED_MODEL, EMBED_MODEL_MAP
from utils.chroma_store import ChromaStore


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


def connect_vector_store(
    chroma_server_host: str, chroma_server_port: str
) -> Optional[ChromaStore]:
    """Connect to Chroma vector store.

    Args:
        chroma_server_host (str): Chroma server host name
        chroma_server_port (str): Chroma server port

    Returns:
        Optional[ChromaStore]: ChromaStore interface object. None when there is an exception.
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
    chroma_client: ChromaStore,
    query_text: Optional[List[str]],
    collection_name: str,
    n_results: int,
) -> str:
    """Query vector store to fetch `n_results` closest documents.

    Args:
        chroma_client (ChromaStore): Chroma vector store client.
        query_text (Optional[List[str]]): Query text.
        collection_name (str): Name of collection
        n_results (int): Number of closest documents to fetch

    Returns:
        str: String containing the closest documents to the query.
    """
    embedding_function = _get_embedding_function(DEFAULT_EMBED_MODEL)
    result_dict = chroma_client.query_collection(
        collection_name=collection_name,
        query_texts=query_text,
        n_results=n_results,
        embedding_function=embedding_function,
    )
    documents = " ".join(result_dict["documents"][0])  # type: ignore
    return documents
