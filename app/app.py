import streamlit as st
import random
import time
import os

from typing import List, Dict

PIPELINE_NAME = "llm_deployment_pipeline"
PIPELINE_STEP = "deploy_model"
MODEL_NAME = "seldon-llm-custom-model"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@st.cache_data
def _get_prediction_endpoint():
    """Get the endpoint for the currently deployed LLM model.

    Returns:
        str: the url endpoint.
    """
    ...


def _create_payload(messages: List[Dict[str, str]]) -> dict:
    """Create a payload from the user input to send to the LLM model.

    Args:
        input_text (str): Input text to summarize.

    Returns:
        dict: the payload to send in the correct format.
    """
    input_text = " ".join(f"{x.get('role', '')}: {x.get('content', '')}" for x in messages)
    return {"data": {"ndarray": [{"text": str(input_text)}]}}


def _get_predictions(prediction_endpoint: str, payload: dict) -> dict:
    """Using the prediction endpont and payload, make a prediction request to the deployed model.

    Args:
        prediction_endpoint (str): the url endpoint.
        payload (dict): the payload to send to the model.

    Returns:
        dict: the predictions from the model.
    """
    response = requests.post(
        url=prediction_endpoint,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(response.text)["jsonData"]["predictions"][0]


def fetch_summary(seldon_url: str, txt: str) -> str:
    """Query seldon endpoint to fetch the summary.

    Args:
        seldon_url (str): Seldon endpoint
        txt (str): Input text to summarize

    Returns:
        str: Summarized text
    """
    with st.spinner("Applying LLM Magic..."):
        payload = _create_payload(txt)
        summary_txt = _get_predictions(seldon_url, payload)
    return summary_txt

st.title("MindGPT")
if hasattr(st.session_state, "messages"):
    st.text(_create_payload(st.session_state.messages))

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

with st.chat_message("assistant"):
    message_placeholder = st.empty()
    full_response = ""
    assistant_response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    # Simulate stream of response with milliseconds delay
    for chunk in assistant_response.split():
        full_response += chunk + " "
        time.sleep(0.05)
        # Add a blinking cursor to simulate typing
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
# Add assistant response to chat history
st.session_state.messages.append({"role": "assistant", "content": full_response})