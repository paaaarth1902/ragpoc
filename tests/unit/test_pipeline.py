from __future__ import annotations

from typing import Sequence
from uuid import UUID

import pytest

from app.query.context import GroundedContext
from app.query.pipeline import NO_CONTEXT_ANSWER, QueryPipeline
from app.query.rerank_fake import FakeReranker
from app.query.types import RetrievedChunk

DOC = UUID("00000000-0000-0000-0000-000000000001")


# ---- Test doubles ---------------------------------------------------------

class FakeEmbedder:
    async def embed_query(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class StubRetriever:
    def __init__(self, chunks: Sequence[RetrievedChunk]) -> None:
        self._chunks = list(chunks)

    async def retrieve(self, vector: Sequence[float], k: int) -> list[RetrievedChunk]:
        return self._chunks[:k]


class ScriptedGenerator:
    def __init__(self, answer: str) -> None:
        self._answer = answer

    async def generate(self, question: str, context: GroundedContext) -> str:
        return self._answer


def _chunk(cid: int, content: str, score: float = 0.5) -> RetrievedChunk:
    return RetrievedChunk(chunk_id=cid, document_id=DOC, content=content, score=score)


def _pipeline(chunks, answer: str) -> QueryPipeline:
    return QueryPipeline(
        FakeEmbedder(),
        StubRetriever(chunks),
        FakeReranker(),
        ScriptedGenerator(answer),
    )


# ---- Tests ----------------------------------------------------------------

@pytest.mark.asyncio
async def test_happy_path_returns_answer_and_used_citations():
    chunks = [
        _chunk(1, "resume the sla timer when reopened"),  # high overlap
        _chunk(2, "unrelated weather notes"),             # zero overlap
    ]
    pipeline = _pipeline(chunks, answer="You resume it [1].")

    result = await pipeline.run("resume sla timer", k=2)

    assert result.answer == "You resume it [1]."
    assert {c.label for c in result.citations} == {1}


@pytest.mark.asyncio
async def test_reranker_promotes_relevant_chunk_to_first():
    # Winner (chunk_id=2) placed LAST; reranker must promote it to label [1].
    chunks = [
        _chunk(1, "nothing relevant here"),               # zero overlap
        _chunk(2, "resume sla timer immediately"),        # high overlap -> wins
    ]
    pipeline = _pipeline(chunks, answer="Answer uses [1].")

    result = await pipeline.run("resume sla timer", k=2)

    # label [1] must map to chunk_id 2 (the promoted, high-overlap chunk)
    first = next(c for c in result.citations if c.label == 1)
    assert first.chunk_id == 2


@pytest.mark.asyncio
async def test_empty_retrieval_refuses():
    pipeline = _pipeline(chunks=[], answer="should not be used")

    result = await pipeline.run("anything", k=5)

    assert result.answer == NO_CONTEXT_ANSWER
    assert result.citations == []


@pytest.mark.asyncio
async def test_llm_refusal_strips_all_citations():
    chunks = [_chunk(1, "resume sla timer")]
    pipeline = _pipeline(chunks, answer="I don't know.")

    result = await pipeline.run("resume sla timer", k=5)

    assert result.citations == []


@pytest.mark.asyncio
async def test_only_referenced_citations_returned():
    chunks = [
        _chunk(1, "resume sla timer one"),
        _chunk(2, "resume sla timer two"),
        _chunk(3, "resume sla timer three"),
    ]
    pipeline = _pipeline(chunks, answer="Uses [1] and [3] only.")

    result = await pipeline.run("resume sla timer", k=3)

    assert {c.label for c in result.citations} == {1, 3}