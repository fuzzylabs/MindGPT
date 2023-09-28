import openai
import guardrails as gd
from pydantic import BaseModel, Field

guardrails_prompt = """
Given the users question, determine its topic, and decide whether it's on topic of mental health or not.

User asked: ${user_question}

${gr.json_suffix_without_examples}
"""

class OffTopicModel(BaseModel):
    topic: str = Field(description="Topic of the question")
    is_mental_health: bool = Field(description="Is the question related to mental health? Set, False, if and only if the question is related to something other than mental health, such as sports, politics or weather.")


guard = gd.Guard.from_pydantic(output_class=OffTopicModel, prompt=guardrails_prompt)

def check_guard(input_text: str) -> OffTopicModel:
    return guard(
        openai.Completion.create,
        engine="text-davinci-003",
        prompt_params={
            "user_question": input_text
        },
        temperature=0.3,
        max_tokens=1024
    )[1]


# def query_llm(input_text: str) -> str: