"""Test script for test_scrape_nhs_data."""
from datetime import date
from unittest.mock import patch

import pandas as pd
import pytest
from bs4 import BeautifulSoup
from pandas.testing import assert_frame_equal
from steps.scrape_nhs_data.scrape_nhs_data_step import (
    HTMLSession,
    NHSMentalHealthScraper,
)


@pytest.fixture
def arguments():
    """A fixture representing the arguments required to test the NHSMentalHealthScraper class."""
    return (
        "./tests/test_steps/test_scrape_nhs_data/test_html/test.html",
        "div",
        {"class": "target_div"},
    )


@pytest.fixture
def nhs_mental_health_scraper(arguments: set):
    """A fixture representing the NHSMentalHealthScraper class.

    Args:
    arguments (set): a list of arguments used to construct the nhs_mental_health_scraper instance
    """
    url, tag, attributes = arguments

    class MockResponse:
        def __init__(self, html_text):
            self.html_text = html_text

        @property
        def text(self):
            return self.html_text

    def mock_get(url):
        with open(url) as file:
            html_text = file.read()
            return MockResponse(html_text)

    with patch.object(HTMLSession, "get", side_effect=mock_get):
        return NHSMentalHealthScraper(url=url, tag=tag, attributes=attributes)


def test_init(nhs_mental_health_scraper: NHSMentalHealthScraper, arguments: set):
    """Tests the constructor for the NHSMentalHealthScraper class.

    Args:;
        nhs_mental_health_scraper (NHSMentalHealthScraper): a patched NHSMentalHealthScraper instance
    arguments (set): a list of arguments used to construct the nhs_mental_health_scraper instance
    """
    url, tag, attributes = arguments
    test_file_content = ""
    timestamp = date.today()

    with open(url) as file:
        test_file_content = file.read()

    assert nhs_mental_health_scraper._url is url
    assert nhs_mental_health_scraper._tag is tag
    assert nhs_mental_health_scraper._attributes is attributes
    assert nhs_mental_health_scraper._scraped_list == [
        "./tests/test_steps/test_scrape_nhs_data/test_html/test.html"
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
    test_df = pd.DataFrame(
        [{"text_scraped": test_text, "timestamp": timestamp, "url": url}]
    )
    assert_frame_equal(nhs_mental_health_scraper.df, test_df)


def test_identify_target(
    nhs_mental_health_scraper: NHSMentalHealthScraper, arguments: set
):
    """Tests the _identify_target method of the NHSMentalHealthScraper class.

    Args:;
        nhs_mental_health_scraper (NHSMentalHealthScraper): a patched NHSMentalHealthScraper instance
    arguments (set): a list of arguments used to construct the nhs_mental_health_scraper instance
    """
    url, tag, attributes = arguments

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


def test_scrape(nhs_mental_health_scraper: NHSMentalHealthScraper, arguments: set):
    """Tests the scrape method of the NHSMentalHealthScraper class.

    Args:;
        nhs_mental_health_scraper (NHSMentalHealthScraper): a patched NHSMentalHealthScraper instance
    arguments (set): a list of arguments used to construct the nhs_mental_health_scraper instance
    """
    url, tag, attributes = arguments
    timestamp = date.today()
    with open(url) as file:
        file_content = file.read()
        test_text = (
            BeautifulSoup(file_content, "lxml")
            .find(name=tag, attrs=attributes)
            .get_text(" ")
        )
        scraper_df = nhs_mental_health_scraper.scrape()
        test_df = pd.DataFrame(
            [{"text_scraped": test_text, "timestamp": timestamp, "url": url}]
        )
        assert_frame_equal(scraper_df, test_df)
