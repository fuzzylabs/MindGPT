"""Unit tests for metric service."""
from contextlib import nullcontext as does_not_raise

import pytest
from monitoring import compute_readability


@pytest.mark.parametrize(
    "response, expectation",
    [
        (int(123), pytest.raises(TypeError)),
        ("", pytest.raises(ValueError)),
        ("Valid response", does_not_raise()),
    ],
)
def test_compute_readability(response: str, expectation: pytest.raises) -> None:
    """Test whether the compute_readability function would raise an error when the input response is incorrect.

    Args:
        response (str): mock responses
        expectation (pytest.raises): exception to raise
    """
    with expectation:
        compute_readability(response)


def test_readability_score() -> None:
    """Test that the compute_readability() function accurately calculates a score that appropriately distinguishes between confusing and easily understood sentences."""
    bad_sentence = "Try different ways of addressing your worries. Try mindfulness. Try complementary and alternative therapies. Try talking therapies."
    good_sentence = "Depression is a low mood that lasts for weeks or months and affects your daily life."

    assert compute_readability(bad_sentence) == pytest.approx(20, 5)
    assert compute_readability(good_sentence) == pytest.approx(80, 5)
