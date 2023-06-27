from zenml.steps import step
import pandas as pd


@step
def load_data() -> pd.DataFrame:
    return pd.DataFrame()


@step
def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame()


@step
def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame()

