"""Data preparation pipeline."""

import pandas as pd
from steps.data_preparation.data_preparation import (
    clean_data,
    validate_data,
    version_data
)
from zenml.pipelines import pipeline
from zenml.logger import get_logger
from zenml.steps import BaseStep

logger = get_logger(__name__)


@pipeline
def data_preparation_pipeline(
        load_data: BaseStep,
        clean_data: BaseStep,
        validate_data: BaseStep,
        version_data: BaseStep,
) -> None:
    """The data preparation pipeline.

    Args:
        load_data: A ZenML step which loads the data.
        clean_data: A ZenML step which cleans the data.
        validate_data: A ZenML step which validates the cleaned data.
        version_data: A ZenML step which versions the cleaned and validated data.
    """
    data = version_data(
        validate_data(
            clean_data(
                load_data()
            )
        )
    )
    return data