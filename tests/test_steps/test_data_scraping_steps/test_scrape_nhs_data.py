"""Test script for test_scrape_nhs_data."""
from unittest.mock import patch

import pandas as pd
import pytest
from bs4 import BeautifulSoup
from pandas.testing import assert_frame_equal
from steps.data_scraping_steps.scrape_nhs_data.scrape_nhs_data_step import (
    HTMLSession,
    NHSMentalHealthScraper,
)


@pytest.fixture
def expected_columns() -> set:
    """The columns that we would expect to be returned from the scraping process.

    Returns:
        set: a set containing the expected columns
    """
    return {"uuid", "html_scraped", "text_scraped", "timestamp", "url"}


@pytest.fixture
def nhs_mental_health_scraper_arguments() -> set:
    """A fixture representing the arguments required to test the NHSMentalHealthScraper class.

    Returns:
    A set containing the arguments used to construct the mocked NHSMentalHealthScraper instance
    """
    return (
        "./tests/test_steps/test_data_scraping_steps/test_html/test.html",
        "div",
        {"class": "target_div"},
    )


@pytest.fixture
def nhs_mental_health_to_discard_arguments() -> set:
    """A fixture representing the arguments required to test the NHSMentalHealthScraper class for discarding.

    Returns:
    A set containing the arguments used to construct the mocked NHSMentalHealthScraper instance
    """
    return (
        "./tests/test_steps/test_data_scraping_steps/test_html/discarded_test.html",
        "div",
        {"class": "target_div"},
    )


def get_mock_nhs_mental_health_scraper(arguments: set) -> NHSMentalHealthScraper:
    """Construct mock NHSMentalHealthScraper.

    Args:
        arguments (set): a list of arguments used to construct the nhs_mental_health_scraper instance

    Returns:
        (NHSMentalHealthScraper): A mocked NHSMentalHealthScraper instance
    """
    url, tag, attributes = arguments

    class MockResponse:
        """A mock response object for the HTML.get method."""

        def __init__(self, html_text):
            self.html_text = html_text

        @property
        def text(self):
            return self.html_text

    def mock_get(url):
        """A mock get method for the HTML class."""
        with open(url) as file:
            html_text = file.read()
            return MockResponse(html_text)

    with patch.object(HTMLSession, "get", side_effect=mock_get):
        return NHSMentalHealthScraper(url=url, tag=tag, attributes=attributes)


@pytest.fixture
def nhs_mental_health_scraper(
    nhs_mental_health_scraper_arguments: set,
) -> NHSMentalHealthScraper:
    """A fixture representing the NHSMentalHealthScraper class.

    Args:
        nhs_mental_health_scraper_arguments (set): a list of arguments used to construct the NHSMentalHealthScraper instance

    Returns:
        (NHSMentalHealthScraper): A mocked NHSMentalHealthScraper instance
    """
    return get_mock_nhs_mental_health_scraper(nhs_mental_health_scraper_arguments)


@pytest.fixture
def nhs_mental_health_scraper_discarded(
    nhs_mental_health_to_discard_arguments: set,
) -> NHSMentalHealthScraper:
    """A fixture representing the NHSMentalHealthScraper class with discarded pages.

    Args:
        nhs_mental_health_to_discard_arguments (set): a list of arguments used to construct the NHSMentalHealthScraper instance

    Returns:
        (NHSMentalHealthScraper): A mocked NHSMentalHealthScraper instance
    """
    return get_mock_nhs_mental_health_scraper(nhs_mental_health_to_discard_arguments)


