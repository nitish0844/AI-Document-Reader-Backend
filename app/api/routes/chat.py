from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_db

from app.services.embedding_service import (
    generate_embedding
)
from app.services.search_service import (
    search_similar_chunks
)
from app.services.rag_service import generate_answer
from app.auth.dependencies import (
    get_current_user
)
router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask_question(
    data: QuestionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    
    user_id = current_user["user_id"]

    if not user_id:
        return {
            "error": "User not authenticated"
        }

    # Convert question to embedding
    question_embedding = generate_embedding(
        data.question
    )

    # Search PostgreSQL
    documents = search_similar_chunks(
        db,
        question_embedding,
        user_id
    )

    if not documents:
        return {
            "error": "No relevant documents found"
        }

    # Merge chunks into context
    context = "\n\n".join(documents)

    # Generate AI answer
    answer = generate_answer(
        data.question,
        context
    )

    return {
        "question": data.question,
        "answer": answer
    }