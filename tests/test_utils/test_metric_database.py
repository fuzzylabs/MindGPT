"""Test suite for testing metric database utility."""
import os
from contextlib import nullcontext as does_not_raise
from unittest import mock
from unittest.mock import patch

import pytest
from utils.metric_database import DatabaseCredentials, DatabaseInterface, SQLQueries

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
    ) as mock_environ:
        yield mock_environ


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


def test_insert_query_is_correct_for_readability_relation() -> None:
    """Test that the insert_readability_data query is built as expected."""
    expected_query = """
            INSERT INTO readability (time_stamp, readability_score, dataset)
            VALUES (NOW(), %(score)s, %(dataset)s);
        """.strip()

    generated_query = SQLQueries.insert_readability_data().strip()

    assert generated_query == expected_query


def test_insert_query_is_correct_for_embedding_drift_relation() -> None:
    """Test that the insert_embedding_drift_data query is built as expected."""
    expected_query = """
            INSERT INTO embedding_drift (time_stamp, reference_dataset, current_dataset, distance, drifted, dataset)
            VALUES (NOW(), %(reference_dataset)s, %(current_dataset)s, %(distance)s, %(drifted)s, %(dataset)s);
        """.strip()

    generated_query = SQLQueries.insert_embedding_drift_data().strip()

    assert generated_query == expected_query


def test_insert_query_is_correct_for_datasets_relation() -> None:
    """Test that the insert_datasets_data query is built as expected."""
    expected_query = """
            INSERT INTO datasets (name)
            VALUES (%(name)s);
        """.strip()

    generated_query = SQLQueries.insert_datasets_data().strip()

    assert generated_query == expected_query


def test_query_is_correct_for_relation_existence_query() -> None:
    """Test that the relation_existence_query is built as expected."""
    expected_query = """
            SELECT EXISTS (
                SELECT FROM pg_tables
                WHERE  schemaname = 'public'
                AND    tablename  = %(relation_name)s
            );
            """.strip()

    generated_query = SQLQueries.relation_existence_query().strip()

    assert generated_query == expected_query


def test_query_is_correct_get_data_from_relation_query() -> None:
    """Test that the get_data_from_relation query built as expected."""
    expected_query = """
            SELECT * FROM %(relation_name)s
            """.strip()

    generated_query = SQLQueries.get_data_from_relation().strip()

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

        db_interface.create_relation("datasets")
        mock_execute_query.assert_called_with(
            SQLQueries.create_datasets_relation_query()
        )

        db_interface.create_relation("readability")
        mock_execute_query.assert_called_with(
            SQLQueries.create_readability_relation_query()
        )

        db_interface.create_relation("embedding_drift")
        mock_execute_query.assert_called_with(
            SQLQueries.create_embedding_drift_relation_query()
        )

        db_interface.insert_datasets_data()
        mock_execute_query.assert_called_with(
            SQLQueries.insert_datasets_data(),
            {
                "name": "mind"  # This must be mind as it calls with nhs first and then mind.
            },
        )

        db_interface.insert_readability_data(1, "nhs")
        mock_execute_query.assert_called_with(
            SQLQueries.insert_readability_data(), {"score": 1, "dataset": "nhs"}
        )

        mock_embedding_drift_data = {
            "reference_dataset": "1.1",
            "current_dataset": "1.2",
            "distance": 0.1,
            "drifted": True,
            "dataset": "nhs",
        }
        db_interface.insert_embedding_drift_data(mock_embedding_drift_data)
        mock_execute_query.assert_called_with(
            SQLQueries.insert_embedding_drift_data(),
            mock_embedding_drift_data,
        )

        db_interface.query_relation("readability")
        mock_execute_query.assert_called_with(
            SQLQueries.get_data_from_relation(),
            {"relation_name": "readability"},
            fetch=True,
        )

        db_interface.query_relation("embedding_drift")
        mock_execute_query.assert_called_with(
            SQLQueries.get_data_from_relation(),
            {"relation_name": "embedding_drift"},
            fetch=True,
        )

        db_interface.query_relation("datasets")
        mock_execute_query.assert_called_with(
            SQLQueries.get_data_from_relation(),
            {"relation_name": "datasets"},
            fetch=True,
        )
