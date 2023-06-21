"""Scrape data from the Mind charity website."""
import pandas as pd
from zenml.steps import step


@step
def scrape_mind_data() -> pd.DataFrame:
    """Scrape data from Mind.

    Returns:
        pd.DataFrame: data scraped.
    """
    df = pd.DataFrame()

    return df
