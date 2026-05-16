from google import genai
from sqlalchemy.orm import Session

from app.models.document import DocumentChunk
from app.core.config import GEMINI_API_KEY

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_embedding(text: str):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    if not response.embeddings:
        raise ValueError("No embeddings returned")

    return response.embeddings[0].values

def store_embeddings(
    db: Session,
    chunks,
    filename,
    user_id
):
    try:
        for chunk in chunks:
            embedding = generate_embedding(chunk)
            document = DocumentChunk(
                user_id=user_id,
                file_name=filename,
                chunk_text=chunk,
                embedding=embedding
            )
            db.add(document)
            db.commit()
        return True

    except Exception as e:

        db.rollback()

        print("DB Error:", e)

        raise e