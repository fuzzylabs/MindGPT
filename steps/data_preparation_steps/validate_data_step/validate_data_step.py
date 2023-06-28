from zenml.steps import step
import pandas as pd


@step
def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame()
