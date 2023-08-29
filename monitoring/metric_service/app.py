"""A metric service interface for computing readability and handling post and get requests."""
import logging
from typing import Any, List, Tuple

from flask import Flask, Response, jsonify, request
from metric_service import (
    compute_readability,
    validate_data,
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

    required_keys_types = {
        "reference_dataset": str,
        "current_dataset": str,
        "distance": float,
        "drifted": bool,
        "dataset": str,
    }

    try:
        validated_data = validate_data(embedding_drift_data_dict, required_keys_types)
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


@app.route("/user_feedback", methods=["POST"])
def user_feedback() -> Response:
    """Receives and validates the user feedback data from a POST request, and then inserts it into the database if it's valid.

    Returns:
        Response: a tuple containing a success and the HTTP status code.
    """
    user_feedback_data_dict = request.get_json()

    required_keys_types = {
        "user_rating": str,
        "question": str,
        "full_response": str,
    }

    try:
        validated_data = validate_data(user_feedback_data_dict, required_keys_types)
        db_interface.insert_user_feedback_data(validated_data)
    except Exception as e:
        return jsonify({"status_code": 400, "message": f"Validation error: {str(e)}"})

    return jsonify(
        {
            "status_code": 200,
            "data": validated_data,
            "message": "User feedback data has been successfully inserted.",
        }
    )


@app.route("/readability_threshold", methods=["POST"])
def readability_threshold() -> Response:
    """Receives and validates the readability scores threshold data from a POST request, and then inserts it into the database if it's valid.

    Returns:
        Response: a tuple containing a success and the HTTP status code.
    """
    readability_data_dict = request.get_json()

    required_keys_types = {
        "readability_score": float,
        "question": str,
        "response": str,
        "dataset": str,
    }

    try:
        validated_data = validate_data(readability_data_dict, required_keys_types)
        db_interface.insert_readability_threshold_data(validated_data)
    except Exception as e:
        return jsonify({"status_code": 400, "message": f"Validation error: {str(e)}"})

    return jsonify(
        {
            "status_code": 200,
            "data": validated_data,
            "message": "Readability threshold data has been successfully inserted.",
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


@app.route("/query_user_feedback", methods=["GET"])
def query_user_feedback() -> List[Tuple[Any, ...]]:
    """This function queries the "user_feedback" relation using the db_interface's query_relation method and returns the results as a list of tuple.

    Returns:
        List[Tuple[Any, ...]]: the query result
    """
    return db_interface.query_relation(relation_name="user_feedback")


@app.route("/query_readability_threshold", methods=["GET"])
def query_readability_threshold() -> List[Tuple[Any, ...]]:
    """This function queries the "readability_threshold" relation using the db_interface's query_relation method and returns the results as a list of tuple.

    Returns:
        List[Tuple[Any, ...]]: the query result
    """
    return db_interface.query_relation(relation_name="readability_threshold")


@app.route("/")
def hello() -> str:
    """The message for default route.

    Returns:
        str: the message to return
    """
    return "Hello world from the metric service."
