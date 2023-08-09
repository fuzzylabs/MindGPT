"""Load data step (data prep pipeline and embedding pipeline)."""
import os
from typing import Tuple

import pandas as pd
from config import DATA_DIR
from utils.data_version_control import files_exist, git_checkout_folder, pull_data
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def load_data(
    data_version: str,
    data_postfix: str,
    reference_data_version: str = "data/first_version",
) -> Tuple[str, str, pd.DataFrame, pd.DataFrame]:
    """Load two CSVs from the "data/" directory. If no data exists, pull from the DVC storage bucket prior to loading.

    Args:
        data_version (str): Data version tag or commit hash for Git/DVC.
        data_postfix (str): Postfix to data 'raw' or 'validated'.
        reference_data_version (str): The reference data version for computing embedding drift. Defaults to "data/first_version".

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
    git_checkout_folder(tag_name=data_version, folder_name="data")
    pull_data()

    mind_file_path = os.path.join(DATA_DIR, f"mind_data_{data_postfix}.csv")
    nhs_file_path = os.path.join(DATA_DIR, f"nhs_data_{data_postfix}.csv")

    files_exist(
        [mind_file_path, nhs_file_path],
        error_message="Required CSV files do not exist in 'data' folder, ensure the previous pipeline has been run.",
    )

    mind_df = pd.read_csv(mind_file_path)
    nhs_df = pd.read_csv(nhs_file_path)

    return data_version, reference_data_version, mind_df, nhs_df
