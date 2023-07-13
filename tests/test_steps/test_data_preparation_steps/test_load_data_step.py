"""Test load data step file."""

from typing import Tuple
from unittest.mock import MagicMock

from pandas import DataFrame
from pandas.testing import assert_frame_equal
from steps.data_preparation_steps.load_data_step.load_data_step import load_data


def test_load_data_step_new(
    sample_scraping_data: Tuple[DataFrame, DataFrame], mocked_read_data: MagicMock
):
    """Test that the load data step reads in the expected dataframes.

    Args:
        sample_scraping_data: mocked data to emulate the result of the scraping pipeline.
        mocked_read_data: mocked _read_data function from the load_data step.
    """
    sample_data_one, sample_data_two = sample_scraping_data
    mocked_mind_df, mocked_nhs_df = load_data()

    assert_frame_equal(mocked_mind_df, sample_data_one)
    assert_frame_equal(mocked_nhs_df, sample_data_two)
