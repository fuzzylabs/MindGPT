"""Data preparation pipeline."""

from zenml.pipelines import pipeline
from zenml.logger import get_logger
from zenml.steps import BaseStep

logger = get_logger(__name__)


@pipeline
def data_preparation_pipeline(
    load_data: BaseStep,
    clean_data: BaseStep,
    validate_data: BaseStep,
    save_prepared_data: BaseStep,
) -> None:
    """The data preparation pipeline.

    Args:
        load_data: A ZenML step which loads the data.
        clean_data: A ZenML step which cleans the data.
        validate_data: A ZenML step which validates the cleaned data.
        version_data: A ZenML step which versions the cleaned and validated data.
    """
    data = load_data()
    data = clean_data(data)
    data = validate_data(data)
    save_prepared_data(data)
