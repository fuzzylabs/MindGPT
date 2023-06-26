"""Save the scraped data as CSV and push to bucket."""
import os

import pandas as pd
import python_terraform
from azure.storage.blob import BlobServiceClient
from zenml.steps import BaseParameters, step


class SaveDataParameters(BaseParameters):
    """Save Data parameters."""

    # Path to the data folder to save the data within the Azure Blob Storage container
    data_base_dir: str = "raw_scraped_data"

    # Name of the Azure Blob Storage container
    container: str = "scraped_data_store"


@step
def save_data(
    nhs_data_scraped: pd.DataFrame,
    mind_data_scraped: pd.DataFrame,
    params: SaveDataParameters,
) -> None:
    """Save data as CSVs and push to storage bucket.

    Args:
        nhs_data_scraped (pd.DataFrame): NHS data to push.
        mind_data_scraped (pd.DataFrame): Mind data to push.
        params (SaveDataParameters): ZenML step parameters.
    """
    azure_upload_df(params.container, nhs_data_scraped, params.data_base_dir, "nhs")
    azure_upload_df(params.container, mind_data_scraped, params.data_base_dir, "mind")


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
    if all([container, len(dataframe), data_path, filename]):
        upload_file_path = os.path.join(data_path, f"{filename}.csv")
        connect_str = get_azure_connection_string()
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(
            container=container, blob=upload_file_path
        )
        output = dataframe.to_csv(index=False, encoding="utf-8")

        blob_client.upload_blob(output, blob_type="BlockBlob")


def get_azure_connection_string() -> str:
    """Gets the Azure Storage connection string from Terraform outputs.

    TODO: Move to a utils/common functions file

    Returns:
        str: Azure connection string for accessing the provisioned blob storage
    """
    terraform_client = python_terraform.Terraform(
        working_dir=os.path.join("terraform"),
        var_file=os.path.join("terraform", "terraform.tfvars.json"),
    )

    tf_output = terraform_client.output()

    if tf_output is not None:
        return str(
            tf_output.get("azure_storage_primary_connection_string").get("value")
        )

    raise Exception(
        "Unable to fetch Azure storage connection string, ensure the storage account is deployed"
    )
