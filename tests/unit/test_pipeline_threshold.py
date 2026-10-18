from __future__ import annotations

from typing import Sequence
from uuid import UUID

import pytest

from app.embeddings.fake import FakeEmbedder
from app.query.pipeline import QueryPipeline, MAX_DISTANCE, NO_CONTEXT_ANSWER
from app.query.types import RetrievedChunk

DOC = UUID("00000000-0000-0000-0000-000000000001")


class StubRetriever:
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self._chunks = chunks

    async def retrieve(self, query_embedding: Sequence[float], k: int) -> list[RetrievedChunk]:
        return self._chunks[:k]


class SpyGenerator:
    """Records whether it was called — to prove we short-circuit."""
    def __init__(self) -> None:
        self.called = False

    async def generate(self, question, context) -> str:
        self.called = True
        return "real answer"


@pytest.mark.asyncio
async def test_all_chunks_too_far_refuses_without_citations():
    far = [RetrievedChunk(chunk_id=1, document_id=DOC, content="x", score=MAX_DISTANCE + 0.1)]
    gen = SpyGenerator()
    pipeline = QueryPipeline(FakeEmbedder(), StubRetriever(far), gen)

    result = await pipeline.run("irrelevant question", k=5)

    assert result.citations == []            # no fake sources
    assert result.answer == NO_CONTEXT_ANSWER
    assert gen.called is False               # LLM never called -> token saved


@pytest.mark.asyncio
async def test_close_chunks_produce_answer_with_citations():
    close = [RetrievedChunk(chunk_id=7, document_id=DOC, content="relevant", score=MAX_DISTANCE - 0.1)]
    gen = SpyGenerator()
    pipeline = QueryPipeline(FakeEmbedder(), StubRetriever(close), gen)

    result = await pipeline.run("relevant question", k=5)

    assert result.answer == "real answer"
    assert len(result.citations) == 1
    assert result.citations[0].chunk_id == 7
    assert gen.called is True