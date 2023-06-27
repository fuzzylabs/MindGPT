"""Terraform utils file."""
from dataclasses import dataclass
from typing import Optional

from python_terraform import Terraform


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
