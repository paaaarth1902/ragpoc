from __future__ import annotations
import os
from pathlib import Path
import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Document, DocumentChunk
from app.embeddings.fake import FakeEmbedder
from app.ingestion.pipeline import embed_chunks
from app.ingestion.chunker import chunk_document
from app.ingestion.loaders.markdown import MarkdownLoader
from app.ingestion.persist import persist_document
from dotenv import load_dotenv

load_dotenv()

_SAMPLE_DOC = Path("corpus/samples/doc-001-example-runbook.md")

@pytest_asyncio.fixture
async def session() -> AsyncSession:
    url = os.environ["DATABASE_URL"]
    engine = create_async_engine(url)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
        await s.rollback()
    await engine.dispose()


async def _embed_sample(dim: int = 32):
    parsed = MarkdownLoader().load(_SAMPLE_DOC)
    chunks = chunk_document(parsed)
    embedder = FakeEmbedder(dim=dim)
    return parsed, await embed_chunks(embedder, chunks)


@pytest.mark.asyncio
async def test_persist_fresh_insert_lands_document_and_chunks(session: AsyncSession):
    parsed, embedded = await _embed_sample(dim=1536)  # match the pgvector column
    async with session.begin():
        doc_id = await persist_document(
            session,
            source_path=parsed.source_path,
            content_hash="a" * 64,
            title="Test Runbook",
            doc_type="markdown",
            embedded=embedded,
        )

    got_doc = await session.get(Document, doc_id)
    assert got_doc is not None
    assert got_doc.content_hash == "a" * 64

    chunk_count = await session.scalar(
        select(func.count()).select_from(DocumentChunk).where(DocumentChunk.document_id == doc_id)
    )
    assert chunk_count == len(embedded)


@pytest.mark.asyncio
async def test_persist_is_idempotent_by_content_hash(session: AsyncSession):
    parsed, embedded = await _embed_sample(dim=1536)
    async with session.begin():
        first = await persist_document(
            session,
            source_path=parsed.source_path,
            content_hash="b" * 64,
            title="First",
            doc_type="markdown",
            embedded=embedded,
        )

    async with session.begin():
        second = await persist_document(
            session,
            source_path=parsed.source_path,
            content_hash="b" * 64,
            title="Second",  # different title — should be ignored
            doc_type="markdown",
            embedded=embedded,
        )

    assert first == second

    chunk_count = await session.scalar(
        select(func.count()).select_from(DocumentChunk).where(DocumentChunk.document_id == first)
    )
    assert chunk_count == len(embedded)  # not doubled


@pytest.mark.asyncio
async def test_all_chunks_have_vectors_of_correct_dim(session: AsyncSession):
    parsed, embedded = await _embed_sample(dim=1536)
    async with session.begin():
        doc_id = await persist_document(
            session,
            source_path=parsed.source_path,
            content_hash="c" * 64,
            title="Test",
            doc_type="markdown",
            embedded=embedded,
        )

    rows = await session.scalars(
        select(DocumentChunk).where(DocumentChunk.document_id == doc_id)
    )
    for row in rows:
        assert row.embedding is not None
        assert len(row.embedding) == 1536