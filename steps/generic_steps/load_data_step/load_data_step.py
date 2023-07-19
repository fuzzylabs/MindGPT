"""Load data step (data prep pipeline and embedding pipeline)."""
import os

import pandas as pd
from config import DATA_DIR
from utils.data_version_control import git_checkout_folder, pull_data
from zenml import step
from zenml.logger import get_logger
from zenml.steps import Output

logger = get_logger(__name__)


@step
def load_data(data_version: str, data_postfix: str) -> Output(mind_df=pd.DataFrame, nhs_df=pd.DataFrame):  # type: ignore
    """Load two CSVs from the "data/" directory. If no data exists, pull from the DVC storage bucket prior to loading.

    Args:
        data_version (str): Data version tag or commit hash for Git/DVC.
        data_postfix (str): Postfix to data 'raw' or 'validated'.

    Returns:
        mind_data (pd.DataFrame): Data from the Mind website.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: text_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
        nhs_data (pd.DataFrame): Data from the NHS website.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: text_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
    """
    git_checkout_folder(data_version, "data")
    pull_data()
    mind_df = pd.read_csv(os.path.join(DATA_DIR, f"mind_data_{data_postfix}.csv"))
    nhs_df = pd.read_csv(os.path.join(DATA_DIR, f"nhs_data_{data_postfix}.csv"))

    return mind_df, nhs_df
