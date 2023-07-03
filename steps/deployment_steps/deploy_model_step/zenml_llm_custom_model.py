# Derived from ZenML Seldon Integration; source : https://github.com/zenml-io/zenml/blob/main/src/zenml/integrations/seldon/custom_deployer/zenml_custom_model.py
"""Place holder."""
from zenml.logger import get_logger
from zenml.utils import source_utils

logger = get_logger(__name__)


class ZenMLCustomLLMModel:
    """_summary_."""

    def __init__(
        self,
        model_uri: str,
        model_name: str,
        tokenizer_uri: str,
        predict_func: str,
    ):
        """_summary_.

        Args:
            model_uri (str): _description_
            model_name (str): _description_
            tokenizer_uri (str): _description_
            predict_func (str): _description_
        """
        self.name = model_name
        self.model_uri = model_uri
        self.tokenizer_uri = tokenizer_uri
        self.predict_func = source_utils.load(predict_func)
        self.model = None
        self.tokenizer = None
        self.ready = False
