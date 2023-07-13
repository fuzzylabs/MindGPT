"""MindGPT Streamlit app."""
import json
import os
import time
from typing import Any, Dict, List, Optional
import requests
import streamlit as st

from zenml.integrations.seldon.model_deployers.seldon_model_deployer import (
    SeldonModelDeployer,
)

PIPELINE_NAME = "deployment_pipeline"
PIPELINE_STEP = "seldon_llm_model_deployer_step"
MODEL_NAME = "seldon-llm-custom-model"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="MindGPT",
    page_icon="🧠",
    layout="wide",
)

st.title("MindGPT 🧠")
st.caption("_made by [Fuzzy Labs](https://www.fuzzylabs.ai/)_")
st.caption(
    "MindGPT is not a digital counsellor and the answers provided may be innacurate. If you or someone you know is in crisis or experiencing a mental health emergency, please contact your local emergency services or a helpline immediately such as https://www.mind.org.uk/need-urgent-help/using-this-tool/ . This chatbot is not designed to provide immediate crisis intervention or emergency assistance."
)

st.session_state.error_placeholder = st.empty()


@st.cache_data(show_spinner=False)
def _get_prediction_endpoint() -> Optional[str]:
    """Get the endpoint for the currently deployed LLM model.

    Returns:
        Optional[str]: the url endpoint if it exists and is valid, None otherwise.
    """
    try:
        model_deployer = SeldonModelDeployer.get_active_model_deployer()

        deployed_services = model_deployer.find_model_server(
            pipeline_name=PIPELINE_NAME,
            pipeline_step_name=PIPELINE_STEP,
            model_name=MODEL_NAME,
        )

        return deployed_services[0].prediction_url
    except Exception:
        return None


def _create_payload(
    messages: List[Dict[str, str]]
) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    """Create a payload from the user input to send to the LLM model.

    Args:
        messages (List[Dict[str, str]]): List of previous messages from both the AI and user.

    Returns:
        Dict[str, Dict[str, List[Dict[str, str]]]]: the payload to send in the correct format.
    """
    # We currently just append all messages, this could be improved to append a summary of the conversation to the start of the current user message.
    input_text = " ".join(
        f"{x.get('role', '')}: {x.get('content', '')}" for x in messages
    )
    return {"data": {"ndarray": [{"text": str(input_text)}]}}


def _get_predictions(
    prediction_endpoint: str, payload: Dict[str, Dict[str, List[Dict[str, str]]]]
) -> Dict[Any, Any]:
    """Using the prediction endpont and payload, make a prediction request to the deployed model.

    Args:
        prediction_endpoint (str): the url endpoint.
        payload (Dict[str, Dict[str, List[Dict[str, str]]]]): the payload to send to the model.

    Returns:
        Dict[Any, Any]: the predictions from the model.
    """
    response = requests.post(
        url=prediction_endpoint,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(response.text)["jsonData"]["predictions"][0]


def fetch_summary(prediction_endpoint: str, messages: List[Dict[str, str]]) -> str:
    """Query endpoint to fetch the summary.

    Args:
        prediction_endpoint (str): Prediction endpoint.
        messages (List[Dict[str, str]]): List of previous messages from both the AI and user.

    Returns:
        str: Summarized text.
    """
    with st.spinner("Loading response..."):
        payload = _create_payload(messages)
        summary_txt = _get_predictions(prediction_endpoint, payload)
    return summary_txt


def show_disclaimer() -> bool:
    """Show disclamer on sidebar with streamlit.

    Returns:
        bool: True if disclamer accepted, False if not.
    """
    st.sidebar.title("Disclaimer")
    with open("app/disclaimer.txt") as f:
        disclaimer_text = f.read()
    st.sidebar.markdown(disclaimer_text)

    accept = st.sidebar.button("I Accept")

    return accept


def main() -> None:
    """Main streamlit app function."""
    if "accept" not in st.session_state:
        st.session_state.accept = False

    if not st.session_state.accept:
        accept = show_disclaimer()
        if accept:
            st.session_state.accept = True

    if st.session_state.accept:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Enter a question"):
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            prediction_endpoint = _get_prediction_endpoint()

            if prediction_endpoint is None:
                st.session_state.error_placeholder.error(
                    "MindGPT is not currently reachable, please try again later.",
                    icon="🚨",
                )
            else:
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    assistant_response = fetch_summary(
                        prediction_endpoint, st.session_state.messages
                    )
                    # Simulate stream of response with milliseconds delay
                    for chunk in assistant_response.split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        # Add a blinking cursor to simulate typing
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )


if __name__ == "__main__":
    main()
