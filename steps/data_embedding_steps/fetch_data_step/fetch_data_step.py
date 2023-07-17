"""Fetch data step (data embedding pipeline)."""
import pandas as pd
from zenml import step
from zenml.logger import get_logger
from zenml.steps import Output

logger = get_logger(__name__)


@step
def fetch_data(data_version: str) -> Output(mind_df=pd.DataFrame, nhs_df=pd.DataFrame):  # type: ignore
    """Loads the cleaned and prepared data from the DVC versioned data.

    Args:
        data_version (str): Name of DVC data version to pull data from.

    Returns:
        mind_data (pd.DataFrame): Data from the Mind website
        nhs_data (pd.DataFrame): Data from the NHS website
    """
    # Pull data with DVC
    # Load data from local data storage
    mind_df = pd.DataFrame()
    nhs_df = pd.DataFrame()

    return mind_df, nhs_df
