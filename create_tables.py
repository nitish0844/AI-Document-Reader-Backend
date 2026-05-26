from app.core.database import engine
from app.core.database import Base

from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.models.job_application import JobApplication

Base.metadata.create_all(bind=engine)

print("Tables created successfully")