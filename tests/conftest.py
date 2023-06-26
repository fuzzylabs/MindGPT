"""Reusable fixtures."""
from unittest.mock import MagicMock, patch

import pytest
from requests_html import HTMLSession


@pytest.fixture
def mocked_html_text() -> str:
    """A fixture of a mocked html text that will be used for functions that request html text from a webpage.

    Returns:
        str: the mocked HTML text.
    """
    html_text = """
<html>
<head>
<title>Mocked HTML Text</title>
</head>
<body>
<div class="content-area bg-white">
    <div class="test_col_1">
        <a href="/test_href_1/">Test Title 1</a>"
    </div>
    <div class="test_col_2">
        <a href="/test_href_2/">Test Title 2</a>"
    </div>
    <div class="test_col_3">
        <a href="/test_href_3/">Yes</a>"
    </div>
    <div class="test_col_4">
        <a href="/test_href_4/">Test Title 4</a>"
    </div>
</div>
<ul class="sidebar-menu" id="sidebar_menu">
    <li class=""><a href="/test_side_bar_object_1_url/">Side Bar Object 1</a></li>
    <li class=""><a href="/test_side_bar_exclude_me/">exclude_me</a></li>
    <li class=""><a href="/test_side_bar_object_2_url/">Side Bar Object 2</a></li>
</ul>
<div class="col-md-8 column ">
    <div class="test_content_class">
        <h2>Test h2 text</h2>
        <p>Test p text</p>
        <li>Text li text</li>
    </div>
</div>
<div class="col-md-12 column ">
    <div class="test_content_class">
        <h2>Test h3 text</h2>
        <p>Test p text</p>
        <li>Text li text</li>
    </div>
</div>
</body>
</html>
    """

    return html_text


@pytest.fixture(autouse=True)
def mocked_html_session_get(mocked_html_text: str) -> MagicMock:
    """A fixture that mock the result of session.get(url).text.

    Args:
        mocked_html_text (str): the mocked html text.

    Yields:
        MagicMock: the mocked method.
    """
    with patch.object(HTMLSession, "get") as mock_method:
        mock_method.return_value.text = mocked_html_text
        yield mock_method


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
