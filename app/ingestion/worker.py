from __future__ import annotations
from pathlib import Path
from uuid import UUID
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import get_settings
from app.db.models import IngestionJob
# from app.embeddings.openai import OpenAIEmbedder
# from app.embeddings.retry import RetryingEmbedder
from app.embeddings.types import Embedder
from app.ingestion.seed import seed_document

UPLOAD_DIR = Path("corpus/uploads")

async def run_ingestion_job(job_id: UUID, stored_filename: str, embedder: Embedder) -> None:
    settings = get_settings()
    # resource allocation block
    engine = create_async_engine(settings.database_url)
    maker = async_sessionmaker(engine, expire_on_commit=False)

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    # embedder = RetryingEmbedder(inner=OpenAIEmbedder(client=client)) - this should be injected and not created
    path = UPLOAD_DIR / stored_filename

    try:
        async with maker() as session:
            async with session.begin():
                job = await session.get(IngestionJob, job_id)
                job.status = "running"

        # document insert AND job update in ONE transaction — both commit together
        async with maker() as session:
            async with session.begin():
                doc_id, was_new = await seed_document(session, path, embedder)
                job = await session.get(IngestionJob, job_id)
                job.status = "succeeded"
                job.document_id = doc_id
                job.progress = {**(job.progress or {}), "was_new": was_new}
    except Exception as exc:
        async with maker() as session:
            async with session.begin():
                job = await session.get(IngestionJob, job_id)
                job.status = "failed"
                job.error = f"{type(exc).__name__}: {exc}"
    finally:
        await engine.dispose()