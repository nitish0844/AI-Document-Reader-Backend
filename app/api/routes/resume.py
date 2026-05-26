from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
    Query
)

from fastapi.responses import (
    FileResponse
)

from sqlalchemy import or_

from typing import Annotated

from pydantic import WithJsonSchema

from sqlalchemy.orm import Session

import fitz
import os
import uuid

from app.core.dependencies import (
    get_db
)

from app.auth.dependencies import (
    get_current_user
)

from app.services.resume_service import (
    store_resume
)

from app.models.job import Job

from app.models.resume import Resume

from app.models.job_application import (
    JobApplication
)

from app.schemas.candidate_schema import (
    CandidateResponse,
    CandidatePaginationResponse,
    CandidateDetailsResponse
)

from app.schemas.candidate_schema import (
    UpdateCandidateStatusRequest
)

router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)

MAX_FILES = 20

MAX_FILE_SIZE = 5 * 1024 * 1024

MAX_TEXT_LENGTH = 30000

UploadFileType = Annotated[
    UploadFile,
    WithJsonSchema({
        "type": "string",
        "format": "binary"
    })
]

# UPLOAD RESUMES

@router.post("/upload/{job_id}")
async def upload_resumes(

    job_id: int,

    files: list[
        UploadFileType
    ] = File(...),

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_user
    )
):

    # Validate Job

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Validate Max Files

    if len(files) > MAX_FILES:

        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_FILES} resumes allowed"
        )

    user_id = current_user[
        "user_id"
    ]

    uploaded = []

    duplicates = []

    failed = []

    for file in files:

        try:

            # Validate PDF

            if (
                not file.filename or
                not file.filename.endswith(".pdf")
            ):

                failed.append({
                    "file": file.filename,
                    "reason":
                    "Invalid PDF file"
                })

                continue

            content = await file.read()

            # Validate Size

            if len(content) > MAX_FILE_SIZE:

                failed.append({
                    "file": file.filename,
                    "reason":
                    "File too large"
                })

                continue

            # SAVE FILE

            os.makedirs(
                "uploads/resumes",
                exist_ok=True
            )

            unique_filename = (
                f"{uuid.uuid4()}.pdf"
            )

            file_path = os.path.join(
                "uploads/resumes",
                unique_filename
            )

            with open(
                file_path,
                "wb"
            ) as buffer:

                buffer.write(content)

            # Extract PDF Text

            pdf_document = fitz.open(
                stream=content,
                filetype="pdf"
            )

            extracted_text = ""

            for page in pdf_document:

                extracted_text += str(
                    page.get_text()
                )

            pdf_document.close()

            extracted_text = (
                extracted_text.strip()
            )

            # Validate Text

            if not extracted_text:

                failed.append({
                    "file": file.filename,
                    "reason":
                    "No readable text found"
                })

                continue

            # Prevent Huge Payloads

            extracted_text = extracted_text[
                :MAX_TEXT_LENGTH
            ]

            # Store Resume

            result = store_resume(

                db=db,

                user_id=user_id,

                job_id=job_id,

                filename=file.filename,

                file_path=file_path,

                resume_text=
                extracted_text
            )

            # Duplicate

            if result["status"] == "duplicate":

                duplicates.append(
                    file.filename
                )

            else:

                uploaded.append({

                    "file":
                    file.filename,

                    "candidate_name":
                    result[
                        "candidate_name"
                    ],

                    "ai_score":
                    result[
                        "ai_score"
                    ]
                })

        except Exception as e:

            failed.append({

                "file":
                file.filename,

                "reason":
                str(e)
            })

    return {

        "job_id":
        job_id,

        "uploaded_count":
        len(uploaded),

        "duplicate_count":
        len(duplicates),

        "failed_count":
        len(failed),

        "uploaded":
        uploaded,

        "duplicates":
        duplicates,

        "failed":
        failed
    }

# GET CANDIDATES BY JOB

