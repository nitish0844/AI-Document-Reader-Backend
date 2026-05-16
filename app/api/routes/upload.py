from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)
from app.auth.dependencies import (
    get_current_user
)
from sqlalchemy.orm import Session
import os
import fitz

from app.core.dependencies import get_db

from app.services.embedding_service import (
    store_embeddings
)

from app.services.pdf_service import (
    chunk_text
)

router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    
    user_id = current_user["user_id"]

    if not user_id:
        return {
            "error": "User not authenticated"
        }

    if not file.filename or not file.filename.endswith(".pdf"):
        return {
            "error": "Only PDF files are allowed"
        }

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    # Save PDF
    with open(file_path, "wb") as pdf_file:
        content = await file.read()
        pdf_file.write(content)

    # Extract text
    extracted_text = ""

    pdf_document = fitz.open(file_path)

    for page in pdf_document:
        extracted_text += str(page.get_text("text"))

    pdf_document.close()

    print("Creating chunks...")

    # Create chunks
    chunks = chunk_text(extracted_text)

    # Store embeddings in PostgreSQL
    store_embeddings(
        db,
        chunks,
        file.filename,
        user_id
    )

    print("Chunks created")

    return {
        "filename": file.filename,
        "total_chunks": len(chunks),
        "message": "Embeddings stored successfully"
    }