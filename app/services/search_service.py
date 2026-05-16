from sqlalchemy import text
from sqlalchemy.orm import Session


def search_similar_chunks(
    db: Session,
    question_embedding,
    user_id,
    limit=3
):

    query = text("""
        SELECT chunk_text
        FROM document_chunks
        WHERE user_id = :user_id
        ORDER BY embedding <-> :embedding
        LIMIT :limit
    """)

    results = db.execute(
        query,
        {
            "embedding": str(question_embedding),
            "limit": limit,
            "user_id": user_id
        }
    )

    return [row[0] for row in results]