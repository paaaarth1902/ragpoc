from uuid import UUID
from pydantic import BaseModel, Field

class IngestAcceptedDocument(BaseModel):
    job_id: UUID
    status: str

class JobStatus(BaseModel):
    job_id: UUID
    status: str
    document_id: UUID | None = None # queued running job wont have doc_id or
    error: str | None = None # this

class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    k: int = Field(default=5, ge=1, le=20)

class CitationOut(BaseModel):
    label: int
    chunk_id: int
    document_id: UUID

class QueryResponse(BaseModel):
    answer: str
    citations: list[CitationOut]