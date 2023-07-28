"""The metric service interface for computing readability and handling post and get requests."""
import logging
from typing import Dict

import textstat
from flask import Flask, request
from utils import getconn

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


def query_database(table: str) -> None:
    """Place holder."""
    conn = getconn()

    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")

    print(cursor.fetchall())


def send_metric_to_database() -> None:
    """Place holder."""
    ...


def compute_readability(llm_response: str) -> float:
    """This function compute a readability score using the Flesch–Kincaid readability tests.

    Note:
        The maximum score possible is 121.22 but that's only the case if every sentence consists of only one one-syllable word.
        The score does not have a theoretical lower bound.

        Meaning of scores:
            90-100  Very Easy
            80-89   Easy
            70-79   Fairly Easy
            60-69   Standard
            50-59   Fairly Difficult
            30-49   Difficult
            0-29    Very Confusing

    Args:
        llm_response (str): the model's response post by Streamlit

    Raises:
        TypeError: raise if the model response received is not a string
        ValueError: raise if the model response received is a empty string

    Returns:
        str: the readability score of the response with type string
    """
    return float(textstat.flesch_reading_ease(llm_response))


def validate_llm_response(llm_response_dict: Dict[str, str]) -> str:
    """This function validate the payload which should be a dictionary containing the response text.

    Args:
        llm_response_dict (Dict[str, str]): the post request payload

    Raises:
        TypeError: raise if the json payload is not a dictionary.
        ValueError: raise if the dictionary payload does not have the response item.
        TypeError: raise if the model response received is not a string
        ValueError: raise if the model response received is a empty string

    Returns:
        str: the validated response text
    """
    if not isinstance(llm_response_dict, dict):
        raise TypeError("The model response is not a dictionary.")

    response = llm_response_dict.get("response")
    if response is None:
        raise ValueError(
            "Response dictionary does not contain the right key value pair."
        )

    if not isinstance(response, str):
        raise TypeError("The model response is not a string.")
    elif len(response) == 0:
        raise ValueError("The model response must not be an empty string.")

    return response


@app.route("/readability", methods=["POST"])
def readability() -> str:
    """The function is triggered by a post request to the "/"compute_readability" route of the Flask sever which will validate the post request payload and compute a readability score.

    Returns:
        str: the readability score of the response with type string
    """
    llm_response_dict = request.get_json()

    validated_response = validate_llm_response(llm_response_dict)

    return str(
        compute_readability(validated_response)
    )  # Flask response cannot return float


@app.route("/")
def home() -> str:
    """The message for default route.

    Returns:
        str: the message to return
    """
    return "Hello world from the metric service."
