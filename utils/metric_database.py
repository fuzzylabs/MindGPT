"""Postgres metric database utilities."""
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from psycopg2 import Error, extensions, pool

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

    def __init__(self) -> None:
        """Constructor for DatabaseCredentials to get the required environment variables."""
        self.db_name = os.getenv("DB_NAME")
        self.db_host = os.getenv("DB_HOST")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_port = os.getenv("DB_PORT")

    def validate_env(self) -> None:
        """Checks whether the 5 environment variables required to connect to database is empty.

        Raises:
            ValueError: if any one of the 5 environment variables is empty or not set
        """
        for var, value in vars(self).items():
            if value is None or len(value) == 0:
                raise ValueError(f"{var.upper()} is not set")


class SQLQueries:
    """Class containing queries for creating and checking relation existence."""

    @staticmethod
    def create_readability_relation_query() -> str:
        """SQL query for creating the readability relation with 3 columns.

        Columns:
            - id (Primary Key)
            - time_stamp
            - readability_score
            - dataset (the dataset used for generating the response)

        Returns:
            str: SQL query for creating the readability relation
        """
        sql_query = """
            CREATE TABLE readability (
                id SERIAL PRIMARY KEY,
                time_stamp TIMESTAMP,
                readability_score FLOAT(2),
                dataset VARCHAR(50) REFERENCES datasets(name)
            );
            """

        return sql_query

    @staticmethod
    def insert_readability_data() -> str:
        """SQL query for inserting a row of data into the readability relation.

        Returns:
            str: SQL query for inserting a row of data into the readability relation.
        """
        sql_query = """
            INSERT INTO readability (time_stamp, readability_score, dataset)
            VALUES (NOW(), %(score)s, %(dataset)s);
            """

        return sql_query

    @staticmethod
    def create_embedding_drift_relation_query() -> str:
        """SQL query for creating the EmbeddingDrift relation with 6 columns.

        Columns:
            - id (Primary Key)
            - time_stamp
            - reference_dataset (Version Number)
            - current_dataset (Version Number)
            - distance
            - drifted (Bool) - Optional
            - dataset (Foreign Key referencing datasets.name)

        Returns:
            str: SQL query for creating the EmbeddingDrift relation
        """
        sql_query = """
            CREATE TABLE embedding_drift (
                id SERIAL PRIMARY KEY,
                time_stamp TIMESTAMP,
                reference_dataset VARCHAR(50),
                current_dataset VARCHAR(50),
                distance FLOAT(3),
                drifted BOOLEAN,
                dataset VARCHAR(50) REFERENCES datasets(name)
            );
            """

        return sql_query

    @staticmethod
    def insert_embedding_drift_data() -> str:
        """SQL query for inserting a row of data into the EmbeddingDrift relation.

        Returns:
            str: SQL query for inserting a row of data into the EmbeddingDrift relation.
        """
        sql_query = """
            INSERT INTO embedding_drift (time_stamp, reference_dataset, current_dataset, distance, drifted, dataset)
            VALUES (NOW(), %(reference_dataset)s, %(current_dataset)s, %(distance)s, %(drifted)s, %(dataset)s);
            """

        return sql_query

    @staticmethod
    def create_datasets_relation_query() -> str:
        """SQL query for creating the dataset relation with 2 columns, id and tag.

        Returns:
            str: SQL query for creating the datasets relation
        """
        sql_query = """
            CREATE TABLE datasets (
                name varchar(50) PRIMARY KEY
            );
            """

        return sql_query

    @staticmethod
    def insert_datasets_data() -> str:
        """SQL query for inserting a row of data into the datasets relation.

        Returns:
            str: SQL query for inserting a row of data into the datasets relation.
        """
        sql_query = """
            INSERT INTO datasets (name)
            VALUES (%(name)s);
            """

        return sql_query

    @staticmethod
    def relation_existence_query(relation_name: str) -> str:
        """SQL query for checking whether the relation specified exists or not.

        Args:
            relation_name (str): name of the relation to check for.

        Returns:
            str: SQL query for checking a relation existence
        """
        sql_query = f"""
            SELECT EXISTS (
                SELECT FROM pg_tables
                WHERE  schemaname = 'public'
                AND    tablename  = '{relation_name}'
            );
            """
        # This query would return a tuple such as (True,) if the relation exists, otherwise false

        return sql_query

    @staticmethod
    def get_data_from_relation(relation_name: str) -> str:
        """SQL query for getting data from the readability relation.

        Args:
            relation_name (str): name of the relation to get data from.

        Returns:
            str: SQL query for getting data from the readability relation.
        """
        sql_query = f"""
            SELECT * FROM "{relation_name}"
            """

        return sql_query


