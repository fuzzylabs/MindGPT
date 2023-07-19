"""Tests for the data version control functionality."""
import os
from unittest import mock

import pytest
from utils import (
    add_and_commit_dvc_files_to_git,
    add_csv_files_to_dvc,
    git_checkout_folder,
)


def test_file_not_found_error_csv(directory_for_testing):
    """Test that the add_csv_files_to_dvc function raises an error when the files don't exist."""
    test_paths = [
        os.path.join(directory_for_testing, "afile.csv"),
        os.path.join(directory_for_testing, "anotherfile.csv"),
    ]
    with pytest.raises(FileNotFoundError):
        add_csv_files_to_dvc(test_paths)


def test_file_not_found_error_dvc(directory_for_testing):
    """Test that the add_and_commit_dvc_files_to_git function raises an error when the files don't exist."""
    test_paths = [
        os.path.join(directory_for_testing, "afile.csv.dvc"),
        os.path.join(directory_for_testing, "anotherfile.csv.dvc"),
    ]
    with pytest.raises(FileNotFoundError):
        add_and_commit_dvc_files_to_git(test_paths)


def test_git_checkout_folder_raises_file_not_found_error_without_directory(
    directory_for_testing,
):
    """Test the git_checkout_folder function raises a FileNotFound exception when the specified directory does not exist.

    Args:
        directory_for_testing (str): Path to testing directory.
    """
    with mock.patch(
        "utils.data_version_control.git.cmd.Git"
    ) as mock_git_command, mock.patch(
        "utils.data_version_control.git_tag_exists"
    ) as mock_git_tag_exists, mock.patch(
        "utils.data_version_control.git_commit_hash_exists"
    ) as mock_git_commit_hash_exists, mock.patch(
        "utils.data_version_control.PROJECT_ROOT_DIR", directory_for_testing
    ):
        mock_git_command.return_value = mock.MagicMock()
        mock_git_tag_exists.return_value = True
        mock_git_commit_hash_exists.return_value = True

        with pytest.raises(FileNotFoundError):
            git_checkout_folder(tag_name="version1", folder_name="data")
