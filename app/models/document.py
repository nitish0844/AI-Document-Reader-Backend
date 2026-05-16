from sqlalchemy import (
    Column,
    Integer,
    Text,
    String
)

from pgvector.sqlalchemy import Vector

from app.core.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(Integer)

    file_name = Column(String)

    chunk_text = Column(Text)

    embedding = Column(Vector(384))