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
def test_compute_readability(response: str, expectation: pytest.raises):
    """Test whether the compute_readability function would raise an error when the input response is incorrect.

    Args:
        response (str): mock responses
        expectation (pytest.raises): exception to raise
    """
    with expectation:
        compute_readability(response)
