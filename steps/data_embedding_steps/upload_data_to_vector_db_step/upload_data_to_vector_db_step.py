"""Upload data to vector database step."""
import pandas as pd
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def upload_data_to_vector_db(df: pd.DataFrame, data_version: str) -> None:
    """Adds data to the vector database format to be used for creating the context for the LLM inference prompt.

    Args:
        df (pd.DataFrame): Input data with column of text data and embedding.
        data_version (str): Name of DVC data version data was pulled from.
    """
    # Create collection with name data version/"latest"
    # Add df to the collection
    return
