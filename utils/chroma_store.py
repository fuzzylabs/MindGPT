"""ChromaDB vector store class."""
import ipaddress
import uuid
from dataclasses import dataclass
from typing import List, Optional

import chromadb
from chromadb.api.types import CollectionMetadata, EmbeddingFunction
from chromadb.config import Settings

MIN_COLLECTION_NAME_LENGTH = 3
MAX_COLLECTION_NAME_LENGTH = 64


@dataclass
class ValidateCollectionName:
    """Dataclass for validating class name."""

    is_valid: bool
    err_msg: str


class ChromaStore:
    """ChromaStore class for ChromaDB vector store."""

    def __init__(
        self,
        chroma_server_hostname: str = "server.default",
        chroma_server_port: int = 8000,
    ) -> None:
        """Initialize chroma client by connecting it to chroma server.

        Args:
            chroma_server_hostname (str, optional): Hostname for chroma server. Defaults to "server.default".
            chroma_server_port (int, optional): Port for chroma server. Defaults to 8000.
        """
        self._client = chromadb.Client(
            Settings(
                chroma_api_impl="rest",
                chroma_server_host=chroma_server_hostname,
                chroma_server_http_port=chroma_server_port,
            )
        )
        self._collection = None

    def validate_collection_name(self, collection_name: str) -> ValidateCollectionName:
        """Validate collection name to be used in chromadb.

        Args:
            collection_name (str): Name of collection

        Returns:
            ValidateCollectionName: Dataclass containing validation message and boolean for collection name
        """
        # The length of the name must be between 3 and 63 characters.
        if (
            len(collection_name) > MAX_COLLECTION_NAME_LENGTH
            or len(collection_name) < MIN_COLLECTION_NAME_LENGTH
        ):
            err_msg = f"The length of collection name in Chroma must be between 3 and 63 characters, got {len(collection_name)}"
            return ValidateCollectionName(is_valid=False, err_msg=err_msg)

        # The name must start and end with a lowercase letter or a digit
        if not (
            (collection_name[0].islower() or collection_name[0].isdigit())
            and (collection_name[-1].islower() or collection_name[-1].isdigit())
        ):
            err_msg = f"The collection name must start and end with lowercase letter or a digit, got {collection_name}"
            return ValidateCollectionName(is_valid=False, err_msg=err_msg)

        # The name must not contain two consecutive dots.
        if ".." in collection_name:
            err_msg = f"The collection name must not contain two consecutive dots, got {collection_name}"
            return ValidateCollectionName(is_valid=False, err_msg=err_msg)

        # The name must not be a valid IP address
        try:
            ipaddress.ip_address(collection_name)
        except ValueError:
            pass
        else:
            err_msg = f"The collection name must not be a valid IP address, got {collection_name}"
            return ValidateCollectionName(is_valid=False, err_msg=err_msg)

        return ValidateCollectionName(is_valid=True, err_msg="")

    def _get_or_create_collection(
        self,
        collection_name: str,
        embedding_function: Optional[EmbeddingFunction] = None,
        metadata: Optional[CollectionMetadata] = None,
    ) -> None:
        """Function to create or get a collection.

        Args:
            collection_name (str): Name of collection
            embedding_function (Optional[EmbeddingFunction], optional): Embedding function to use. Defaults to None.
            metadata (Optional[CollectionMetadata], optional): Additional metadata for collection. Defaults to None.

        Raises:
            ValueError: If `collection_name` is invalid
        """
        validation = self.validate_collection_name(collection_name)
        if not validation.is_valid:
            raise ValueError(validation.err_msg)

        # If you supply an embedding function, you must supply it every time you get the collection.
        # By default, all-MiniLM-L6-v2 model is as embedding function
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            metadata=metadata,
        )

    def list_collection_names(self) -> List[str]:
        """List all the collection names in chromadb.

        Returns:
            List[str]: List containing names of collections
        """
        collections = self._client.list_collections()
        if not collections:
            return []
        return [collection.name for collection in collections]

    def add_texts(
        self,
        collection_name: str,
        texts: List[str],
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[dict]] = None,
        embedding_function: Optional[EmbeddingFunction] = None,
    ) -> None:
        """Add documents to collection.

        Args:
            collection_name (str): Name of collection to use for adding documents
            texts (List[str]): List of textd to be added to the collection
            ids (Optional[List[str]], optional): Optional list of IDs for documents.
            metadatas (Optional[List[dict]], optional): Optional list of metadatas for documents. Defaults to None.
            embedding_function (Optional[EmbeddingFunction], optional): Embedding function to be used by collection. Defaults to None.
        """
        if self._collection is None:
            self._get_or_create_collection(collection_name, embedding_function)

        # A unique id for each document
        if ids is None:
            ids = [str(uuid.uuid1()) for _ in texts]

        # Automatically tokenize and embed them with the collection's embedding function
        self._collection.upsert(documents=texts, ids=ids, metadatas=metadatas)

    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection from chroma database.

        Args:
            collection_name (str): Name of collection

        Raises:
            ValueError: if collection_name is not present in chroma server
        """
        if collection_name not in self.list_collection_names():
            raise ValueError(f"Collection name {collection_name} not found")
        self._client.delete_collection(collection_name)
