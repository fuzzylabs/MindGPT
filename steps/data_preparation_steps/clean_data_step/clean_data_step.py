"""Clean the scraped data."""
import re

import pandas as pd
from zenml import step


@step
def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Clean the scraped data.

    Clean the data by dropping rows containing NaN, dropping duplicates, removing new line characters, removing
    punctuation, making everything lower case, removing blank space and removing nbsp. The returned data is reformatted
    into a dataframe with one column, each row containing one sentence.

    Args:
        data (pd.DataFrame): The scraped data.

    Returns:
        The cleaned data in the new format described above.
    """
    data = data.dropna().copy()
    data = data.drop_duplicates()

    def remove_new_line(s: str) -> str:
        """Remove new line characters.

        Args:
            s: A string.
        """
        return s.replace("\n", " ")

    def lower_case(s: str) -> str:
        return s.lower()

    def strip_string(s: str) -> str:
        return s.strip()

    def remove_nbsp(s: str) -> str:
        return s.replace("\xa0", " ")

    def insert_space_between_numbers_and_letters(s: str) -> str:
        regex = "(?<=[a-zA-Z])(?=\\d)|(?<=\\d)(?=[a-zA-Z])"
        subst = " "
        result = re.sub(regex, subst, s, 0)
        return result

    def contract_white_space(s: str) -> str:
        return re.sub(" +", " ", s)

    data["text_scraped"] = data["text_scraped"].map(remove_new_line)
    data["text_scraped"] = data["text_scraped"].map(lower_case)
    data["text_scraped"] = data["text_scraped"].map(strip_string)
    data["text_scraped"] = data["text_scraped"].map(remove_nbsp)
    data["text_scraped"] = data["text_scraped"].map(contract_white_space)
    data["text_scraped"] = data["text_scraped"].map(
        insert_space_between_numbers_and_letters
    )
    # data["text_scraped"] = data["text_scraped"].map(remove_punctuation)

    # drop empty strings
    data = data.drop(data[data.text_scraped == ""].index)
    data = data.drop_duplicates()

    return data.reset_index(drop=True)
