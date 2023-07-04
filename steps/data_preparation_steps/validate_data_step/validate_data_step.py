"""Validate data step."""
import re

import pandas as pd
import requests
from zenml import step
from zenml.steps import Output


def validate_links(s: str) -> bool:
    """_summary_.

    Args:
        s (str): _description_

    Returns:
        bool: _description_
    """
    link_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    # Find all links in the string
    links = re.findall(link_pattern, s)

    # Check validity of each link
    for link in links:
        response = requests.head(link)
        if response.ok:
            return False

    return True


# def validate_empty_strings(dataframe: pd.DataFrame) -> bool:
#     """Validates if a Pandas DataFrame contains any empty strings.

#     Args:
#         dataframe (pandas.DataFrame): The input DataFrame.

#     Returns:
#         bool: True if no empty strings are found, False otherwise.
#     """
#     # Check if any value in the DataFrame is an empty string
#     has_empty_strings = (
#         dataframe.apply(lambda column: column.astype(str).str.strip().eq(""))
#         .any()
#         .any()
#     )

#     return not has_empty_strings


def check_column_not_null(dataframe: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Checks if all entries in a column of a Pandas DataFrame are not NaN or Null.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame.
        column_name (str): The name of the column to check.

    Returns:
        pandas.DataFrame: All rows that violate the current validation assertion.
    """
    df = dataframe.copy()
    df["is_notnull"] = df[column_name].notnull()
    df = df.drop(df[df["is_notnull"] is True].index)
    df["validation_warning"] = "Warning: row contains Null value."
    df = df.drop(["is_notnull"], axis=1)
    return df


def check_column_is_string(dataframe: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Checks if a column in a Pandas DataFrame contains only string values.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame.
        column_name (str): The name of the column to check.

    Returns:
        pandas.DataFrame: All rows that violate the current validation assertion.
    """
    df = dataframe.copy()
    df["is_str"] = df[column_name].apply(lambda x: isinstance(x, str))
    df = df.drop(df[df["is_str"] is True].index)
    df["validation_warning"] = "Warning: row is not a string data type."
    df = df.drop(["is_str"], axis=1)
    return df


def check_column_ascii(dataframe: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Checks if every entry in a column of a Pandas DataFrame is ASCII.

    Args:
        dataframe (pandas.DataFrame): The input DataFrame.
        column_name (str): The name of the column to check.

    Returns:
        pandas.DataFrame: All rows that violate the current validation assertion.
    """
    df = dataframe.copy()
    df["is_ascii"] = df[column_name].apply(lambda x: isinstance(x, str) and x.isascii())
    df = df.drop(df[df["is_ascii"] is True].index)
    df["validation_warning"] = "Warning: row contains non ASCII characters."
    df = df.drop(["is_ascii"], axis=1)
    return df


@step
def validate_data(
    data: pd.DataFrame,
) -> Output(is_valid=bool, rows_with_warning=pd.DataFrame):  # type: ignore
    """A step to validate text within the data DataFrame.

    Args:
        data (pd.DataFrame): Data to validate.

    Returns:
        is_valid (bool): True, if all rows pass data validation checks, otherwise False.
        rows_with_warning (pd.DataFrame): Data rows with validation warning.
    """
    rows_with_warning = check_column_ascii(data, column_name="text_scraped")
    rows_with_warning = pd.concat(
        [rows_with_warning, check_column_is_string(data, column_name="text_scraped")]
    )
    # print(validate_empty_strings(data))
    rows_with_warning = pd.concat(
        [rows_with_warning, check_column_not_null(data, column_name="text_scraped")]
    )
    print(data.apply(lambda s: validate_links(str(s))).all())

    return len(rows_with_warning) == 0, rows_with_warning
