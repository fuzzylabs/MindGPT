"""NeMo guardrails."""
import json
import logging
from typing import Any, List, Optional, Sequence

from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import Callbacks
from langchain.schema import BaseMessage, PromptValue, LLMResult
from langchain.schema.runnable import Input, RunnableConfig, Output
from nemoguardrails.llm.providers import register_llm_provider
import streamlit as st

from app_utils.llm import MessagesType, _create_payload, _get_predictions, clean_fastchat_t5_output, \
    get_prediction_endpoint


class MindGPTLLM(BaseLanguageModel):
    """MindGPT LLM wrapper for NeMo."""

    def generate_prompt(self, prompts: List[PromptValue], stop: Optional[List[str]] = None, callbacks: Callbacks = None,
                        **kwargs: Any) -> LLMResult:
        pass

    async def agenerate_prompt(self, prompts: List[PromptValue], stop: Optional[List[str]] = None,
                               callbacks: Callbacks = None, **kwargs: Any) -> LLMResult:
        text = prompts[0].to_string()
        prediction = _get_predictions(get_prediction_endpoint(), text)


    def predict_messages(self, messages: List[BaseMessage], *, stop: Optional[Sequence[str]] = None,
                         **kwargs: Any) -> BaseMessage:
        pass

    async def apredict(self, text: str, *, stop: Optional[Sequence[str]] = None, **kwargs: Any) -> str:
        pass

    async def apredict_messages(self, messages: List[BaseMessage], *, stop: Optional[Sequence[str]] = None,
                                **kwargs: Any) -> BaseMessage:
        pass

    def invoke(self, input: Input, config: Optional[RunnableConfig] = None) -> Output:
        pass

    def predict(self, text: str, *, stop: Optional[Sequence[str]] = None, **kwargs: Any) -> str:
        return _get_predictions(get_prediction_endpoint(), text)


register_llm_provider("mind_gpt", MindGPTLLM)

colang = """
define flow
  user ask about household survey data
  bot response about household survey data

define user ask about household survey data
  "How many long term unemployment individuals were reported?"
  "What's the number of part-time employed number?"
"""

config = """
models:
  - type: main
    engine: mind_gpt
"""


def get_rails():
    """"""
    from nemoguardrails import RailsConfig, LLMRails

    rails_config = RailsConfig.from_content(colang, config)
    rails = LLMRails(rails_config)
    return rails


def query_nemo_llm(
        rails: Any,
        messages: MessagesType,
        temperature: float,
        max_length: int,
) -> str:
    """Query endpoint to fetch the summary.

    Args:
        prediction_endpoint (str): Prediction endpoint.
        messages (MessagesType): Dict of message containing prompt and context.
        temperature (float): inference temperature
        max_length (int): max response length in tokens

    Returns:
        str: Summarised text.
    """
    with st.spinner("Loading response..."):
        payload = _create_payload(messages, temperature, max_length)
        logging.info(f"Payload:\n{payload}")
        summary_txt = rails.generate(messages=[{
            "role": "user",
            "content": json.dumps(payload)
        }])
        summary_txt = clean_fastchat_t5_output(summary_txt)
        logging.info(f"LLM Response:\n{summary_txt}")

    return summary_txt
