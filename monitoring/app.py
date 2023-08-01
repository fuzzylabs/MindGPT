"""A metric service interface for computing readability and handling post and get requests."""
import logging
from typing import Any, List, Tuple

from flask import Flask, Response, jsonify, request
from utils import DatabaseInterface

from .metric_service import (
    compute_readability,
    validate_embedding_drift_data,
    validate_llm_response,
)

app = Flask(__name__)
db_interface = DatabaseInterface()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


@app.route("/readability", methods=["POST"])
def readability() -> Tuple[Response, int]:
    """The function is triggered by a post request to the "/"compute_readability" route of the Flask sever which will validate the post request payload and compute a readability score.

    After a readability is computed, the score will be stored in the readability relation.

    Returns:
        Tuple[Response, int]: a tuple containing a success message and the HTTP status code.
    """
    llm_response_dict = request.get_json()

    try:
        validated_response = validate_llm_response(llm_response_dict)
        score = compute_readability(validated_response)
    except Exception as e:  # catch any exception from response validation
        return jsonify({"message": str(e)}), 400

    db_interface.insert_readability_data(float(score))

    return jsonify({"message": "Readability data has been successfully inserted"}), 200


@app.route("/embedding_drift", methods=["POST"])
def embedding_drift() -> Tuple[Response, int]:
    """Receives and validates the embedding drift data from a POST request, and then inserts it into the database if it's valid.

    Returns:
        Tuple[Response, int]: a tuple containing a success message and the HTTP status code.
    """
    embedding_drift_data_dict = request.get_json()

    try:
        validated_data = validate_embedding_drift_data(embedding_drift_data_dict)
        db_interface.insert_embedding_drift_data(validated_data)
    except Exception as e:  # catch any exception from data validation
        return jsonify({"message": "Validation error: " + str(e)}), 400

    return (
        jsonify({"message": "Embedding drift data has been successfully inserted"}),
        200,
    )


@app.route("/query_readability", methods=["GET"])
def query_readability() -> List[Tuple[Any, ...]]:
    """This function queries the "Readability" relation using the db_interface's query_relation method and returns the results as a list of tuple.

    Returns:
        List[Tuple[Any, ...]]: the query result
    """
    return db_interface.query_relation(relation_name="Readability")


@app.route("/query_embedding_drift", methods=["GET"])
def query_embedding_drift() -> List[Tuple[Any, ...]]:
    """This function queries the "EmbeddingDrift" relation using the db_interface's query_relation method and returns the results as a list of tuple.

    Returns:
        List[Tuple[Any, ...]]: the query result
    """
    return db_interface.query_relation(relation_name="EmbeddingDrift")


@app.route("/")
def hello() -> str:
    """The message for default route.

    Returns:
        str: the message to return
    """
    return "Hello world from the metric service."
