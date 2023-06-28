"""Unit tests for scrape mind data step."""
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from bs4 import BeautifulSoup
from freezegun import freeze_time
from pandas.testing import assert_frame_equal
from requests_html import HTMLSession
from steps.scrape_mind_data.scrape_mind_data_step import (
    Scraper,
    scrape_conditions_and_drugs_sections,
    scrape_helping_someone_section,
    scrape_mind_data,
)


@pytest.fixture(autouse=True)
def mocked_html_session_get(mocked_html_text: str) -> MagicMock:
    """A fixture that mock the result of session.get(url).text.

    Args:
        mocked_html_text (str): the mocked html text.

    Yields:
        MagicMock: the mocked method.
    """
    with patch.object(HTMLSession, "get") as mock_method:
        mock_method.return_value.text = mocked_html_text
        yield mock_method


@pytest.fixture
def scraper() -> Scraper:
    """A fixture for an instance of the Scraper class.

    Returns:
        BaseScraper: a Scraper instance for testing.
    """
    return Scraper()


@pytest.fixture
def mocked_html_text() -> str:
    """A fixture of a mocked html text that will be used for functions that request html text from a webpage.

    Returns:
        str: the mocked HTML text.
    """
    html_text = """
<html>
<head>
<title>Mocked HTML Text</title>
</head>
<body>
<div class="content-area bg-white">
    <div class="test_col_1">
        <a href="/test_href_1/">Test Title 1</a>"
    </div>
    <div class="test_col_2">
        <a href="/test_href_2/">Test Title 2</a>"
    </div>
    <div class="test_col_3">
        <a href="/test_href_3/">Yes</a>"
    </div>
    <div class="test_col_4">
        <a href="/test_href_4/">Test Title 4</a>"
    </div>
</div>
<ul class="sidebar-menu" id="sidebar_menu">
    <li class=""><a href="/test_side_bar_object_1_url/">Side Bar Object 1</a></li>
    <li class=""><a href="/test_side_bar_exclude_me/">exclude_me</a></li>
    <li class=""><a href="/test_side_bar_object_2_url/">Side Bar Object 2</a></li>
</ul>
<div class="col-md-8 column ">
    <div class="test_content_class">
        <h2>Test h2 text</h2>
        <p>Test p text</p>
        <li>Text li text</li>
    </div>
</div>
<div class="col-md-12 column ">
    <div class="test_content_class">
        <h2>Test h3 text</h2>
        <p>Test p text</p>
        <li>Text li text</li>
    </div>
</div>
</body>
</html>
    """

    return html_text


def test_get_html_text(scraper: Scraper, mocked_html_text: str):
    """Test if whether get().text from the HTMLSession class returns the mocked HTML text.

    Args:
        scraper (Scraper): a Scraper instance.
        mocked_html_text (str): the mocked html texts from conftest.
    """
    result = scraper.get_html_text("test_url")
    assert result == mocked_html_text


def test_create_soup(scraper: Scraper, mocked_html_session_get: MagicMock):
    """Test that the create_soup function is returning a BeautifulSoup object with the expected html text.

    Args:
        scraper (Scraper): a Scraper instance.
        mocked_html_session_get (str): the mocked html texts from conftest.
    """
    soup = scraper.create_soup("test_url")

    mocked_html_session_get.assert_called_with("test_url")
    assert isinstance(soup, BeautifulSoup)


def test_build_subpage_url(scraper: Scraper):
    """Test that the build_subpage_url function returns the expected url.

    Args:
        scraper (Scraper): a BaseScraper instance.
    """
    expected_result = "https://www.mind.org.uk/test_subpage_url"
    result = scraper.build_subpage_url("/test_subpage_url")

    assert isinstance(result, str)
    assert result == expected_result


@freeze_time("2023-06-25")
def test_create_dataframe(scraper: Scraper):
    """Test that the create_dataframe function creates a pandas dataframe with th 4 expected columns and contains the expected data.

    Args:
        scraper (Scraper): a BaseScraper instance.
    """
    mocked_data = {"mocked_url": "mocked_text_scraped"}

    result_df = scraper.create_dataframe(mocked_data)

    expected_df = pd.DataFrame(
        {
            "text_scraped": ["mocked_text_scraped"],
            "timestamp": ["20230625"],
            "url": ["mocked_url"],
        }
    )

    assert isinstance(result_df, pd.DataFrame)
    assert_frame_equal(result_df, expected_df)


def test_extract_section_list(scraper: Scraper):
    """Test that the extract_section_list function returns the expected dictionary.

    Based on the mocked html text defined in conftest. We should expected the dictionary returned to have two objects.

    Args:
        scraper (Scraper): a Scraper instance.
    """
    objects_dict = scraper.extract_section_list("test_url")

    expected_objects_dict = {
        "Test Title 1": "/test_href_1/",
        "Test Title 2": "/test_href_2/",
    }
    assert isinstance(objects_dict, dict)
    assert objects_dict == expected_objects_dict


