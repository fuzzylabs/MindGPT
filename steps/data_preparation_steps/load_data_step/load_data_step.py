from zenml.steps import step
import pandas as pd


@step
def load_data() -> pd.DataFrame:
    return pd.DataFrame()
