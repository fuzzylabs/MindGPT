"""Load data step (data prep pipeline)."""

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
        Tuple[pd.DataFrame, pd.DataFrame]: the two raw datasets.
    """
    mind_df = pd.read_csv(os.path.join(DATA_DIR, "mind_data_raw.csv"))
    nhs_df = pd.read_csv(os.path.join(DATA_DIR, "nhs_data_raw.csv"))

    return mind_df, nhs_df


@step
def load_data() -> Output(mind_df=pd.DataFrame, nhs_df=pd.DataFrame):  # type: ignore
    """Loads the data from the data/ directory.

    Returns:
        mind_data (pd.DataFrame): Raw scraped data from the Mind website
        nhs_data (pd.DataFrame): Raw scraped data from the NHS website
    """
    mind_df, nhs_df = _read_data()

    return mind_df, nhs_df
