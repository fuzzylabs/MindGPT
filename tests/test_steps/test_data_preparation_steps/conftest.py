"""Conftest for the data preparation steps."""
import os
from tempfile import TemporaryDirectory
from typing import Iterator, Tuple
from unittest.mock import MagicMock, patch

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


@pytest.fixture
def mocked_read_data(sample_scraping_data: Tuple[DataFrame, DataFrame]) -> MagicMock:
    """Mocked _read_data function from the load_data step.

    Args:
        sample_scraping_data: sample data which is used as the return value of the mocked function.

    Yields:
        MagicMock: the mocked function.
    """
    with patch(f"{LOAD_DATA_STEP}._read_data") as read_data:
        read_data.return_value = sample_scraping_data
        yield read_data


@pytest.fixture
def directory_for_testing() -> Iterator[str]:
    """A directory for testing purposes.

    Yields:
        Iterator[str]: the name of the directory.
    """
    temp_directory = TemporaryDirectory()
    original_directory = os.getcwd()

    yield temp_directory.name

    os.chdir(original_directory)
    temp_directory.cleanup()
