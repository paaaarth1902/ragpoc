from __future__ import annotations
from pathlib import Path
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Document, DocumentChunk
from app.embeddings.types import EmbeddedChunk

async def persist_document(session: AsyncSession, *, source_path: Path, content_hash: str, title: str, doc_type: str, embedded: list[EmbeddedChunk]) -> UUID:
    existing = await session.scalar(
        select(Document.id).where(Document.content_hash == content_hash)
    )
    if existing is not None:
        return existing

    doc = Document(title=title, doc_type=doc_type, content_hash=content_hash)
    session.add(doc)
    await session.flush()

    session.add_all(
        DocumentChunk(
            document_id=doc.id,
            chunk_index=c.chunk_index,
            content=c.content,
            embedding=c.vector,
            chunk_metadata={
                "heading_path": list(c.heading_path),
                "heading_level": c.heading_level,
                "token_count": c.token_count,
                "source_path": str(source_path),
            },
        )
        for c in embedded
    )
    await session.flush()
    return doc.id