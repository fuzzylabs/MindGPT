"""Embed data step."""
import pandas as pd
from chromadb.utils import embedding_functions
from utils.chroma_store import ChromaStore
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


EMBED_MODEL_MAP = {
    "xl": "hkunlp/instructor-xl",
    "large": "hkunlp/instructor-large",
    "base": "hkunlp/instructor-large",
}


@step
def embed_data(
    df: pd.DataFrame, embed_model_type: str, data_version: str, collection_name: str
) -> None:
    """Embeds each row of the given DataFrame and uploads to the vector database.

    Args:
        df (pd.DataFrame): Input data frame to be embedded
        embed_model_type (str): Name of embedding model to use
        data_version (str): Data version of input dataset
        collection_name (str): Name of collection for input dataset

    Raises:
        ValueError: if `embed_model_type` is not supported or invalid
    """
    uuids = df["uuid"].values.tolist()
    texts = df["text_scraped"].values.tolist()
    src_urls = df["url"].values.tolist()

    model_name = EMBED_MODEL_MAP.get(embed_model_type, None)
    if model_name is None:
        raise ValueError(
            f"{embed_model_type} is not supported. The list of supported models is {EMBED_MODEL_MAP.keys()}"
        )

    # Create a embedding function
    ef = embedding_functions.InstructorEmbeddingFunction(model_name=model_name)

    # Create a chromadb client
    chroma_client = ChromaStore(
        chroma_server_hostname="server.default", chroma_server_port=8000
    )

    chroma_client.add_texts(
        collection_name=collection_name,
        texts=texts,
        ids=uuids,
        metadatas=[{"source": url, "data_version": data_version} for url in src_urls],
        embedding_function=ef,
    )
