"""Test validate data file."""
from unittest import mock

import pandas as pd
from steps.data_preparation_steps.validate_data_step.validate_data_step import (
    check_column_ascii,
    check_column_empty_strings,
    check_column_is_string,
    check_column_not_null,
    check_links_within_column,
    flag_outliers,
    validate_data,
)

REQUESTS_FUNCTION_TARGET = (
    "steps.data_preparation_steps.validate_data_step.validate_data_step.requests.head"
)


def test_validate_data_step():
    """Test validate data step returns True with valid data."""
    df = pd.DataFrame({"text_scraped": ["abcd", "https://www.bbc.co.uk/news", "42"]})
    with mock.patch(REQUESTS_FUNCTION_TARGET) as mock_request:
        mock_request_code = mock.MagicMock()
        mock_request.return_value = mock_request_code
        mock_request_code.ok = True

        is_valid, rows_with_warning = validate_data(df)

    assert is_valid
    assert rows_with_warning.empty


def test_validate_data_step_with_invalid_data():
    """Test validate data steps returns False with invalid data."""
    df = pd.DataFrame(
        {
            "text_scraped": [
                "abcd",
                42,
                "https://www.notarealwebsite.com/news",
                None,
                "",
            ]
        }
    )

    with mock.patch(REQUESTS_FUNCTION_TARGET) as mock_request:
        mock_request_code = mock.MagicMock()
        mock_request.return_value = mock_request_code
        mock_request_code.ok = False

        is_valid, rows_with_warning = validate_data(df)

    assert not is_valid
    assert len(rows_with_warning) > 0
    assert "validation_warning" in rows_with_warning.columns
    assert "text_scraped" in rows_with_warning.columns


def test_check_column_empty_strings():
    """Test check column empty strings returns a DataFrame containing the invalid rows with warnings when the input contains invalid rows with empty strings."""
    df = pd.DataFrame(
        {
            "text_scraped": [
                "abcd",
                "",
            ]
        }
    )
    expected_output = pd.DataFrame(
        {
            "text_scraped": [""],
            "validation_warning": [
                "Warning: row contains an empty string in column 'text_scraped'."
            ],
        },
        index=[1],
    )

    empty_string_warnings = check_column_empty_strings(df, "text_scraped")

    assert len(empty_string_warnings) > 0
    pd.testing.assert_frame_equal(expected_output, empty_string_warnings)


def test_check_column_ascii():
    """Test check column ASCII returns a DataFrame containing the invalid rows with warnings when the input contains invalid rows with non ASCII characters."""
    df = pd.DataFrame(
        {
            "text_scraped": [
                "abcd",
                "四十二",
            ]
        }
    )
    expected_output = pd.DataFrame(
        {
            "text_scraped": ["四十二"],
            "validation_warning": ["Warning: row contains non ASCII characters."],
        },
        index=[1],
    )

    empty_string_warnings = check_column_ascii(df, "text_scraped")

    assert len(empty_string_warnings) > 0
    pd.testing.assert_frame_equal(expected_output, empty_string_warnings)


def test_flag_outliers():
    """Test flag outliers returns a DataFrame containing the invalid rows with warnings when the input contains invalid rows with anomalous numbers of words."""
    df = pd.DataFrame(
        {
            "text_scraped": [
                "word1",
                "word2",
                "word3",
                "word4",
                "word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5",
                "word6",
                "word7",
                "",
                "",
                "",
                "",
                "",
            ]
        }
    )
    expected_output = pd.DataFrame(
        {
            "text_scraped": [
                "word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5 word5"
            ],
            "validation_warning": [
                "Warning: the number of words '24' in this row has been flagged as an outlier."
            ],
        },
        index=[4],
    )

    empty_string_warnings = flag_outliers(df, "text_scraped")

    assert len(empty_string_warnings) > 0
    pd.testing.assert_frame_equal(expected_output, empty_string_warnings)


def test_check_column_is_string():
    """Test check column is string returns a DataFrame containing the invalid rows with warnings when the input contains invalid rows with non string values."""
    df = pd.DataFrame(
        {
            "text_scraped": [
                "abcd",
                set("a"),
            ]
        }
    )
    expected_output = pd.DataFrame(
        {
            "text_scraped": [set("a")],
            "validation_warning": ["Warning: row is not a string data type."],
        },
        index=[1],
    )

    not_string_warnings = check_column_is_string(df, "text_scraped")

    assert len(not_string_warnings) > 0
    pd.testing.assert_frame_equal(expected_output, not_string_warnings)


def test_check_column_not_null():
    """Test check column not null returns a DataFrame containing the invalid rows with warnings when the input contains invalid rows with None/Null values."""
    df = pd.DataFrame(
        {
            "text_scraped": [
                "abcd",
                None,
            ]
        }
    )
    expected_output = pd.DataFrame(
        {
            "text_scraped": [None],
            "validation_warning": ["Warning: row contains Null value."],
        },
        index=[1],
    )

    null_warnings = check_column_not_null(df, "text_scraped")

    assert len(null_warnings) > 0
    pd.testing.assert_frame_equal(expected_output, null_warnings)


def test_check_links_within_column():
    """Test check links within column returns a DataFrame containing the invalid rows with warnings when the input contains rows that contain invalid URL links."""
    df = pd.DataFrame(
        {
            "text_scraped": [
                "abcd",
                "https://www.notarealwebsite.com/news",
            ]
        }
    )
    expected_output = pd.DataFrame(
        {
            "text_scraped": ["https://www.notarealwebsite.com/news"],
            "validation_warning": ["Warning: row contains invalid links."],
        },
        index=[1],
    )

    with mock.patch(REQUESTS_FUNCTION_TARGET) as mock_request:
        mock_request_code = mock.MagicMock()
        mock_request.return_value = mock_request_code
        mock_request_code.ok = False

        link_warnings = check_links_within_column(df, "text_scraped")

    assert len(link_warnings) > 0
    pd.testing.assert_frame_equal(expected_output, link_warnings)
