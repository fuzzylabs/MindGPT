"""Test suite for testing embed_data step."""
import tempfile

import chromadb
import pandas as pd
import pytest
from chromadb.api import API
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings


@pytest.fixture
def dummy_dataframe() -> pd.DataFrame:
    """Fixture to create a dummy dataframe.

    Returns:
        pd.DataFrame: Dummy dataframe
    """
    return []


@pytest.fixture
def local_persist_api() -> API:
    """Fixture to create a local chroma server for testing.

    Returns:
        API: Local chroma server
    """
    return chromadb.Client(
        Settings(
            chroma_api_impl="local",
            chroma_db_impl="duckdb+parquet",
            persist_directory=tempfile.gettempdir() + "/test_server",
        )
    )


class FakeEmbeddingFunction(EmbeddingFunction):
    """Fake embedding class for testing."""

    def __call__(self, texts: Documents) -> Embeddings:
        """Calls the fake embedding function.

        Args:
            texts (Documents): Documents to embed

        Returns:
            Embeddings: Return fixed embedding
        """
        return [[float(1.0)] * 9 + [float(i)] for i in range(len(texts))]


# def test_embed_data_step(local_persist_api: API, dummy_dataframe: pd.DataFrame):
#     """_summary_

#     Args:
#         local_persist_api (API): _description_
#         dummy_dataframe (pd.DataFrame):
#     """

#     embed_data.entrypoint()
