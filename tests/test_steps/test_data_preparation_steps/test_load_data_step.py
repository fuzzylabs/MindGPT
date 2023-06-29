"""Test load data step file."""

from unittest.mock import patch

import pandas as pd
import pytest
from steps.data_preparation_steps.load_data_step.load_data_step import (
    LoadDataParameters,
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
        expected_df = pd.concat([mock_df, mock_df])
        get_df_from_step.return_value = mock_df

        result_df = load_data.entrypoint(LoadDataParameters())

        pd.testing.assert_frame_equal(result_df, expected_df)


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
            _ = load_data.entrypoint(LoadDataParameters())

        assert "Pipeline 'data_scraping_pipeline' does not exist" in str(e)
