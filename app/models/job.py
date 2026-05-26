from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from app.core.database import Base

class Job(Base):

    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    experience = Column(
        String,
        nullable=False
    )

    skills = Column(
        ARRAY(String),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )