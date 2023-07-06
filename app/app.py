"""MindGPT Streamlit app."""
import json
import os
import time
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

PIPELINE_NAME = "deployment_pipeline"
PIPELINE_STEP = "deploy_model"
MODEL_NAME = "placeholder"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="MindGPT",
    page_icon="🧠",
    layout="wide",
)

st.title("MindGPT 🧠")
st.session_state.error_placeholder = st.empty()


@st.cache_data
def _get_prediction_endpoint() -> Optional[str]:
    """Get the endpoint for the currently deployed LLM model.

    Returns:
        Optional[str]: the url endpoint if it exists and is valid, None otherwise.
    """
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
    st.sidebar.markdown(
        """
Please read and accept the following conditions before using this chatbot:

We are not affiliated, associated, authorized, endorsed by, or in any way officially connected with the NHS or the Mind charity. The official Mind website can be found at https://www.mind.org.uk/.

Your data: We want to assure you that we do not store any data you input through this chatbot. Your privacy and confidentiality are important to us. However, please note that this chatbot may utilize temporary storage or caching solely for the purpose of providing you with a smooth and interactive experience. Any temporary storage or caching is designed to be ephemeral and is not intended for data retention.

The following disclaimer applies to the chatbot's mental health information and any advice or suggestions it provides.

1. Informational purposes only: The mental health information provided by this chatbot is intended for general informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified mental health professional or healthcare provider with any questions you may have regarding a mental health condition.

2. Not a substitute for professional help: This chatbot is not a licensed mental health professional and should not be relied upon as a substitute for professional diagnosis or treatment. It is designed to provide general information and support, but it cannot replace the expertise and individualized care provided by trained professionals.

3. Individual differences: Mental health is a complex and highly individualized field. The information provided by this chatbot may not be applicable to everyone. It is important to recognize that each person's mental health needs are unique, and what works for one individual may not work for another. Use the information provided by this chatbot as a starting point for further exploration and discussion with a qualified professional.

4. Accuracy and reliability: While efforts have been made to ensure the accuracy and reliability of the information provided by this chatbot, it is not guaranteed to be complete, up-to-date, or error-free. Mental health research and knowledge are constantly evolving, and new information may emerge that could change the understanding or recommendations in the field. Therefore, it is always advisable to consult current and reputable sources for the most accurate and reliable information.

5. Emergency situations: If you or someone you know is in crisis or experiencing a mental health emergency, please contact your local emergency services or a helpline immediately such as https://www.mind.org.uk/need-urgent-help/using-this-tool/ . This chatbot is not designed to provide immediate crisis intervention or emergency assistance.

6. User responsibility: By using this chatbot, you acknowledge and accept that you are solely responsible for any actions or decisions you make based on the information provided. The creators and developers of this chatbot shall not be held liable for any damages, losses, or adverse outcomes resulting from the use of this chatbot.

Remember, seeking professional help from qualified mental health professionals is crucial for accurate diagnosis, personalized treatment, and ongoing care. Use this chatbot as a tool to enhance your understanding, but always consult with professionals for specific guidance and support.
    """
    )

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
                    "MindGPT is not reachable, please try again later.", icon="🚨"
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
