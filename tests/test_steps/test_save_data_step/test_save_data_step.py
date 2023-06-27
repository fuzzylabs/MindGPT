"""Tests for save_data_step."""
from contextlib import nullcontext as does_not_raise
from unittest.mock import call, patch

import pandas as pd
import pytest
from azure.storage.blob import BlobClient
from steps.save_data.save_data_step import (
    SaveDataParameters,
    azure_upload_df,
    save_data,
)


@pytest.fixture(autouse=True)
def mock_blob_client() -> BlobClient:
    """Pytest fixture for mocking a blob client and connection string.

    Yields:
        BlobClient: Mocked Azure blob client
    """
    with patch("steps.save_data.save_data_step.BlobServiceClient") as mock_blob_service:
        # Mock container client
        mock_container_client = mock_blob_service.from_connection_string.return_value

        # Mock blob client for the container
        mock_blob_client = mock_container_client.get_blob_client.return_value

        yield mock_blob_client


@pytest.fixture
def mock_get_azure_connection_string() -> str:
    """Fixture for mocked Azure Storage connection string.

    Yields:
        str: Mock connection string
    """
    with patch(
        "steps.save_data.save_data_step.get_azure_connection_string"
    ) as get_azure_connection_string:
        get_azure_connection_string.return_value = "azure-connection-string"
        yield get_azure_connection_string


def test_azure_upload_df(
    mock_blob_client: BlobClient, mock_get_azure_connection_string: str
):
    """Test AzureStorage upload file function.

    Args:
        mock_blob_client (BlobServiceClient): Mocked blob service client
        mock_get_azure_connection_string (str): Mocked Azure Storage connection string
    """
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    azure_upload_df("scraped-data-store", df, "data", "nhs")

    # Check if upload_blob function is called exactly once with the data
    mock_blob_client.upload_blob.assert_called_once_with(
        "col1,col2\n1,3\n2,4\n", blob_type="BlockBlob"
    )


def test_save_data_step(
    mock_blob_client: BlobClient, mock_get_azure_connection_string: str
):
    """Test save data step works as expected.

    Args:
        mock_blob_client (BlobServiceClient): Mocked blob service client
        mock_get_azure_connection_string (str): Mocked Azure Storage connection string
    """
    nhs_df = pd.DataFrame({"NHS1": [1, 2], "NHS2": [3, 4]})
    mind_df = pd.DataFrame({"MIND1": [100, 200], "MIND2": [300, 400]})

    with does_not_raise():
        save_data.entrypoint(nhs_df, mind_df, SaveDataParameters())

    calls = [
        call("NHS1,NHS2\n1,3\n2,4\n", blob_type="BlockBlob"),
        call("MIND1,MIND2\n100,300\n200,400\n", blob_type="BlockBlob"),
    ]
    mock_blob_client.upload_blob.assert_has_calls(calls)
