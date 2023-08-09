"""Test the data cleaning functionality."""
import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

from steps.data_preparation_steps import clean_data
from steps.data_preparation_steps.clean_data_step.clean_data_step import (
    contract_white_space,
    insert_space_between_numbers_and_letters,
    remove_nbsp,
    remove_new_line,
    strip_string, add_punctuation, clean_html,
)

@pytest.fixture
def dirty_html_case() -> str:
    """Fixture for a dirty HTML case.

    It's reused both in scraped data and in other unit tests.

    Returns:
        str
    """
    return "<div><h2>Special HTML case</h2><h3>Inner heading!</h3><p>Some content</p><aside>Shall be removed</aside></div>"


@pytest.fixture
def expected_cleaned_html_case() -> str:
    """Fixture for the expected cleaned counter-part of the dirty HTML case.

    Returns:
        str
    """
    return "Special HTML case. Inner heading! Some content"


@pytest.fixture
def scraped_data_fixture(dirty_html_case: str) -> pd.DataFrame:
    """Fixture mocking the result of the scraping pipeline.

    Returns:
        A pandas DataFrame mimicking the results of the scraping procedure.
    """
    data = {
        "html_scraped": [
            "<p>This is some scraped data! It has some really wild  spacing.</p>",
            "<p>It also has some BiZzArE casing. And lots - of * ridiculous,, %% punctuation.</p>",
            "<p>But otherwise, it's not so bad.</p>",
            "<p>But otherwise, it's not so bad.</p>",
            dirty_html_case
        ],
        "text_scraped": [
            "This is some scraped data! It has some really wild  spacing.",
            "It also has some BiZzArE casing. And lots - of * ridiculous,, %% punctuation.",
            "But otherwise, it's not so bad.",
            "But otherwise, it's not so bad.",
            "Special HTML case"
        ],
        "url": [
            "https://www.link1.com",
            "https://www.link2.com",
            "https://www.link3.com",
            "https://www.link3.com",
            "https://www.link4.com",
        ],
    }
    return pd.DataFrame(data)


@pytest.fixture
def expected_cleaned_data(expected_cleaned_html_case: str) -> pd.DataFrame:
    """Fixture for expected cleaned data results.

    Returns:
        A pandas DataFrame with expected cleaned data results.
    """
    data = {
        "text_scraped": [
            "This is some scraped data! It has some really wild spacing.",
            "It also has some BiZzArE casing. And lots - of * ridiculous,, %% punctuation.",
            "But otherwise, it's not so bad.",
            expected_cleaned_html_case
        ],
        "url": [
            "https://www.link1.com",
            "https://www.link2.com",
            "https://www.link3.com",
            "https://www.link4.com",
        ],
    }
    return pd.DataFrame(data)


def test_clean_data(scraped_data_fixture: pd.DataFrame, expected_cleaned_data: pd.DataFrame):
    """Run a short test on the fake scraped data.

    Args:
        scraped_data_fixture: A pandas dataframe mimicking the scraped data format.
        expected_cleaned_data: A pandas DataFrame with expected cleaned data results.
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
    assert_frame_equal(expected_cleaned_data, cleaned_data)


def test_clean_html(dirty_html_case: str, expected_cleaned_html_case: str):
    """Test clean_html function.

    Args:
        dirty_html_case (str): Dirty HTML to test with
        expected_cleaned_html_case (str): expected cleaning results
    """
    assert "" == clean_html("")
    assert expected_cleaned_html_case == clean_html(dirty_html_case)


def test_add_punctuation():
    """Test add_punctuation function."""

    assert "" == add_punctuation("")  # Special case for empty strings
    assert "Heading." == add_punctuation("Heading")
    assert "Heading." == add_punctuation("Heading.")
    assert "Heading!" == add_punctuation("Heading!")
    assert "Heading?" == add_punctuation("Heading?")
    assert "Heading;." == add_punctuation("Heading;")  # We do not accept non-end-of-sentence punctuation

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
