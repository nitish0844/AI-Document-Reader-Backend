from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user
)

from app.core.dependencies import (
    get_db
)

from app.schemas.job_schema import (
    JobCreate,
    JobResponse
)

from app.services.job_service import (
    create_job,
    get_all_jobs,
    get_job_by_id,
    delete_job
)

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)

# CREATE JOB

@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    return create_job(
        db=db,
        payload=payload
    )

# GET ALL JOBS

@router.get(
    "/",
    response_model=list[JobResponse]
)
def fetch_jobs(
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    jobs = get_all_jobs(db)

    return jobs

# GET SINGLE JOB

@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def fetch_single_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    job = get_job_by_id(
        db,
        job_id
    )

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job

# DELETE JOB

@router.delete(
    "/{job_id}"
)
def remove_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    job = get_job_by_id(
        db,
        job_id
    )

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    delete_job(
        db,
        job
    )

    return {
        "message":
        "Job deleted successfully"
    }