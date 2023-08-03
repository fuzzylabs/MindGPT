"""Test suite to test TextSplitter class and other utility functions."""
from typing import List

import pytest
from utils.text_splitter import TextSplitter, join_docs, split_text_with_regex

newline_string = """dummy text
is dummy"""

double_newline_string = """dummy text

is dummy"""


@pytest.mark.parametrize(
    "docs, separator, expected_text",
    [
        (["dummy text", "is dummy"], " ", "dummy text is dummy"),
        (
            ["dummy text", "is dummy"],
            "\n",
            newline_string,
        ),
        (["dummy text", "is dummy"], "\n\n", double_newline_string),
        (["dummy text", "is dummy"], "", "dummy textis dummy"),
    ],
)
def test_join_docs(docs: List[str], separator: str, expected_text: str):
    """Test join_docs function using various separators as input.

    Args:
        docs (List[str]): List of texts to join
        separator (str): Separator to use for texts in a document
        expected_text (str): Expected string after joining texts in a document
    """
    assert join_docs(docs, separator) == expected_text


@pytest.mark.parametrize(
    "text, separator, expected_list",
    [
        ("dummy text", " ", ["dummy", " text"]),
        (
            newline_string,
            "\n",
            ["dummy text", "\nis dummy"],
        ),
        (
            newline_string,
            "\n\n",
            ["dummy text\nis dummy"],
        ),
        (
            double_newline_string,
            "\n",
            ["dummy text", "\n", "\nis dummy"],
        ),
        (
            double_newline_string,
            "\n\n",
            ["dummy text", "\n\nis dummy"],
        ),
        ("dummy text", "", ["d", "u", "m", "m", "y", " ", "t", "e", "x", "t"]),
    ],
)
def test_split_text_with_regex(text: str, separator: str, expected_list: List[str]):
    """Test split_text_with_regex function using various separators as input.

    Args:
        text (str): Input text to split
        separator (str): Separator used to split the text
        expected_list (List[str]): Expected list of texts after splitting the text
    """
    assert split_text_with_regex(text, separator) == expected_list


@pytest.mark.parametrize(
    "docs, separator, chunk_size, expected_list",
    [
        ("dummy text", "", 3, ["dum", "my", "tex", "t"]),
        ("dummy text", " ", 3, ["d u", "m m", "y", "t e", "x t"]),
        (["dummy text", "\nis dummy"], "\n", 12, ["dummy text", "is dummy"]),
        (["dummy text", "\nis dummy"], "\n\n", 12, ["dummy text", "is dummy"]),
        (["dummy text", "\n\nis dummy"], "\n", 12, ["dummy text", "is dummy"]),
        (["dummy text", "\n\nis dummy"], "\n\n", 12, ["dummy text", "is dummy"]),
    ],
)
def test_merge_splits_no_overlap(
    docs: List[str], separator: str, chunk_size: int, expected_list: List[str]
):
    """Test merge_splits function using various separators as input and no chunk overlap.

    Args:
        docs (List[str]): List of texts to join
        separator (str): Separator used to merge the texts
        chunk_size (int): Chunk size to use for merging the texts
        expected_list (List[str]): Expected list of texts after merging the input texts
    """
    text_splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=0)
    assert text_splitter.merge_splits(docs, separator) == expected_list


@pytest.mark.parametrize(
    "docs, separator, chunk_size, chunk_overlap, expected_list",
    [
        (
            "dummy text",
            "",
            3,
            2,
            ["dum", "umm", "mmy", "my", "y t", "te", "tex", "ext"],
        ),
        (
            "dummy text",
            " ",
            3,
            2,
            ["d u", "u m", "m m", "m y", "y", "t", "t e", "e x", "x t"],
        ),
        (["dummy text", "\nis dummy"], "\n", 12, 4, ["dummy text", "is dummy"]),
        (["dummy text", "\nis dummy"], "\n\n", 12, 4, ["dummy text", "is dummy"]),
        (["dummy text", "\n\nis dummy"], "\n", 12, 4, ["dummy text", "is dummy"]),
        (["dummy text", "\n\nis dummy"], "\n\n", 12, 4, ["dummy text", "is dummy"]),
    ],
)
def test_merge_splits_with_overlap(
    docs: List[str],
    separator: str,
    chunk_size: int,
    chunk_overlap: int,
    expected_list: List[str],
):
    """Test merge_splits function using various separators as input and chunk overlap.

    Args:
        docs (List[str]): List of texts to join
        separator (str): Separator used to merge the texts
        chunk_size (int): Chunk size to use for merging the texts
        chunk_overlap (int): Chunk overlap to use for merging the texts
        expected_list (List[str]): Expected list of texts after merging the input texts
    """
    text_splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    assert text_splitter.merge_splits(docs, separator) == expected_list


@pytest.mark.parametrize(
    "text, chunk_size, expected_list",
    [
        ("dummy text", 3, ["dum", "my", "te", "xt"]),
        (newline_string, 3, ["dum", "my", "te", "xt", "is", "du", "mmy"]),
        (double_newline_string, 8, ["dummy", "text", "is", "dummy"]),
    ],
)
def test_split_text_no_overlap(text: str, chunk_size: int, expected_list: List[str]):
    """Test split_text function to split text using no chunk overlap.

    Args:
        text (str): Input string to split
        chunk_size (int): Chunk size to use for splitting the texts
        expected_list (List[str]): Expected list of texts after splitting the input texts
    """
    text_splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=0)
    assert (
        text_splitter.split_text(text, separators=["\n\n", "\n", " ", ""])
        == expected_list
    )


@pytest.mark.parametrize(
    "text, chunk_size, chunk_overlap, expected_list",
    [
        ("dummy text", 3, 2, ["dum", "umm", "mmy", "te", "tex", "ext"]),
        (
            newline_string,
            3,
            5,
            ["dum", "umm", "mmy", "te", "tex", "ext", "is", "du", "dum", "umm", "mmy"],
        ),
        (double_newline_string, 8, 3, ["dummy", "text", "is", "dummy"]),
    ],
)
def test_split_text_with_overlap(
    text: str, chunk_size: int, chunk_overlap: int, expected_list: List[str]
):
    """Test split_text function to split text using chunk overlap.

    Args:
        text (str): Input string to split
        chunk_size (int): Chunk size to use for splitting the texts
        chunk_overlap (int): Chunk overlap to use for splitting the texts
        expected_list (List[str]): Expected list of texts after splitting the input texts
    """
    text_splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    assert (
        text_splitter.split_text(text, separators=["\n\n", "\n", " ", ""])
        == expected_list
    )
