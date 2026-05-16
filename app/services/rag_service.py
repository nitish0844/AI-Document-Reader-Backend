from google import genai

from app.core.config import GEMINI_API_KEY

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_answer(question, context):

    prompt = f"""
    You are an AI PDF assistant.

    Answer the user's question ONLY from the provided context.

    Context:
    {context}

    Question:
    {question}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text