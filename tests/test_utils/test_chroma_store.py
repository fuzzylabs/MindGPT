"""Test suite for testing chroma_store utility."""
import tempfile

import chromadb
import pytest
from chromadb.api import API
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings
from utils.chroma_store import ChromaStore


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


@pytest.mark.parametrize(
    "collection_name, is_valid",
    [
        ("areallylongnameforcollectionname" * 3, False),
        ("a..b", False),
        ("Test_b", False),
        ("ba_tesT", False),
        ("192.124.0.1", False),
        ("AbbA", False),
        ("a_valid-name", True),
    ],
)
def test_validate_collection_name(collection_name: str, is_valid: bool):
    """Test if collection names are valid.

    Args:
        collection_name (str): Name of collection
        is_valid (bool): Whether the input collection name is valid
    """
    store = ChromaStore()
    store._client = local_persist_api
    success, _ = store.validate_collection_name(collection_name)
    assert success == is_valid


def test_get_or_create_collection(local_persist_api: API):
    """Test creating multiple collections in chromadb using `_get_or_create_collection` function.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    store = ChromaStore()
    store._client = local_persist_api

    # Create collection "test"
    store._get_or_create_collection("test", FakeEmbeddingFunction())
    assert store._collection.name == "test"
    assert "test" in store.list_collection_names()

    # Create collection "test1"
    store._get_or_create_collection("test1", FakeEmbeddingFunction())
    assert store._collection.name == "test1"
    assert "test1" in store.list_collection_names()


def test_add_texts(local_persist_api: API):
    """Test adding documents to chromadb using `add_texts` function.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    input_texts = ["a", "b"]
    expected_embeddings = [
        [float(1.0)] * 9 + [float(i)] for i in range(len(input_texts))
    ]

    store = ChromaStore()
    store._client = local_persist_api

    # Add example documents to the test collection
    store.add_texts(
        collection_name="test",
        texts=input_texts,
        embedding_function=FakeEmbeddingFunction(),
    )
    data = store._collection.get(include=["embeddings", "documents"])

    assert data["documents"] == input_texts

    assert data["embeddings"] == expected_embeddings


def test_llist_collection_names(local_persist_api: API):
    """Test listing collection in chromadb using `list_collection_names` function.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    store = ChromaStore()
    store._client = local_persist_api

    # Get list of all collections in chromadb
    assert sorted(["test", "test1"]) == sorted(store.list_collection_names())


def test_delete_collections(local_persist_api: API):
    """Test deleting a collection in chromadb using `delete_collection` function.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    store = ChromaStore()
    store._client = local_persist_api

    # Delete collection "test"
    store.delete_collection("test")

    assert "test" not in store.list_collection_names()

    assert "test1" in store.list_collection_names()