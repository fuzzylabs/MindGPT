"""Reusable fixtures."""
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mocked_get_archived_url() -> MagicMock:
    """A fixture that mock the result of Wayback Machine API calls.

    Yields:
        MagicMock: the mocked method.
    """
    with patch("requests.get") as get:
        get.return_value.json.return_value = {
            "url": "test_url",
            "archived_snapshots": {
                "closest": {
                    "status": "200",
                    "available": True,
                    "url": "test_archived_url",
                    "timestamp": "202306061888",
                }
            },
            "timestamp": "20230606",
        }

        yield get
