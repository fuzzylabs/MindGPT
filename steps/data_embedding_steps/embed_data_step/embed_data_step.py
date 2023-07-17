"""Embed data step."""
import pandas as pd
from chromadb.utils import embedding_functions
from utils.chroma_store import ChromaStore
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def embed_data(
    df: pd.DataFrame, embed_model_type: str, data_version: str, collection_name: str
) -> None:
    """Embeds each row of the given DataFrame and uploads to the vector database.

    Args:
        df (pd.DataFrame): _description_
        embed_model_type (str): _description_
        data_version (str): _description_
        collection_name (str): _description_
    """
    texts = df["text_scraped"].values
    src_urls = df["url"].values

    model_name = None
    if embed_model_type == "xl":
        model_name = "hkunlp/instructor-xl"
    elif embed_model_type == "large":
        model_name = "hkunlp/instructor-large"
    elif embed_model_type == "base":
        model_name = "hkunlp/instructor-base"

    # Create a embedding function
    ef = embedding_functions.InstructorEmbeddingFunction(model_name=model_name)

    # Create a chromadb client
    chroma_client = ChromaStore(
        chroma_server_hostname="server.default", chroma_server_port=8000
    )

    # Add text to a collection
    chroma_client.get_or_create_collection(
        collection_name=collection_name, embedding_function=ef
    )
    chroma_client.add_texts(
        collection_name=collection_name,
        texts=texts,
        metadatas=[{"source": url, "data_version": data_version} for url in src_urls],
    )
