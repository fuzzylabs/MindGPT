"""Postgres metric database utilities."""
import logging
import os
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

import psycopg2
from psycopg2 import Error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


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
            raise ValueError("No DB_NAME environment variable found.")
        if self.db_host is None:
            raise ValueError("No DB_HOST environment variable found.")
        if self.db_user is None:
            raise ValueError("No DB_USER environment variable found.")
        if self.db_password is None:
            raise ValueError("No DB_PASSWORD environment variable found.")
        if self.db_port is None:
            raise ValueError("No DB_PORT environment variable found.")

        # Check if any of the 5 environment variables set is empty
        if len(self.db_name) == 0:
            raise ValueError("DB_NAME is empty")
        if len(self.db_host) == 0:
            raise ValueError("DB_HOST is empty")
        if len(self.db_user) == 0:
            raise ValueError("DB_USER is empty")
        if len(self.db_password) == 0:
            raise ValueError("DB_PASSWORD is empty")
        if len(self.db_port) == 0:
            raise ValueError("DB_PORT is empty")


class SQLQueries:
    """Class containing queries for creating and checking relation existence."""

    @staticmethod
    def create_readability_relation_query() -> str:
        """SQL query for creating the readability relation with 3 columns, ID, TimeStamp and ReadabilityScore.

        Returns:
            str: SQL query for creating the readability relation
        """
        sql_query = """
            CREATE TABLE Readability (
                ID SERIAL PRIMARY KEY,
                TimeStamp TIMESTAMP,
                ReadabilityScore FLOAT(2)
            );
            """

        return sql_query

    @staticmethod
    def readability_relation_existence_query() -> str:
        """SQL query for checking whether the readability score relation exists or not.

        Returns:
            str: SQL query for checking the readability relation existence
        """
        sql_query = """
            SELECT EXISTS (
                SELECT FROM pg_tables
                WHERE  schemaname = 'public'
                AND    tablename  = 'readability'
            );
            """
        # This query would return a tuple such as (True,) if the relation exists, otherwise false

        return sql_query

    @staticmethod
    def insert_readability_data(score: float) -> str:
        """SQL query for inserting a row of data into the readability relation.

        Returns:
            str: SQL query for cinserting a row of data into the readability relation.
        """
        sql_query = f"""
            INSERT INTO readability (TimeStamp, ReadabilityScore)
            VALUES (NOW(), {score});
            """

        return sql_query

    @staticmethod
    def get_readability_data() -> str:
        """SQL query for getting data from the readability relation.

        Returns:
            str: SQL query for getting data from the readability relation.
        """
        sql_query = """
            SELECT * FROM readability
            """

        return sql_query


class DatabaseInterface:
    """Class containing methods for interacting with the postgres database."""

    def __init__(self) -> None:
        """Constructor which will initialise a database connection."""
        self.db_credentials = DatabaseCredentials()

        try:
            self.conn = psycopg2.connect(
                database=self.db_credentials.db_name,
                host=self.db_credentials.db_host,
                user=self.db_credentials.db_user,
                password=self.db_credentials.db_password,
                port=self.db_credentials.db_port,
            )
        except Error as e:
            logging.error(f"{e} error: Unable to connect to the data base")

        if not self.check_relation_existence():
            self.create_relation()

    def check_relation_existence(self) -> bool:
        """This function checks whether the readability relation exists.

        Returns:
            bool: returns True if exists, False otherwise
        """
        result: Optional[Any] = None

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(SQLQueries.readability_relation_existence_query())
                result = cursor.fetchone()
        except Error as e:
            logging.error(f"{e} error: Unable to check relation existence.")
            return False

        if result is None or len(result) == 0:
            return False

        return bool(result[0])

    def create_relation(self) -> None:
        """This function creates a relation."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(SQLQueries.create_readability_relation_query())
                self.conn.commit()
        except Error as e:
            logging.error(f"{e} error: Unable to create the readability relation.")

    def insert_data(self, score: float) -> None:
        """This function insert a row of data into to readability relation.

        Args:
            score (float): the readability score computed.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(SQLQueries.insert_readability_data(score))
                self.conn.commit()
        except Error as e:
            logging.error(
                f"{e} error: Unable to insert data into the readability relation."
            )

    def query_relation(self, relation: str) -> List[Tuple[Any, ...]]:
        """This function queries a specific relation in the database, based on the provided relation name.

        Args:
            relation (str): the name of the relation in database

        Returns:
            List[Tuple[Any, ...]]: a list of tuples representing the data rows from the queried relation.
        """
        result: List[Tuple[Any, ...]] = []

        if relation == "readability":
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute(SQLQueries.get_readability_data())
                    result = cursor.fetchall()
            except Error as e:
                logging.error(f"{e} error: Unable to query the {relation} relation.")

        return result
