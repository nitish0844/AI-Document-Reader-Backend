from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from app.models.document import DocumentChunk

# Load embedding model
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def store_embeddings(
    db: Session,
    chunks,
    filename,
    user_id
):

    for chunk in chunks:

        # Generate embedding
        embedding = model.encode(
            chunk
        ).tolist()

        # Create DB object
        document = DocumentChunk(
            user_id=user_id,
            file_name=filename,
            chunk_text=chunk,
            embedding=embedding
        )

        db.add(document)

    db.commit()

    return True