@router.get(
    "/job/{job_id}",
    response_model=list[
        CandidateResponse
    ]
)
def get_candidates_by_job(

    job_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_user
    )
):

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    applications = db.query(

        JobApplication,
        Resume

    ).join(

        Resume,

        JobApplication.resume_id ==
        Resume.id

    ).filter(

        JobApplication.job_id ==
        job_id

    ).order_by(

        JobApplication.ai_score.desc()

    ).all()

    results = []

    for application, resume in applications:

        results.append({

            "resume_id":
            resume.id,

            "application_id":
            application.id,

            "job_id":
            application.job_id,

            "candidate_name":
            resume.candidate_name,

            "current_role":
            resume.current_role,

            "years_experience":
            resume.years_experience,

            "skills":
            resume.skills,

            "resume_filename":
            resume.resume_filename,

            "ai_score":
            application.ai_score,

            "status":
            application.status
        })

    return results

# GET ALL CANDIDATES

@router.get(
    "/candidates",
    response_model=
    CandidatePaginationResponse
)
def get_all_candidates(

    page: int = Query(
        1,
        ge=1
    ),

    limit: int = Query(
        10,
        ge=1,
        le=100
    ),

    search: str | None = None,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_user
    )
):

    query = db.query(

        JobApplication,
        Resume

    ).join(

        Resume,

        JobApplication.resume_id ==
        Resume.id
    )

    # SEARCH

    if search:

        query = query.filter(

            or_(

                Resume.candidate_name.ilike(
                    f"%{search}%"
                ),

                Resume.current_role.ilike(
                    f"%{search}%"
                ),

                Resume.skills.ilike(
                    f"%{search}%"
                )
            )
        )

    total = query.count()

    applications = query.order_by(

        JobApplication.created_at.desc()

    ).offset(

        (page - 1) * limit

    ).limit(limit).all()

    results = []

    for application, resume in applications:

        results.append({

            "resume_id":
            resume.id,

            "application_id":
            application.id,

            "job_id":
            application.job_id,

            "candidate_name":
            resume.candidate_name,

            "current_role":
            resume.current_role,

            "years_experience":
            resume.years_experience,

            "skills":
            resume.skills,

            "resume_filename":
            resume.resume_filename,

            "ai_score":
            application.ai_score,

            "status":
            application.status
        })

    return {

        "total":
        total,

        "page":
        page,

        "limit":
        limit,

        "results":
        results
    }

# GET CANDIDATE DETAILS

@router.get(
    "/application/{application_id}",
    response_model=
    CandidateDetailsResponse
)
def get_candidate_details(

    application_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_user
    )
):

    result = db.query(

        JobApplication,
        Resume

    ).join(

        Resume,

        JobApplication.resume_id ==
        Resume.id

    ).filter(

        JobApplication.id ==
        application_id

    ).first()

    if not result:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    application, resume = result

    return {

        "application_id":
        application.id,

        "resume_id":
        resume.id,

        "job_id":
        application.job_id,

        "candidate_name":
        resume.candidate_name,

        "current_role":
        resume.current_role,

        "years_experience":
        resume.years_experience,

        "skills":
        resume.skills,

        "resume_filename":
        resume.resume_filename,

        "resume_text":
        resume.resume_text,

        "ai_score":
        application.ai_score,

        "status":
        application.status
    }

# DOWNLOAD RESUME

@router.get(
    "/download/{resume_id}"
)
def download_resume(

    resume_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_user
    )
):

    resume = db.query(
        Resume
    ).filter(
        Resume.id == resume_id
    ).first()

    if not resume:

        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    if not resume.resume_path:

        raise HTTPException(
            status_code=404,
            detail="Resume file missing"
        )

    return FileResponse(

        path=resume.resume_path,

        filename=str(
            resume.resume_filename
        ),

        media_type=
        "application/pdf"
    )

@router.patch(
    "/application/{application_id}/status"
)
def update_candidate_status(

    application_id: int,

    payload:
    UpdateCandidateStatusRequest,

    db: Session = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_user
    )
):

    application = db.query(
        JobApplication
    ).filter(
        JobApplication.id ==
        application_id
    ).first()

    if not application:

        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    allowed_statuses = [
        "applied",
        "shortlisted",
        "interviewed",
        "rejected",
        "hired"
    ]

    if payload.status not in (
        allowed_statuses
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    setattr(
        application,
        "status",
        payload.status
    )

    db.commit()

    return {

        "message":
        "Candidate status updated",

        "status":
        application.status
    }