"""Embed data step."""
import uuid

import pandas as pd
from chromadb.utils import embedding_functions
from utils.chroma_store import ChromaStore
from utils.text_splitter import TextSplitter
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


EMBED_MODEL_MAP = {
    "xl": "hkunlp/instructor-xl",
    "large": "hkunlp/instructor-large",
    "base": "hkunlp/instructor-base",
}
DEFAULT_EMBED_INSTRUCTION = "Represent the document for retrieval: "


@step
def embed_data(
    df: pd.DataFrame,
    embed_model_type: str,
    data_version: str,
    collection_name: str,
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    """Embeds each row of the given DataFrame and uploads to the vector database.

    Args:
        df (pd.DataFrame): Input data frame to be embedded
        embed_model_type (str): Name of embedding model to use
        data_version (str): Data version of input dataset
        collection_name (str): Name of collection for input dataset
        chunk_size (int): Size of chunks to split input text into
        chunk_overlap (int): Number of characters to overlap between chunks

    Raises:
        ValueError: if `embed_model_type` is not supported or invalid
    """
    texts = df["text_scraped"].values.tolist()

    logger.info(f"Using chunk_size={chunk_size} and chunk_overlap={chunk_overlap}")
    text_splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # Split text into chunks
    chunks = []
    for text in texts:
        chunks.extend(text_splitter.split_text(text))
    uuids = [str(uuid.uuid4()) for _ in range(len(chunks))]

    logger.info(f"Split {len(texts)} texts into {len(chunks)} chunks")

    model_name = EMBED_MODEL_MAP.get(embed_model_type, None)
    if model_name is None:
        raise ValueError(
            f"{embed_model_type} is not supported. The list of supported models is {EMBED_MODEL_MAP.keys()}"
        )

    # Create a embedding function
    ef = embedding_functions.InstructorEmbeddingFunction(
        model_name=model_name, instruction=DEFAULT_EMBED_INSTRUCTION
    )

    # Create a chromadb client
    # Switch hostname to chroma-service.default if running the pipeline on k8s
    chroma_client = ChromaStore(
        chroma_server_hostname="localhost", chroma_server_port=8000
    )

    chroma_client.add_texts(
        collection_name=collection_name,
        texts=chunks,
        ids=uuids,
        embedding_function=ef,
    )
