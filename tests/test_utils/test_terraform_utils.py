"""Test Terraform utils file."""
import os
from unittest.mock import MagicMock, patch

import pytest
from utils.terraform_utils import TerraformOutputNotFoundError, TerraformVariables


def test_terraform_variables_is_created_correctly():
    """Test that the TerraformVariables dataclass constructor works as intended."""
    with patch("utils.terraform_utils.Terraform") as terraform:
        terraform_mock = MagicMock()
        terraform.return_value = terraform_mock
        terraform_mock.output.return_value = {
            "azure_storage_primary_connection_string": {"value": "test_value"}
        }

        terraform_vars = TerraformVariables(
            working_dir=os.path.join("terraform"),
            var_file=os.path.join("terraform", "terraform.tfvars.json"),
        )
        assert terraform_vars.storage_connection_string == "test_value"


def test_terraform_variables_with_no_connection_string_raises_exception():
    """Test that when initialising a TerraformVariables dataclass without the required Terraform outputs it raises an exception."""
    with patch("utils.terraform_utils.Terraform") as terraform:
        terraform_mock = MagicMock()
        terraform.return_value = terraform_mock
        terraform_mock.output.return_value = {
            "terraform_output": {"value": "test_value"}
        }

        with pytest.raises(TerraformOutputNotFoundError):
            TerraformVariables(
                working_dir=os.path.join("terraform"),
                var_file=os.path.join("terraform", "terraform.tfvars.json"),
            )


def test_terraform_variables_with_no_tf_output_raises_exception():
    """Test that when initialising a TerraformVariables dataclass without any Terraform outputs it raises an exception."""
    with patch("utils.terraform_utils.Terraform") as terraform:
        terraform_mock = MagicMock()
        terraform.return_value = terraform_mock
        terraform_mock.output.return_value = None

        with pytest.raises(TerraformOutputNotFoundError):
            TerraformVariables(
                working_dir=os.path.join("terraform"),
                var_file=os.path.join("terraform", "terraform.tfvars.json"),
            )
