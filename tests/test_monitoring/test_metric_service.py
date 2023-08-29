"""Unit tests for metric service."""
from contextlib import nullcontext as does_not_raise

import pytest
from monitoring.metric_service.metric_service import (
    compute_readability,
    validate_data,
    validate_llm_response,
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
    "test_data, expectation",
    [
        (
            {
                "str": 1.1,
                "float": 1.2,
                "bool": True,
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "str": "1.1",
                "float": "1.2",
                "bool": True,
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "str": "1.1",
                "float": 1.2,
                "bool": "True",
            },
            pytest.raises(TypeError),
        ),
        (
            {
                "wrong_key": "1.1",
                "float": 1.2,
                "bool": True,
            },
            pytest.raises(KeyError),
        ),
        (
            {
                "str": "1.1",
                "wrong_key": 1.2,
                "bool": True,
            },
            pytest.raises(KeyError),
        ),
        (
            {
                "str": "1.1",
                "float": 1.2,
                "wrong_key": True,
            },
            pytest.raises(KeyError),
        ),
    ],
)
def test_validate_user_feedback_data(
    test_data: dict, expectation: pytest.raises
) -> None:
    """Test whether the validate_data function would raise the expected error when the data dictionary passed in contains incorrect data.

    Args:
        test_data (dict): the mock data
        expectation (pytest.raises): exception to raise
    """
    required_keys_types = {
        "str": str,
        "float": float,
        "bool": bool,
    }

    with expectation:
        validate_data(test_data, required_keys_types)
