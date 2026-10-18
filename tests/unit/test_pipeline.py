from __future__ import annotations
from typing import Sequence
from uuid import UUID
import pytest
from app.embeddings.fake import FakeEmbedder
from app.query.generator import FakeGenerator
from app.query.pipeline import QueryPipeline, NO_CONTEXT_ANSWER
from app.query.types import RetrievedChunk

DOC = UUID("00000000-0000-0000-0000-000000000001")

class StubRetriever:
    """In-memory retriever — returns canned chunks, ignores the vector."""

    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self._chunks = chunks

    async def retrieve(
        self, query_embedding: Sequence[float], k: int
    ) -> list[RetrievedChunk]:
        return self._chunks[:k]


@pytest.mark.asyncio
async def test_pipeline_end_to_end():
    chunks = [
        RetrievedChunk(chunk_id=10, document_id=DOC, content="cats purr", score=0.1),
        RetrievedChunk(chunk_id=20, document_id=DOC, content="dogs bark", score=0.2),
    ]
    pipeline = QueryPipeline(
        embedder=FakeEmbedder(),
        retriever=StubRetriever(chunks),
        generator=FakeGenerator(),
    )

    result = await pipeline.run("what do pets do?", k=5)

    # answer came back (FakeGenerator echoed question + source count)
    assert "what do pets do?" in result.answer
    assert "2" in result.answer                     # 2 citations reached it

    # citations surfaced from context, traceable to real chunk ids
    assert len(result.citations) == 2
    assert result.citations[0].chunk_id == 10
    assert result.citations[1].chunk_id == 20
    assert all(c.document_id == DOC for c in result.citations)


@pytest.mark.asyncio
async def test_pipeline_empty_retrieval():
    pipeline = QueryPipeline(
        embedder=FakeEmbedder(),
        retriever=StubRetriever([]),   # nothing found
        generator=FakeGenerator(),
    )
    result = await pipeline.run("anything?", k=5)

    assert result.citations == []       # no sources
    assert result.answer == NO_CONTEXT_ANSWER         # Fake reports 0 sources