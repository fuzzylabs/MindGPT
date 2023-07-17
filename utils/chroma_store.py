"""ChromaDB vector store class."""
import ipaddress
import uuid
from typing import Iterable, List, Optional

import chromadb
from chromadb.api.types import CollectionMetadata, EmbeddingFunction
from chromadb.config import Settings

MIN_COLLECTION_NAME_LENGTH = 3
MAX_COLLECTION_NAME_LENGTH = 64


class ChromaStore:
    """ChromaStore class for ChromaDB vector store."""

    def __init__(
        self,
        chroma_server_hostname: str = "server.default",
        chroma_server_port: int = 8000,
    ) -> None:
        """_summary_.

        Args:
            chroma_server_hostname (str, optional): _description_. Defaults to "server.default".
            chroma_server_port (int, optional): _description_. Defaults to 8000.
        """
        self._client = chromadb.Client(
            Settings(
                chroma_api_impl="rest",
                chroma_server_host=chroma_server_hostname,
                chroma_server_http_port=chroma_server_port,
            )
        )
        self._collection = None

    def validate_collection_name(self, collection_name: str) -> tuple[bool, str]:
        """_summary_.

        Args:
            collection_name (str): _description_

        Returns:
            tuple[bool, str]: _description_
        """
        # The length of the name must be between 3 and 63 characters.
        if (
            len(collection_name) > MAX_COLLECTION_NAME_LENGTH
            or len(collection_name) < MIN_COLLECTION_NAME_LENGTH
        ):
            err_msg = f"The length of collection name in Chroma must be between 3 and 63 characters, got {len(collection_name)}"
            return False, err_msg

        # The name must start and end with a lowercase letter or a digit
        if not (
            (collection_name[0].islower() or collection_name[0].isdigit())
            and (collection_name[-1].islower() or collection_name[-1].isdigit())
        ):
            err_msg = f"The collection name must start and end with lowercase letter or a digit, got {collection_name}"
            return False, err_msg

        # The name must not contain two consecutive dots.
        if ".." in collection_name:
            err_msg = f"The collection name must not contain two consecutive dots, got {collection_name}"
            return False, err_msg

        # The name must not be a valid IP address
        try:
            ipaddress.ip_address(collection_name)
        except ValueError:
            pass
        else:
            err_msg = f"The collection name must not be a valid IP address, got {collection_name}"
            return False, err_msg

        return True, ""

    def get_or_create_collection(
        self,
        collection_name: str,
        embedding_function: Optional[EmbeddingFunction] = None,
        metadata: Optional[CollectionMetadata] = None,
    ):
        """_summary_.

        Args:
            collection_name (str): _description_
            embedding_function (Optional[EmbeddingFunction], optional): _description_. Defaults to None.
            metadata (Optional[CollectionMetadata], optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
        """
        is_valid, err_msg = self.validate_collection_name(collection_name)
        if not is_valid:
            raise ValueError(err_msg)
        #  If you supply an embedding function, you must supply it every time you get the collection.
        # By default, all-MiniLM-L6-v2 model is as embedding function
        self._collection = self._client.get_or_create_collection(
            collection_name,
            embedding_function=embedding_function,
            metadata=metadata,
        )

    def list_collection_names(self) -> List[str]:
        """_summary_.

        Returns:
            List[str]: _description_
        """
        collections = self._client.list_collections()
        if not collections:
            return []
        return [collection.name for collection in collections]

    def add_texts(
        self,
        collection_name: str,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
    ):
        """_summary_.

        Args:
            collection_name (str): _description_
            texts (Iterable[str]): _description_
            metadatas (Optional[List[dict]], optional): _description_. Defaults to None.
        """
        if self._collection is None:
            self.get_or_create_collection(collection_name)

        # A unique id for each document
        ids = [str(uuid.uuid1()) for _ in texts]
        # automatically tokenize and embed them with the collection's embedding function
        self._collection.upsert(documents=texts, ids=ids, metadatas=metadatas)

    def delete_collection(self, collection_name: str):
        """_summary_.

        Args:
            collection_name (str): _description_

        Raises:
            ValueError: _description_
        """
        if collection_name not in self.list_collection_names():
            raise ValueError(f"Collection name {collection_name} not found")
        self._client.delete_collection(self._collection.name)
