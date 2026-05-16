from fastapi import FastAPI

from app.api.routes.upload import router as upload_router
from app.api.routes.chat import router as chat_router
from app.api.routes.auth import router as auth_router 

app = FastAPI()

app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {
        "message": "AI PDF Assistant Backend Running"
    }