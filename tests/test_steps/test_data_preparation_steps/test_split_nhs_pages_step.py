"""Test split NHS pages step."""
from typing import List

import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

from steps.data_preparation_steps.split_nhs_pages_step.split_nhs_pages_step import split_pages, split_page


@pytest.fixture
def nhs_pages_split() -> List[pd.DataFrame]:
    """A fixture with NHS pages after splitting.

    Returns:
        List[pd.DataFrame]: The list of mock scraped NHS data.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: html_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
    """
    return [
        pd.DataFrame([], columns=["uuid", "html_scraped", "timestamp", "url"]),
        pd.DataFrame([
            {
                "uuid": "1-0",
                "html_scraped": "<section><p>Section1</p></section>",
                "timestamp": pd.to_datetime(0),
                "url": f"https://example.com/1#section-0",
            }
        ]),
        pd.DataFrame([
            {
                "uuid": "2-0",
                "html_scraped": "<section><p>Section1</p></section>",
                "timestamp": pd.to_datetime(0),
                "url": f"https://example.com/2#section-0",
            },
            {
                "uuid": "2-1",
                "html_scraped": "<section><p>Section2</p></section>",
                "timestamp": pd.to_datetime(0),
                "url": f"https://example.com/2#section-1",
            }
        ]),
        pd.DataFrame([
            {
                "uuid": "3-0",
                "html_scraped": "<section><h1>Heading1</h1><p>Section1</p></section>",
                "timestamp": pd.to_datetime(0),
                "url": f"https://example.com/3#section-0",
            },
            {
                "uuid": "3-1",
                "html_scraped": "<section><p>Section2</p></section>",
                "timestamp": pd.to_datetime(0),
                "url": f"https://example.com/3#section-1",
            }
        ]),
        pd.DataFrame([
            {
                "uuid": "4-0",
                "html_scraped": "<section><h1>Heading1</h1><p>Section1</p></section>",
                "timestamp": pd.to_datetime(0),
                "url": f"https://example.com/4#section-0",
            },
            {
                "uuid": "4-1",
                "html_scraped": "<section><p>Section2</p></section>",
                "timestamp": pd.to_datetime(0),
                "url": f"https://example.com/4#section-1",
            }
        ])
    ]

@pytest.fixture
def nhs_pages_raw() -> pd.DataFrame:
    """A fixture with NHS pages before splitting.

    Returns:
        pd.DataFrame: The mock scraped NHS data.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: html_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
    """
    html_scraped = [
        "<p>No section</p>",
        "<section><p>Section1</p></section>",
        "<section><p>Section1</p></section><section><p>Section2</p></section>",
        "<section><h1>Heading1</h1><p>Section1</p></section><section><p>Section2</p></section>",
        "<h1>Outside</h1><section><h1>Heading1</h1><p>Section1</p></section><section><p>Section2</p></section>",
    ]
    cases = [{
        "uuid": i,
        "url": f"https://example.com/{i}",
        "html_scraped": text,
        "timestamp": pd.to_datetime(0)
    } for i, text in enumerate(html_scraped)]

    return pd.DataFrame(cases)


def test_split_page(nhs_pages_raw: pd.DataFrame, nhs_pages_split: List[pd.DataFrame]):
    """Test splitting individual pages.

    Args:
        nhs_pages_raw (pd.DataFrame): The mock raw scraped NHS data.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: html_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
        nhs_pages_split (List[pd.DataFrame]): The list of mock split scraped NHS data.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: html_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
    """
    nhs_pages_raw_rows = [row for _, row in nhs_pages_raw.iterrows()]
    for expected, nhs_page in zip(nhs_pages_split, nhs_pages_raw_rows):
        got = split_page(nhs_page, "NHS")
        assert_frame_equal(expected, got)


def test_split_nhs_pages(nhs_pages_raw: pd.DataFrame, nhs_pages_split: List[pd.DataFrame]):
    """Test split NHS pages step.

    Args:
        nhs_pages_raw (pd.DataFrame): The mock raw scraped NHS data.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: html_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
        nhs_pages_split (List[pd.DataFrame]): The list of mock split scraped NHS data.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: html_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object

    """
    expected = pd.concat(nhs_pages_split)
    got = split_pages.entrypoint(nhs_pages_raw)
    assert_frame_equal(expected, got)