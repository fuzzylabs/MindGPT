"""Postgres metric database utilities."""
import os
from dataclasses import dataclass

import psycopg2


@dataclass
class DatabaseCredentials:
    """Class for getting and validating env variables.

    Raises:
        ValueError: if any of the environment variables is not set or empty, then we can connect to the database
    """

    db_name = os.getenv("DB_NAME")
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT")

    def validate_env(self) -> None:
        """Checks whether the 5 environment variables required to connect to database is empty.

        Raises:
            ValueError: if any one of the 5 environment variables is empty or not set
        """
        # Check if the required environment variables are set
        if self.db_name is None:
            raise ValueError("No db_name environment variable found.")
        if self.db_host is None:
            raise ValueError("No db_host environment variable found.")
        if self.db_user is None:
            raise ValueError("No db_user environment variable found.")
        if self.db_password is None:
            raise ValueError("No db_password environment variable found.")
        if self.db_port is None:
            raise ValueError("No db_port environment variable found.")

        # Check if any of the 5 environment variables set is empty
        if len(self.db_name) == 0:
            raise ValueError("db_name is empty")
        if len(self.db_host) == 0:
            raise ValueError("db_host is empty")
        if len(self.db_user) == 0:
            raise ValueError("db_user is empty")
        if len(self.db_password) == 0:
            raise ValueError("db_password is empty")
        if len(self.db_port) == 0:
            raise ValueError("db_port is empty")


def getconn() -> psycopg2.extensions.connection:
    """Connect to Postgres database instance.

    Returns:
        psycopg2.extensions.connection: a connection established using 4 local variables and the “pg8000” driver
    """
    db_credentials = DatabaseCredentials()

    conn: psycopg2.extensions.connection = psycopg2.connect(
        database=db_credentials.db_name,
        host=db_credentials.db_host,
        user=db_credentials.db_user,
        password=db_credentials.db_password,
        port=db_credentials.db_port,
    )
    return conn
