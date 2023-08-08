"""Unit tests for the compute embedding drift step."""
from contextlib import nullcontext as does_not_raise
from typing import List

import pytest
from steps.data_embedding_steps.compute_embedding_drift_step.compute_embedding_drift_step import (
    calculate_euclidean_distance,
    calculate_means,
    validate_embeddings,
)


@pytest.mark.parametrize(
    "reference_embeddings, current_embeddings, expectation",
    [
        (int(123), [[1.0, 2.1, 3.2], [3.1, 4.2, 5.3]], pytest.raises(TypeError)),
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
            pytest.raises(ValueError),
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


def test_calculate_euclidean_distance():
    """Test that the calculate_euclidean_distance function raises the expected error and compute the expected Euclidean distance."""
    mock_reference_embedding = [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1]]
    mock_current_embedding = [[1.1, 2.2], [3.1, 4.1]]

    with pytest.raises(ValueError):
        result = calculate_euclidean_distance(
            mock_reference_embedding, mock_current_embedding
        )

    mock_reference_embedding = [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1]]
    mock_current_embedding = [[1.1, 2.2, 3.3], [3.1, 4.1, 5.1]]

    result = calculate_euclidean_distance(
        mock_reference_embedding, mock_current_embedding
    )

    assert result == 0
