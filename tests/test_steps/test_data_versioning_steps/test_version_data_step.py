"""Tests for the version data step."""
from unittest.mock import MagicMock, patch

import pytest
import steps.data_versioning_steps
from steps.data_versioning_steps import version_data


def test_develop_push_refusal():
    """Test that if a user tries to push directly to develop by using this step, a RuntimeError is raised."""
    with patch(
        "steps.data_versioning_steps.version_data_step.get_active_branch_name"
    ) as mock_method:
        mock_method.return_value = "develop"

        with pytest.raises(RuntimeError):
            version_data("test_", ["test_, test_0"], False)


def test_push_block_reached():
    """Test that the block of code responsible for pushing changes to git and dvc is reached."""
    # mock all function calls to remove ugly prints as we are only testing bool logic here
    with (
        patch(
            "steps.data_versioning_steps.version_data_step.get_active_branch_name"
        ) as branch_name,
        patch(
            "steps.data_versioning_steps.version_data_step.push_and_tag_dvc_changes_to_git"
        ) as push_and_tag,
        patch("steps.data_versioning_steps.version_data_step.push_data") as push_data,
        patch(
            "steps.data_versioning_steps.version_data_step.version_new_data"
        ) as version_new,
    ):
        branch_name.return_value = "not_develop"
        push_and_tag.return_value, push_data.return_value, version_new.return_value = (
            None,
            None,
            None,
        )
        steps.data_versioning_steps.version_data_step.push_and_tag_dvc_changes_to_git = (
            MagicMock()
        )
        steps.data_versioning_steps.version_data_step.push_data = MagicMock()
        steps.data_versioning_steps.version_data_step.version_new_data = MagicMock()
        version_data("test_", ["test_", "test_0"], False)

        assert (
            steps.data_versioning_steps.version_data_step.push_and_tag_dvc_changes_to_git.called
        )
        assert steps.data_versioning_steps.version_data_step.push_data.called
        assert steps.data_versioning_steps.version_data_step.version_new_data.called


def test_error_raised_if_files_not_present():
    """Test that the files_exist function is called and an appropriate error raised when called without files present."""
    with pytest.raises(FileNotFoundError), patch(
        "steps.data_versioning_steps.version_data_step.get_active_branch_name"
    ) as branch_name:
        branch_name.return_value = "not_develop"
        version_data("test_", ["test_", "test_0"], False)
