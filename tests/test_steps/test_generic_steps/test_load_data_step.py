"""Test load data step."""
import os
from typing import Tuple
from unittest import mock
from unittest.mock import patch

import pytest
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from steps.generic_steps import load_data


@pytest.fixture
def mock_git_checkout_folder():
    """Mock git checkout folder function.

    Yields:
        git_checkout_folder (mock.MagicMock): Mocked git_checkout_folder function.
    """
    with patch(
        "steps.generic_steps.load_data_step.load_data_step.git_checkout_folder"
    ) as git_checkout_folder:
        yield git_checkout_folder


@pytest.fixture
def mock_pull_data():
    """Mock pull_data function.

    Yields:
        pull_data (mock.MagicMock): Mocked pull_data function.
    """
    with patch(
        "steps.generic_steps.load_data_step.load_data_step.pull_data"
    ) as pull_data:
        yield pull_data


@pytest.fixture(autouse=True)
def mock_project_root_directory(directory_for_testing: str):
    """Mocked PROJECT_ROOT_DIR constant.

    Args:
        directory_for_testing (str): Mocked local directory.

    Yields:
        mock_project_root_dir (mock.MagicMock): Mocked directory.
    """
    with mock.patch(
        "utils.data_version_control.PROJECT_ROOT_DIR", directory_for_testing
    ) as mock_project_root_dir:
        yield mock_project_root_dir


@pytest.fixture(autouse=True)
def mock_project_data_directory(directory_for_testing: str):
    """Mocked DATA_DIR constant.

    Args:
        directory_for_testing (str): Mocked local directory.

    Yields:
        mock_data_dir (mock.MagicMock): Mocked data directory.
    """
    with mock.patch(
        "steps.generic_steps.load_data_step.load_data_step.DATA_DIR",
        os.path.join(directory_for_testing, "data"),
    ) as mock_data_dir:
        yield mock_data_dir


def test_load_data(
    directory_for_testing: str,
    sample_scraping_data: Tuple[DataFrame, DataFrame],
    mock_git_checkout_folder: mock.MagicMock,
    mock_pull_data: mock.MagicMock,
):
    """Tests that the correct functions are called when loading data.

    Args:
        directory_for_testing (str): Mock testing directory.
        sample_scraping_data (Tuple[DataFrame, DataFrame]): Mock DataFrames for saving/loading.
        mock_git_checkout_folder (mock.MagicMock): Mocked git_checkout_folder function.
        mock_pull_data (mock.MagicMock): Mocked pull_data function.
    """
    data_location = os.path.join(directory_for_testing, "data")
    os.mkdir(data_location)
    mind, nhs = sample_scraping_data
    mind.to_csv(f"{data_location}/mind_data_raw.csv", index=False)
    nhs.to_csv(f"{data_location}/nhs_data_raw.csv", index=False)

    loaded_mind_df, loaded_nhs_df = load_data(data_version="test", data_postfix="raw")

    mock_git_checkout_folder.assert_called_once()
    mock_pull_data.assert_called_once()
    assert_frame_equal(mind, loaded_mind_df)
    assert_frame_equal(nhs, loaded_nhs_df)


def test_load_data_raises_exception_when_data_does_not_exist(
    directory_for_testing: str,
    mock_git_checkout_folder: mock.MagicMock,
    mock_pull_data: mock.MagicMock,
):
    """Tests that an error is raised when required data files do not exist.

    Args:
        directory_for_testing (str): Mock testing directory.
        sample_scraping_data (Tuple[DataFrame, DataFrame]): Mock DataFrames for saving/loading.
        mock_git_checkout_folder (mock.MagicMock): Mocked git_checkout_folder function.
        mock_pull_data (mock.MagicMock): Mocked pull_data function.
    """
    data_location = os.path.join(directory_for_testing, "data")
    os.mkdir(data_location)

    with pytest.raises(FileNotFoundError) as e:
        _, _ = load_data(data_version="test", data_postfix="raw")

        assert (
            "Required CSV files do not exist in 'data' folder, ensure the previous pipeline has been run."
            in str(e)
        )

    mock_git_checkout_folder.assert_called_once()
    mock_pull_data.assert_called_once()


def test_load_data_raises_exception_when_data_directory_does_not_exist(
    mock_git_checkout_folder: mock.MagicMock, mock_pull_data: mock.MagicMock
):
    """Tests that an error is raised when the data folder does not exist.

    Args:
        mock_git_checkout_folder (mock.MagicMock): Mocked git_checkout_folder function.
        mock_pull_data (mock.MagicMock): Mocked pull_data function.
    """
    mock_git_checkout_folder.side_effect = FileNotFoundError(
        "Folder with the name 'data' does not exist."
    )

    with pytest.raises(FileNotFoundError) as e:
        _, _ = load_data(data_version="test", data_postfix="raw")

        assert "Folder with the name 'data' does not exist." in str(e)

    mock_git_checkout_folder.assert_called_once()
    mock_pull_data.assert_not_called()
