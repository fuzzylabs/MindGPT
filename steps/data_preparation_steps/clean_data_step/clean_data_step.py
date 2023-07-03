"""Clean the scraped data."""
import pandas as pd
from zenml import step


def reformat(df: pd.DataFrame) -> pd.DataFrame:
    """Reformat the scraped data dataframe into a one-sentence-per-row dataframe.

    Args:
        df (pd.DataFrame): A pandas dataframe holding the scraped data.

    Returns:
        A reformatted pandas DataFrame.
    """
    sentences = []
    df["text_scraped"].map(lambda s: sentences.extend(s.split(".")))
    return pd.DataFrame({"sentences": sentences})


def remove_punctuation(data_string: str) -> str:
    """Remove punctuation from a scraped data string.

    Args:
        data_string (str): A string representing a sentence from which to remove the punctuation.

    Returns: The string but with punctuation removed.
    """
    punc_nospace = {
        "!",
        "?",
        ".",
        ",",
        "-",
        "–",
        "+",
        "=",
        "(",
        ")",
        ":",
        "'",
        ";",
        '"',
        "%",
        "&",
        "*",
        "_",
    }
    for p in punc_nospace:
        data_string = data_string.replace(p, "")

    punc_space = {"/"}
    for p in punc_space:
        data_string = data_string.replace(p, " ")

    return data_string


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
        return s.replace("\n", " ")

    def lower_case(s: str) -> str:
        return s.lower()

    def strip_string(s: str) -> str:
        return s.strip()

    def remove_nbsp(s: str) -> str:
        return s.replace("\xa0", " ")

    data["text_scraped"] = data["text_scraped"].map(remove_new_line)
    data["text_scraped"] = data["text_scraped"].map(lower_case)
    data["text_scraped"] = data["text_scraped"].map(strip_string)
    data["text_scraped"] = data["text_scraped"].map(remove_nbsp)

    data = reformat(data)

    # now text is split into sentences, remove punc
    data["sentences"] = data["sentences"].map(remove_punctuation)

    def remove_double_spaces(s: str) -> str:
        return s.replace("  ", " ")

    data["sentences"] = data["sentences"].map(remove_double_spaces)

    data["sentences"] = data["sentences"].map(strip_string)

    # drop empty strings
    data = data.drop(data[data.sentences == ""].index)
    data = data.drop_duplicates()

    return data
