import pandas as pd
from zenml.steps import step


@step
def save_prepared_data(data: pd.DataFrame) -> None:
    """Save the prepped data as a CSV and push to storage bucket.

    Args:
        data (pd.DataFrame): The prepped data to push.
    """
    ...