"""Clean the scraped data."""
import re
from typing import Union

import pandas as pd
from bs4 import BeautifulSoup, Tag
from zenml import step


def add_punctuation(text: str) -> str:
    """Add a full stop if the text does not end with a punctuation mark.

    Args:
        text (str): text to update

    Returns:
        str: updated text
    """
    if len(text) == 0:
        return text
    elif text[-1] not in [".", "!", "?"]:
        return text + "."
    else:
        return text


def is_lone_link(a_tag: Tag) -> bool:
    """Check whether the link is lone.

    Lone link is when it does not have any other text within the same parent tag,
    i.e. the only text there is the link text itself.

    Args:
        a_tag (Tag): <a> tag to test

    Returns:
        bool: decision
    """

    def get_text_parent(tag: Tag) -> Union[Tag, None]:
        """Get the innermost text tag.

        Text tag is a p, h1, h2, or h3

        Args:
            tag (Tag): tag to get the parent for

        Returns:
            Tag: text parent tag
        """
        text_tags = ["p", "h1", "h2", "h3"]
        parent = tag.parent
        if parent:
            if parent.name in text_tags:
                return parent
            else:
                return get_text_parent(parent)
        else:
            return None

    parent = get_text_parent(a_tag)
    if parent is None:
        return False  # Special case, when the link is not within any text tag

    return parent.text == a_tag.text


def clean_mind_dataset(bs: BeautifulSoup) -> BeautifulSoup:
    """_summary_.

    Args:
        bs (BeautifulSoup): _description_

    Returns:
        str: _description_
    """
    # Remove videos for Mind dataset
    video_class = bs.find_all("div", {"class": "video-wrapper"})
    for video in video_class:
        video.parent.decompose()

    # Remove podcast for Mind dataset
    podcast_href = bs.find_all("a", {"href": "/information-support/podcasts/"})
    for podcast in podcast_href:
        podcast.parent.parent.decompose()

    return bs


def clean_nhs_dataset(bs: BeautifulSoup) -> BeautifulSoup:
    """_summary_.

    Args:
        bs (BeautifulSoup): _description_

    Returns:
        BeautifulSoup: _description_
    """
    # Remove videos for NHS dataset
    video_class = bs.find_all("div", {"class": "app-brightcove-video"})
    for video in video_class:
        video.decompose()

    return bs


def clean_html(html: str) -> str:
    """Clean html.

    Args:
        html (str): HTML string to clean

    Return:
        str: cleaned text, with html tags removed
    """
    bs = BeautifulSoup(html, "lxml")

    # Remove <aside>
    aside = bs.find_all("aside")
    for tag in aside:
        tag.decompose()

    # Clean Mind dataset
    bs = clean_mind_dataset(bs)

    # Clean NHS dataset
    bs = clean_nhs_dataset(bs)

    # Punctuate headings
    headings = bs.find_all(["h1", "h2", "h3", "li"])
    for heading in headings:
        heading.replace_with(add_punctuation(heading.text.strip()))

    # Remove lone links
    links = bs.find_all("a")
    for link in links:
        if is_lone_link(link):
            link.decompose()

    return bs.get_text(" ")


def remove_new_line(s: str) -> str:
    r"""Remove new line characters.

    Args:
        s: String from which to remove the '\n' characters.

    Returns:
        The string but without any new line characters.
    """
    return s.replace("\n", " ")


def strip_string(s: str) -> str:
    """Strip the string.

    Args:
        s: The string to strip.

    Returns:
        Stripped version of the s arg.
    """
    return s.strip()


def remove_nbsp(s: str) -> str:
    r"""Remove non-blank spaces from the string, insert a space instead.

    Args:
        s: the string from which to remove non-blank white space.

    Returns:
        The s arg but with no \xa0 present.
    """
    return s.replace("\xa0", " ")


def insert_space_between_numbers_and_letters(s: str) -> str:
    """Insert a space anywhere there's a number and a letter next to each other.

    Args:
        s: The string to which spaces are added between numbers and letters.

    Returns:
        The s arg but with spaces inserted anywhere a letter and number are adjacent.
    """
    regex = "(?<=[a-zA-Z])(?=\\d)|(?<=\\d)(?=[a-zA-Z])"
    subst = " "
    result = re.sub(regex, subst, s, 0)
    return result


def contract_white_space(s: str) -> str:
    """Contract multiple white spaces into one.

    Args:
        s: The string from which consecutive white spaces are removed and replaced with single spaces.

    Returns:
        A string containing no consecutive white space.
    """
    return re.sub(" +", " ", s)


@step
def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Clean the scraped data.

    Clean the data by dropping rows containing NaN, dropping duplicates, removing new line characters, removing
    punctuation, making everything lower case, removing blank space and removing nbsp. The returned data is reformatted
    into a dataframe with one column, each row containing one sentence.

    Args:
        data (pd.DataFrame): The scraped data.

    Returns:
        pd.DataFrame: The cleaned data in the new format described above.
            Index:
                RangeIndex
            Columns:
                Name: uuid, dtype: object
                Name: text_scraped, dtype: object
                Name: timestamp, dtype: datetime64[ns]
                Name: url, dtype: object
    """
    data = data.dropna().copy()

    data["text_scraped"] = data["html_scraped"].map(clean_html)

    data["text_scraped"] = data["text_scraped"].map(remove_new_line)
    data["text_scraped"] = data["text_scraped"].map(strip_string)
    data["text_scraped"] = data["text_scraped"].map(remove_nbsp)
    data["text_scraped"] = data["text_scraped"].map(contract_white_space)
    data["text_scraped"] = data["text_scraped"].map(
        insert_space_between_numbers_and_letters
    )

    data = data.drop(data[data.text_scraped == ""].index)
    data = data.drop_duplicates()
    data = data.drop(columns=["html_scraped"])

    return data.reset_index(drop=True)
