"""Data preparation pipeline."""

from typing import Optional

from steps.data_preparation_steps import clean_data, load_data, validate_data
from zenml import pipeline
from zenml.logger import get_logger

logger = get_logger(__name__)


@pipeline
def data_preparation_pipeline(
    pipeline_name: str = "data_scraping_pipeline",
    pipeline_version: Optional[int] = None,
) -> None:
    """The data preparation pipeline.

    Args:
        pipeline_name (str): Name of pipeline to get raw scraped data from
        pipeline_version (Optional[int]): Optional pipeline version, defaults to None

    Steps:
        load_data: A ZenML step which loads the data.
        clean_data: A ZenML step which cleans the data.
        validate_data: A ZenML step which validates the cleaned data.
        save_prepared_data: A ZenML step which versions the cleaned and validated data.
    """
    mind_df, nhs_df = load_data(
        pipeline_name=pipeline_name, pipeline_version=pipeline_version
    )
    data = clean_data(mind_df)
    data = validate_data(data)