def test_init(
    nhs_mental_health_scraper: NHSMentalHealthScraper,
    nhs_mental_health_scraper_arguments: set,
    expected_columns: set,
):
    """Tests the constructor for the NHSMentalHealthScraper class.

    Args:
        nhs_mental_health_scraper (NHSMentalHealthScraper): a patched NHSMentalHealthScraper instance
        nhs_mental_health_scraper_arguments (set): a list of arguments used to construct the nhs_mental_health_scraper instance
        expected_columns (set): a set of columns that we would expect to be returned by the scraping process
    """
    url, tag, attributes = nhs_mental_health_scraper_arguments
    test_file_content = ""

    with open(url) as file:
        test_file_content = file.read()

    assert nhs_mental_health_scraper._url is url
    assert nhs_mental_health_scraper._tag is tag
    assert nhs_mental_health_scraper._attributes is attributes
    assert nhs_mental_health_scraper._scraped_list == [
        "./tests/test_steps/test_data_scraping_steps/test_html/test.html"
    ]
    assert isinstance(nhs_mental_health_scraper._session, HTMLSession)
    assert nhs_mental_health_scraper._html_text == test_file_content
    assert nhs_mental_health_scraper._soup == BeautifulSoup(test_file_content, "lxml")
    assert nhs_mental_health_scraper.links == [
        "https://www.targetlink1.com",
        "https://www.targetlink2.com",
    ]
    test_text = (
        BeautifulSoup(test_file_content, "lxml")
        .find(name=tag, attrs=attributes)
        .get_text(" ")
    )
    test_df = pd.DataFrame([{"text_scraped": test_text, "url": url}])

    assert expected_columns == set(nhs_mental_health_scraper.df.columns.tolist())
    assert_frame_equal(nhs_mental_health_scraper.df[["text_scraped", "url"]], test_df)


def test_identify_target(
    nhs_mental_health_scraper: NHSMentalHealthScraper,
    nhs_mental_health_scraper_arguments: set,
):
    """Tests the _identify_target method of the NHSMentalHealthScraper class.

    Args:;
        nhs_mental_health_scraper (NHSMentalHealthScraper): a patched NHSMentalHealthScraper instance
        nhs_mental_health_scraper_arguments (set): a list of arguments used to construct the nhs_mental_health_scraper instance
    """
    url, tag, attributes = nhs_mental_health_scraper_arguments

    with open(url) as file:
        file_content = file.read()
        assert nhs_mental_health_scraper._identify_target() == BeautifulSoup(
            file_content, "lxml"
        ).find(name=tag, attrs=attributes)


def test_get_links(nhs_mental_health_scraper: NHSMentalHealthScraper):
    """Tests the get_links method of the NHSMentalHealthScraper class.

    Args:
        nhs_mental_health_scraper (NHSMentalHealthScraper): a patched NHSMentalHealthScraper instance
    """
    assert nhs_mental_health_scraper.get_links() == [
        "https://www.targetlink1.com",
        "https://www.targetlink2.com",
    ]


def test_scrape(
    nhs_mental_health_scraper: NHSMentalHealthScraper,
    nhs_mental_health_scraper_arguments: set,
    expected_columns: set,
):
    """Tests the scrape method of the NHSMentalHealthScraper class.

    Args:;
        nhs_mental_health_scraper (NHSMentalHealthScraper): a patched NHSMentalHealthScraper instance
        nhs_mental_health_scraper_arguments (set): a list of arguments used to construct the nhs_mental_health_scraper instance
        expected_columns (set): a set of columns that we would expect to be returned by the scraping process
    """
    url, tag, attributes = nhs_mental_health_scraper_arguments
    with open(url) as file:
        file_content = file.read()
        test_text = (
            BeautifulSoup(file_content, "lxml")
            .find(name=tag, attrs=attributes)
            .get_text(" ")
        )
        scraper_df = nhs_mental_health_scraper.scrape()
        test_df = pd.DataFrame([{"text_scraped": test_text, "url": url}])
        assert expected_columns == set(scraper_df.columns.tolist())
        assert_frame_equal(scraper_df[["text_scraped", "url"]], test_df)


def test_discard(
    nhs_mental_health_scraper_discarded: NHSMentalHealthScraper,
    expected_columns: set,
):
    """Tests the discard method of the NHSMentalHealthScraper class.

    Args:;
        nhs_mental_health_scraper_discarded (NHSMentalHealthScraper): a patched NHSMentalHealthScraper instance
        expected_columns (set): a set of columns that we would expect to be returned by the scraping process
    """
    nhs_mental_health_scraper_discarded.scrape_recursively()
    nhs_mental_health_scraper_discarded.discard_non_content()
    test_df = pd.DataFrame([], columns=["text_scraped", "url"], index=pd.Int64Index([]))
    assert expected_columns == set(
        nhs_mental_health_scraper_discarded.df.columns.tolist()
    )
    assert_frame_equal(
        nhs_mental_health_scraper_discarded.df[["text_scraped", "url"]], test_df
    )