def test_get_object_side_bar_urls(scraper: Scraper):
    """Test that the get_object_side_bar_urls function is able to get the side bar urls based on the tags that side bars have.

    Args:
        scraper (Scraper): a Scraper instance.
    """
    side_bar_urls = scraper.get_object_side_bar_urls("test_url", "exclude_me/")

    expected_side_bar_urls = [
        "/test_side_bar_object_1_url/",
        "/test_side_bar_object_2_url/",
    ]
    assert isinstance(side_bar_urls, list)
    assert side_bar_urls == expected_side_bar_urls


def test_scrape_sub_page_data(scraper: Scraper):
    """Test that the scrape_sub_page_data function is able to scrape data from a webpage given a url and the class name that contents have.

    Args:
        scraper (Scraper): a Scraper instance.
    """
    sub_page_data = scraper.scrape_sub_page_data(
        "test_sub_page_url", "test_content_class"
    )

    expected_sub_page_data = [
        "Test h2 text",
        "Test p text",
        "Text li text",
        "Test h3 text",
        "Test p text",
        "Text li text",
    ]
    assert isinstance(expected_sub_page_data, list)
    assert sub_page_data == expected_sub_page_data


def test_scrape_conditions_and_drugs_sections(scraper: Scraper):
    """Test that the scrape_conditions_and_drugs_sections function is able to scrape the expected data from the mocked html text.

    The way Mind structure their webpage is that if a pages contains side bar, content will be under the "col-md-8 column" class, otherwise, the "col-md-12 column" class.

    Args:
        scraper (Scraper): a Scraper instance.
    """
    data_scraped = scrape_conditions_and_drugs_sections(scraper, {})

    # If get_object_side_bar_urls() returns a list of side bar urls, it will scrape data with the "col-md-8 column" class name as this is how mind structured their webpage.
    expected_data_scraped = {
        "https://www.mind.org.uk/test_side_bar_object_1_url/": "Test h2 text\nTest p text\nText li text",
        "https://www.mind.org.uk/test_side_bar_exclude_me/": "Test h2 text\nTest p text\nText li text",
        "https://www.mind.org.uk/test_side_bar_object_2_url/": "Test h2 text\nTest p text\nText li text",
    }
    assert isinstance(expected_data_scraped, dict)
    assert data_scraped == expected_data_scraped

    scraper.get_object_side_bar_urls = MagicMock(return_value=None)
    # If get_object_side_bar_urls() returns None, it will scrape data with the "col-md-12 column" class name as this is how mind structured their webpage.
    data_scraped = scrape_conditions_and_drugs_sections(scraper, {})

    expected_data_scraped = {
        "https://www.mind.org.uk/test_href_1/": "Test h3 text\nTest p text\nText li text",
        "https://www.mind.org.uk/test_href_2/": "Test h3 text\nTest p text\nText li text",
    }
    assert isinstance(expected_data_scraped, dict)
    assert data_scraped == expected_data_scraped


def test_scrape_helping_someone_section(scraper: Scraper):
    """Test that the scrape_helping_someone_section function is able to scrape the expected data from the mocked html text.

    The way Mind structure their webpage is that if a pages contains side bar, content will be under the "col-md-8 column" class, otherwise, the "col-md-12 column" class.

    Args:
        scraper (Scraper): a Scraper instance.
    """
    data_scraped = scrape_helping_someone_section(scraper, {})

    expected_dict_values = {"Test h2 text\nTest p text\nText li text"}
    assert isinstance(data_scraped, dict)
    assert set(data_scraped.values()) == expected_dict_values

    scraper.get_object_side_bar_urls = MagicMock(return_value=None)
    data_scraped = scrape_helping_someone_section(scraper, {})

    expected_dict_values = {"Test h3 text\nTest p text\nText li text"}
    assert isinstance(data_scraped, dict)
    assert set(data_scraped.values()) == expected_dict_values


@freeze_time("2023-06-25")
def test_scrape_mind_data():
    """Test that the scrape_mind_data step returns the expected dataframe."""
    result_df = scrape_mind_data.entrypoint()

    expected_df = pd.DataFrame(
        {
            "text_scraped": [
                "Test h2 text\nTest p text\nText li text",
                "Test h2 text\nTest p text\nText li text",
                "Test h2 text\nTest p text\nText li text",
            ],
            "timestamp": ["20230625", "20230625", "20230625"],
            "url": [
                "https://www.mind.org.uk/test_side_bar_object_1_url/",
                "https://www.mind.org.uk/test_side_bar_exclude_me/",
                "https://www.mind.org.uk/test_side_bar_object_2_url/",
            ],
        }
    )

    assert_frame_equal(result_df, expected_df)
