from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_db

from app.models.user import User

from app.auth.password import (
    hash_password,
    verify_password
)

from app.auth.jwt_handler import (
    create_access_token
)

router = APIRouter()

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
async def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        return {
            "error": "User already exists"
        }

    hashed_password = hash_password(
        data.password
    )

    user = User(
        email=data.email,
        password=hashed_password
    )

    db.add(user)

    db.commit()

    return {
        "message": "User registered successfully"
    }

@router.post("/login")
async def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:
        return {
            "error": "Invalid credentials"
        }

    is_valid = verify_password(
        data.password,
        str(user.password)
    )

    if not is_valid:
        return {
            "error": "Invalid credentials"
        }

    access_token = create_access_token({
        "user_id": user.id
    })

    return {
        "access_token": access_token
    }