"""Utility functions for interacting with the monitoring service."""
import logging
from typing import Any, Dict, Union

import requests
import streamlit as st
from configs.app_config import READABILITY_SCORE_THRESHOLD
from configs.service_config import (
    METRIC_SERVICE_NAME,
    METRIC_SERVICE_NAMESPACE,
    METRIC_SERVICE_PORT,
)
from requests.models import Response


@st.cache_data(show_spinner=False)
def get_metric_service_endpoint() -> str:
    """Get the endpoint for the currently deployed metric service.

    Returns:
        str: the url endpoint if it exists and is valid, None otherwise.
    """
    return (
        f"http://{METRIC_SERVICE_NAME}.{METRIC_SERVICE_NAMESPACE}:{METRIC_SERVICE_PORT}"
    )


def post_response_to_metric_service(
    metric_service_endpoint: str, response: str, dataset: str
) -> Response:
    """Send the LLM's response to the metric service for readability computation using a POST request.

    Args:
        metric_service_endpoint (str): the metric service endpoint where the readability is computed
        response (str): the response produced by the LLM
        dataset (str): the dataset that was used to generate the response.

    Returns:
        Response: the post request response
    """
    response_dict = {"response": response, "dataset": dataset.lower()}
    result = requests.post(url=metric_service_endpoint, json=response_dict)

    return result


def post_feedback_data_to_metric_service(
    metric_service_endpoint: str, data: Dict[str, Union[str, Any]]
) -> None:
    """Sends data to the metric service using a POST request.

    Args:
        metric_service_endpoint (str): The metric service endpoint where the data is expected.
        data (Dict[str, Union[str, Any]]): The data to be sent.
    """
    # Store the response to metric database if user agrees to share.
    if st.session_state.data_sharing_consent:
        try:
            result = requests.post(url=metric_service_endpoint, json=data)
            logging.info(result.text)
        except requests.RequestException as e:
            logging.error(f"Failed to post data to metric service: {e}")


def post_user_rating_feedback_to_metric_service(
    metric_service_endpoint: str, user_rating: str, question: str, full_response: str
) -> None:
    """Send the user feedback data to the metric service.

    Args:
        metric_service_endpoint (str): the metric service endpoint where the the user feedback is expected
        user_rating (str): thumbs up or thumbs down
        question (str): the question asked by the user
        full_response (str): the full response used rated.
    """
    data = {
        "user_rating": user_rating,
        "question": question,
        "full_response": full_response,
    }
    post_feedback_data_to_metric_service(metric_service_endpoint, data)


def post_readability_threshold_data_to_metric_service(
    metric_service_endpoint: str,
    readability_score: float,
    question: str,
    response: str,
    dataset: str,
) -> None:
    """Send the user question and response data to the metric service.

    Args:
        metric_service_endpoint (str): the metric service endpoint where the below readability score threshold data is expected
        readability_score (float): the readability score
        question (str): the question asked by the user
        response (str): the response used to compute the readability score
        dataset (str): the name of the dataset used to generate the response.
    """
    data = {
        "readability_score": readability_score,
        "question": question,
        "response": response,
        "dataset": dataset.lower(),
    }
    post_feedback_data_to_metric_service(metric_service_endpoint, data)


def create_score_threshold_collector(
    metric_service_endpoint: str,
    readability_scores: Dict[str, Dict[str, Union[str, float]]],
) -> None:
    """Create the readability score threshold collector.

    This function will display a message saying that we have detected the readability score of the response is below a certain threshold.
    If the user agree to share data with us, we will send this data to our metric service and store them in the metric database.

    Args:
        metric_service_endpoint (str): the metric service endpoint
        readability_scores (Dict[str, Dict[str, Union[str, float]]]): a dictionary containing the score, question response.
    """
    sources = readability_scores.keys()
    below_threshold_sources = []

    for source in sources:
        score = float(readability_scores[source]["score"])
        src_question = str(readability_scores[source]["question"])
        src_response = str(readability_scores[source]["response"])

        if score < READABILITY_SCORE_THRESHOLD:
            below_threshold_sources.append(source)
            post_readability_threshold_data_to_metric_service(
                f"{metric_service_endpoint}/readability_threshold",
                score,
                src_question,
                src_response,
                source,
            )

    if below_threshold_sources:
        if len(below_threshold_sources) == 1:
            source_text = below_threshold_sources[0]
        else:
            source_text = " and ".join(below_threshold_sources)

        verb = "falls" if len(below_threshold_sources) == 1 else "fall"

        (threshold_message,) = st.columns(spec=1)
        with threshold_message:
            st.markdown(
                f'<p style="color:#EBEBEB; font-size: 12px; font-style: italic;">We\'ve noticed that the readability score for the {source_text} response {verb} below our established threshold.</p>',
                unsafe_allow_html=True,
            )
