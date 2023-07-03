"""Fetch the FLAN base model and tokenizer from the HuggingFace hub."""
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizerBase,
)
from zenml import step
from zenml.logger import get_logger
from zenml.steps import Output

logger = get_logger(__name__)


@step
def fetch_model(
    model_name: str,
) -> Output(model=PreTrainedModel, tokenizers=PreTrainedTokenizerBase):  # type: ignore
    """A step to fetch a model and tokenizer (specified by model_name) from the HuggingFace Hub.

    Args:
        model_name: the name of the model to fetch from the hub.

    Returns:
        PreTrainedModel: the model.
        PreTrainedTokenizerBase: the tokenizer for the model
    """
    logger.info(
        f"Fetching the model '{model_name}' and tokenizer from the HuggingFace Hub"
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    logger.info("Model and tokenizer loaded")

    return model, tokenizer
