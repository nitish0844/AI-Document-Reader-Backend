from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    DateTime
)
from sqlalchemy.sql import func
from app.core.database import Base

class JobApplication(Base):
    __tablename__ = "job_applications"
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False
    )
    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=False
    )
    ai_score = Column(
        Integer,
        default=0
    )
    status = Column(
        String,
        default="applied"
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )