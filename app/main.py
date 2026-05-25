from fastapi import FastAPI

from app.api.routes.auth import router as auth_router 
from app.api.routes.resume import (
    router as resume_router
)
from app.api.routes.scan import (
    router as scan_router
)

app = FastAPI()

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(scan_router)

@app.get("/")
async def root():
    return {
        "message": "AI PDF Assistant Backend Running"
    }