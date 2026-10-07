from __future__ import annotations
import shutil
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, UploadFile, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import IngestAcceptedDocument
from app.db.models import IngestionJob
from app.db.session import get_db_session
from app.ingestion.worker import run_ingestion_job

router = APIRouter(prefix="/api/v1", tags=["documents"])

UPLOAD_DIR = Path("corpus/uploads")

# handles async document uploads by saving files to disk and lining up BG ingestion jobs
@router.post("/documents", response_model=IngestAcceptedDocument, status_code=status.HTTP_202_ACCEPTED)
async def ingest_document_endpoint(background: BackgroundTasks, file: UploadFile = File(...), session: AsyncSession = Depends(get_db_session)) -> IngestAcceptedDocument:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename or "upload.md").name
    dest = UPLOAD_DIR / f"{uuid4().hex}-{safe_name}"
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    job = IngestionJob(status="queued", progress={"source": dest.name})
    session.add(job)
    await session.commit()

    background.add_task(run_ingestion_job, job.id, dest.name)
    
    return IngestAcceptedDocument(job_id=job.id, status=job.status)