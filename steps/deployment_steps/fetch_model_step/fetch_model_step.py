"""Fetch the FLAN base model and tokenizer from HuggingFace using Langchain."""
from zenml import step


@step
def fetch_model() -> None:
    """Fetch the FLAN base model and tokenizer from HuggingFace using Langchain.

    This step should return the model and tokenizer fetched from HuggingFace.
    """
    ...
