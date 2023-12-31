"""Functions for the metric service for computing readability and validate llm response and embedding drift data."""
from typing import Any, Dict, Tuple, Type, Union

import textstat


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
        float: the readability score of the response
    """
    return float(textstat.flesch_reading_ease(llm_response))


def validate_llm_response(llm_response_dict: Dict[str, str]) -> Tuple[str, str]:
    """This function validate the payload which should be a dictionary containing the response text.

    Args:
        llm_response_dict (Dict[str, str]): the post request payload

    Raises:
        TypeError: raise if the json payload is not a dictionary.
        ValueError: raise if the dictionary payload does not have the response item.
        TypeError: raise if the model response received is not a string
        ValueError: raise if the model response received is a empty string

    Returns:
        Tuple[str, str]: the validated response text
    """
    if not isinstance(llm_response_dict, dict):
        raise TypeError("The model response is not a dictionary.")

    response = llm_response_dict.get("response")
    if response is None:
        raise ValueError(
            "The response dictionary does not contain the response key value pair."
        )
    dataset = llm_response_dict.get("dataset")
    if dataset is None:
        raise ValueError(
            "The response dictionary does not contain the dataset key value pair."
        )

    if not isinstance(response, str):
        raise TypeError("The model response is not a string.")
    elif len(response) == 0:
        raise ValueError("The model response must not be an empty string.")

    if not isinstance(dataset, str):
        raise TypeError("The name of the dataset is not a string.")
    elif len(dataset) == 0:
        raise ValueError("The dataset name must not be an empty string.")

    return response, dataset


def validate_data(
    data: Dict[str, Union[str, float, bool]], required_keys_types: Dict[str, Type[Any]]
) -> Dict[str, Union[str, float, bool]]:
    """Validate that the given data dictionary has the required keys and values of correct types.

    Args:
        data (Dict[str, Union[str, float, bool]]): The data dictionary to be validated.
        required_keys_types (Dict[str, Type]): A mapping of expected keys to their types.

    Raises:
        KeyError: Raise if any of the required keys is not found in the dictionary.
        TypeError: Raise if the value associated with any of the keys is of incorrect type.

    Returns:
        Dict[str, Union[str, float, bool]]: The validated data dictionary.
    """
    for key, expected_type in required_keys_types.items():
        if key not in data:
            raise KeyError(f"'{key}' is not found in the data dictionary.")
        if not isinstance(data[key], expected_type):
            raise TypeError(
                f"'{key}' has incorrect type, expected {expected_type.__name__}."
            )

    return data


def validate_user_feedback_data(data: Dict[str, str]) -> Dict[str, str]:
    """Validate that the given user feedback data dictionary has the required keys and values of correct types.

    Args:
        data (Dict[str, str]): a dictionary containing the user feedback data to be validated.

    Raises:
        KeyError: raise if any of the required keys is not found in the dictionary.
        TypeError: raise if the value associated with any of the keys is of incorrect type.

    Returns:
        Dict[str, str]: the validated user feedback data dictionary.
    """
    required_keys_types = {
        "user_rating": str,
        "question": str,
        "full_response": str,
    }

    for key, expected_type in required_keys_types.items():
        if key not in data:
            raise KeyError(f"{key} is not found in the data dictionary.")
        if not isinstance(data[key], expected_type):
            raise TypeError(
                f"'{key}' has incorrect type, expected {expected_type.__name__}."
            )

    return data
