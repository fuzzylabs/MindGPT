from unittest.mock import MagicMock

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from steps.data_preparation_steps import clean_data
from steps.data_preparation_steps.clean_data_step.clean_data_step import remove_punctuation, reformat

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
            "https://www.link3.com"
        ]
    }
    return pd.DataFrame(data)


@pytest.fixture
def cleaned_data_fixture() -> pd.DataFrame:
    """Fixture corresponding to cleaned data from the mocked_scraped_data fixture."""

    data = {
        "sentences": [
            "this is some scraped data it has some really wild spacing",
            "it also has some bizzare casing"
            "and lots of ridiculous punctuation"
            "but otherwise, its not so bad"
        ]
    }

    return pd.DataFrame(data)


def test_clean_data(scraped_data_fixture):
    cleaned_data = clean_data(scraped_data_fixture)
    for idx in cleaned_data.index:
        assert cleaned_data.loc[idx, "sentences"].lower() == cleaned_data.loc[idx, "sentences"]
        assert "\n" not in cleaned_data.loc[idx, "sentences"]
        assert cleaned_data.loc[idx, "sentences"].strip() == cleaned_data.loc[idx, "sentences"]
        assert "\xa0" not in cleaned_data.loc[idx, "sentences"]
        assert "  " not in cleaned_data.loc[idx, "sentences"]


def test_remove_punctuation():
    assert (
        remove_punctuation(
            "! this? string. should, ,,+contain, no =punctuation: because -–that is the rule+=():';%&_"
        ) == " this string should contain no punctuation because that is the rule"
    )
    assert (
        remove_punctuation("this string exists because python '") == "this string exists because python "
    )
    assert (
        remove_punctuation('so does this one "') == "so does this one "
    )
    assert remove_punctuation("either/or") == "either or"

def test_reformat(scraped_data_fixture, cleaned_data_fixture):
    pass