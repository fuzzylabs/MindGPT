"""Test load data step file."""
from unittest.mock import MagicMock, PropertyMock, patch

import pandas as pd
import pytest
from steps.data_preparation_steps.load_data_step.load_data_step import (
    get_df_from_step,
    get_output_from_step,
    load_data,
)
from zenml.post_execution import PipelineView


def test_load_data_step():
    """Test that data is loaded correctly in the step when a valid pipeline is found."""
    with patch(
        "steps.data_preparation_steps.load_data_step.load_data_step.get_pipeline"
    ) as get_pipeline, patch(
        "steps.data_preparation_steps.load_data_step.load_data_step.get_df_from_step"
    ) as get_df_from_step:
        get_pipeline.return_value = PipelineView("test-pipeline")
        mock_df = pd.DataFrame({"COL1": [1, 2], "COL2": [3, 4]})

        get_df_from_step.return_value = mock_df

        result_df1, result_df2 = load_data(pipeline_name="test-pipeline")

        pd.testing.assert_frame_equal(result_df1, mock_df)
        pd.testing.assert_frame_equal(result_df2, mock_df)


def test_load_data_step_raises_exception_when_no_pipeline_found():
    """Test that exception is raised when a pipeline with the specified name is not found."""
    with patch(
        "steps.data_preparation_steps.load_data_step.load_data_step.get_pipeline"
    ) as get_pipeline, patch(
        "steps.data_preparation_steps.load_data_step.load_data_step.get_df_from_step"
    ) as get_df_from_step:
        get_pipeline.return_value = None
        mock_df = pd.DataFrame({"COL1": [1, 2], "COL2": [3, 4]})
        get_df_from_step.return_value = mock_df

        with pytest.raises(ValueError) as e:
            _ = load_data(pipeline_name="data_scraping_pipeline")

        assert "Pipeline 'data_scraping_pipeline' does not exist" in str(e)


def test_get_output_from_step_raises_key_error_when_step_name_does_not_exist():
    """Test get_output_from_step function raises a KeyError when the step name does not exist for a specified pipeline."""
    with patch(
        "zenml.post_execution.PipelineView.runs", new_callable=PropertyMock
    ) as get_runs_from_pipeline:
        mock_run = MagicMock()
        get_runs_from_pipeline.return_value = [mock_run]
        # Raise KeyError when get_step is called on a PipelineRunView object
        mock_run.get_step.side_effect = KeyError

        with pytest.raises(KeyError):
            _ = get_output_from_step(PipelineView("test-pipeline"), "test-step-name")


def test_get_output_from_step_raises_value_error_when_step_output_does_not_exist():
    """Test get_output_from_step function raises a ValueError when a step does not have any output."""
    with patch(
        "zenml.post_execution.PipelineView.runs", new_callable=PropertyMock
    ) as get_runs_from_pipeline:
        mock_run = MagicMock()
        get_runs_from_pipeline.return_value = [mock_run]
        mock_step = MagicMock()
        mock_run.get_step.return_value = mock_step
        mock_step.outputs = {}

        with pytest.raises(ValueError):
            _ = get_output_from_step(PipelineView("test-pipeline"), "test-step-name")


def test_get_df_from_step_raises_type_error():
    """Test get_df_from_step function raises a TypeError when the loaded artifact is not a DataFrame."""
    with patch(
        "steps.data_preparation_steps.load_data_step.load_data_step.get_output_from_step"
    ) as get_output_from_step:
        artifact_data = MagicMock()
        get_output_from_step.return_value = artifact_data

        artifact_data.read.return_value = None

        with pytest.raises(TypeError):
            _ = get_df_from_step(PipelineView("test-pipeline"), "test-step-name")
