import json

from google import genai

from app.core.config import (
    GEMINI_API_KEY
)

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def parse_resume(resume_text: str):

    prompt = f"""
    Extract the following details from this resume.

    Return ONLY valid JSON.

    {{
      "candidate_name": "",
      "current_role": "",
      "years_experience": 0,
      "skills": []
    }}

    Resume:
    {resume_text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text or "{}"

    text = text.replace(
        "```json",
        ""
    ).replace(
        "```",
        ""
    )

    return json.loads(text)