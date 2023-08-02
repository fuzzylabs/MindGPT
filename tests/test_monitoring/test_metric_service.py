"""Unit tests for metric service."""
from contextlib import nullcontext as does_not_raise

import pytest
from monitoring import (
    compute_readability,
    validate_embedding_drift_data,
    validate_llm_response,
)


@pytest.mark.parametrize(
    "response, expectation",
    [
        (int(123), pytest.raises(TypeError)),
        ({"incorrect key": "mock response"}, pytest.raises(ValueError)),
        ({"response": int(123)}, pytest.raises(TypeError)),
        ({"response": ""}, pytest.raises(ValueError)),
        ({"response": "mock response"}, does_not_raise()),
    ],
)
def test_validate_llm_response(response: dict, expectation: pytest.raises) -> None:
    """Test whether the validate_llm_response function would raise an error when the response payload is incorrect.

    Args:
        response (dict): mock responses
        expectation (pytest.raises): exception to raise
    """
    with expectation:
        validate_llm_response(response)


def test_readability_score_for_bad_sentences() -> None:
    """Test that the compute_readability() function accurately calculates a score that appropriately distinguishes confusing sentences."""
    bad_sentence = "Try different ways of addressing your worries. Try mindfulness. Try complementary and alternative therapies. Try talking therapies."
    nonsense = "Self-help - Generalised anxiety disorder in adults Self-help - Generalised anxiety disorder in adults Self-help - Generalised anxiety disorder in adults Self-help - Generalised anxiety disorder in adults Self-help - Generalised anxiety disorder in adults Self-help - Generalised anxiety disorder in adults Self-help - Generalised anxiety disorder in adults Self-help - Generalised anxiety disorder in adults Self-help - Generalised anxiety disorder in adults Self-help - Generalised anxiety disorder in adults Self-help - Generalised"

    assert compute_readability(bad_sentence) == pytest.approx(20, 5)
    assert compute_readability(nonsense) <= 0


def test_readability_score_for_good_sentences() -> None:
    """Test that the compute_readability() function accurately calculates a score that appropriately distinguishes easily understood sentences."""
    good_sentence = "Depression is a low mood that lasts for weeks or months and affects your daily life."
    very_easy_to_read_sentence = "I like cats."

    assert compute_readability(good_sentence) == pytest.approx(80, 5)
    assert compute_readability(very_easy_to_read_sentence) >= 100


@pytest.mark.parametrize(
    "embedding_drift_data, expectation",
    [
        (
            {
                "ReferenceDataset": "1.1",
                "CurrentDataset": 1.2,
                "Distance": 0.1,
                "Drifted": True,
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "ReferenceDataset": 1.1,
                "CurrentDataset": "str",
                "Distance": 0.1,
                "Drifted": True,
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "ReferenceDataset": "1.1",
                "CurrentDataset": "1.2",
                "Distance": False,
                "Drifted": True,
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "ReferenceDataset": "1.1",
                "CurrentDataset": "1.2",
                "Distance": 0.1,
                "Drifted": "True",
            },
            pytest.raises(TypeError),
        ),
        (
            {"CurrentDataset": "1.2", "Distance": 0.1, "Drifted": "True"},
            pytest.raises(KeyError),
        ),
        (
            {"ReferenceDataset": "1.1", "Distance": 0.1, "Drifted": "True"},
            pytest.raises(KeyError),
        ),
        (
            {"ReferenceDataset": "1.1", "CurrentDataset": "1.2", "Drifted": "True"},
            pytest.raises(KeyError),
        ),
        (
            {"ReferenceDataset": "1.1", "CurrentDataset": "1.2", "Distance": 0.1},
            pytest.raises(KeyError),
        ),
        (
            {
                "ReferenceDataset": "1.1",
                "CurrentDataset": "1.2",
                "Distance": 0.1,
                "Drifted": True,
            },
            does_not_raise(),
        ),
    ],
)
def test_validate_embedding_drift_data(
    embedding_drift_data: dict, expectation: pytest.raises
) -> None:
    """Test whether the validate_embedding_drift_data function would raise the expected error when the embedding data contains incorrect data.

    Args:
        embedding_drift_data (dict): mock embedding drift data dictionary
        expectation (pytest.raises): exception to raise
    """
    with expectation:
        validate_embedding_drift_data(embedding_drift_data)
