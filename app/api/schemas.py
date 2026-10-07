from uuid import UUID
from pydantic import BaseModel

class IngestAcceptedDocument(BaseModel):
    job_id: UUID
    status: str