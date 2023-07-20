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
    validation = store.validate_collection_name(collection_name)
    assert validation.is_valid == is_valid


def test_get_or_create_collection(local_persist_api: API):
    """Test creating multiple collections in chromadb using `_get_or_create_collection` function.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    embedding_function = lambda x: [[1, 2, 3] for _ in range(len(x))]

    store = ChromaStore()
    store._client = local_persist_api

    # Create collection "test"
    store._get_or_create_collection("test", embedding_function)
    assert store._collection.name == "test"

    # Create collection "test1"
    store._get_or_create_collection("test1", embedding_function)
    assert store._collection.name == "test1"

    assert {"test", "test1"} == set(store.list_collection_names())


def test_add_texts(local_persist_api: API):
    """Test adding documents to chromadb using `add_texts` function.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    embedding_function = lambda x: [[1, 2, 3] for _ in range(len(x))]
    uuids = [
        "bdd640fb-0667-4ad1-9c80-317fa3b1799d",
        "bdd740fb-0667-4ad1-9c80-317fa3b1799d",
    ]
    input_texts = ["a", "b"]
    expected_embeddings = [[1.0, 2.0, 3.0, 1.0, 2.0, 3.0]]

    store = ChromaStore()
    store._client = local_persist_api

    # Add example documents to the test collection
    store.add_texts(
        collection_name="test",
        texts=input_texts,
        embedding_function=embedding_function,
        ids=uuids,
    )
    data = store._collection.get(include=["embeddings", "documents"])

    assert data

    assert data["documents"] == input_texts

    assert data["embeddings"] == expected_embeddings


def test_list_collection_names(local_persist_api: API):
    """Test listing collection in chromadb using `list_collection_names` function.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    embedding_function = lambda x: [[1, 2, 3] for _ in range(len(x))]
    store = ChromaStore()
    store._client = local_persist_api

    # Add collections for testing
    store._get_or_create_collection("test", embedding_function)
    store._get_or_create_collection("test1", embedding_function)

    # Get list of all collections in chromadb
    assert {"test", "test1"} == set(store.list_collection_names())


def test_delete_collections(local_persist_api: API):
    """Test deleting a collection in chromadb using `delete_collection` function.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    embedding_function = lambda x: [[1, 2, 3] for _ in range(len(x))]
    store = ChromaStore()
    store._client = local_persist_api

    # Add collections for testing
    store._get_or_create_collection("test", embedding_function)
    store._get_or_create_collection("test1", embedding_function)

    # Delete collection "test"
    store.delete_collection("test")

    assert "test" not in store.list_collection_names()

    assert "test1" in store.list_collection_names()


def test_delete_collections_invalid_collection_name(local_persist_api: API):
    """Test deleting a collection using invalid collection name in chromadb using `delete_collection` function.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    store = ChromaStore()
    store._client = local_persist_api

    # Use invalid collection "dummy_test"
    with pytest.raises(ValueError):
        store.delete_collection("dummy_test")


def test_query_collection(local_persist_api: API):
    """Test querying collections in chromadb using `query_collection` function.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    embedding_function = lambda x: [[1, 2, 3] for _ in range(len(x))]
    uuids = [
        "bdd440fb-0667-4ad1-9c80-317fa3b1799d",
        "bdd540fb-0667-4ad1-9c80-317fa3b1799d",
    ]
    input_texts = ["foo", "dummy"]
    store = ChromaStore()
    store._client = local_persist_api

    # Add example documents to the test collection
    store.add_texts(
        collection_name="test",
        texts=input_texts,
        embedding_function=embedding_function,
        ids=uuids,
    )

    results = store.query_collection(
        collection_name="test",
        query_texts="dummy",
        n_results=1,
        embedding_function=embedding_function,
        where_document={"$contains": "foo"},
    )

    assert results
    assert len(results["documents"][0]) == 1
    assert len(results["ids"][0]) == 1
    assert results["documents"][0] == ["foo"]
    assert results["ids"][0] == ["bdd440fb-0667-4ad1-9c80-317fa3b1799d"]


def test_query_collection_raise_embedding_function_error(local_persist_api: API):
    """Test querying collections raise error when passed a different embedding function.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    embedding_function = lambda x: [[1, 2, 3] for _ in range(len(x))]
    dummy_embedding_function = lambda x: [[1, 2] for _ in range(len(x))]

    store = ChromaStore()
    store._client = local_persist_api

    # Use a different embedding function when querying
    with pytest.raises(ValueError):
        _ = store.query_collection(
            collection_name="test",
            query_texts="dummy",
            n_results=1,
            embedding_function=dummy_embedding_function,
        )
