"""Test the data cleaning functionality."""
import pandas as pd
import pytest
from steps.data_preparation_steps import clean_data
from steps.data_preparation_steps.clean_data_step.clean_data_step import (
    contract_white_space,
    insert_space_between_numbers_and_letters,
    remove_nbsp,
    remove_new_line,
    strip_string,
)


@pytest.fixture
def scraped_data_fixture() -> pd.DataFrame:
    """Fixture mocking the result of the scraping pipeline.

    Returns:
        A pandas DataFrame mimicking the results of the scraping procedure.
    """
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


def test_clean_data(scraped_data_fixture: pd.DataFrame):
    """Run a short test on the fake scraped data.

    Args:
        scraped_data_fixture: A pandas dataframe mimicking the scraped data format.
    """
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


def test_remove_new_line():
    """Test that new line chars are removed from strings."""
    assert (
        remove_new_line("\n\na string\n \ncontaining \nnewline chars.")
        == "  a string   containing  newline chars."
    )


def test_strip_string():
    """Test that strings are appropriately stripped."""
    assert (
        strip_string("  a string which needs stripping   ")
        == "a string which needs stripping"
    )


def test_remove_nbsp():
    """Check that nbsp characters are removed from strings."""
    assert (
        remove_nbsp("a string\xa0containing\xa0non-blank white space.")
        == "a string containing non-blank white space."
    )


def test_insert_space_between_numbers_and_letters():
    """Test confirming that insertion of white space between numbers and letters behaves as desired."""
    assert (
        insert_space_between_numbers_and_letters(
            "for help with this test, call 0800123456or visit helpwiththistest.com"
        )
        == "for help with this test, call 0800123456 or visit helpwiththistest.com"
    )
    assert (
        insert_space_between_numbers_and_letters(
            "for help with this test, visit or call helpwiththistest.com0800123456"
        )
        == "for help with this test, visit or call helpwiththistest.com 0800123456"
    )


def test_contract_white_space():
    """Test confirming contraction of white space behaves as expected."""
    assert (
        contract_white_space("   this   string  has      strange     spacing         ")
        == " this string has strange spacing "
    )
