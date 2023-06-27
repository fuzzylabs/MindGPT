from zenml.steps import step
import pandas as pd


@step
def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame()
