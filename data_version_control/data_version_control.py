"""Data version control tools for interacting with DVC CLI."""
import subprocess as sp

from config import ROOT_DIR


def pull_data() -> None:
    """Pull the most recently pushed data from the storage bucket."""
    sp.run("dvc pull", shell=True, cwd=ROOT_DIR)


def push_data() -> None:
    """Push the current data to the bucket."""
    sp.run("dvc push", shell=True, cwd=ROOT_DIR)


def add_csv_files_to_dvc() -> None:
    """Add the current csv files to dvc."""
    sp.run("dvc add data/*.csv", shell=True, cwd=ROOT_DIR)


def add_dvc_files_to_git() -> None:
    """Add *.dvc files in the data/ directory to git."""
    sp.run("git add data/*.dvc", shell=True, cwd=ROOT_DIR)


def checkout_data_files() -> None:
    """Checkout the data files consistent with the hash in the current .dvc files in the data/ directory."""
    sp.run("dvc checkout", shell=True, cwd=ROOT_DIR)


def commit_new_dcv_changes() -> None:
    """Commit the changes to the dcv files to git."""
    sp.run('git commit -m "Update the scraped data"')


def version_new_data() -> None:
    """Version new data."""
    add_csv_files_to_dvc()
    add_dvc_files_to_git()
    commit_new_dcv_changes()


def pull_data_consistent_with_git() -> None:
    """Checkout the data consistent with the dcv files in the current commit."""
    sp.run("dvc checkout", shell=True, cwd=ROOT_DIR)
