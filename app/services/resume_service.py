from google import genai

from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.job import Job
from app.models.job_application import (
    JobApplication
)

from app.core.config import (
    GEMINI_API_KEY
)

from app.utils.hash import (
    generate_resume_hash
)

from app.services.parser_service import (
    parse_resume
)

from app.services.scoring_service import (
    calculate_ai_score
)

client = genai.Client(
    api_key=GEMINI_API_KEY
)

def generate_embedding(
    text: str
):

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    if not response.embeddings:

        raise ValueError(
            "No embeddings returned"
        )

    return response.embeddings[0].values


def extract_candidate_name(
    text: str
):

    first_line = text.split("\n")[0]

    return first_line[:100]


def store_resume(
    db: Session,
    user_id: int,
    job_id: int,
    filename: str,
    file_path: str,
    resume_text: str
):

    # Fetch Job

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:

        raise ValueError(
            "Job not found"
        )

    # Parse Resume

    parsed_data = parse_resume(
        resume_text
    )

    # Generate Resume Hash

    resume_hash = generate_resume_hash(
        resume_text
    )

    # Candidate Skills

    candidate_skills = parsed_data.get(
        "skills",
        []
    )

    # Candidate Experience

    candidate_experience = (
        parsed_data.get(
            "years_experience",
            0
        )
    )

    # Requirement Text

    requirement_text = str(
        job.description or ""
    )

    # Calculate AI Score

    ai_score = calculate_ai_score(

        candidate_skills=
        candidate_skills,

        candidate_experience=
        candidate_experience,

        requirement_text=
        requirement_text
    )

    # Check Existing Resume

    existing_resume = db.query(
        Resume
    ).filter(
        Resume.resume_hash ==
        resume_hash
    ).first()

    # Resume Already Exists

    if existing_resume:

        resume = existing_resume

    # Create New Resume

    else:

        embedding = generate_embedding(
            resume_text
        )

        candidate_name = (
            extract_candidate_name(
                resume_text
            )
        )

        resume = Resume(

            user_id=user_id,

            candidate_name=parsed_data.get(
                "candidate_name"
            ),

            current_role=parsed_data.get(
                "current_role"
            ),

            years_experience=
            candidate_experience,

            skills=", ".join(
                candidate_skills
            ),

            resume_filename=filename,

            resume_text=resume_text,

            resume_hash=resume_hash,

            embedding=embedding
        )

        db.add(resume)

        db.commit()

        db.refresh(resume)

    # Check Existing Application

    existing_application = db.query(
        JobApplication
    ).filter(
        JobApplication.job_id ==
        job_id,

        JobApplication.resume_id ==
        resume.id
    ).first()

    if existing_application:

        return {
            "status": "duplicate"
        }

    # Create Application

    application = JobApplication(

        job_id=job_id,

        resume_id=resume.id,

        ai_score=ai_score
    )

    db.add(application)

    db.commit()

    return {

        "status": "uploaded",

        "candidate_name":
        resume.candidate_name,

        "ai_score":
        ai_score
    }