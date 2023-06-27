"""Save the scraped data as CSV and push to bucket."""
import pandas as pd
from zenml.steps import step


@step
def save_data(nhs_data_scraped: pd.DataFrame, mind_data_scraped: pd.DataFrame) -> None:
    """Save data as CSVs and push to storage bucket.

    Args:
        nhs_data_scraped (pd.DataFrame): NHS data to push.
        mind_data_scraped (pd.DataFrame): Mind data to push.
    """
    ...
