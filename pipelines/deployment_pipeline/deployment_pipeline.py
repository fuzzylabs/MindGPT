"""Deployment pipeline for MindGPT."""
from steps.deployment_steps import fetch_model, seldon_llm_custom_deployment
from zenml import pipeline
from zenml.logger import get_logger

logger = get_logger(__name__)


@pipeline
def deployment_pipeline() -> None:
    """A pipeline for deploying the MindGPT model."""
    _, model_uri, _, tokenizer_uri = fetch_model()

    seldon_llm_custom_deployment(
        model_uri=model_uri, tokenizer_uri=tokenizer_uri, deploy_decision=True
    )
