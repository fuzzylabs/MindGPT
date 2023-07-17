"""Steps for versioning new data."""
from typing import List

from utils import (
    get_active_branch_name,
    push_and_tag_dvc_changes_to_git,
    push_data,
    version_new_data,
)
from zenml import step


@step
def version_data(
    data_version_name: str, filename_roots: List[str], debug_mode: bool
) -> None:
    """Step for versioning new data.

    Args:
        data_version_name: Forms part of the git tag for this data version.
        filename_roots: filenames without extensions of the data to be versioned.
        debug_mode: If in debug mode, calls to this step won't push anything to the repository.

    """
    if not debug_mode and get_active_branch_name() == "develop":
        raise RuntimeError(
            "Aborting data versioning. Pushing directly to develop is not allowed!"
        )

    version_new_data(filename_roots=filename_roots)

    if not debug_mode:
        push_data()
        push_and_tag_dvc_changes_to_git(tag=f"data/{data_version_name}")
