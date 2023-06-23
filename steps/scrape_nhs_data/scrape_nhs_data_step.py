"""Scrape data from the NHS website."""
from abc import ABC
from datetime import datetime
from typing import Dict, Optional

import pandas as pd
from bs4 import BeautifulSoup, NavigableString, Tag
from requests import post
from requests_html import HTMLSession  # type: ignore


class Scraper(ABC):
    """A base scraper class that can be extended to create specific scrapers."""

    def __init__(
        self,
        url: str,
        tag: Optional[str] = None,
        attribute: Optional[Dict[str, str]] = None,
    ) -> None:
        """Constructor for the Scraper class.

        The scraper constructor takes a URL for the target website to be scraped, alongside optional tag and attribute arguments that are used to identify a specific tag (i.e. subset of a page) to be scraped.

        Args:
            url (str): the target URL for the scraper.
            tag (Optional[str]): the target HTML tag for the scraper.
            attribute (Optional[Dict[str, str]]): the target attributes for scraper.
        """
        self._url = url
        self._tag = tag
        self._attribute = attribute
        self._session = HTMLSession()
        self._request = self._session.get(self._url)
        self._html_text = self._request.text
        self._soup = BeautifulSoup(self._html_text, "lxml")

    def _identify_target(self) -> Tag | NavigableString | None | BeautifulSoup:
        """A method to identify the HTML elements to scrape.

        Returns:
        (Tag | NavigableString | None | BeautifulSoup): if a tag or attribute is passed, the relevant Tag or NavigableString will be returned if present, otherwise None will be returned. If no tag or attribute is passed, a BeautifulSoup object representing the target URL will be returned.
        """
        if self._tag and self._attribute:
            return self._soup.find(name=self._tag, attrs=self._attribute)
        elif self._tag:
            return self._soup.find(name=self._tag)
        elif self._attribute:
            return self._soup.find(attrs=self._attribute)
        else:
            return self._soup

    def get_links(self) -> list[str]:
        """A method to extract all links present within the target tag or page.

        Returns:
        (list[str]): a list containing strings representing all links found within the target tag or page.
        """
        target = self._identify_target()
        a_tags = target.find_all(name="a", recursive=True)  # type: ignore
        return [a_tag.get("href") for a_tag in a_tags]

    def scrape(self) -> pd.DataFrame:
        """A method for scraping the text from target pages.

        Returns:
        (DataFrame): a Pandas DataFrame with four columns ("text_scraped", "timestamp", "url", "archived_url") and a single record representing the results of the scrape.
        """
        timestamp = datetime.now()
        wayback_timestamp = timestamp.strftime("%Y%m%d%H%M%S")
        archived_url = f"https://web.archive.org/web/{wayback_timestamp}/{self._url}"
        target = self._identify_target()
        _ = post("https://web.archive.org/save", data={"url": self._url})
        return pd.DataFrame(
            [
                {
                    "text_scraped": target.get_text(" "),  # type: ignore
                    "timestamp": timestamp,
                    "url": self._url,
                    "archived_url": archived_url,
                }
            ]
        )


class NHSMentalHealthScraper(Scraper):
    """A scraper class for scraping the NHS Mental Health (https://www.nhs.uk/mental-health/) website."""

    def __init__(
        self,
        url: str,
        tag: Optional[str] = None,
        attribute: Optional[Dict[str, str]] = None,
    ) -> None:
        """Constructor for the NHSMentalHealthScraper class.

        The NHSMentalHealthScraper constructor takes a URL for the target website to be scraped, alongside optional tag and attribute arguments that are used to identify a specific tag (i.e. subset of a page) to be scraped.

        Args:
            url (str): the target URL for the scraper.
            tag (Optional[str]): the target HTML tag for the scraper.
            attribute (Optional[Dict[str, str]]): the target attributes for scraper.
        """
        super().__init__(url=url, tag=tag, attribute=attribute)


scraper = NHSMentalHealthScraper(
    url="https://www.nhs.uk/mental-health/",
    tag="main",
    attribute={"class": "nhsuk-main-wrapper"},
)


# @step
# def scrape_nhs_data() -> pd.DataFrame:
#     """..."""
#     ...
