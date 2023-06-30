"""Clean data step."""
import pandas as pd
from zenml import step


@step
def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """_summary_.

    Args:
        data (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: _description_
    """
    return pd.DataFrame()
