from __future__ import annotations
import shutil
from pathlib import Path
from uuid import uuid4, UUID
from fastapi import APIRouter, Depends, File, UploadFile, status, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import IngestAcceptedDocument, JobStatus
from app.api.deps import get_embedder
from app.embeddings.types import Embedder
from app.db.models import IngestionJob
from app.db.session import get_db_session
from app.ingestion.worker import run_ingestion_job

router = APIRouter(prefix="/api/v1", tags=["documents"])
UPLOAD_DIR = Path("corpus/uploads")

# provides current status of the job
@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: UUID, session: AsyncSession = Depends(get_db_session)) -> JobStatus:
    job = await session.get(IngestionJob, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No job with id {job_id}",
        )
    return JobStatus(job_id=job.id, status=job.status, document_id=job.document_id, error=job.error)

# handles async document uploads by saving files to disk and lining up BG ingestion jobs
@router.post("/documents", response_model=IngestAcceptedDocument, status_code=status.HTTP_202_ACCEPTED)
async def ingest_document_endpoint(background: BackgroundTasks, file: UploadFile = File(...), session: AsyncSession = Depends(get_db_session), embedder: Embedder = Depends(get_embedder)) -> IngestAcceptedDocument:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename or "upload.md").name
    dest = UPLOAD_DIR / f"{uuid4().hex}-{safe_name}"
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    job = IngestionJob(status="queued", progress={"source": dest.name})
    session.add(job)
    await session.commit()

    background.add_task(run_ingestion_job, job.id, dest.name, embedder)
    
    return IngestAcceptedDocument(job_id=job.id, status=job.status)