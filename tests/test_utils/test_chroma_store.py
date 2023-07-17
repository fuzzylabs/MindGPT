import pytest
from unittest.mock import patch
import chromadb

from utils.chroma_store import ChromaStore


@pytest.fixture
def mock_collection():
    pass


@pytest.fixture
def mock_chroma_client():
    pass


@pytest.mark.parametrize(
    "collection_name, is_valid",
    [
        ("areallylongnameforcollectionname" * 3, False),
        ("a..b", False),
        ("A_b", False),
        ("b_A", False),
        ("192.124.0.1", False),
        ("AbbA", False),
        ("a_valid-name", True),
    ],
)
def test_validate_collection_name(mock_chroma_client, collection_name, is_valid):
    chroma_client = ChromaStore()
    chroma_client._client = mock_chroma_client

    success, _ = chroma_client.validate_collection_name(collection_name)
    assert success == is_valid


# def test_get_or_create_collection(mock_chroma_client):
#     chroma_client = ChromaStore()
#     chroma_client._client = mock_chroma_client

#     collection_name = "test"
#     chroma_client.get_or_create_collection(collection_name)
#     assert collection_name in chroma_client.list_collection_names()
