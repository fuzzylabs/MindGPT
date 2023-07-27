"""The metric service interface for computing readability and handling post and get requests."""
import textstat


def compute_readability(llm_response: str) -> float:
    """This function compute a readability score using the Flesch–Kincaid readability tests.

    Args:
        llm_response (str): the model's response post by Streamlit

    Raises:
        TypeError: raise if the model response received is not a string
        ValueError: raise if the model response received is a empty string

    Returns:
        float: the readability score of the response
    """
    if not isinstance(llm_response, str):
        raise TypeError("The model response is not a string.")
    elif len(llm_response) <= 0:
        raise ValueError("The model response must not be an empty string.")
    else:
        return float(textstat.flesch_reading_ease(llm_response))
