"""Utility functions for interacting with the deployed LLM."""
import json
import logging
from typing import Any, Dict, List, TypedDict

import requests
import streamlit as st
from configs.prompt_template import DEFAULT_CONTEXT, PROMPT_TEMPLATES
from configs.service_config import (
    SELDON_NAMESPACE,
    SELDON_PORT,
    SELDON_SERVICE_NAME,
)


class MessagesType(TypedDict, total=False):
    """The class specifies constraints about which keys map to which types in the payload messages.

    This is required for mypy to understand the structure of the `messages` dictionary.

    Args:
        TypedDict (type): A class from the `typing` module to define types for specific dictionary keys.
        total (bool, optional): this signify that not all keys are mandatory in the dictionary.
    """

    history: List[Dict[str, str]]
    context: str
    prompt_query: str


@st.cache_data(show_spinner=False)
def get_prediction_endpoint() -> str:
    """Get the endpoint for the currently deployed LLM model.

    Returns:
        str: the url endpoint if it exists and is valid, None otherwise.
    """
    return f"http://{SELDON_SERVICE_NAME}.{SELDON_NAMESPACE}:{SELDON_PORT}/v2/models/transformer/infer"


def _build_conversation_history_template(history_list: List[Dict[str, str]]) -> str:
    """Build the conversation history as a string to be append to the prompt template.

    Args:
        history_list (List[Dict[str, str]]): the conversation history dictionary containing the questions posed by user and the response by the model.

    Returns:
        str: the conversation history string.
    """
    history_string = ""
    for history in history_list:
        user_input = history["user_input"]
        ai_response = history["ai_response"]

        history_string += f"\nUser: {user_input}\nAI: {ai_response}\n"

    return history_string


def build_memory_dict(question: str, response: str) -> Dict[str, str]:
    """Build the memory dictionary from user's question and the model's response.

    Args:
        question (str): the question asked by the user.
        response (str): the response by the model.

    Returns:
        Dict[str, str]: the memory dictionary.
    """
    return {"user_input": question, "ai_response": response}


def _create_payload(
    messages: MessagesType,
    temperature: float,
    max_length: int,
) -> Dict[str, List[Dict[str, Any]]]:
    """Create a payload from the user input to send to the LLM model.

    Args:
        messages (Dict[str, str]): List of previous messages from both the AI and user.
        temperature (float): inference temperature
        max_length (int): max response length in tokens

    Returns:
        Dict[str, List[Dict[str, Any]]]: the payload to send in the correct format.
    """
    context = messages.get("context", DEFAULT_CONTEXT)
    history: List[Dict[str, str]] = messages.get("history", [])
    question = messages["prompt_query"]

    if st.session_state.prompt_template == "conversational":
        if history:
            history_string = _build_conversation_history_template(history)
            template = PROMPT_TEMPLATES["conversational"]
            input_text = template.format(
                history=history_string, question=question, context=context
            )
        else:
            template = PROMPT_TEMPLATES["simple"]
            input_text = template.format(question=question, context=context)
    else:
        template = PROMPT_TEMPLATES[st.session_state.prompt_template]
        input_text = template.format(question=question, context=context)

    logging.info(f"Prompt to LLM : {input_text}")

    return {
        "inputs": [
            {
                "name": "array_inputs",
                "shape": [-1],
                "datatype": "string",
                "data": str(input_text),
            },
            {
                "name": "max_length",
                "shape": [-1],
                "datatype": "INT32",
                "data": [max_length],
                "parameters": {"content_type": "raw"},
            },
            {
                "name": "temperature",
                "shape": [-1],
                "datatype": "INT32",
                "data": [temperature],
                "parameters": {"content_type": "raw"},
            },
        ]
    }


def _get_predictions(
    prediction_endpoint: str, payload: Dict[str, List[Dict[str, Any]]]
) -> str:
    """Using the prediction endpoint and payload, make a prediction request to the deployed model.

    Args:
        prediction_endpoint (str): the url endpoint.
        payload (Dict[str, List[Dict[str, Any]]]): the payload to send to the model.

    Returns:
        str: the predictions from the model.
    """
    response = requests.post(
        url=prediction_endpoint,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )
    data = json.loads(json.loads(response.text)["outputs"][0]["data"][0])

    return str(data["generated_text"])


def query_llm(
    prediction_endpoint: str,
    messages: MessagesType,
    temperature: float,
    max_length: int,
) -> str:
    """Query endpoint to fetch the summary.

    Args:
        prediction_endpoint (str): Prediction endpoint.
        messages (MessagesType): Dict of message containing prompt and context.
        temperature (float): inference temperature
        max_length (int): max response length in tokens

    Returns:
        str: Summarised text.
    """
    with st.spinner("Loading response..."):
        payload = _create_payload(messages, temperature, max_length)
        logging.info(payload)
        summary_txt = _get_predictions(prediction_endpoint, payload)

    return summary_txt
