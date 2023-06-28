"""Terraform utils file."""
import os
from dataclasses import dataclass

from python_terraform import Terraform


class TerraformOutputNotFoundError(Exception):
    """Terraform output not found exception, is raised when a required variable does not exist in the tf output.

    Args:
        Exception: Inherits from the exception class.
    """

    pass


@dataclass
class TerraformVariables:
    """TerraformVariables dataclass used for accessing Terraform output variables."""

    storage_connection_string: str
    terraform_client: Terraform

    def __init__(self) -> None:
        """TerraformVariables constructor.

        Raises:
            TerraformOutputNotFoundError: if specific Terraform outputs are not found
        """
        working_dir = os.path.join("terraform")
        var_file = os.path.join("terraform", "terraform.tfvars.json")

        self.terraform_client = Terraform(working_dir, var_file)

        tf_output = self.terraform_client.output()

        if tf_output is None:
            raise TerraformOutputNotFoundError(
                "Required Terraform outputs were not found. Ensure the required resources have been provisioned."
            )

        self.storage_connection_string = tf_output.get(
            "azure_storage_primary_connection_string", {}
        ).get("value")

        if self.storage_connection_string is None:
            raise TerraformOutputNotFoundError(
                "Azure Storage Connection String was not found. Ensure the required resources have been provisioned."
            )