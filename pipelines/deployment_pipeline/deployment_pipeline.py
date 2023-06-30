"""Deployment pipeline for MindGPT."""
from steps.deployment_steps import deploy_model, fetch_model
from zenml import pipeline


@pipeline
def deployment_pipeline() -> None:
    """A pipeline for deploying the MindGPT model."""
    fetch_model()
    deploy_model()
