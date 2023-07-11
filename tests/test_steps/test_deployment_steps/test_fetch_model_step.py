"""Tests for the fetch_model step in the deployment pipeline."""
from unittest.mock import patch

import pytest
from steps.deployment_steps import fetch_model
from transformers import (
    PretrainedConfig,
    PreTrainedModel,
    PreTrainedTokenizerBase,
)
from zenml.materializers.base_materializer import BaseMaterializer
from zenml.steps import StepContext


FUNCTION_LOCATION_PREFIX = "steps.deployment_steps.fetch_model_step.fetch_model_step"


@pytest.fixture
def model_name() -> str:
    """A fixture to define a mock `model_name` parameter for the `from_pretrained` function.

    Returns:
        str: the mocked model_name
    """
    return "fuzzylabs-llm-base"


def test_fetch_model_expected(model_name: str):
    """Test whether the fetch_model step returns the expected objects, a model and a tokenizer."""
    with patch(f"{FUNCTION_LOCATION_PREFIX}.AutoTokenizer") as mock_tokenizer, patch(
        f"{FUNCTION_LOCATION_PREFIX}.AutoModelForSeq2SeqLM"
    ) as mock_model:
        mock_model.from_pretrained.return_value = PreTrainedModel(PretrainedConfig())
        mock_tokenizer.from_pretrained.return_value = PreTrainedTokenizerBase()

        materializers = {
            "model": (PreTrainedModel,),
            "tokenizers": (PreTrainedTokenizerBase,),
        }
        artifact_uris = {"model": "", "tokenizers": ""}

        model, _, tokenizer, _ = fetch_model.entrypoint(
            model_name=model_name,
            context=StepContext(
                step_name="fetch_model",
                output_materializers=materializers,
                output_artifact_uris=artifact_uris,
            ),
        )

        assert isinstance(model, PreTrainedModel)
        assert isinstance(tokenizer, PreTrainedTokenizerBase)
