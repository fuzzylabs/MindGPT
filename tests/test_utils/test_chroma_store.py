"""Test suite for testing chroma_store utility."""
import tempfile

import chromadb
import pytest
from chromadb.api import API
from chromadb.api.models.Collection import Collection
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
            chroma_api_impl="chromadb.api.segment.SegmentAPI",
            chroma_sysdb_impl="chromadb.db.impl.sqlite.SqliteDB",
            chroma_producer_impl="chromadb.db.impl.sqlite.SqliteDB",
            chroma_consumer_impl="chromadb.db.impl.sqlite.SqliteDB",
            chroma_segment_manager_impl="chromadb.segment.impl.manager.local.LocalSegmentManager",
            allow_reset=True,
            is_persistent=True,
            persist_directory=tempfile.gettempdir(),
        ),
    )


class MockEmbeddingFunction(EmbeddingFunction):
    """Mock embedding class for testing."""

    def __call__(self, texts: Documents) -> Embeddings:
        """Calls the mock embedding function.

        Args:
            texts (Documents): Documents to embed

        Returns:
            Embeddings: Return fixed embedding
        """
        return [[float(1.0)] * 2 + [float(i)] for i in range(len(texts))]


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
    store = ChromaStore()
    store._client = local_persist_api

    # Create collection "test"
    collection = store._get_or_create_collection("test", MockEmbeddingFunction())
    assert isinstance(collection, Collection)
    assert collection.name == "test"

    # Create collection "test1"
    collection = store._get_or_create_collection("test1", MockEmbeddingFunction())
    assert isinstance(collection, Collection)
    assert collection.name == "test1"

    assert {"test", "test1"} == set(store.list_collection_names())


def test_add_texts(local_persist_api: API):
    """Test adding documents to chromadb using `add_texts` function.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    uuids = [
        "bdd640fb-0667-4ad1-9c80-317fa3b1799d",
        "bdd740fb-0667-4ad1-9c80-317fa3b1799d",
    ]
    input_texts = ["a", "b"]
    expected_embeddings = [
        [float(1.0)] * 2 + [float(i)] for i in range(len(input_texts))
    ]

    store = ChromaStore()
    store._client = local_persist_api

    # Add example documents to the test collection
    store.add_texts(
        collection_name="test",
        texts=input_texts,
        embedding_function=MockEmbeddingFunction(),
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
    store = ChromaStore()
    store._client = local_persist_api

    # Add collections for testing
    store._get_or_create_collection("test", MockEmbeddingFunction())
    store._get_or_create_collection("test1", MockEmbeddingFunction())

    # Get list of all collections in chromadb
    assert {"test", "test1"} == set(store.list_collection_names())


def test_delete_collections(local_persist_api: API):
    """Test deleting a collection in chromadb using `delete_collection` function.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    store = ChromaStore()
    store._client = local_persist_api

    # Add collections for testing
    store._get_or_create_collection("test", MockEmbeddingFunction())
    store._get_or_create_collection("test1", MockEmbeddingFunction())

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
        embedding_function=MockEmbeddingFunction(),
        ids=uuids,
    )

    results = store.query_collection(
        collection_name="test",
        query_texts="dummy",
        n_results=1,
        embedding_function=MockEmbeddingFunction(),
        where_document={"$contains": "foo"},
    )

    assert results
    assert len(results["documents"][0]) == 1
    assert len(results["ids"][0]) == 1
    assert results["documents"][0] == ["foo"]
    assert results["ids"][0] == ["bdd440fb-0667-4ad1-9c80-317fa3b1799d"]


def test_fetch_reference_and_current_embeddings(local_persist_api: API):
    """Test that the fetch_reference_and_current_embeddings returns the expected embeddings.

    Args:
        local_persist_api (API): Local chroma server for testing
    """
    uuids = [
        "bdd440fb-0667-4ad1-9c80-317fa3b1799d",
        "bdd540fb-0667-4ad1-9c80-317fa3b1799d",
        "bdd640fb-0667-4ad1-9c80-317fa3b1799d",
    ]
    input_texts = ["foo", "dummy", "I like apples"]
    store = ChromaStore()
    store._client = local_persist_api

    metadatas = [
        {"data_version": "test_version"},
        {"data_version": "test_version"},
        {"data_version": "test_version"},
    ]

    # Add example documents to the test collection
    store.add_texts(
        collection_name="test_new",
        texts=input_texts,
        embedding_function=MockEmbeddingFunction(),
        ids=uuids,
        metadatas=metadatas,
    )

    (
        reference_embeddings,
        current_embeddings,
    ) = store.fetch_reference_and_current_embeddings(
        collection_name="test_new",
        reference_data_version="test_version",
        current_data_version="test_version",
    )

    assert isinstance(reference_embeddings, list)
    assert isinstance(current_embeddings, list)
    assert len(reference_embeddings) == 3
    assert len(current_embeddings) == 3
    assert all(len(item) == 3 for item in reference_embeddings)
    assert all(len(item) == 3 for item in current_embeddings)
