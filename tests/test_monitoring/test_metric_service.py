"""Unit tests for metric service."""
from contextlib import nullcontext as does_not_raise

import pytest
from monitoring.metric_service.metric_service import (
    compute_readability,
    validate_embedding_drift_data,
    validate_llm_response,
    validate_user_feedback_data,
)


@pytest.mark.parametrize(
    "response, expectation",
    [
        (int(123), pytest.raises(TypeError)),
        (
            {"incorrect key": "mock response", "dataset": "mock_dataset"},
            pytest.raises(ValueError),
        ),
        (
            {"response": "mock response", "incorrect key": "mock_dataset"},
            pytest.raises(ValueError),
        ),
        ({"response": int(123), "dataset": "mock_dataset"}, pytest.raises(TypeError)),
        ({"response": "", "dataset": "mock_dataset"}, pytest.raises(ValueError)),
        ({"response": "mock response", "dataset": int(123)}, pytest.raises(TypeError)),
        ({"response": "mock response", "dataset": ""}, pytest.raises(ValueError)),
        ({"response": "mock response", "dataset": "mock_dataset"}, does_not_raise()),
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
                "reference_dataset": "1.1",
                "current_dataset": 1.2,
                "distance": 0.1,
                "drifted": True,
                "dataset": "nhs",
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "reference_dataset": 1.1,
                "current_dataset": "str",
                "distance": 0.1,
                "drifted": True,
                "dataset": "mind",
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "reference_dataset": "1.1",
                "current_dataset": "1.2",
                "distance": False,
                "drifted": True,
                "dataset": "nhs",
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "reference_dataset": "1.1",
                "current_dataset": "1.2",
                "distance": 0.1,
                "drifted": "True",
                "dataset": "mind",
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "reference_dataset": "1.1",
                "current_dataset": "1.2",
                "distance": 0.1,
                "drifted": "True",
                "dataset": 0.1,
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "current_dataset": "1.2",
                "distance": 0.1,
                "drifted": "True",
                "dataset": "nhs",
            },
            pytest.raises(KeyError),
        ),
        (
            {
                "reference_dataset": "1.1",
                "distance": 0.1,
                "drifted": "True",
                "dataset": "nhs",
            },
            pytest.raises(KeyError),
        ),
        (
            {
                "reference_dataset": "1.1",
                "current_dataset": "1.2",
                "drifted": "True",
                "dataset": "nhs",
            },
            pytest.raises(KeyError),
        ),
        (
            {
                "reference_dataset": "1.1",
                "current_dataset": "1.2",
                "distance": 0.1,
                "dataset": "nhs",
            },
            pytest.raises(KeyError),
        ),
        (
            {
                "reference_dataset": "1.1",
                "current_dataset": "1.2",
                "distance": 0.1,
                "drifted": True,
            },
            pytest.raises(KeyError),
        ),
        (
            {
                "reference_dataset": "1.1",
                "current_dataset": "1.2",
                "distance": 0.1,
                "drifted": True,
                "dataset": "nhs",
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


@pytest.mark.parametrize(
    "user_feedback_data, expectation",
    [
        (
            {
                "user_rating": 1.1,
                "question": "1.2",
                "full_response": "1.3",
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "user_rating": "1.1",
                "question": 1.2,
                "full_response": "1.3",
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "user_rating": "1.1",
                "question": "1.2",
                "full_response": 1.3,
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "not_user_rating": "1.1",
                "question": "1.2",
                "full_response": "1.3",
            },
            pytest.raises(KeyError),
        ),
        (
            {
                "user_rating": "1.1",
                "not_question": "1.2",
                "full_response": "1.3",
            },
            pytest.raises(KeyError),
        ),
        (
            {
                "user_rating": "1.1",
                "question": "1.2",
                "not_full_response": "1.3",
            },
            pytest.raises(KeyError),
        ),
    ],
)
def test_validate_user_feedback_data(
    user_feedback_data: dict, expectation: pytest.raises
) -> None:
    """Test whether the validate_user_feedback_data function would raise the expected error when the user feedback dictionary contains incorrect data.

    Args:
        user_feedback_data (dict): mock embedding user feedback data dictionary
        expectation (pytest.raises): exception to raise
    """
    with expectation:
        validate_user_feedback_data(user_feedback_data)
