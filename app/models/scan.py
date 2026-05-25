from pydantic import BaseModel

class ScanRequest(BaseModel):

    requirement: str