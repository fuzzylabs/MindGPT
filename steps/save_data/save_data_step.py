"""Save the scraped data as CSV and push to bucket."""
import pandas as pd
from zenml.steps import step
from typing import Optional


@step
def save_data(
        nhs_data_scraped: Optional[pd.DataFrame] = None,
        mind_data_scraped: Optional[pd.DataFrame] = None,
        prepared_data: Optional[pd.DataFrame] = None
) -> None:
    """Save data as CSVs and push to storage bucket.

    Args:
        nhs_data_scraped (pd.DataFrame): NHS data to push.
        mind_data_scraped (pd.DataFrame): Mind data to push.
    """
    ...
