from fastapi import FastAPI

from app.api.routes.auth import router as auth_router 
from app.api.routes.resume import (
    router as resume_router
)
from app.api.routes.scan import (
    router as scan_router
)
from app.api.routes.jobs import (
    router as jobs_router
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(scan_router)
app.include_router(jobs_router)

@app.get("/")
async def root():
    return {
        "message": "AI PDF Assistant Backend Running"
    }