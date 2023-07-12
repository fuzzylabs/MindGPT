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

    Note: this will need updating in the subsequent integration of DVC proper.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: the two raw datasets
    """
    mind_df = pd.read_csv(os.path.join(DATA_DIR, "mind_data_raw.csv"))
    nhs_df = pd.read_csv(os.path.join(DATA_DIR, "nhs_data_raw.csv"))

    return mind_df, nhs_df


@step
def load_data(pipeline_name: str = "pipeline") -> Output(mind_df=pd.DataFrame, nhs_df=pd.DataFrame):  # type: ignore
    """Loads the data from the output of the last run of the data_scraping_pipeline.

    Args:
        pipeline_name (str): Name of pipeline to get raw scraped data from
        data_state (str): The state of the data. Either 'raw' or 'validated'

    Returns:
        mind_data (pd.DataFrame): Raw scraped data from the Mind website
        nhs_data (pd.DataFrame): Raw scraped data from the NHS website
    """
    mind_df, nhs_df = _read_data()

    return mind_df, nhs_df
