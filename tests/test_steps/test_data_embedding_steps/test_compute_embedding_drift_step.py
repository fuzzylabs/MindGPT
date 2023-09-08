"""Unit tests for the compute embedding drift step."""
from contextlib import nullcontext as does_not_raise
from typing import List
from unittest.mock import patch

import pytest
from steps.data_embedding_steps.compute_embedding_drift_step.compute_embedding_drift_step import (
    build_embedding_drift_payload,
    calculate_euclidean_distance,
    calculate_means,
    compute_embedding_drift,
    validate_embeddings,
)


@pytest.mark.parametrize(
    "reference_embeddings, current_embeddings, expectation",
    [
        (123, [[1.0, 2.1, 3.2], [3.1, 4.2, 5.3]], pytest.raises(TypeError)),
        (
            [[1.1, 2.2, 3.3], ["a", "a", True]],
            [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1]],
            pytest.raises(TypeError),
        ),
        (
            [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1]],
            [(1.1, 2.2), (3.1, 4.1, 5.1)],
            pytest.raises(TypeError),
        ),
        ([[1, 2, 3], [3, 4, 5]], [[1, 2, 3], [3, 4, 5]], pytest.raises(TypeError)),
        (
            [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1]],
            [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1], [4.1, 5.1, 6.1]],
            does_not_raise(),
        ),
        (
            [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1]],
            [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1]],
            does_not_raise(),
        ),
    ],
)
def test_validate_embeddings(
    reference_embeddings: List[List[float]],
    current_embeddings: List[List[float]],
    expectation: pytest.raises,
):
    """Test whether the validate_embeddings functions raises an error when either the reference or the current embeddings are not correct.

    Args:
        reference_embeddings (List[List[float]]): the mock reference dataset embeddings to check
        current_embeddings (List[List[float]]): the mock current dataset embeddings to check
        expectation (pytest.raises): exception to raise
    """
    with expectation:
        validate_embeddings(reference_embeddings, current_embeddings)


def test_calculate_means():
    """Test that the calculate_means function is able to return expected result."""
    test_list = [[1, 1, 1], [2, 2, 2], [1.5, 2.5, 3.5]]
    expected_result = [1, 2, 2.5]

    result = calculate_means(test_list)

    assert result == expected_result


def test_calculate_euclidean_distance_raise_value_error():
    """Test that the calculate_euclidean_distance function raises the expected error when the embedding length does not equal between the reference and the current dataset."""
    mock_reference_embedding = [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1]]
    mock_current_embedding = [[1.1, 2.2], [3.1, 4.1]]

    with pytest.raises(ValueError):
        calculate_euclidean_distance(mock_reference_embedding, mock_current_embedding)


def test_calculate_euclidean_distance_expected_result():
    """Test that the calculate_euclidean_distance function is able to compute the correct Euclidean distance."""
    mock_reference_embedding = [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1]]
    mock_current_embedding = [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1]]

    result = calculate_euclidean_distance(
        mock_reference_embedding, mock_current_embedding
    )

    assert result == 0


def test_build_embedding_drift_payload():
    """Test that the build_embedding_drift_payload function returns the expected dictionary payload."""
    result = build_embedding_drift_payload("test_version", "test_version", 1.1, "nhs")

    assert result == {
        "reference_dataset": "test_version",
        "current_dataset": "test_version",
        "distance": 1.1,
        "drifted": True,
        "dataset": "nhs",
    }


def test_compute_embedding_drift_step():
    """Test that the compute_embedding_drift step returns the expected output."""
    mock_reference_embedding = [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1]]
    mock_current_embedding = [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1]]

    with patch(
        "steps.data_embedding_steps.compute_embedding_drift_step.compute_embedding_drift_step.ChromaStore"
    ) as mock_chroma, patch(
        "steps.data_embedding_steps.compute_embedding_drift_step.compute_embedding_drift_step.requests.post"
    ) as mock_post_requests, patch(
        "steps.data_embedding_steps.compute_embedding_drift_step.compute_embedding_drift_step.COLLECTION_NAME_MAP"
    ) as mock_collection_name_map:
        mock_chroma_instance = mock_chroma.return_value
        mock_chroma_instance.fetch_reference_and_current_embeddings.return_value = (
            mock_reference_embedding,
            mock_current_embedding,
        )

        mock_collection_name_map.return_value = {
            "mock_collection_name": "mock_collection"
        }

        mock_post_requests.return_value.text = "OK"

        distance = compute_embedding_drift(
            "mock_collection_name", "mock_version", "mock_version"
        )

        assert isinstance(distance, float)
        assert distance == 0
