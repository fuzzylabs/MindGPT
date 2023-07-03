# Derived from ZenML Seldon Integration; source : https://github.com/zenml-io/zenml/blob/main/src/zenml/integrations/seldon/custom_deployer/zenml_custom_model.py
"""Place holder."""
import os
import subprocess
from typing import Any, Dict, List, Optional, Union

import click
import numpy as np
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from zenml.logger import get_logger
from zenml.utils import source_utils

logger = get_logger(__name__)

DEFAULT_MODEL_NAME = "model"
DEFAULT_LOCAL_MODEL_DIR = "/mnt/models"

DEFAULT_PT_MODEL_DIR = "hf_pt_model"  # This is the default dir that the pt model materializer look into. See https://github.com/zenml-io/zenml/blob/main/src/zenml/integrations/huggingface/materializers/huggingface_pt_model_materializer.py
DEFAULT_TOKENIZER_DIR = "hf_tokenizer"

Array_Like = Union[np.ndarray, List[Any], str, bytes, Dict[str, Any]]


class ZenMLCustomLLMModel:
    """_summary_."""

    def __init__(
        self,
        model_uri: str,
        tokenizer_uri: str,
        model_name: str,
        predict_func: str,
    ):
        """Initializes a ZenMLCustomModel object.

        Args:
            model_uri (str): The URI of the model.
            tokenizer_uri (str): The URI of tokenizer.
            model_name (str): The name of the model.
            predict_func (str): The predict function of the model.
        """
        self.name = model_name
        self.model_uri = model_uri
        self.tokenizer_uri = tokenizer_uri
        self.predict_func = source_utils.load(predict_func)
        self.model = None
        self.tokenizer = None
        self.ready = False

    def load(self) -> bool:
        """Load the model.

        This function loads the model into memory and sets the ready flag to True.
        The model is loaded using the materializer, by saving the information of
        the artifact to a file at the preparing time and loading it again at the
        prediction time by the materializer.

        Returns:
            bool: True if the model was loaded successfully, False otherwise.
        """
        try:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                os.path.join(self.model_uri, DEFAULT_PT_MODEL_DIR)
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                os.path.join(self.tokenizer_uri, DEFAULT_TOKENIZER_DIR)
            )
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
        self.ready = True
        return self.ready

    def predict(
        self,
        X: Array_Like,  # noqa: N803
        features_names: Optional[List[str]],
        **kwargs: Any,
    ) -> Array_Like:
        """Predict the given request.

        The main predict function of the model. This function is called by the
        Seldon Core server when a request is received. Then inside this function,
        the user-defined predict function is called.

        Args:
            X: The request to predict in a dictionary.
            features_names: The names of the features.
            **kwargs: Additional arguments.

        Returns:
            The prediction dictionary.

        Raises:
            Exception: If function could not be called.
            NotImplementedError: If the model is not ready.
            TypeError: If the request is not a dictionary.
        """
        if self.predict_func is not None:
            try:
                prediction = {"predictions": self.predict_func(self.model, X)}
            except Exception as e:
                raise Exception(f"Failed to predict: {e}")
            if isinstance(prediction, dict):
                return prediction
            else:
                raise TypeError(
                    f"Prediction is not a dictionary. Expected dict type but got {type(prediction)}"
                )
        else:
            raise NotImplementedError("Predict function is not implemented")


@click.command()
@click.option(
    "--model_uri",
    default=DEFAULT_LOCAL_MODEL_DIR,
    type=click.STRING,
    help="The directory where the model is stored locally.",
)
@click.option(
    "--tokenizer_uri",
    default=DEFAULT_LOCAL_MODEL_DIR,
    type=click.STRING,
    help="The directory where the model is stored locally.",
)
@click.option(
    "--model_name",
    default=DEFAULT_MODEL_NAME,
    required=True,
    type=click.STRING,
    help="The name of the model to deploy.",
)
@click.option(
    "--predict_func",
    required=True,
    type=click.STRING,
    help="The path to the custom predict function defined by the user.",
)
def main(
    model_name: str, model_uri: str, tokenizer_uri: str, predict_func: str
) -> None:
    """Main function for the custom model.

    Within the deployment process, the built-in custom deployment step is used to
    to prepare the Seldon Core deployment with an entry point that calls this script,
    which then starts a subprocess to start the Seldon server and waits for requests.
    The following is an example of the entry point:
    ```
    entrypoint_command = [
        "python",
        "-m",
        "zenml.integrations.seldon.custom_deployer.zenml_custom_model",
        "--model_name",
        config.service_config.model_name,
        "--predict_func",
        config.custom_deploy_parameters.predict_function,
    ]
    ```
    Args:
        model_name: The name of the model.
        model_uri: The URI of the model.
        tokenizer_uri: The URI of tokenizer.
        predict_func: The path to the predict function.
    """
    command = [
        "seldon-core-microservice",
        "steps.zenml_llm_custom_model.ZenMLCustomLLMModel",
        "--service-type",
        "MODEL",
        "--parameters",
        (
            f'[{{"name":"model_uri","value":"{model_uri}","type":"STRING"}},'
            f'{{"name":"tokenizer_uri","value":"{tokenizer_uri}","type":"STRING"}},'
            f'{{"name":"model_name","value":"{model_name}","type":"STRING"}},'
            f'{{"name":"predict_func","value":"{predict_func}","type":"STRING"}}]'
        ),
    ]
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as ProcessError:  # noqa: N806
        logger.error(
            f"Failed to start the seldon-core-microservice process. {ProcessError}"
        )
        return


if __name__ == "__main__":
    main()
