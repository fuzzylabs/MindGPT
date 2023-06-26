import pandas as pd

from steps.data_preparation.data_preparation import (
    clean_data,
    validate_data,
    version_data
)
from zenml.pipelines import pipeline


@pipeline
def prepare_data(data:pd.DataFrame) -> pd.DataFrame:
    ...