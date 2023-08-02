"""Test suite for testing metric database utility."""
import os
from contextlib import nullcontext as does_not_raise
from typing import Dict, Union
from unittest import mock
from unittest.mock import patch

import pytest
from utils import DatabaseCredentials, DatabaseInterface, SQLQueries

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(autouse=True)
def mock_database_env() -> None:
    """A fixture for setting the environment variables required for a database connection."""
    with mock.patch.dict(
        os.environ,
        {
            "DB_NAME": "mock_name",
            "DB_HOST": "mock_host",
            "DB_USER": "mock_user",
            "DB_PORT": "mock_port",
            "DB_PASSWORD": "mock_password",
        },
    ):
        yield


def test_validate_env() -> None:
    """Test the `validate_env` method in `DatabaseCredentials` class for correct behaviours.

    The function tests three cases:
        1. Validates that the method doesn't raise an error when environment variables are set correctly.
        2. Ensures that the method raises a `ValueError` when all environment variables are cleared (No ENV).
        3. Verifies that the method raises a `ValueError` when a environment variable empty string.
    """
    # Case 1
    with does_not_raise():
        database_credentials = DatabaseCredentials()
        database_credentials.validate_env()

    # Case 2
    with pytest.raises(ValueError):
        os.environ.clear()
        database_credentials = DatabaseCredentials()
        database_credentials.validate_env()

    # Case 3
    with pytest.raises(ValueError):
        database_credentials = DatabaseCredentials()
        database_credentials.db_name = ""
        database_credentials.validate_env()


def test_query_is_correct_with_readability_data() -> None:
    """Test that the insert_readability_data query is built as expected based on the argument passed."""
    mock_score: float = 88

    expected_query = """
            INSERT INTO "Readability" ("TimeStamp", "ReadabilityScore")
            VALUES (NOW(), 88);
        """.strip()

    generated_query = SQLQueries.insert_readability_data(mock_score).strip()

    assert generated_query == expected_query


def test_query_is_correct_with_embedding_data_dict() -> None:
    """Test that the insert_embedding_drift_data query is built as expected based on the argument passed."""
    mock_data_dict: Dict[str, Union[str, float, bool]] = {
        "ReferenceDataset": "1.1",
        "CurrentDataset": "1.2",
        "Distance": 0.1,
        "Drifted": True,
    }

    expected_query = """
            INSERT INTO "EmbeddingDrift" ("TimeStamp", "ReferenceDataset", "CurrentDataset", "Distance", "Drifted")
            VALUES (NOW(), 1.1, 1.2, 0.1, True);
        """.strip()

    generated_query = SQLQueries.insert_embedding_drift_data(mock_data_dict).strip()

    assert generated_query == expected_query


def test_query_is_correct_with_relation_name() -> None:
    """Test that the relation_existence_query is built as expected based on the argument passed."""
    mock_relation_name: str = "mock_name"

    expected_query = """
            SELECT EXISTS (
                SELECT FROM pg_tables
                WHERE  schemaname = 'public'
                AND    tablename  = 'mock_name'
            );
            """.strip()

    generated_query = SQLQueries.relation_existence_query(mock_relation_name).strip()

    assert generated_query == expected_query


def test_database_interface():
    """Test that methods in the database interface are called with the expected queries."""
    with patch("psycopg2.pool.SimpleConnectionPool", return_value=None), patch.object(
        DatabaseInterface, "check_relation_existence", return_value=True
    ) as mock_check_relation_existence, patch.object(
        DatabaseInterface, "execute_query", return_value=None
    ) as mock_execute_query:
        db_interface = DatabaseInterface()

        mock_check_relation_existence.assert_called()

        db_interface.create_relation("Readability")
        mock_execute_query.assert_called_with(
            SQLQueries.create_readability_relation_query()
        )

        db_interface.create_relation("EmbeddingDrift")
        mock_execute_query.assert_called_with(
            SQLQueries.create_embedding_drift_relation_query()
        )

        db_interface.insert_readability_data(1)
        mock_execute_query.assert_called_with(SQLQueries.insert_readability_data(1))

        mock_embedding_drift_data = {
            "ReferenceDataset": "1.1",
            "CurrentDataset": "1.2",
            "Distance": 0.1,
            "Drifted": True,
        }
        db_interface.insert_embedding_drift_data(mock_embedding_drift_data)
        mock_execute_query.assert_called_with(
            SQLQueries.insert_embedding_drift_data(mock_embedding_drift_data)
        )

        db_interface.query_relation("Readability")
        mock_execute_query.assert_called_with(
            SQLQueries.get_data_from_relation("Readability"), fetch=True
        )

        db_interface.query_relation("EmbeddingDrift")
        mock_execute_query.assert_called_with(
            SQLQueries.get_data_from_relation("EmbeddingDrift"), fetch=True
        )
