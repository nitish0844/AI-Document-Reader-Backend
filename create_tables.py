from app.core.database import engine
from app.core.database import Base

from app.models.document import DocumentChunk
from app.models.user import User

Base.metadata.create_all(bind=engine)

print("Tables created successfully")