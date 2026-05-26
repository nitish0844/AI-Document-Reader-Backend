from pydantic import BaseModel

from typing import Optional

class JobCreate(BaseModel):
    title: str
    experience: str
    skills: list[str]
    description: Optional[str] = None

class JobResponse(JobCreate):
    id: int
    class Config:
        from_attributes = True