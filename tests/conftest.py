"""General testing fixtures for all tests."""

import os
from tempfile import TemporaryDirectory
from typing import Iterator

import pytest


@pytest.fixture
def directory_for_testing() -> Iterator[str]:
    """A directory for testing purposes.

    Yields:
        Iterator[str]: the name of the directory.
    """
    temp_directory = TemporaryDirectory()
    original_directory = os.getcwd()

    yield temp_directory.name

    os.chdir(original_directory)
    temp_directory.cleanup()
