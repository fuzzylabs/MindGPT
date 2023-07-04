"""Test validate data file."""
import pandas as pd
from steps.data_preparation_steps.validate_data_step.validate_data_step import (
    validate_data,
)


def test_validate_data_step():
    """_summary_."""
    df = pd.DataFrame(
        {
            "text_scraped": [
                "abcd",
                "https://www.bbc.co.uk/news",
                42,
                "https://www.notarealwebsite.com/news",
                None,
            ]
        }
    )
    # df = pd.DataFrame({"text_scraped": ["abcd", "https://www.bbc.co.uk/news", "42"]})

    is_valid, rows_with_warning = validate_data(df)
    print(rows_with_warning)
    assert False
