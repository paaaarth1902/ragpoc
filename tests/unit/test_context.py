from __future__ import annotations
from uuid import UUID
from app.query.context import build_context
from app.query.types import RetrievedChunk

DOC = UUID("00000000-0000-0000-0000-000000000001")

def _chunk(chunk_id: int, content: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=DOC,
        content=content,
        score=0.1,
    )

def test_build_context_numbers_and_maps():
    chunks = [
        _chunk(10, "cats are great"),
        _chunk(20, "dogs are loyal"),
    ]
    ctx = build_context(chunks)

    # text block is numbered 1-based
    assert "[1] cats are great" in ctx.prompt_block
    assert "[2] dogs are loyal" in ctx.prompt_block

    # citation map parallels the text
    assert len(ctx.citations) == 2
    assert ctx.citations[0].label == 1
    assert ctx.citations[0].chunk_id == 10
    assert ctx.citations[1].label == 2
    assert ctx.citations[1].chunk_id == 20
    # every citation resolves to the real document
    assert all(c.document_id == DOC for c in ctx.citations)

def test_build_context_empty():
    ctx = build_context([])
    assert ctx.prompt_block == ""
    assert ctx.citations == []