from google import genai
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.core.config import GEMINI_API_KEY

from app.utils.hash import (
    generate_resume_hash
)
from app.services.parser_service import (
    parse_resume
)

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_embedding(text: str):

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    if not response.embeddings:
        raise ValueError(
            "No embeddings returned"
        )

    return response.embeddings[0].values


def extract_candidate_name(text: str):

    first_line = text.split("\n")[0]

    return first_line[:100]


def store_resume(
    db: Session,
    user_id: int,
    resume_text: str
):
    
    parsed_data = parse_resume(
        resume_text
    )

    resume_hash = generate_resume_hash(
        resume_text
    )

    existing_resume = db.query(Resume).filter(
        Resume.user_id == user_id,
        Resume.resume_hash == resume_hash
    ).first()

    if existing_resume:

        return {
            "status": "duplicate"
        }

    embedding = generate_embedding(
        resume_text
    )

    candidate_name = extract_candidate_name(
        resume_text
    )

    resume = Resume(
        user_id=user_id,
        candidate_name=parsed_data.get(
            "candidate_name"
        ),
        current_role=parsed_data.get(
            "current_role"
        ),
        years_experience=parsed_data.get(
            "years_experience"
        ),
        skills=", ".join(
            parsed_data.get("skills", [])
        ),
        resume_text=resume_text,
        resume_hash=resume_hash,
        embedding=embedding
    )

    db.add(resume)

    db.commit()

    return {
        "status": "uploaded",
        "candidate_name": candidate_name
    }