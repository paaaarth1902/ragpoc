from uuid import UUID
from pydantic import BaseModel

class IngestAcceptedDocument(BaseModel):
    job_id: UUID
    status: str

class JobStatus(BaseModel):
    job_id: UUID
    status: str
    document_id: UUID | None = None # queued running job wont have doc_id or
    error: str | None = None # this

