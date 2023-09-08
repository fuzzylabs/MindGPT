"""Data version control tools for interacting with DVC CLI."""
import os
import subprocess as sp
from typing import List, Optional

import git
from config import DATA_DIR, PROJECT_ROOT_DIR
from pygit2 import Repository
from zenml.logger import get_logger

logger = get_logger(__name__)


def files_exist(filepaths: List[str], error_message: str) -> bool:
    """A function for checking files exist, and returning an interpretable error message.

    Arguments:
        filepaths (List[str]): A list of filepaths.
        error_message (str): The error message to show in the event a file does not exist.

    Returns:
        True if all files exist.
    """
    files_present = [(fname, os.path.isfile(fname)) for fname in filepaths]
    for fname, exists in files_present:
        if not exists:
            raise FileNotFoundError(f"{error_message}: {fname} does not exist.")
    return all(exists for _, exists in files_present)


def get_active_branch_name() -> str:
    """Get the name of the current active branch of the git tree."""
    return str(Repository(PROJECT_ROOT_DIR).head.shorthand)


def pull_data() -> None:
    """Pull the most recently pushed data from the storage bucket."""
    sp.run("dvc pull", shell=True, cwd=PROJECT_ROOT_DIR, check=False)


def push_data() -> None:
    """Push the current data to the bucket."""
    sp.run("dvc push", shell=True, cwd=PROJECT_ROOT_DIR, check=False)


def add_csv_files_to_dvc(filenames: List[str]) -> None:
    """Add the current csv files to dvc.

    Args:
        filenames: .csv files to be added to data version control
    """
    if files_exist(
        filepaths=[os.path.join(DATA_DIR, filename) for filename in filenames],
        error_message="Cannot add .csv files to dvc",
    ):
        files = "".join(f"data/{fname} " for fname in filenames)
        sp.run(f"dvc add {files}", shell=True, cwd=PROJECT_ROOT_DIR, check=False)


def add_and_commit_dvc_files_to_git(filenames: List[str]) -> None:
    """Add .dvc files in the data/ directory to git and commit them.

    Args:
        filenames: The .dvc filenames.
    """
    if files_exist(
        filepaths=[os.path.join(DATA_DIR, filename) for filename in filenames],
        error_message="Cannot add .dvc files to git",
    ):
        files = "".join(f"data/{fname} " for fname in filenames)
        sp.run(f"git add {files}", shell=True, cwd=PROJECT_ROOT_DIR, check=False)
        sp.run(
            f'git commit {files} -m "Update dvc files"',
            shell=True,
            cwd=PROJECT_ROOT_DIR,
            check=False,
        )


def push_and_tag_dvc_changes_to_git(tag: str) -> None:
    """Push the current commits to remote, then tag the commit and push the tag.

    Args:
        tag: Used to form the data tag.
    """
    sp.run("git push", shell=True, cwd=PROJECT_ROOT_DIR, check=False)
    sp.run(f"git tag {tag}", shell=True, cwd=PROJECT_ROOT_DIR, check=False)
    sp.run(f"git push origin {tag}", shell=True, cwd=PROJECT_ROOT_DIR, check=False)


def checkout_data_files() -> None:
    """Checkout the data files consistent with the hash in the current .dvc files in the data/ directory."""
    sp.run("dvc checkout", shell=True, cwd=PROJECT_ROOT_DIR, check=False)


def version_new_data(filename_roots: List[str]) -> None:
    """Version new data in the data/ directory.

    Args:
        filename_roots: Roots of the filenames for the data to be versioned.
    """
    csv_files = [f"{fname}.csv" for fname in filename_roots]
    dvc_files = [f"{fname}.csv.dvc" for fname in filename_roots]
    add_csv_files_to_dvc(csv_files)
    add_and_commit_dvc_files_to_git(dvc_files)


def _git_tag_exists(tag_name: str) -> bool:
    """Checks for the existence of a given Git tag name.

    Args:
        tag_name (str): Name of tag to check existence.

    Returns:
        bool: True, if Git tag exists. False otherwise.
    """
    try:
        repo = git.Repo(PROJECT_ROOT_DIR)  # type: ignore
        return tag_name in repo.tags
    except git.GitCommandError as e:
        logger.error(f"Error tag '{tag_name}' does not exist: {e}")
        return False


def _git_commit_hash_exists(commit_hash: str) -> bool:
    """Check for commit hash existence.

    Args:
        commit_hash (str): Commit hash string.

    Returns:
        bool: True, if commit hash exists. False otherwise.
    """
    try:
        repo = git.Repo(PROJECT_ROOT_DIR)  # type: ignore
        return commit_hash in {str(c) for c in repo.iter_commits()}
    except Exception as e:
        logger.error(f"Error: Commit hash '{commit_hash}' does not exist: {e}")
        return False


def git_checkout_folder(
    tag_name: Optional[str] = None,
    commit_hash: Optional[str] = None,
    folder_name: str = "data",
) -> None:
    """Checkout a specified folder within a tagged commit or commit hash on Git.

    Args:
        tag_name (Optional[str]): Git tag to checkout.
        commit_hash (Optional[str]): Git commit hash to checkout.
        folder_name (str): Folder name to checkout e.g. 'data'.

    Raises:
        ValueError: If the tag or commit hash is invalid or both are None.
    """
    if not os.path.exists(os.path.join(PROJECT_ROOT_DIR, folder_name)):
        raise FileNotFoundError(f"Folder with the name '{folder_name}' does not exist.")
    if tag_name is not None and _git_tag_exists(tag_name):
        g = git.cmd.Git(PROJECT_ROOT_DIR)
        g.checkout(tag_name, folder_name)
    elif commit_hash is not None and _git_commit_hash_exists(commit_hash):
        g = git.cmd.Git(PROJECT_ROOT_DIR)
        g.checkout(commit_hash, folder_name)
    else:
        raise ValueError("Error, you must specify a valid tag or commit hash.")
