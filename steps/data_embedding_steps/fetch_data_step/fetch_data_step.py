"""Fetch data step (data embedding pipeline)."""
import os
from typing import Tuple

import pandas as pd
from config import DATA_DIR
from zenml import step
from zenml.logger import get_logger
from zenml.steps import Output

logger = get_logger(__name__)


def _read_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Read in the data from the data directory.

    Note:
        This will need updating as part of the full implementation of DVC. This includes either pulling the latest
        version of data or a specific version.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: the two cleaned and validated datasets.
    """
    mind_df = pd.read_csv(os.path.join(DATA_DIR, "mind_data_validated.csv"))
    nhs_df = pd.read_csv(os.path.join(DATA_DIR, "nhs_data_validated.csv"))

    return mind_df, nhs_df


@step
def fetch_data(data_version: str) -> Output(mind_df=pd.DataFrame, nhs_df=pd.DataFrame):  # type: ignore
    """Load the cleaned and prepared data from the data/ directory. If no data exists, pull from the DVC storage bucket prior to loading.

    Args:
        data_version (str): Name of DVC data version to pull data from.

    Returns:
        mind_data (pd.DataFrame): Data from the Mind website.
        nhs_data (pd.DataFrame): Data from the NHS website.
    """
    mind_df, nhs_df = _read_data()

    return mind_df, nhs_df
