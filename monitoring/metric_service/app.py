"""A metric service interface for computing readability and handling post and get requests."""
import logging
from typing import Any, List, Tuple

from flask import Flask, Response, jsonify, request
from metric_service import (
    compute_readability,
    validate_embedding_drift_data,
    validate_llm_response,
)
from utils.metric_database import DatabaseInterface

db_interface = DatabaseInterface()
app = Flask(__name__)
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
        Response: a tuple containing a success message and the HTTP status code.
    """
    llm_response_dict = request.get_json()

    try:
        validated_response, dataset = validate_llm_response(llm_response_dict)
        score = compute_readability(validated_response)
    except Exception as e:  # catch any exception from response validation
        return jsonify({"status_code": 400, "message": f"Validation error: {str(e)}"})

    db_interface.insert_readability_data(float(score), str(dataset))

    return jsonify(
        {
            "status_code": 200,
            "score": score,
            "dataset": dataset,
            "message": "Readability data has been successfully inserted.",
        }
    )


@app.route("/embedding_drift", methods=["POST"])
def embedding_drift() -> Response:
    """Receives and validates the embedding drift data from a POST request, and then inserts it into the database if it's valid.

    Returns:
        Response: a tuple containing a success message and the HTTP status code.
    """
    embedding_drift_data_dict = request.get_json()

    try:
        validated_data = validate_embedding_drift_data(embedding_drift_data_dict)
        db_interface.insert_embedding_drift_data(validated_data)
    except Exception as e:  # catch any exception from data validation
        return jsonify({"status_code": 400, "message": f"Validation error: {str(e)}"})

    return jsonify(
        {
            "status_code": 200,
            "data": validated_data,
            "message": "Embedding drift data has been successfully inserted.",
        }
    )


@app.route("/query_readability", methods=["GET"])
def query_readability() -> List[Tuple[Any, ...]]:
    """This function queries the "Readability" relation using the db_interface's query_relation method and returns the results as a list of tuple.

    Returns:
        List[Tuple[Any, ...]]: the query result
    """
    return db_interface.query_relation(relation_name="readability")


@app.route("/query_embedding_drift", methods=["GET"])
def query_embedding_drift() -> List[Tuple[Any, ...]]:
    """This function queries the "EmbeddingDrift" relation using the db_interface's query_relation method and returns the results as a list of tuple.

    Returns:
        List[Tuple[Any, ...]]: the query result
    """
    return db_interface.query_relation(relation_name="embedding_drift")


@app.route("/")
def hello() -> str:
    """The message for default route.

    Returns:
        str: the message to return
    """
    return "Hello world from the metric service."
