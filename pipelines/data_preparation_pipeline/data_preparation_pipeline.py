"""Data preparation pipeline."""
from steps.data_preparation_steps import clean_data, validate_data
from steps.data_preparation_steps.split_nhs_pages_step.split_nhs_pages_step import split_pages
from steps.data_versioning_steps import version_data
from steps.generic_steps import load_data
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
    _, _, mind_df, nhs_df = load_data()

    mind_df = split_pages(mind_df, "mind", after=["load_data"], id="split_pages_mind")
    nhs_df = split_pages(nhs_df, "nhs", after=["load_data"], id="split_pages_nhs")

    mind_df = clean_data(mind_df, after=["split_pages_mind"], id="clean_data_mind")
    nhs_df = clean_data(nhs_df, after=["split_pages_nhs"], id="clean_data_nhs")

    mind_df = validate_data(mind_df, "mind", after=["clean_data_mind"], id="validate_data_mind")
    nhs_df = validate_data(nhs_df, "nhs", after=["clean_data_nhs"], id="validate_data_nhs")

    version_data(after=["validate_data_mind", "validate_data_nhs"], data_postfix="validated")
