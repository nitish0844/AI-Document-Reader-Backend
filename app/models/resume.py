from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float
)

from sqlalchemy import ForeignKey

from pgvector.sqlalchemy import Vector

from app.core.database import Base


class Resume(Base):

    __tablename__ = "resumes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(Integer)

    candidate_name = Column(String)

    current_role = Column(String)

    years_experience = Column(Float)

    skills = Column(Text)

    resume_text = Column(Text)

    resume_hash = Column(
        String,
        unique=True
    )

    embedding = Column(Vector(3072))

    resume_filename = Column(
        String,
        nullable=True
    )