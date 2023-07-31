"""A metric service interface for computing readability and handling post and get requests."""
import logging
from typing import Any, List, Tuple

from flask import Flask, Response, request
from utils import DatabaseInterface

from .metric_service import compute_readability, validate_llm_response

app = Flask(__name__)
db_interface = DatabaseInterface()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


@app.route("/readability", methods=["POST"])
def readability() -> Response:
    """The function is triggered by a post request to the "/"compute_readability" route of the Flask sever which will validate the post request payload and compute a readability score.

    After a readability is computed, the score will be stored in the readability relation.

    Returns:
        Response: return a success response code if successfully insert data into relation.
    """
    llm_response_dict = request.get_json()

    validated_response = validate_llm_response(llm_response_dict)

    score = compute_readability(validated_response)

    db_interface.insert_data(float(score))

    return Response(status=200)


@app.route("/query_readability", methods=["GET"])
def query_readability() -> List[Tuple[Any, ...]]:
    """This function queries the "readability" relation using the db_interface's query_relation method and returns the results as a list of list.

    Returns:
        List[Tuple[Any, ...]]: the query result
    """
    return db_interface.query_relation(relation="readability")


@app.route("/")
def hello() -> str:
    """The message for default route.

    Returns:
        str: the message to return
    """
    return "Hello world from the metric service."
