"""Data preparation pipeline."""
from steps.data_preparation_steps import clean_data, validate_data
from steps.generic_steps import load_data
from steps.data_versioning_steps import version_data
from zenml import pipeline
from zenml.logger import get_logger

logger = get_logger(__name__)


@pipeline
def data_preparation_pipeline() -> None:
    """The data preparation pipeline.

    Steps:
        load_data: A ZenML step which loads the data.
        clean_data: A ZenML step which cleans the data.
        validate_data: A ZenML step which validates the cleaned data.
        version_data: A ZenML step which versions the cleaned data and pushes it to the storage bucket.
    """
    mind_df, nhs_df = load_data()

    mind_df = clean_data(mind_df)
    nhs_df = clean_data(nhs_df)

    mind_df = validate_data(mind_df, "mind")
    nhs_df = validate_data(nhs_df, "nhs")

    version_data(after=["load_data", "clean_data", "validate_data"])
