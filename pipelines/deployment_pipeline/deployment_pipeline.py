"""Deployment pipeline for MindGPT."""
from steps.deployment_steps import deploy_model, fetch_model
from zenml import pipeline
from zenml.logger import get_logger

logger = get_logger(__name__)


@pipeline
def deployment_pipeline() -> None:
    """A pipeline for deploying the MindGPT model."""
    model, tokenizer = fetch_model()

    deploy_model()
