"""Functions related to app's UI."""
from typing import Dict, Union

import streamlit as st
from app_utils.monitoring import (
    create_score_threshold_collector,
    post_user_rating_feedback_to_metric_service,
)


def accept_disclaimer() -> None:
    """Set session state accept variable."""
    st.session_state.accept = True


def set_data_sharing_consent(accept: bool) -> None:
    """Set session state data sharing consent variable to True.

    Args:
        accept (bool): whether the user accept or decline to share data with us.
    """
    st.session_state.data_sharing_consent = accept
    st.session_state.accepted_or_declined_data_sharing_consent = True


def show_disclaimer() -> None:
    """Show disclaimer on the sidebar."""
    st.title("Disclaimer")
    with open("app/docs/disclaimer.txt") as f:
        disclaimer_text = f.read()
    st.sidebar.markdown(disclaimer_text)

    st.button("I Accept", on_click=accept_disclaimer)


def show_data_collection_permission() -> None:
    """Show data sharing consent document on the sidebar."""
    st.title("Data Sharing Consent")
    with open("app/docs/data_sharing_consent.txt") as f:
        data_sharing_consent_text = f.read()
    st.sidebar.markdown(data_sharing_consent_text)

    st.button(
        "Sure, I'm happy to share!", on_click=set_data_sharing_consent, args=(True,)
    )
    st.button(
        "No thanks, I'd rather not share.",
        on_click=set_data_sharing_consent,
        args=(False,),
    )


def create_thumbs_buttons(
    metric_service_endpoint: str, question: str, full_response: str
) -> None:
    """Create thumbs up and thumbs down buttons for feedback.

    Args:
        metric_service_endpoint (str): the metric service endpoint
        question (str): the question user asked
        full_response (str): the full response the user rated.
    """
    _, thumbs_up_button, thumbs_down_button = st.columns(spec=[0.9, 0.05, 0.05])

    with thumbs_up_button:
        st.button(
            "👍",
            on_click=post_user_rating_feedback_to_metric_service,
            args=(
                f"{metric_service_endpoint}/user_feedback",
                "thumbs_up",
                question,
                full_response,
            ),
        )
    with thumbs_down_button:
        st.button(
            "👎",
            on_click=post_user_rating_feedback_to_metric_service,
            args=(
                f"{metric_service_endpoint}/user_feedback",
                "thumbs_down",
                question,
                full_response,
            ),
        )


def create_feedback_components(
    metric_service_endpoint: str,
    question: str,
    full_response: str,
    readability_scores: Dict[str, Dict[str, Union[str, float]]],
) -> None:
    """This function construct two feedback components.

    The thumbs and down buttons using streamlit buttons and column.
    With columns, we can define where buttons should be places, in our case, two buttons side by side on the lower left.
    Reference: https://discuss.streamlit.io/t/st-button-in-one-line/25966/2

    A readability score threshold collector which display a message when the readability score falls below a threshold and store the score, question and response if user agree to share.

    Args:
        metric_service_endpoint (str): the metric service endpoint where the readability is computed
        question (str): the question user asked
        full_response (str): the full response the user rated.
        readability_scores (Dict[str, Dict[str, Union[str, float]]]): the readability score for Mind and NHS responses.
    """
    create_thumbs_buttons(metric_service_endpoint, question, full_response)
    create_score_threshold_collector(metric_service_endpoint, readability_scores)


def show_settings() -> None:
    """Show inference settings on the sidebar."""
    st.title("Settings")
    st.session_state.temperature = st.slider(
        "Temperature", min_value=0.0, max_value=2.0, value=0.8
    )
    st.session_state.max_length = st.slider(
        "Max response length", min_value=50, max_value=500, value=300, step=1
    )
    st.session_state.prompt_template = st.select_slider(
        "Prompt template",
        options=["simple", "complex", "advanced", "conversational"],
        value="simple",
    )


def show_sidebar() -> None:
    """Show the sidebar."""
    with st.sidebar:
        if not st.session_state.accept:
            show_disclaimer()
        elif (
            not st.session_state.accepted_or_declined_data_sharing_consent
        ):  # Show data sharing consent after accepted disclaimer
            show_data_collection_permission()
        else:
            show_settings()
