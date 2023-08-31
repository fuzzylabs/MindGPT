"""Functions for getting the endpoints for various services."""
import streamlit as st
from configs.service_config import (
    METRIC_SERVICE_NAME,
    METRIC_SERVICE_NAMESPACE,
    METRIC_SERVICE_PORT,
    SELDON_NAMESPACE,
    SELDON_PORT,
    SELDON_SERVICE_NAME,
)


@st.cache_data(show_spinner=False)
def get_prediction_endpoint() -> str:
    """Get the endpoint for the currently deployed LLM model.

    Returns:
        str: the url endpoint if it exists and is valid, None otherwise.
    """
    return f"http://{SELDON_SERVICE_NAME}.{SELDON_NAMESPACE}:{SELDON_PORT}/v2/models/transformer/infer"


@st.cache_data(show_spinner=False)
def get_metric_service_endpoint() -> str:
    """Get the endpoint for the currently deployed metric service.

    Returns:
        str: the url endpoint if it exists and is valid, None otherwise.
    """
    return (
        f"http://{METRIC_SERVICE_NAME}.{METRIC_SERVICE_NAMESPACE}:{METRIC_SERVICE_PORT}"
    )
