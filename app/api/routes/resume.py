from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)

from typing import Annotated

from pydantic import WithJsonSchema

from typing import List

from sqlalchemy.orm import Session

import fitz

from app.core.dependencies import get_db

from app.auth.dependencies import (
    get_current_user
)

from app.services.resume_service import (
    store_resume
)

router = APIRouter()

MAX_FILES = 20

MAX_FILE_SIZE = 5 * 1024 * 1024

MAX_TEXT_LENGTH = 30000

UploadFileType = Annotated[
    UploadFile,
    WithJsonSchema({
        "type": "string",
        "format": "binary"
    })
]

@router.post("/upload-resumes")
async def upload_resumes(
    files: list[UploadFileType] = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if len(files) > MAX_FILES:

        return {
            "error": f"Maximum {MAX_FILES} resumes allowed"
        }

    user_id = current_user["user_id"]

    uploaded = []

    duplicates = []

    failed = []

    invalid_files = []

    for file in files:

        try:

            if (
                not file.filename or
                not file.filename.endswith(".pdf")
            ):

                invalid_files.append(
                    "Invalid file"
                )

                continue

            content = await file.read()

            if len(content) > MAX_FILE_SIZE:

                failed.append({
                    "file": file.filename,
                    "reason": "File too large"
                })

                continue

            pdf_document = fitz.open(
                stream=content,
                filetype="pdf"
            )

            extracted_text = ""

            for page in pdf_document:

                extracted_text += str(
                    page.get_text()
                )

            pdf_document.close()

            extracted_text = extracted_text.strip()

            if not extracted_text:

                failed.append({
                    "file": file.filename,
                    "reason": "No readable text found"
                })

                continue

            # Prevent extremely large embedding payloads
            extracted_text = extracted_text[
                :MAX_TEXT_LENGTH
            ]

            result = store_resume(
                db,
                user_id,
                extracted_text
            )

            if result["status"] == "duplicate":

                duplicates.append(
                    file.filename
                )

            else:

                uploaded.append({
                    "file": file.filename,
                    "candidate_name": result[
                        "candidate_name"
                    ]
                })

        except Exception as e:

            failed.append({
                "file": file.filename,
                "reason": str(e)
            })

    return {
        "uploaded_count": len(uploaded),
        "duplicate_count": len(duplicates),
        "failed_count": len(failed),
        "uploaded": uploaded,
        "duplicates": duplicates,
        "failed": failed
    }