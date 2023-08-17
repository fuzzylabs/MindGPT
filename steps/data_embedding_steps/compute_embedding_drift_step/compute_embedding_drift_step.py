"""Compute embedding drift step."""
from statistics import mean
from typing import Dict, List, Union

import requests
from scipy.spatial import distance
from utils.chroma_store import ChromaStore
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)

MONITORING_METRICS_HOST_NAME = "localhost"  # if pipeline runs on k8s, "localhost" should be replaced with "monitoring-service.default"
MONITORING_METRICS_PORT = 5000

CHROMA_SERVER_HOSTNAME = "localhost"  # Switch hostname to chroma-service.default if running the pipeline on k8s
CHROMA_SERVER_PORT = 8000

COLLECTION_NAME_MAP = {"mind_data": "mind", "nhs_data": "nhs"}


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
    reference_lengths = [len(embedding) for embedding in reference_embeddings]
    current_lengths = [len(embedding) for embedding in current_embeddings]

    if reference_lengths != current_lengths:
        raise ValueError(
            "The length of the reference embeddings mean list should equal to the length of the current embeddings mean list"
        )

    reference_embeddings_mean = calculate_means(reference_embeddings)
    current_embeddings_mean = calculate_means(current_embeddings)

    return float(distance.euclidean(reference_embeddings_mean, current_embeddings_mean))


def build_embedding_drift_payload(
    reference_data_version: str,
    current_data_version: str,
    distance: float,
    dataset: str,
) -> Dict[str, Union[str, float, bool]]:
    """Construct a payload for send the embedding drift data to the metric service via post request.

    Args:
        reference_data_version (str): the version identifier for the reference data.
        current_data_version (str): the version identifier for the current data.
        distance (float): the computed Euclidean distance between the embeddings of the reference and current data.
        dataset (str): the dataset used for computing embedding drift.

    Returns:
        Dict[str, Union[str, float, bool]]: a dictionary containing the 4 items required by the metric service embedding drift relation.
    """
    drifted = distance > 0

    formatted_reference_data_version = f"'{reference_data_version}'"
    formatted_current_data_version = f"'{current_data_version}'"

    return {
        "reference_dataset": f"{formatted_reference_data_version}",
        "current_dataset": f"{formatted_current_data_version}",
        "distance": distance,
        "drifted": drifted,
        "dataset": dataset,
    }


@step
def compute_embedding_drift(
    collection_name: str, reference_data_version: str, current_data_version: str
) -> float:
    """Compute the measure of 'drift' in data embeddings between the current and reference datasets, identified by the given collection name.

    This function calculates the Euclidean distance between the mean values of the reference and current embeddings
    This distance signifies the 'drift' or variation in the data distribution between the reference and current datasets, which will be visualised over time using a plot of the distance
    This function will also prepare and send the embedding drift data to our monitoring service via post request

    Args:
        collection_name (str): the name of the collection to compute
        reference_data_version (str): the reference data version
        current_data_version (str): the current data version

    Returns:
        float: the Euclidean distance representing the drift between the reference and current datasets. 0 if reference and current embeddings are the same.
    """
    # Create a chromadb client
    chroma_client = ChromaStore(
        chroma_server_hostname=CHROMA_SERVER_HOSTNAME,
        chroma_server_port=CHROMA_SERVER_PORT,
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

    payload = build_embedding_drift_payload(
        reference_data_version,
        current_data_version,
        distance,
        COLLECTION_NAME_MAP[collection_name],
    )
    response = requests.post(
        f"http://{MONITORING_METRICS_HOST_NAME}:{MONITORING_METRICS_PORT}/embedding_drift",
        json=payload,
    )

    logger.info(response.text)

    return float(distance)
