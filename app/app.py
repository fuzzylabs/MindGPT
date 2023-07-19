"""MindGPT Streamlit app."""
import json
import os
import time
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

# Paragraph from https://www.nhs.uk/mental-health/conditions/depression-in-adults/overview/
DEFAULT_CONTEXT = """Most people experience feelings of stress, anxiety or low mood during difficult times. 
A low mood may improve after a short period of time, rather than being a sign of depression."""

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
    ingress_ip = os.environ.get("SELDON_INGRESS")
    if ingress_ip is None:
        return None
    return f"http://{ingress_ip}/seldon/matcha-seldon-workloads/llm/v2/models/transformer/infer"


def _create_payload(
    messages: List[Dict[str, str]]
) -> Dict[str, List[Dict[str, str]]]:
    """Create a payload from the user input to send to the LLM model.

    Args:
        messages (List[Dict[str, str]]): List of previous messages from both the AI and user.

    Returns:
        Dict[str, List[Dict[str, str]]]: the payload to send in the correct format.
    """
    template = "Context: {context}\n\nQuestion: {question}\n\n"
    input_text = template.format(question=messages[-1]["content"], context=DEFAULT_CONTEXT)

    return {
        "inputs": [
            {
                "name": "array_inputs",
                "shape": [-1],
                "datatype": "string",
                "data": str(input_text)
            }
        ]
    }


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
    data = json.loads(json.loads(response.text)["outputs"][0]["data"][0])
    return data["generated_text"]


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
