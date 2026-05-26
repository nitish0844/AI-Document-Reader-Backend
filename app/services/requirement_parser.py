import json

from google import genai

from app.core.config import (
    GEMINI_API_KEY
)

client = genai.Client(
    api_key=GEMINI_API_KEY
)

def parse_requirement(
    requirement: str
):

    prompt = f"""
    Extract hiring requirements.

    Return ONLY valid JSON.

    {{
      "skills": [],
      "minimum_years_experience": 0
    }}

    Requirement:
    {requirement}
    """

    try:

        response = (
            client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
        )

        text = response.text or "{}"

        text = text.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        parsed = json.loads(text)

        return {
            "skills":
            parsed.get("skills", []),

            "minimum_years_experience":
            parsed.get(
                "minimum_years_experience",
                0
            )
        }

    except Exception:

        return {
            "skills": [],
            "minimum_years_experience": 0
        }