"""The metric service interface for computing readability and handling post and get requests."""
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
    if not isinstance(llm_response, str):
        raise TypeError("The model response is not a string.")
    elif len(llm_response) <= 0:
        raise ValueError("The model response must not be an empty string.")
    else:
        return float(textstat.flesch_reading_ease(llm_response))
