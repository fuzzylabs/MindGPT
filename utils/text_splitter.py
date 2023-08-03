"""Text splitter class."""
# Modified from : https://github.com/langchain-ai/langchain/blob/37aade19da2f4c974e95d0758a796467cdccf1b1/libs/langchain/langchain/text_splitter.py
import re
from typing import Iterable, List, Optional


def join_docs(docs: List[str], separator: str) -> Optional[str]:
    """Join input texts using input separator.

    Args:
        docs (List[str]): List of texts to join
        separator (str): Separator to use for joining.

    Returns:
        Optional[str]: Joined text.
    """
    text = separator.join(docs)
    text = text.strip()
    if not text:
        return None
    else:
        return text


def split_text_with_regex(text: str, separator: str) -> List[str]:
    """Split text using input separator.

    Args:
        text (str): Input text to split
        separator (str): Separator to use for splitting.

    Returns:
        List[str]: List of split text.
    """
    # The parentheses in the pattern keep the delimiters in the result.
    _splits = re.split(f"({separator})", text)
    splits = [_splits[i] + _splits[i + 1] for i in range(1, len(_splits), 2)]
    if len(_splits) % 2 == 0:
        splits += _splits[-1:]
    splits = [_splits[0]] + splits
    return [s for s in splits if s]


class TextSplitter:
    """Text splitter class."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        """Constructor for TextSplitter.

        Args:
            chunk_size (int): Chunk size to use.
            chunk_overlap (int): Chunk overlap to use.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def merge_splits(self, splits: Iterable[str], separator: str) -> List[str]:
        """Merge splits into chunks using given separator.

        Args:
            splits (Iterable[str]): Splits to merge.
            separator (str): Separator to use for merging.

        Returns:
            List[str]: Merged splits.
        """
        # Combine these smaller pieces into medium size chunks to send to the LLM.
        separator_len = len(separator)

        docs = []
        current_doc: List[str] = []
        total = 0
        for d in splits:
            _len = len(d)
            if (
                total + _len + (separator_len if len(current_doc) > 0 else 0)
                > self.chunk_size
            ):
                if total > self.chunk_size:
                    print(
                        f"Created a chunk of size {total}, "
                        f"which is longer than the specified {self.chunk_size}"
                    )
                if len(current_doc) > 0:
                    doc = join_docs(current_doc, separator)
                    if doc is not None:
                        docs.append(doc)
                    # Keep on popping if:
                    # - we have a larger chunk than in the chunk overlap
                    # - or if we still have any chunks and the length is long
                    while total > self.chunk_overlap or (
                        total + _len + (separator_len if len(current_doc) > 0 else 0)
                        > self.chunk_size
                        and total > 0
                    ):
                        total -= len(current_doc[0]) + (
                            separator_len if len(current_doc) > 1 else 0
                        )
                        current_doc = current_doc[1:]
            current_doc.append(d)
            total += _len + (separator_len if len(current_doc) > 1 else 0)
        doc = join_docs(current_doc, separator)
        if doc is not None:
            docs.append(doc)
        return docs

    def split_text(
        self, text: str, separators: List[str] = ["\n\n", "\n", " ", ""]
    ) -> List[str]:
        r"""Split incoming text and return chunks.

        Args:
            text (str): Input text to split
            separators (List[str], optional): List of separator to use for splitting.
                Defaults to ["\n\n", "\n", " ", ""].

        Returns:
            List[str]: List of chunks
        """
        final_chunks = []
        # Get appropriate separator to use
        separator = separators[-1]
        new_separators = []
        for i, _s in enumerate(separators):
            if not _s:
                separator = _s
                break
            if re.search(_s, text):
                separator = _s
                new_separators = separators[i + 1 :]
                break

        splits = split_text_with_regex(text, separator)
        # Now go merging things, recursively splitting longer texts.
        _good_splits = []
        _separator = ""
        for s in splits:
            if len(s) < self.chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self.merge_splits(_good_splits, _separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    other_info = self.split_text(s, new_separators)
                    final_chunks.extend(other_info)
        if _good_splits:
            merged_text = self.merge_splits(_good_splits, _separator)
            final_chunks.extend(merged_text)
        return final_chunks
