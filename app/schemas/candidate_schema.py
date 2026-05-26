from pydantic import BaseModel

class CandidateResponse(BaseModel):
    resume_id: int
    application_id: int
    job_id: int
    candidate_name: str | None
    current_role: str | None
    years_experience: int | None
    resume_filename: str | None
    skills: str | None
    ai_score: int
    status: str
    class Config:
        from_attributes = True

class CandidateDetailsResponse(
    BaseModel
):
    application_id: int
    resume_id: int
    job_id: int
    candidate_name: str | None
    current_role: str | None
    years_experience: int | None
    skills: str | None
    resume_filename: str | None
    resume_text: str | None
    ai_score: int
    status: str
    class Config:
        from_attributes = True

class CandidatePaginationResponse(
    BaseModel
):
    total: int
    page: int
    limit: int
    results: list[
        CandidateResponse
    ]

class UpdateCandidateStatusRequest(
    BaseModel
):

    status: str