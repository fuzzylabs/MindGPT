"""Tests for save_data_step."""
from contextlib import nullcontext as does_not_raise
from unittest.mock import MagicMock, call, patch

import pandas as pd
import pytest
from azure.storage.blob import BlobClient
from steps.save_data.save_data_step import (
    SaveDataParameters,
    azure_upload_df,
    save_data,
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


def test_save_data_step(
    mock_blob_client: BlobClient,
    nhs_dataframe: pd.DataFrame,
    mind_dataframe: pd.DataFrame,
):
    """Test save data step works as expected.

    Args:
        mock_blob_client (BlobClient): Mocked Azure blob client
        nhs_dataframe (pd.DataFrame): Mocked "NHS" data in dataframe
        mind_dataframe (pd.DataFrame): Mocked "Mind" data in dataframe
    """
    with does_not_raise():
        save_data.entrypoint(nhs_dataframe, mind_dataframe, SaveDataParameters())

    calls = [
        call("NHS1,NHS2\n1,3\n2,4\n", blob_type="BlockBlob"),
        call("MIND1,MIND2\n100,300\n200,400\n", blob_type="BlockBlob"),
    ]

    mock_blob_client.upload_blob.assert_has_calls(calls)


def test_empty_dataframe_not_uploaded(mock_blob_client: BlobClient):
    """Assert that empty dataframes are not uploaded to Azure.

    Args:
        mock_blob_client (BlobClient): Mocked Azure blob client
    """
    df = pd.DataFrame()
    with does_not_raise():
        azure_upload_df("scraped-data-store", df, "data", "nhs")

    mock_blob_client.upload_blob.assert_not_called()
