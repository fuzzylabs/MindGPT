"""Prompt templates, and default context."""
# Paragraph from https://www.nhs.uk/mental-health/conditions/depression-in-adults/overview/
DEFAULT_CONTEXT = """Most people experience feelings of stress, anxiety or low mood during difficult times.
A low mood may improve after a short period of time, rather than being a sign of depression."""

DEFAULT_QUERY_INSTRUCTION = (
    "Represent the question for retrieving supporting documents: "
)

# Prompt Templates
PROMPT_TEMPLATES = {
    "simple": "Context: {context}\n\nQuestion: {question}\n\n",
    "complex": """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use three sentences maximum and keep the answer as concise as possible.
Always say "thanks for asking!" at the end of the answer.
{context}
Question: {question}
Helpful Answer:""",
    "advanced": """You are a highly skilled AI trained in language comprehension and summarisation.
I would like you to read the following text and summarise it into a concise abstract paragraph. Use the following pieces of context to answer the question at the end.
Aim to retain the most important points, providing a coherent and readable summary that could help a person understand the main points of the discussion without needing to read the entire text.
Please avoid unnecessary details or tangential points.
{context}
Question: {question}
Helpful Answer:""",
    "conversational": """Use the conversation history and context provided to inform your response.

Start of conversation history
{history}
End of conversation history

Context: {context}

Question: {question}
""",
}
