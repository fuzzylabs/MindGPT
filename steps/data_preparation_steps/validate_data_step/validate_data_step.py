"""Validate data step."""
import os
import re

import numpy as np
import pandas as pd
import requests
from config import DATA_DIR
from zenml import step
from zenml.steps import Output

VALIDATED_FILE_NAME_POSTFIX = "_data_validated.csv"


def validate_links(s: str) -> bool:
    """Extracts links from a string and sends requests to see if the links are valid.

    Args:
        s (str): Input string.

    Returns:
        bool: True, if all links within a string return a 200:OK response. False, otherwise.
    """
    link_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    # Find all links in the string
    links = re.findall(link_pattern, s)

    # Check validity of each link
    for link in links:
        response = requests.head(link)
        if not response.ok:
            return False

    return True


def check_links_within_column(
    dataframe: pd.DataFrame, column_name: str
) -> pd.DataFrame:
    """Checks all entries in a column of a Pandas DataFrame does not contain unreachable website links.

    Args:
        dataframe (pd.DataFrame): The input DataFrame.
        column_name (str): Name of the column to check.

    Returns:
        pd.DataFrame: All rows that violate the current validation assertion.
    """
    mask = ~dataframe[column_name].apply(lambda x: validate_links(str(x)))
    df = dataframe[mask].copy()
    df["validation_warning"] = "Warning: row contains invalid links."
    return df


def check_column_empty_strings(
    dataframe: pd.DataFrame, column_name: str
) -> pd.DataFrame:
    """Checks if a column in a Pandas DataFrame contains any empty strings.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame.
        column_name (str): The name of the column to check.

    Returns:
        pandas.DataFrame: All rows that contain empty strings in the specified column.
    """
    mask = dataframe[column_name].apply(lambda x: not str(x))
    df = dataframe[mask].copy()
    df[
        "validation_warning"
    ] = f"Warning: row contains an empty string in column '{column_name}'."
    return df


def check_column_not_null(dataframe: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Checks if all entries in a column of a Pandas DataFrame are not NaN or Null.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame.
        column_name (str): The name of the column to check.

    Returns:
        pandas.DataFrame: All rows that violate the current validation assertion.
    """
    mask = dataframe[column_name].isnull()
    df = dataframe[mask].copy()
    df["validation_warning"] = "Warning: row contains Null value."
    return df


def check_column_is_string(dataframe: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Checks if a column in a Pandas DataFrame contains only string values.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame.
        column_name (str): The name of the column to check.

    Returns:
        pandas.DataFrame: All rows that violate the current validation assertion.
    """
    mask = ~dataframe[column_name].apply(lambda x: isinstance(x, str))
    df = dataframe[mask].copy()
    df["validation_warning"] = "Warning: row is not a string data type."
    return df


def check_column_ascii(dataframe: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Checks if every entry in a column of a Pandas DataFrame is ASCII.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame.
        column_name (str): The name of the column to check.

    Returns:
        pandas.DataFrame: All rows that violate the current validation assertion.
    """
    mask = ~dataframe[column_name].apply(lambda x: isinstance(x, str) and x.isascii())
    df = dataframe[mask].copy()
    df["validation_warning"] = "Warning: row contains non ASCII characters."
    return df


def flag_outliers(dataframe: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Calculates the mean and standard deviation of the number of words for all strings in a column of a Pandas DataFrame and flags rows that are greater than two standard deviations away from the mean on either side.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame.
        column_name (str): The name of the column to calculate the statistics and flag outliers for.

    Returns:
        pandas.DataFrame: The input DataFrame with an additional "outlier_flag" column indicating the outliers.
    """
    words_count = dataframe[column_name].astype(str).str.split().apply(len)
    mean = np.mean(words_count)
    std = np.std(words_count)

    # ~= Normal distribution with 98% confidence interval
    mask = (words_count > mean + 2 * std) | (words_count < mean - 2 * std)
    df: pd.DataFrame = dataframe[mask].copy()
    df["validation_warning"] = df[column_name].apply(
        lambda x: f"Warning: the number of words '{len(str(x).split())}' in this row has been flagged as an outlier."
    )
    return df


def _write_data(data: pd.DataFrame, destination: str, data_source: str) -> None:
    """A function to write the validated dataframe to file.

    Args:
        data (pd.DataFrame): the dataframe to write to disk.
        destination (str): the directory to save the dataframe in.
        data_source (str): the source for the data, i.e., the website.
    """
    data.to_csv(
        os.path.join(destination, f"{data_source}{VALIDATED_FILE_NAME_POSTFIX}"),
        index=False,
    )


@step
def validate_data(
    data: pd.DataFrame, source: str
) -> Output(is_valid=bool, rows_with_warning=pd.DataFrame):  # type: ignore
    """A step to validate text within the data DataFrame.

    Args:
        data (pd.DataFrame): Data to validate.
        source (str): The source of the data being validated.

    Returns:
        is_valid (bool): True, if all rows pass data validation checks, otherwise False.
        rows_with_warning (pd.DataFrame): Data rows with validation warning.
    """
    num_words_outlier = flag_outliers(data, column_name="text_scraped")
    not_ascii_warnings = check_column_ascii(data, column_name="text_scraped")
    empty_string_warnings = check_column_empty_strings(data, column_name="text_scraped")
    not_string_warnings = check_column_is_string(data, column_name="text_scraped")
    null_warnings = check_column_not_null(data, column_name="text_scraped")
    link_warnings = check_links_within_column(data, column_name="text_scraped")
    warnings = [
        num_words_outlier,
        not_ascii_warnings,
        empty_string_warnings,
        not_string_warnings,
        null_warnings,
        link_warnings,
    ]
    rows_with_warning = pd.concat(warnings)

    _write_data(data, DATA_DIR, source)

    return len(rows_with_warning) == 0, rows_with_warning
