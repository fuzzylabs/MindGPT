# Derived from ZenML example custom code deployment; source : https://github.com/zenml-io/zenml/blob/release/0.40.3/examples/custom_code_deployment/seldon_pytorch/steps/pytorch_custom_deploy_code.py
"""Custom Prediction function for LLM models."""
from typing import Any, Dict, List, Union

import numpy as np

Array_Like = Union[np.ndarray, List[Any], str, bytes, Dict[str, Any]]


def custom_predict(
    model: Any,
    tokenizer: Any,
    request: Array_Like,
) -> Array_Like:
    """Custom Prediction function.

    Request input is in the format: [{"text": "What is depression?"}]
    where each dictionary is a question to be answered.

    The custom predict function is the core of the custom deployment, the function
    is called by the custom deployment class defined for the serving tool.
    The current implementation requires the function to get the model loaded in the memory and
    a request with the data to predict.

    Args:
        model (Any): The model to use for prediction.
        tokenizer (Any): The tokenizer to use for prediction.
        request (Array_Like): The request response is an array-like format.

    Returns:
        Array_Like: The prediction in an array-like format.
                    (e.g: np.ndarray, List[Any], str, bytes, Dict[str, Any])
    """
    inputs = []
    for instance in request:
        text = instance["text"]
        inp = tokenizer(text, return_tensors="pt").input_ids
        outputs = model.generate(
            inp,
            max_length=300,
            min_length=30,
            length_penalty=2.0,
            num_beams=4,
            no_repeat_ngram_size=3,
            early_stopping=True,
        )
        pred = tokenizer.decode(outputs[0], skip_special_tokens=True)
        inputs.append(pred)

    return inputs
