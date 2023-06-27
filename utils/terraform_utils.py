"""Terraform utils file."""
from dataclasses import dataclass
from typing import Optional

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
    terraform_client: Optional[Terraform] = None

    def __init__(self, working_dir: str, var_file: str):
        """TerraformVariables constructor.

        Args:
            working_dir (str): Path to Terraform working directory.
            var_file (str): Path to Terraform variables file.

        Raises:
            Exception: if specific Terraform outputs are not found
        """
        self.terraform_client = Terraform(working_dir, var_file)

        tf_output = self.terraform_client.output()
        if (
            tf_output is not None
            and tf_output.get("azure_storage_primary_connection_string") is not None
        ):
            self.storage_connection_string = str(
                tf_output.get("azure_storage_primary_connection_string").get("value")
            )
        else:
            raise TerraformOutputNotFoundError(
                "Required Terraform outputs were not found. Ensure the required resources have been provisioned."
            )
