"""Scrape data from the NHS website."""
import os
import re
import uuid
from datetime import datetime
from typing import Annotated, Dict, List, Optional, Union

import pandas as pd
from bs4 import BeautifulSoup, NavigableString, Tag
from config import DATA_DIR
from requests_html import HTMLSession  # type: ignore
from zenml import step


class NHSMentalHealthScraper:
    """A scraper class for scraping the NHS Mental Health (https://www.nhs.uk/mental-health/) website."""

    def __init__(
        self,
        url: str,
        tag: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
        scraped_list: List[str] = [],
    ) -> None:
        """Constructor for the NHSMentalHealthScraper class.

        The NHSMentalHealthScraper constructor takes a URL for the target website to be scraped, alongside optional tag and attribute arguments that are used to identify a specific tag (i.e. subset of a page) to be scraped.

        Args:
            url (str): the target URL for the scraper.
            tag (Optional[str]): the target HTML tag for the scraper.
            attributes (Optional[Dict[str, str]]): the target attributes for scraper.
            scraped_list (List[str]): the list containing previously scraped URLs.
        """
        self._url = url
        self._tag = tag
        self._attributes = attributes
        self._scraped_list = scraped_list
        self._session = HTMLSession()
        self._response = self._session.get(self._url)
        self._html_text = self._response.text
        self._soup = BeautifulSoup(self._html_text, "lxml")
        self.links = self.get_links()
        self.df = self.scrape()

        if self._scraped_list == []:
            self._scraped_list = [self._url]

    def _identify_target(self) -> Union[Tag, NavigableString, BeautifulSoup]:
        """A method to identify the HTML elements to scrape.

        Returns:
            (Union[Tag, NavigableString, BeautifulSoup]): if a tag or attribute is passed, the relevant Tag or NavigableString will be returned if present. If no tag or attribute is passed, a BeautifulSoup object representing the target URL will be returned.
        """
        target = None
        if self._tag and self._attributes:
            target = self._soup.find(name=self._tag, attrs=self._attributes)
        elif self._tag:
            target = self._soup.find(name=self._tag)
        elif self._attributes:
            target = self._soup.find(attrs=self._attributes)
        else:
            target = self._soup

        if target:
            return target
        else:
            return self._soup

    def get_links(self) -> List[str]:
        """A method to extract all links present within the target tag or page.

        Returns:
            (List[str]): a list containing strings representing all links found within the target tag or page.
        """
        target = self._identify_target()
        a_tags = target.find_all(name="a")  # type: ignore
        return [a_tag.get("href") for a_tag in a_tags]

    def scrape(self) -> pd.DataFrame:
        """A method for scraping the text from target pages.

        Returns:
            pd.DataFrame: a Pandas DataFrame with four columns ("text_scraped", "timestamp", "url") and a single record representing the results of the scrape.
                Index:
                    RangeIndex
                Columns:
                    Name: uuid, dtype: object
                    Name: html_scraped, dtype: object
                    Name: text_scraped, dtype: object
                    Name: timestamp, dtype: datetime64[ns]
                    Name: url, dtype: object
        """
        timestamp = datetime.now()
        target = self._identify_target()
        return pd.DataFrame(
            [
                {
                    "uuid": str(uuid.uuid4()),
                    "html_scraped": str(target),
                    "text_scraped": target.get_text(" "),
                    "timestamp": timestamp,
                    "url": self._url,
                }
            ]
        )

    def discard_non_content(self):
        def discard_decision(html_scraped: str) -> bool:
            bs = BeautifulSoup(html_scraped, parser="lxml")
            return bs.find(class_="nhsuk-lede-text") is not None

        df_index = self.df.html_scraped.apply(discard_decision)
        print(f"Discarded pages: {df_index.sum()}")
        self.df = self.df[~df_index]

    def scrape_recursively(self) -> None:
        """A method for recursively scraping all nested links found within a target website or Tag subject to conditions.

        Conditions:
            - the URL begins "https://www.nhs.uk/mental-health
            - the URL has not previously been scraped.
        """
        for link in self.links:
            # some links on the NHS Mental Health website do not follow the typical (i.e. https://www.nhs.uk/mental-health) format, and are truncated (e.g. /mental-health/...). The below conditional enforces a consistent format.
            if re.match(r"^(\/mental-health){1}.+", link):
                valid_link = str(f"https://www.nhs.uk{link}")
            else:
                valid_link = str(link)
            # if the link has a URL beginning https://www.nhs.uk/mental-health and has not already been scraped, it will be scraped recursively.
            if (
                re.match(r"^(https:\/\/www.nhs.uk\/mental-health){1}.+", valid_link)
                and valid_link not in self._scraped_list
            ):
                self._scraped_list.append(valid_link)
                nhs_mental_health_scraper = NHSMentalHealthScraper(
                    url=valid_link,
                    tag=self._tag,
                    attributes=self._attributes,
                    scraped_list=self._scraped_list,
                )
                nhs_mental_health_scraper.scrape_recursively()
                self.df = pd.concat([self.df, nhs_mental_health_scraper.df])


@step
def scrape_nhs_data() -> Annotated[pd.DataFrame, "output_nhs_data"]:
    """A ZenML pipeline step for scraping the NHS Mental Health website.

    Returns:
        pd.DataFrame: a Pandas DataFrame with four columns ("text_scraped", "timestamp", "url") and a single record representing the results of the scrape.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: html_scraped, dtype: object
                Name: text_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
    """
    nhs_scraper = NHSMentalHealthScraper(
        url="https://www.nhs.uk/mental-health/",
        attributes={"class": "nhsuk-main-wrapper"},
    )
    nhs_scraper.scrape_recursively()
    nhs_scraper.discard_non_content()

    nhs_scraper.df.to_csv(os.path.join(DATA_DIR, "nhs_data_raw.csv"))

    return nhs_scraper.df
