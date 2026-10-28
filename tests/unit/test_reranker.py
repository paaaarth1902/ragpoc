from __future__ import annotations

from uuid import UUID
import pytest
from app.query.rerank_fake import FakeReranker
from app.query.types import RetrievedChunk

DOC = UUID("00000000-0000-0000-0000-000000000001")

def _chunk(cid: int, content: str) -> RetrievedChunk:
    """Helper: build a chunk. score=0.5 is irrelevant here (reranker ignores it)."""
    return RetrievedChunk(chunk_id=cid, document_id=DOC, content=content, score=0.5)


@pytest.mark.asyncio
async def test_promotes_high_overlap_chunk_even_if_last():
    # The winner (chunk 2) has every query word but is LAST in the input.
    # Proves the reranker REORDERS, not just trims.
    query = "resume sla timer"
    candidates = [
        _chunk(1, "unrelated text about cats and weather"),  # 0 overlap
        _chunk(2, "resume the sla timer when ticket reopens"),  # 3 overlap -> wins
    ]

    result = await FakeReranker().rerank(query, candidates, top_n=2)

    assert result[0].chunk_id == 2   # high-overlap chunk promoted to first


@pytest.mark.asyncio
async def test_trims_to_top_n():
    # 3 candidates, top_n=2 -> exactly 2 returned. Proves TRIMMING.
    query = "resume sla timer"
    candidates = [
        _chunk(1, "resume sla timer"),   # 3 overlap
        _chunk(2, "sla timer"),          # 2 overlap
        _chunk(3, "nothing relevant"),   # 0 overlap -> should be dropped
    ]

    result = await FakeReranker().rerank(query, candidates, top_n=2)

    assert len(result) == 2
    ids = {c.chunk_id for c in result}
    assert ids == {1, 2}        # the two highest-overlap kept
    assert 3 not in ids         # lowest-overlap dropped


@pytest.mark.asyncio
async def test_full_ordering_is_correct():
    # Verify the COMPLETE order, not just the winner.
    query = "resume sla timer"
    candidates = [
        _chunk(1, "sla timer"),                 # 2 overlap -> middle
        _chunk(2, "nothing here"),              # 0 overlap -> last
        _chunk(3, "resume sla timer exactly"),  # 3 overlap -> first
    ]

    result = await FakeReranker().rerank(query, candidates, top_n=3)

    assert [c.chunk_id for c in result] == [3, 1, 2]   # 3>1>2 by overlap


@pytest.mark.asyncio
async def test_empty_candidates_returns_empty():
    # Edge case: nothing to rerank -> empty list, no crash.
    result = await FakeReranker().rerank("anything", [], top_n=5)
    assert result == []

@pytest.mark.asyncio
async def test_top_n_larger_than_candidates():
    # Asking for more than exist -> return all available, no error.
    query = "resume sla timer"
    candidates = [_chunk(1, "resume sla timer")]

    result = await FakeReranker().rerank(query, candidates, top_n=10)

    assert len(result) == 1   # only 1 exists, so only 1 returned