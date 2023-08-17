"""Split NHS pages step."""
from typing import List, Dict

import pandas as pd
from bs4 import BeautifulSoup
from zenml import step


SOURCE_MAPPING = {
    "nhs": {
        "tag": "section",
        "kwargs": {}
    },
    "mind": {
        "tag": "div",
        "kwargs": {
            "class_": "column"
        }
    }
}


def split_html(html: str, tag: str, kwargs: Dict[str, str]) -> List[str]:
    """Split html using the tag and some other optional Beautiful Soup arguments.

    Args:
        html (str): HTML text to split
        tag (str): tag to split by
        kwargs (Dict[str, str]): Beautiful Soup keyword arguments

    Returns:
        List[str]: list of HTML strings
    """
    soup = BeautifulSoup(html, "lxml")
    sections = soup.find_all(tag, **kwargs)
    return [str(section) for section in sections]


def split_page(data: pd.Series, source: str) -> pd.DataFrame:
    """Split a page.

    Preserve other metadata.
    * url is appended with an anchor suffix of the form '#section-{n}'
    * uuid is appended with an anchor suffix of the form '-{n}'
    * timestamp is kept as is

    Args:
        data (pd.Series): The scraped NHS data.
            Index:
                Name: uuid, dtype: object
                Name: html_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
        source (str): source of the page; determines how the page is split

    Returns:
        pd.DataFrame: The split page.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: html_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
    """
    params = SOURCE_MAPPING[source]
    if data.html_scraped:
        sections = split_html(data.html_scraped, params["tag"], params["kwargs"])
    else:
        sections = []
    return pd.DataFrame(
        [{
            "uuid": f"{data.uuid}-{i}",
            "html_scraped": section,
            "timestamp": data.timestamp,
            "url": f"{data.url}#section-{i}"
        } for i, section in enumerate(sections)],
        columns=["uuid", "html_scraped", "timestamp", "url"]
    )


@step
def split_pages(data: pd.DataFrame, source: str) -> pd.DataFrame:
    """Split the NHS pages by the <section> tag.

    Preserve other metadata.

    Args:
        data (pd.DataFrame): The scraped NHS data.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: html_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
        source (str): source of the page; determines how the page is split

    Returns:
        pd.DataFrame: The split data in the format described above.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: html_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
    """
    frames = data.apply(split_page, args=(source,), axis=1)
    return pd.concat(frames.tolist())
