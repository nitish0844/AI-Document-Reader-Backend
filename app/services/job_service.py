from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job_schema import (
    JobCreate
)

def create_job(
    db: Session,
    payload: JobCreate
):
    new_job = Job(
        title=payload.title,
        experience=payload.experience,
        skills=payload.skills,
        description=payload.description
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

def get_all_jobs(
    db: Session
):
    return db.query(Job).order_by(
        Job.id.desc()
    ).all()

def get_job_by_id(
    db: Session,
    job_id: int
):
    return db.query(Job).filter(
        Job.id == job_id
    ).first()

def delete_job(
    db: Session,
    job: Job
):
    db.delete(job)
    db.commit()