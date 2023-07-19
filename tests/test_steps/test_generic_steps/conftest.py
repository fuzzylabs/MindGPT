"""Conftest for the generic steps."""
from typing import Tuple

import pytest
from pandas import DataFrame

LOAD_DATA_STEP = "steps.data_preparation_steps.load_data_step.load_data_step"


@pytest.fixture
def sample_scraping_data() -> Tuple[DataFrame, DataFrame]:
    """Mocked data to emulate the result of the scraping pipeline.

    Returns:
        Tuple[DataFrame, DataFrame]: the two mocked dataframes with toy data.
    """
    return (
        DataFrame(
            {
                "text_scraped": ["sample text", "more sample text"],
                "url": ["www.mind.org.uk", "www.mind.org.uk"],
            }
        ),
        DataFrame(
            {
                "text_scraped": ["additional text", "more additional text"],
                "url": ["www.nhs.uk", "www.nhs.uk"],
            }
        ),
    )
