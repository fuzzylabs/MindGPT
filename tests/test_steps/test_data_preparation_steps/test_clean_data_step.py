"""Test the data cleaning functionality."""
import pandas as pd
import pytest
from steps.data_preparation_steps import clean_data


@pytest.fixture
def scraped_data_fixture() -> pd.DataFrame:
    """Fixture mocking the result of the scraping pipeline."""
    data = {
        "text_scraped": [
            "This is some scraped data! It has some really wild  spacing.",
            "It also has some BiZzArE casing. And lots - of * ridiculous,, %% punctuation.",
            "But otherwise, it's not so bad.",
            "But otherwise, it's not so bad.",
        ],
        "url": [
            "https://www.link1.com",
            "https://www.link2.com",
            "https://www.link3.com",
            "https://www.link3.com",
        ],
    }
    return pd.DataFrame(data)


def test_clean_data(scraped_data_fixture):
    """Run a short test on the fake scraped data."""
    cleaned_data = clean_data(scraped_data_fixture)
    for idx in cleaned_data.index:
        assert "\n" not in cleaned_data.loc[idx, "text_scraped"]
        assert (
            cleaned_data.loc[idx, "text_scraped"].strip()
            == cleaned_data.loc[idx, "text_scraped"]
        )
        assert "\xa0" not in cleaned_data.loc[idx, "text_scraped"]
        assert "  " not in cleaned_data.loc[idx, "text_scraped"]
        assert len(cleaned_data) == len(scraped_data_fixture.dropna().drop_duplicates())
    assert len(cleaned_data) == len(scraped_data_fixture) - 1
