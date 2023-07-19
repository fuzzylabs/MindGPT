"""Tests for the data version control functionality."""
import os
from unittest import mock

import pytest
from utils import (
    add_and_commit_dvc_files_to_git,
    add_csv_files_to_dvc,
    git_checkout_folder,
)
from utils.data_version_control import _git_commit_hash_exists, _git_tag_exists


@pytest.fixture
def mock_git_repo():
    """Mock git repo object.

    Yields:
        mocked_git_repo: Mocked git repo.
    """
    with mock.patch("utils.data_version_control.git.Repo") as git_repo:
        yield git_repo


@pytest.fixture
def mock_git_command():
    """Mock git command object.

    Yields:
        mocked_git_repo: Mocked git command.
    """
    with mock.patch("utils.data_version_control.git.cmd.Git") as git_command:
        yield git_command


@pytest.fixture(autouse=True)
def mock_project_root_directory(directory_for_testing: str):
    """Mocked PROJECT_ROOT_DIR constant.

    Args:
        directory_for_testing (str): Mocked local directory.

    Yields:
        mock_project_root_dir (str): Mocked directory name
    """
    with mock.patch(
        "utils.data_version_control.PROJECT_ROOT_DIR", directory_for_testing
    ) as mock_project_root_dir:
        yield mock_project_root_dir


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
    mock_git_command,
):
    """Test the git_checkout_folder function raises a FileNotFound exception when the specified directory does not exist.

    Args:
        directory_for_testing (str): Path to testing directory.
        mock_git_command (mock.MagicMock()): Mocked git command object.
    """
    with mock.patch(
        "utils.data_version_control._git_tag_exists"
    ) as mock_git_tag_exists, mock.patch(
        "utils.data_version_control._git_commit_hash_exists"
    ) as mock_git_commit_hash_exists:
        mock_git_command.return_value = mock.MagicMock()
        mock_git_tag_exists.return_value = True
        mock_git_commit_hash_exists.return_value = True

        with pytest.raises(FileNotFoundError):
            git_checkout_folder(tag_name="version1", folder_name="data")


def test_git_checkout_folder_raises_vaue_error_invalid_tag(
    directory_for_testing,
    mock_git_command,
):
    """Test the git_checkout_folder function raises ValueError when the tag is invalid.

    Args:
        directory_for_testing (str): Path to testing directory.
        mock_git_command (mock.MagicMock()): Mocked git command object.
    """
    data_path = os.path.join(directory_for_testing, "data")
    os.mkdir(data_path)
    with mock.patch(
        "utils.data_version_control._git_tag_exists"
    ) as mock_git_tag_exists, mock.patch(
        "utils.data_version_control._git_commit_hash_exists"
    ) as mock_git_commit_hash_exists:
        mock_git_command.return_value = mock.MagicMock()
        mock_git_tag_exists.return_value = False
        mock_git_commit_hash_exists.return_value = True

        with pytest.raises(ValueError):
            git_checkout_folder(tag_name="version1", folder_name="data")


def test_git_checkout_folder_raises_vaue_error_invalid_commit(
    directory_for_testing, mock_git_command
):
    """Test the git_checkout_folder function raises ValueError when the commit is invalid.

    Args:
        directory_for_testing (str): Path to testing directory.
        mock_git_command (mock.MagicMock()): Mocked git command object.
    """
    data_path = os.path.join(directory_for_testing, "data")
    os.mkdir(data_path)
    with mock.patch(
        "utils.data_version_control._git_tag_exists"
    ) as mock_git_tag_exists, mock.patch(
        "utils.data_version_control._git_commit_hash_exists"
    ) as mock_git_commit_hash_exists:
        mock_git_command.return_value = mock.MagicMock()
        mock_git_tag_exists.return_value = True
        mock_git_commit_hash_exists.return_value = False

        with pytest.raises(ValueError):
            git_checkout_folder(commit_hash="abcdefg", folder_name="data")


def test_git_tag_exists(directory_for_testing, mock_git_repo):
    """Test the _git_tag_exists function works as expected.

    Args:
        directory_for_testing (str): Path to testing directory.
        mock_git_repo (mock.MagicMock()): Mocked git repo object.
    """
    data_path = os.path.join(directory_for_testing, "data")
    os.mkdir(data_path)

    mock_git_repo_value = mock.MagicMock()
    mock_git_repo.return_value = mock_git_repo_value
    mock_git_repo_value.tags = ["tag1", "tag2"]

    assert _git_tag_exists("tag2")


def test_git_tag_exists_returns_false_when_tag_does_not_exist(
    directory_for_testing,
    mock_git_repo,
):
    """Test the _git_tag_exists returns false when a Git tag does not exist.

    Args:
        directory_for_testing (str): Path to testing directory.
        mock_git_repo (mock.MagicMock()): Mocked git repo object.
    """
    data_path = os.path.join(directory_for_testing, "data")
    os.mkdir(data_path)

    mock_git_repo_value = mock.MagicMock()
    mock_git_repo.return_value = mock_git_repo_value
    mock_git_repo_value.tags = ["tag1", "tag2"]

    assert not _git_tag_exists("tag3")


def test_git_commit_hash_exists(directory_for_testing, mock_git_repo):
    """Test the _git_commit_hash_exists function works as expected.

    Args:
        directory_for_testing (str): Path to testing directory.
        mock_git_repo (mock.MagicMock()): Mocked git repo object.
    """
    mock_git_repo_value = mock.MagicMock()
    mock_git_repo.return_value = mock_git_repo_value
    mock_git_repo_value.iter_commits.return_value = ["hash1", "hash2"]

    assert _git_commit_hash_exists("hash1")


def test_git_commit_hash_exists_returns_false_when_tag_does_not_exist(
    directory_for_testing, mock_git_repo
):
    """Test the _git_commit_hash_exists returns false when a Git tag does not exist.

    Args:
        directory_for_testing (str): Path to testing directory.
        mock_git_repo (mock.MagicMock()): Mocked git repo object.
    """
    mock_git_repo_value = mock.MagicMock()
    mock_git_repo.return_value = mock_git_repo_value
    mock_git_repo_value.iter_commits.return_value = ["hash1", "hash2"]

    assert not _git_commit_hash_exists("hash3")