class DatabaseInterface:
    """Class containing methods for interacting with the postgres database."""

    relation_names = {
        "datasets",
        "readability",
        "embedding_drift",
    }  # The datasets relation must be created first as the other two relations reference to it.

    def __init__(self) -> None:
        """Constructor which will initialise a database connection."""
        self.db_credentials = DatabaseCredentials()
        self.db_credentials.validate_env()
        self.conn_pool = None
        self.connected = False

        while not self.connected:
            logging.info("Connecting to metric database")

            try:
                self.conn_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    database=self.db_credentials.db_name,
                    host=self.db_credentials.db_host,
                    user=self.db_credentials.db_user,
                    password=self.db_credentials.db_password,
                    port=self.db_credentials.db_port,
                )
                self.connected = True
                logging.info("Successfully connected to metric database")
            except Error as e:
                logging.error(
                    f"{e} error: Unable to connect to the data base, trying again in 5 seconds."
                )

                time.sleep(5)

        for name in self.relation_names:
            if not self.check_relation_existence(name) and name == "datasets":
                self.create_relation(name)
                self.insert_datasets_data()
            elif not self.check_relation_existence(name):
                self.create_relation(name)

    def get_conn(self) -> extensions.connection:
        """Retrieve a connection from the connection pool.

        Raises:
            Exception: raise if the connection pool is not initialised.

        Returns:
            extensions.connection: an instance of a connection to the database from the connection pool.
        """
        if not self.conn_pool:
            raise Exception("The connection pool is not initialised.")

        return cast(
            extensions.connection, self.conn_pool.getconn()
        )  # cast type for mypy

    def execute_query(
        self,
        query: str,
        query_parameters: Optional[Dict[str, Any]] = None,
        fetch: bool = False,
    ) -> Optional[List[Tuple[Any, ...]]]:
        """Executes a SQL query on the database.

        Args:
            query (str): the SQL query to be executed.
            query_parameters (Optional[Dict[str, Any]]): The parameters that the SQL query to execute should take. Defaults to None.
            fetch (bool): if set to True, the method will fetch and return the results of the query. Defaults to False.

        Returns:
            Optional[List[Tuple[Any, ...]]]: a list of tuples representing the query results if 'fetch' is True, None otherwise.
        """
        result = None

        try:
            conn = self.get_conn()

            with conn.cursor() as cursor:
                if query_parameters:
                    cursor.execute(query, query_parameters)
                else:
                    cursor.execute(query)
                if fetch:
                    result = cursor.fetchall()

            conn.commit()
        except Exception as e:
            logging.error(f"{e} error: Unable to execute the query.")
            # conn.rollback()  # roll back transaction on error
        finally:
            if self.conn_pool:
                self.conn_pool.putconn(conn)  # return connection back to pool

        return result

    def check_relation_existence(self, relation_name: str) -> bool:
        """This function checks whether the readability relation exists.

        Args:
            relation_name (str): name of the relation to check for.

        Returns:
            bool: returns True if exists, False otherwise
        """
        result = self.execute_query(
            SQLQueries.relation_existence_query(relation_name), fetch=True
        )
        if result:  # mypy
            return bool(result[0][0])

        return False

    def create_relation(self, relation_name: str) -> None:
        """This function creates a relation."""
        query_map = {
            "datasets": SQLQueries.create_datasets_relation_query(),
            "readability": SQLQueries.create_readability_relation_query(),
            "embedding_drift": SQLQueries.create_embedding_drift_relation_query(),
        }
        self.execute_query(str(query_map.get(relation_name)))

    def insert_readability_data(self, score: float, dataset: str) -> None:
        """This function insert a row of data into to readability relation.

        Args:
            score (float): the readability score computed.
            dataset (str): the dataset used to generate the response.
        """
        self.execute_query(
            SQLQueries.insert_readability_data(), {"score": score, "dataset": dataset}
        )

    def insert_embedding_drift_data(
        self, data: Dict[str, Union[str, float, bool]]
    ) -> None:
        """This function insert a row of data into to EmbeddingDrift relation.

        Args:
            data (Dict[str, Union[str, float, bool]]): a dictionary containing the embedding drift data to be inserted to the relation.
        """
        self.execute_query(
            SQLQueries.insert_embedding_drift_data(),
            {
                "reference_dataset": data["reference_dataset"],
                "current_dataset": data["current_dataset"],
                "distance": data["distance"],
                "drifted": data["drifted"],
                "dataset": data["dataset"],
            },
        )

    def insert_datasets_data(self) -> None:
        """This function insert two rows of data into the dataset relation which are the names of the dataset."""
        dataset_names = ["nhs", "mind"]

        for dataset_name in dataset_names:
            self.execute_query(
                SQLQueries.insert_datasets_data(), {"name": dataset_name}
            )

    def query_relation(self, relation_name: str) -> List[Tuple[Any, ...]]:
        """This function queries a specific relation in the database, based on the provided relation name.

        Args:
            relation_name (str): the name of the relation in database

        Returns:
            List[Tuple[Any, ...]]: a list of tuples representing the data rows from the queried relation.
        """
        result = self.execute_query(
            SQLQueries.get_data_from_relation(relation_name), fetch=True
        )

        return result  # type: ignore
