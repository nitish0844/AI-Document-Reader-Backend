from app.core.database import engine
from app.core.database import Base

from app.models.user import User
from app.models.resume import Resume

Base.metadata.create_all(bind=engine)

print("Tables created successfully")