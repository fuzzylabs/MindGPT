"""Save the scraped data as CSV and push to bucket."""
import os
from datetime import datetime
from enum import Enum

import pandas as pd
from azure.storage.blob import BlobServiceClient
from utils.constants import DATE_TIME_FORMAT
from utils.terraform_utils import TerraformVariables
from zenml.steps import BaseParameters, step


class DataStorageLocation(str, Enum):
    """DataStorageLocation enum of valid locations.

    Args:
        str: Inherits from str class
        Enum: Inherits from Enum class
    """

    AZURE = "azure"
    LOCAL = "local"


class SaveDataParameters(BaseParameters):
    """Save Data parameters."""

    # Location of data store
    data_location = DataStorageLocation.LOCAL

    # Path to the data folder (Local or Azure)
    data_base_dir: str = "raw_scraped_data"

    # Name of the Azure Blob Storage container, only required if using Azure Storage
    container: str = "scraped-data-store"


def azure_upload_df(
    container: str, dataframe: pd.DataFrame, data_path: str, filename: str
) -> None:
    """Upload Pandas DataFrame as a csv to Azure Blob Storage container.

    Args:
        container (str): the container name
        dataframe (pd.DataFrame): the DataFrame object
        data_path (str): the path to save the data within the blob storage container
        filename (str): the filename to use for the blob
    """
    if len(dataframe):
        upload_file_path = os.path.join(data_path, f"{filename}.csv")
        terraform_vars = TerraformVariables()
        blob_service_client = BlobServiceClient.from_connection_string(
            terraform_vars.storage_connection_string
        )
        blob_client = blob_service_client.get_blob_client(
            container=container, blob=upload_file_path
        )
        output = dataframe.to_csv(index=False, encoding="utf-8")

        blob_client.upload_blob(output, blob_type="BlockBlob")


def save_df_local(dataframe: pd.DataFrame, data_path: str, filename: str) -> None:
    """Upload Pandas DataFrame as a csv to Azure Blob Storage container.

    Args:
        dataframe (pd.DataFrame): the DataFrame object
        data_path (str): the path to save the data within the local storage
        filename (str): the filename to use for the blob
    """
    if len(dataframe):
        upload_file_dir = os.path.join("data", data_path)

        # Create directories
        if not os.path.exists(upload_file_dir):
            os.makedirs(upload_file_dir)

        upload_file_path = os.path.join(upload_file_dir, f"{filename}.csv")
        output = dataframe.to_csv(index=False, encoding="utf-8")

        with open(upload_file_path, "w") as f:
            f.write(output)


@step
def save_data(
    nhs_data_scraped: pd.DataFrame,
    mind_data_scraped: pd.DataFrame,
    params: SaveDataParameters,
) -> None:
    """Save data as CSVs and save to specified location.

    Args:
        nhs_data_scraped (pd.DataFrame): NHS data to save.
        mind_data_scraped (pd.DataFrame): Mind data to save.
        params (SaveDataParameters): ZenML step parameters.
    """
    # Add DateTime directory to where the data will be saved
    current_datetime = datetime.now().strftime(DATE_TIME_FORMAT)
    data_base_dir = os.path.join(params.data_base_dir, str(current_datetime))

    if params.data_location == DataStorageLocation.AZURE:
        azure_upload_df(params.container, nhs_data_scraped, data_base_dir, "nhs")
        azure_upload_df(params.container, mind_data_scraped, data_base_dir, "mind")
    elif params.data_location == DataStorageLocation.LOCAL:
        save_df_local(nhs_data_scraped, data_base_dir, "nhs")
        save_df_local(mind_data_scraped, data_base_dir, "mind")
