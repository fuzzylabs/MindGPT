"""Tests for save_data_step."""
import os
import tempfile
from contextlib import nullcontext as does_not_raise
from typing import Iterator
from unittest.mock import MagicMock, call, patch

import pandas as pd
import pytest
from azure.storage.blob import BlobClient
from freezegun import freeze_time
from steps.save_data.save_data_step import (
    DataStorageLocation,
    SaveDataParameters,
    azure_upload_df,
    save_data,
    save_df_local,
)
from utils.terraform_utils import TerraformVariables


@pytest.fixture(autouse=True)
def mock_terraform_variables() -> TerraformVariables:
    """Fixture for mocked Terraform output variables.

    Yields:
        TerraformVariables: Mock Terraform output variables
    """
    with patch(
        "steps.save_data.save_data_step.TerraformVariables"
    ) as mock_terraform_variables:
        mock_instance = MagicMock()
        mock_terraform_variables.return_value = mock_instance
        mock_instance.connection_string = "azure-connection-string"
        yield mock_terraform_variables


@pytest.fixture
def mock_local_testing_directory() -> Iterator[str]:
    """A fixture for creating and removing temporary test directory for storing and moving files.

    Yields:
        str: a path to temporary directory for storing and moving files from tests.
    """
    temp_dir = tempfile.TemporaryDirectory()
    original_working_directory = (
        os.getcwd()
    )  # save in case a test changes to temp directory which will be deleted

    # tests are executed at this point
    yield temp_dir.name

    # delete temp folder
    os.chdir(original_working_directory)  # restore original working directory
    temp_dir.cleanup()


@pytest.fixture()
def mock_blob_client() -> BlobClient:
    """Pytest fixture for mocking an Azure blob client and connection string.

    Yields:
        BlobClient: Mocked Azure blob client
    """
    with patch("steps.save_data.save_data_step.BlobServiceClient") as mock_blob_service:
        # Mock container client
        mock_container_client = mock_blob_service.from_connection_string.return_value

        # Mock blob client for the container
        mock_blob_client = mock_container_client.get_blob_client.return_value

        yield mock_blob_client


@pytest.fixture(autouse=True)
def mock_save_data_parameters() -> SaveDataParameters:
    """Mock step parameters.

    Returns:
        SaveDataParameters: Step parameters.
    """
    params = SaveDataParameters()
    params.data_location = DataStorageLocation.AZURE
    params.data_base_dir = "raw_scraped_data"
    params.container = "blob_storage_container"
    yield params


@pytest.fixture()
def nhs_dataframe() -> pd.DataFrame:
    """NHS mock dataframe.

    Returns:
        pd.DataFrame: Mock dataframe
    """
    return pd.DataFrame({"NHS1": [1, 2], "NHS2": [3, 4]})


@pytest.fixture()
def mind_dataframe() -> pd.DataFrame:
    """Mind mock dataframe.

    Returns:
        pd.DataFrame: Mock dataframe
    """
    return pd.DataFrame({"MIND1": [100, 200], "MIND2": [300, 400]})


def test_azure_upload_df(mock_blob_client: BlobClient, nhs_dataframe: pd.DataFrame):
    """Test AzureStorage upload file function.

    Args:
        mock_blob_client (BlobClient): Mocked Azure blob client
        nhs_dataframe (pd.DataFrame): Mocked "NHS" data in dataframe
    """
    azure_upload_df("scraped-data-store", nhs_dataframe, "data", "nhs")

    # Check if upload_blob function is called exactly once with the data
    mock_blob_client.upload_blob.assert_called_once_with(
        "NHS1,NHS2\n1,3\n2,4\n", blob_type="BlockBlob"
    )


def test_save_data_step_azure(
    mock_blob_client: BlobClient,
    nhs_dataframe: pd.DataFrame,
    mind_dataframe: pd.DataFrame,
    mock_save_data_parameters: SaveDataParameters,
):
    """Test save data step works as expected using Azure tools.

    Args:
        mock_blob_client (BlobClient): Mocked Azure blob client
        nhs_dataframe (pd.DataFrame): Mocked "NHS" data in dataframe
        mind_dataframe (pd.DataFrame): Mocked "Mind" data in dataframe
        mock_save_data_parameters (SaveDataParameters): Mocked step parameters
    """
    with does_not_raise():
        save_data.entrypoint(nhs_dataframe, mind_dataframe, mock_save_data_parameters)

    calls = [
        call("NHS1,NHS2\n1,3\n2,4\n", blob_type="BlockBlob"),
        call("MIND1,MIND2\n100,300\n200,400\n", blob_type="BlockBlob"),
    ]

    mock_blob_client.upload_blob.assert_has_calls(calls)


@freeze_time("1066-10-14")
def test_save_data_step_local(
    nhs_dataframe: pd.DataFrame,
    mind_dataframe: pd.DataFrame,
    mock_save_data_parameters: SaveDataParameters,
    mock_local_testing_directory: str,
):
    """Test save data step works as expected locally.

    Args:
        nhs_dataframe (pd.DataFrame): Mocked "NHS" data in dataframe
        mind_dataframe (pd.DataFrame): Mocked "Mind" data in dataframe
        mock_save_data_parameters (SaveDataParameters): Mocked step parameters
        mock_local_testing_directory (str): Location of temporary local directory for testing
    """
    os.chdir(mock_local_testing_directory)
    mock_save_data_parameters.data_location = DataStorageLocation.LOCAL

    with does_not_raise():
        save_data.entrypoint(nhs_dataframe, mind_dataframe, mock_save_data_parameters)

    with open(
        os.path.join(
            mock_local_testing_directory,
            "data",
            mock_save_data_parameters.data_base_dir,
            "1066_10_14-00_00_00",
            "nhs.csv",
        )
    ) as f:
        assert f.read() == "NHS1,NHS2\n1,3\n2,4\n"


def test_save_df_local(nhs_dataframe: pd.DataFrame, mock_local_testing_directory: str):
    """Test local save dataframe function.

    Args:
        nhs_dataframe (pd.DataFrame): Mocked "NHS" data in dataframe
        mock_local_testing_directory (str): Location of temporary local directory for testing
    """
    os.chdir(mock_local_testing_directory)
    save_df_local(nhs_dataframe, "raw_scraped_data", "nhs")
    with open(
        os.path.join(
            mock_local_testing_directory, "data", "raw_scraped_data", "nhs.csv"
        )
    ) as f:
        assert f.read() == "NHS1,NHS2\n1,3\n2,4\n"


def test_empty_dataframe_not_uploaded(mock_blob_client: BlobClient):
    """Assert that empty dataframes are not uploaded to Azure.

    Args:
        mock_blob_client (BlobClient): Mocked Azure blob client
    """
    df = pd.DataFrame()
    with does_not_raise():
        azure_upload_df("scraped-data-store", df, "data", "nhs")

    mock_blob_client.upload_blob.assert_not_called()
