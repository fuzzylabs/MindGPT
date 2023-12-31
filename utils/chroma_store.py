"""ChromaDB vector store class."""
import ipaddress
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.api.types import (
    CollectionMetadata,
    EmbeddingFunction,
    Metadata,
    OneOrMany,
    QueryResult,
    Where,
)
from chromadb.errors import InvalidDimensionException

MIN_COLLECTION_NAME_LENGTH = 3
MAX_COLLECTION_NAME_LENGTH = 64
DEFAULT_N_RESULTS = 5


@dataclass
class CollectionNameValidationOutcome:
    """Dataclass for validating class name."""

    is_valid: bool
    err_msg: str


class ChromaStore:
    """ChromaStore class for ChromaDB vector store."""

    def __init__(
        self,
        chroma_server_hostname: str = "chroma-service.default",
        chroma_server_port: str = "8000",
    ) -> None:
        """Initialise chroma client by connecting it to chroma server.

        Args:
            chroma_server_hostname (str, optional): Hostname for chroma server. Defaults to "chroma-service.default".
            chroma_server_port (str, optional): Port for chroma server. Defaults to 8000.
        """
        self._client = chromadb.HttpClient(
            host=chroma_server_hostname, port=chroma_server_port
        )
        self._collection: Optional[Collection] = None

    def validate_collection_name(
        self, collection_name: str
    ) -> CollectionNameValidationOutcome:
        """Validate collection name to be used in ChromaDB.

        Args:
            collection_name (str): Name of collection

        Returns:
            CollectionNameValidationOutcome: Dataclass containing validation message and boolean for collection name
        """
        # The length of the name must be between 3 and 63 characters.
        if (
            len(collection_name) > MAX_COLLECTION_NAME_LENGTH
            or len(collection_name) < MIN_COLLECTION_NAME_LENGTH
        ):
            err_msg = f"The length of collection name in Chroma must be between 3 and 63 characters, got {len(collection_name)}"
            return CollectionNameValidationOutcome(is_valid=False, err_msg=err_msg)

        # The name must start and end with a lowercase letter or a digit
        if not (
            (collection_name[0].islower() or collection_name[0].isdigit())
            and (collection_name[-1].islower() or collection_name[-1].isdigit())
        ):
            err_msg = f"The collection name must start and end with lowercase letter or a digit, got {collection_name}"
            return CollectionNameValidationOutcome(is_valid=False, err_msg=err_msg)

        # The name must not contain two consecutive dots.
        if ".." in collection_name:
            err_msg = f"The collection name must not contain two consecutive dots, got {collection_name}"
            return CollectionNameValidationOutcome(is_valid=False, err_msg=err_msg)

        # The name must not be a valid IP address
        try:
            ipaddress.ip_address(collection_name)
        except ValueError:
            pass
        else:
            err_msg = f"The collection name must not be a valid IP address, got {collection_name}"
            return CollectionNameValidationOutcome(is_valid=False, err_msg=err_msg)

        return CollectionNameValidationOutcome(is_valid=True, err_msg="")

    def _get_or_create_collection(
        self,
        collection_name: str,
        embedding_function: Optional[EmbeddingFunction] = None,
        metadata: Optional[CollectionMetadata] = None,
    ) -> Collection:
        """Function to create or get a collection.

        Args:
            collection_name (str): Name of collection
            embedding_function (Optional[EmbeddingFunction], optional): Embedding function to use. Defaults to None.
            metadata (Optional[CollectionMetadata], optional): Additional metadata for collection. Defaults to None.

        Returns:
            Collection: a collection retrieved or created

        Raises:
            ValueError: If `collection_name` is invalid
        """
        validation = self.validate_collection_name(collection_name)
        if not validation.is_valid:
            raise ValueError(validation.err_msg)

        # If you supply an embedding function, you must supply it every time you get the collection.
        # By default, all-MiniLM-L6-v2 model is as embedding function
        return self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            metadata=metadata,
        )

    def list_collection_names(self) -> List[str]:
        """List all the collection names in ChromaDB.

        Returns:
            List[str]: List containing names of collections
        """
        collections = self._client.list_collections()
        if not collections:
            return []
        return [collection.name for collection in collections]

    def query_collection(
        self,
        collection_name: str,
        query_texts: Optional[List[str]] = None,
        n_results: int = DEFAULT_N_RESULTS,
        where: Optional[Where] = None,
        embedding_function: Optional[EmbeddingFunction] = None,
        **kwargs: Any,
    ) -> QueryResult:
        """Query the collection to return closest documents matching query.

        Args:
            collection_name (str): Name of the collection
            query_texts (Optional[List[str]], optional): List of query texts. Defaults to None.
            n_results (int, optional): Number of closest matches to return. Defaults to DEFAULT_N_RESULTS.
            where (Optional[Where], optional): Additional filtering using where. Defaults to None.
            embedding_function (Optional[EmbeddingFunction], optional):  Embedding function to use. Defaults to None.
            **kwargs (Dict): Additional keyword arguments

        Returns:
            QueryResult: a QueryResult object containing the results.

        Raises:
            InvalidDimensionException: If the dimension of the embedding function does not match the dimension of the collection
        """
        self._collection = self._get_or_create_collection(
            collection_name, embedding_function
        )

        # Chroma will embed each query_text with the collection's embedding function
        # and then query using generated embeddings
        try:
            return self._collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                **kwargs,
            )
        except InvalidDimensionException:
            raise ValueError(
                "Invalid dimension. Please check if the embedding function matches to the collection's embedding function"
            )

    def add_texts(
        self,
        collection_name: str,
        texts: List[str],
        ids: List[str],
        metadatas: Optional[OneOrMany[Metadata]] = None,
        embedding_function: Optional[EmbeddingFunction] = None,
    ) -> None:
        """Add documents to collection.

        Args:
            collection_name (str): Name of collection to use for adding documents
            texts (List[str]): List of texts to be added to the collection
            ids (List[str]): List of IDs for texts.
            metadatas (Optional[OneOrMany[Metadata]], optional): Optional list of metadatas for documents. Defaults to None.
            embedding_function (Optional[EmbeddingFunction], optional): Embedding function to be used by collection. Defaults to None.
        """
        self._collection = self._get_or_create_collection(
            collection_name, embedding_function
        )

        # Automatically tokenize and embed them with the collection's embedding function
        self._collection.upsert(documents=texts, ids=ids, metadatas=metadatas)

    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection from Chroma database.

        Args:
            collection_name (str): Name of collection

        Raises:
            ValueError: if collection_name is not present in Chroma server
        """
        if collection_name not in self.list_collection_names():
            raise ValueError(f"Collection name {collection_name} not found")
        self._client.delete_collection(collection_name)

    def fetch_reference_and_current_embeddings(
        self,
        collection_name: str,
        reference_data_version: str,
        current_data_version: str,
    ) -> Tuple[List[List[float]], List[List[float]]]:
        """Fetches the embeddings for the reference dataset and the current dataset.

        Args:
            collection_name (str): the name of the collection to fetch for
            reference_data_version (str): the name reference data version.
            current_data_version (str): the name current data version.

        Returns:
            Tuple[list, list]: the reference embeddings and the current embeddings
        """
        collection = self._client.get_collection(collection_name)

        reference_dataset = collection.get(
            where={"data_version": reference_data_version}, include=["embeddings"]
        )
        reference_embeddings = reference_dataset["embeddings"]

        current_dataset = collection.get(
            where={"data_version": current_data_version}, include=["embeddings"]
        )
        current_embeddings = current_dataset["embeddings"]

        return reference_embeddings, current_embeddings  # type: ignore
