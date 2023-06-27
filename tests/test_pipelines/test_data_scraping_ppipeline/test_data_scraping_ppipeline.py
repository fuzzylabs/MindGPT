"""Test suite to test the data scarping pipeline."""
import pytest
import zenml
from pipelines.data_scraping_pipeline.data_scraping_pipeline import (
    data_scraping_pipeline,
)


@pytest.fixture
def whole_pipeline() -> zenml.pipeline:
    """Pytest fixture for running the all the steps in the zenml data_scraping_pipeline.

    Returns:
        zenml.pipelines.base_pipeline.BasePipelineMeta: ZenML pipeline
    """
    return data_scraping_pipeline


def test_whole_pipeline(
    whole_pipeline: zenml.pipeline,
    capsys: pytest.CaptureFixture,
):
    """Test the whole data_scraping_pipeline.

    Args:
        whole_pipeline (zenml.pipelines.base_pipeline.BasePipelineMeta): Pytest fixture for data_scraping_pipeline.
        capsys (pytest.CaptureFixture): fixture to capture the standard output.
    """
    pass
