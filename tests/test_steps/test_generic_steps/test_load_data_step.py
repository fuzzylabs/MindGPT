"""Test load data step."""
import os
from typing import Tuple
from unittest.mock import patch

import pytest
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
        pull_data.assert_called_once()
        assert_frame_equal(mind, loaded_mind_df)
        assert_frame_equal(nhs, loaded_nhs_df)


def test_load_data_raises_exception_when_data_does_not_exist(
    directory_for_testing: str,
):
    """Tests that an error is raised when required data files do not exist.

    Args:
        directory_for_testing (str): Mock testing directory.
        sample_scraping_data (Tuple[DataFrame, DataFrame]): Mock DataFrames for saving/loading.
    """
    data_location = os.path.join(directory_for_testing, "data")
    os.mkdir(data_location)

    with patch(
        "steps.generic_steps.load_data_step.load_data_step.git_checkout_folder"
    ) as git_checkout_folder, patch(
        "steps.generic_steps.load_data_step.load_data_step.pull_data"
    ) as pull_data, patch(
        "steps.generic_steps.load_data_step.load_data_step.DATA_DIR", data_location
    ):
        with pytest.raises(FileNotFoundError) as e:
            _, _ = load_data(data_version="test", data_postfix="raw")

            assert (
                "Required CSV files do not exist in 'data' folder, ensure the previous pipeline has been run."
                in str(e)
            )

        git_checkout_folder.assert_called_once()
        pull_data.assert_called_once()


def test_load_data_raises_exception_when_data_directory_does_not_exist(
    directory_for_testing: str,
):
    """Tests that an error is raised when the data folder does not exist.

    Args:
        directory_for_testing (str): Mock testing directory.
        sample_scraping_data (Tuple[DataFrame, DataFrame]): Mock DataFrames for saving/loading.
    """
    data_location = os.path.join(directory_for_testing, "data")

    with patch(
        "steps.generic_steps.load_data_step.load_data_step.git_checkout_folder"
    ) as git_checkout_folder, patch(
        "steps.generic_steps.load_data_step.load_data_step.pull_data"
    ) as pull_data, patch(
        "steps.generic_steps.load_data_step.load_data_step.DATA_DIR", data_location
    ):
        git_checkout_folder.side_effect = FileNotFoundError(
            "Folder with the name 'data' does not exist."
        )

        with pytest.raises(FileNotFoundError) as e:
            _, _ = load_data(data_version="test", data_postfix="raw")

            assert "Folder with the name 'data' does not exist." in str(e)

        git_checkout_folder.assert_called_once()
        pull_data.assert_not_called()
