"""Tests for the data version control functionality."""
import os

import pytest
from utils import add_and_commit_dvc_files_to_git, add_csv_files_to_dvc


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
