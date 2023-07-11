"""Embed data step."""
import pandas as pd
from zenml import step
from zenml.logger import get_logger
from zenml.steps import Output

logger = get_logger(__name__)


@step
def embed_data(df: pd.DataFrame) -> Output(df=pd.DataFrame):  # type: ignore
    """Embeds each row of the given DataFrame.

    Args:
        df (pd.DataFrame): Input data with column of text data.

    Returns:
        df (pd.DataFrame): Data with a new column "embedding" containing the vector embedding for the given row.
    """
    # embedding_model = load_embedding_model()
    # Embed each row of dataframe and create new column
    return df
