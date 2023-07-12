"""Embed data step."""
import pandas as pd
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def embed_data(df: pd.DataFrame) -> None:
    """Embeds each row of the given DataFrame and uploads to the vector database.

    Args:
        df (pd.DataFrame): Input data with column of text data.
    """
    # embedding_model = load_embedding_model()
    # Upload and embed each row of the dataframe with Chroma DB
    ...
