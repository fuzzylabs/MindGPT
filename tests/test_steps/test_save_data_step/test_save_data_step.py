"""Tests for save_data_step."""
from unittest.mock import patch

import pandas as pd
import pytest
from azure.storage.blob import BlobServiceClient
from steps.save_data.save_data_step import azure_upload_df


@pytest.fixture
def mock_blob_service() -> BlobServiceClient:
    """Pytest fixture for mocking a blob service client and connection string.

    Yields:
        BlobServiceClient: Mocked blob service client
    """
    with patch("steps.save_data.save_data_step.BlobServiceClient") as mock_blob_service:
        yield mock_blob_service


def test_azure_upload_df(
    mock_blob_service: BlobServiceClient,
):
    """Test AzureStorage upload file function.

    Args:
        mock_blob_service (BlobServiceClient): Mocked blob service client
    """
    # Mock container client
    mock_container_client = mock_blob_service.from_connection_string.return_value

    # Mock blob client
    mock_blob_client = mock_container_client.get_blob_client.return_value

    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    azure_upload_df("scraped-data-store", df, "nhs_data", "nhs")

    # Check if upload_blob function is called exactly once with the data
    mock_blob_client.upload_blob.assert_called_once_with(
        "col1,col2\n1,3\n2,4\n", blob_type="BlockBlob"
    )
