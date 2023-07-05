"""Test validate data file."""
from unittest import mock

import pandas as pd
from steps.data_preparation_steps.validate_data_step.validate_data_step import (
    check_column_empty_strings,
    validate_data,
)


def test_validate_data_step():
    """Test validate data step returns True with valid data."""
    df = pd.DataFrame({"text_scraped": ["abcd", "https://www.bbc.co.uk/news", "42"]})
    with mock.patch(
        "steps.data_preparation_steps.validate_data_step.validate_data_step.requests.head"
    ) as mock_request:
        mock_request_code = mock.MagicMock()
        mock_request.return_value = mock_request_code
        mock_request_code.ok is True

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

    with mock.patch(
        "steps.data_preparation_steps.validate_data_step.validate_data_step.requests.head"
    ) as mock_request:
        mock_request_code = mock.MagicMock()
        mock_request.return_value = mock_request_code
        mock_request_code.ok is False

        is_valid, rows_with_warning = validate_data(df)

    assert not is_valid
    assert len(rows_with_warning) > 0
    assert "validation_warning" in rows_with_warning.columns
    assert "text_scraped" in rows_with_warning.columns


def test_check_column_empty_strings():
    """Test check column empty strings returns a DataFrame containing the invalid rows with warnings when the input contains invalid rows."""
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
