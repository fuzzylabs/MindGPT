"""Compute embedding drift step."""
from statistics import mean
from typing import List

from scipy.spatial import distance
from utils.chroma_store import ChromaStore
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


def validate_embeddings(
    reference_embeddings: List[List[float]], current_embeddings: List[List[float]]
) -> None:
    """Validate that reference and current embeddings are both lists of lists of floats.

    Args:
        reference_embeddings (List[List[float]]): reference dataset embeddings to validate
        current_embeddings (List[List[float]]): current dataset embeddings to validate

    Raises:
        TypeError: raise if reference or current embeddings are not lists of lists of floats.
    """
    for name, embeddings in [
        ("reference", reference_embeddings),
        ("current", current_embeddings),
    ]:
        if not isinstance(embeddings, list) or not all(
            isinstance(sublist, list)
            and all(isinstance(item, float) for item in sublist)
            for sublist in embeddings
        ):
            raise TypeError(
                f"The {name} embeddings should be a list of lists of floats."
            )

    if len(reference_embeddings) != len(current_embeddings):
        raise ValueError(
            "The length of the reference embeddings does not equal to the length of the current embeddings"
        )


def calculate_means(embeddings: List[List[float]]) -> List[float]:
    """Calculate the mean of each list of embeddings.

    Args:
        embeddings (List[List[float]]): a list of lists, where each inner list contains floats

    Returns:
        List[float]: the mean of each list of embeddings.
    """
    return [mean(embedding) for embedding in embeddings]


def calculate_euclidean_distance(
    reference_embeddings: List[List[float]], current_embeddings: List[List[float]]
) -> float:
    """Calculate the Euclidean distance between the mean of reference embeddings and the mean of current embeddings.

    Args:
        reference_embeddings (List[List[float]]): a list of lists, where each inner list contains floats of reference embeddings
        current_embeddings (List[List[float]]): a list of lists, where each inner list contains floats of current embeddings

    Raises:
        ValueError: raise if the len of the reference dataset embedding mean does not equal the length current dataset

    Returns:
        float: the Euclidean distance between the mean of reference embeddings and the mean of current embeddings
    """
    reference_embeddings_mean = calculate_means(reference_embeddings)
    current_embeddings_mean = calculate_means(current_embeddings)

    reference_lengths = [len(embedding) for embedding in reference_embeddings]
    current_lengths = [len(embedding) for embedding in current_embeddings]

    if reference_lengths != current_lengths:
        raise ValueError(
            "The length of the reference embeddings mean list should equal to the length of the current embeddings mean list"
        )

    return float(distance.euclidean(reference_embeddings_mean, current_embeddings_mean))


@step
def compute_embedding_drift(
    collection_name: str, reference_data_version: str, current_data_version: str
) -> float:
    """Compute the measure of 'drift' in data embeddings between the current and reference datasets, identified by the given collection name.

    This function calculates the Euclidean distance between the mean values of the reference and current embeddings
    This distance signifies the 'drift' or variation in the data distribution between the reference and current datasets, which will be visualised over time using a plot of the distance

    Args:
        collection_name (str): the name of the collection to compute
        reference_data_version (str): the reference data version
        current_data_version (str): the current data version

    Returns:
        float: the Euclidean distance representing the drift between the reference and current datasets. 0 if reference and current embeddings are the same.
    """
    # Create a chromadb client
    # Switch hostname to chroma-service.default if running the pipeline on k8s
    chroma_client = ChromaStore(
        chroma_server_hostname="localhost", chroma_server_port=8000
    )
    (
        reference_embeddings,
        current_embeddings,
    ) = chroma_client.fetch_reference_and_current_embeddings(
        collection_name, reference_data_version, current_data_version
    )
    validate_embeddings(reference_embeddings, current_embeddings)
    distance = calculate_euclidean_distance(reference_embeddings, current_embeddings)

    logger.info(
        f"The Euclidean distance between the mean of reference embeddings and the mean of current embeddings is: {distance}"
    )

    return float(distance)
