"""Tests for the data version control functionality."""
import os

import pytest
from config import PROJECT_ROOT_DIR
from utils import add_and_commit_dvc_files_to_git, add_csv_files_to_dvc

DUMMY_DATA_DIR = os.path.join(PROJECT_ROOT_DIR, "tests/test_utils/dummy_data_directory")


def test_file_not_found_error_csv():
    """Test that the add_csv_files_to_dvc function raises an error when the files don't exist."""
    test_paths = [
        os.path.join(DUMMY_DATA_DIR, "afile.csv"),
        os.path.join(DUMMY_DATA_DIR, "anotherfile.csv"),
    ]
    with pytest.raises(FileNotFoundError):
        add_csv_files_to_dvc(test_paths)


def test_file_not_found_error_dvc():
    """Test that the add_and_commit_dvc_files_to_git function raises an error when the files don't exist."""
    test_paths = [
        os.path.join(DUMMY_DATA_DIR, "afile.csv.dvc"),
        os.path.join(DUMMY_DATA_DIR, "anotherfile.csv.dvc"),
    ]
    with pytest.raises(FileNotFoundError):
        add_and_commit_dvc_files_to_git(test_paths)
