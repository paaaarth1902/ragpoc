from __future__ import annotations
import hashlib
from pathlib import Path
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Document
from app.embeddings.types import Embedder
from app.ingestion.loaders.markdown import MarkdownLoader
from app.ingestion.persist import persist_document
from app.ingestion.pipeline import ingest_parsed

async def seed_document(session: AsyncSession, path: Path, embedder: Embedder) -> tuple[UUID, bool]:
    content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    existing = await session.scalar(
        select(Document.id).where(Document.content_hash == content_hash)
    )
    
    if existing is not None: return existing, False

    parsed = MarkdownLoader().load(path)
    embedded = await ingest_parsed(parsed, embedder)

    fm = parsed.front_matter
    doc_id = await persist_document(
        session,
        source_path=path,
        content_hash=content_hash,
        title=str(fm.get("title") or path.stem),
        doc_type=str(fm.get("doc_type") or "markdown"),
        embedded=embedded,
    )
    return doc_id, True