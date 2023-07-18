"""Test load data step."""
import os
from typing import Tuple
from unittest.mock import patch

from pandas import DataFrame
from pandas.testing import assert_frame_equal
from steps.generic_steps import load_data


def test_load_data(
    directory_for_testing: str, sample_scraping_data: Tuple[DataFrame, DataFrame]
):
    """Tests that the correct functions are called when loading data.

    Args:
        directory_for_testing (str): Mock testing directory.
        sample_scraping_data (Tuple[DataFrame, DataFrame]): Mock DataFrames for saving/loading.
    """
    data_location = os.path.join(directory_for_testing, "data")
    os.mkdir(data_location)
    mind, nhs = sample_scraping_data
    mind.to_csv(f"{data_location}/mind_data_raw.csv", index=False)
    nhs.to_csv(f"{data_location}/nhs_data_raw.csv", index=False)

    with patch(
        "steps.generic_steps.load_data_step.load_data_step.git_checkout_folder"
    ) as git_checkout_folder, patch(
        "steps.generic_steps.load_data_step.load_data_step.pull_data"
    ) as pull_data, patch(
        "steps.generic_steps.load_data_step.load_data_step.DATA_DIR", data_location
    ):
        loaded_mind_df, loaded_nhs_df = load_data(
            data_version="test", data_postfix="raw"
        )

        git_checkout_folder.assert_called_once()
        pull_data.assert_called_once_with()
        assert_frame_equal(mind, loaded_mind_df)
        assert_frame_equal(nhs, loaded_nhs_df)
