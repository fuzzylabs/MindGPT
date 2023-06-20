"""Scrape data from the NHS website."""
import pandas as pd
from zenml.steps import step


@step
def scrape_nhs_data() -> pd.DataFrame:
    """Scrape data from nhs.

    Returns:
        pd.DataFrame: data scarped.
    """
    df = pd.DataFrame()

    return df
