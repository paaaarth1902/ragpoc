from pathlib import Path
import pytest
from app.embeddings.fake import FakeEmbedder
from app.embeddings.types import EmbeddedChunk
from app.ingestion.pipeline import ingest_document

_SAMPLE_DOC = Path("corpus/samples/doc-001-example-runbook.md")

@pytest.mark.asyncio
async def test_ingest_returns_embedded_chunks():
    embedded = await ingest_document(_SAMPLE_DOC, embedder=FakeEmbedder(dim=32))
    assert len(embedded) > 0
    assert all(isinstance(c, EmbeddedChunk) for c in embedded)
    assert all(len(c.vector) == 32 for c in embedded)

@pytest.mark.asyncio
async def test_ingest_preserves_chunk_metadata():
    embedded = await ingest_document(_SAMPLE_DOC, embedder=FakeEmbedder(dim=32))
    # chunk_index should be 0, 1, 2, ... across the whole doc
    assert [c.chunk_index for c in embedded] == list(range(len(embedded)))
    # every chunk should have a non-empty heading_path
    assert all(len(c.heading_path) > 0 for c in embedded)