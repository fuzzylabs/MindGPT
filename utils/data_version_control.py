"""Data version control tools for interacting with DVC CLI."""
import os
import subprocess as sp
from typing import List

import git
from config import DATA_DIR, PROJECT_ROOT_DIR
from pygit2 import Repository  # type: ignore


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
    return all([exists for _, exists in files_present])


def get_active_branch_name() -> str:
    """Get the name of the current active branch of the git tree."""
    return str(Repository(PROJECT_ROOT_DIR).head.shorthand)


def pull_data() -> None:
    """Pull the most recently pushed data from the storage bucket."""
    sp.run("dvc pull", shell=True, cwd=PROJECT_ROOT_DIR)


def push_data() -> None:
    """Push the current data to the bucket."""
    sp.run("dvc push", shell=True, cwd=PROJECT_ROOT_DIR)


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
        sp.run(f"dvc add {files}", shell=True, cwd=PROJECT_ROOT_DIR)


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
        sp.run(f"git add {files}", shell=True, cwd=PROJECT_ROOT_DIR)
        sp.run(
            f'git commit {files} -m "Update dvc files"',
            shell=True,
            cwd=PROJECT_ROOT_DIR,
        )


def push_and_tag_dvc_changes_to_git(tag: str) -> None:
    """Push the current commits to remote, then tag the commit and push the tag.

    Args:
        tag: Used to form the data tag.
    """
    sp.run("git push", shell=True, cwd=PROJECT_ROOT_DIR)
    sp.run(f"git tag {tag}", shell=True, cwd=PROJECT_ROOT_DIR)
    sp.run(f"git push origin {tag}", shell=True, cwd=PROJECT_ROOT_DIR)


def checkout_data_files() -> None:
    """Checkout the data files consistent with the hash in the current .dvc files in the data/ directory."""
    sp.run("dvc checkout", shell=True, cwd=PROJECT_ROOT_DIR)


def version_new_data(filename_roots: List[str]) -> None:
    """Version new data in the data/ directory.

    Args:
        filename_roots: Roots of the filenames for the data to be versioned.
    """
    csv_files = [f"{fname}.csv" for fname in filename_roots]
    dvc_files = [f"{fname}.csv.dvc" for fname in filename_roots]
    add_csv_files_to_dvc(csv_files)
    add_and_commit_dvc_files_to_git(dvc_files)


def git_checkout_folder(tag_name: str, folder_name: str) -> None:
    """Checkout a specified folder within a tagged commit or commit hash on Git.

    Args:
        tag_name (str): Git tag or commit hash to checkout.
        folder_name (str): Folder name to checkout e.g. 'data'.
    """
    g = git.cmd.Git("")
    g.checkout(tag_name, folder_name)
