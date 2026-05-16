from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DATABASE_URL = os.getenv("DATABASE_URL")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY is not set")

# TYPE SAFE CASTS
DATABASE_URL = str(DATABASE_URL)

JWT_SECRET_KEY = str(JWT_SECRET_KEY)