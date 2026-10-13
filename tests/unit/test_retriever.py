from __future__ import annotations
import pytest
from sqlalchemy import text
from app.query.retriever import PgVectorRetriever
from app.db.models import Document, DocumentChunk

def _vec(lead: float) -> list[float]:
    """A vector that leans in a known direction: [lead, 0, 0, ...]."""
    v = [0.0] * 1536
    v[0] = lead
    return v

@pytest.mark.asyncio
async def test_retriever_returns_nearest_first(db_session):
    # 1. Create mock document
    doc = Document(
        id="00000000-0000-0000-0000-000000000001",
        title="Test Document",
        content_hash="dummy-hash-123",
        doc_type="markdown",
        version=1,
    )
    db_session.add(doc)
    await db_session.flush()

    seeds = [
        ("chunk about cats", _vec(1.0)),
        ("chunk about dogs", _vec(0.9)),   # closest to query below
        ("chunk about cars", _vec(-1.0)),  # opposite direction = far
    ]
    
    # 2. Loop with enumerate and explicitly pass chunk_index=idx
    for idx, (content, vec) in enumerate(seeds):
        chunk = DocumentChunk(
            document_id=doc.id,
            content=content,
            embedding=vec,
            chunk_index=idx,  # <-- Must be explicitly provided here!
        )
        db_session.add(chunk)
    
    await db_session.flush()

    # 3. search with a vector pointing the same way as "dogs" (0.9)
    retriever = PgVectorRetriever(db_session)
    results = await retriever.retrieve(_vec(0.95), k=2)

    # 4. assertions
    assert len(results) == 2
    assert results[0].content in {"chunk about cats", "chunk about dogs"}
    assert results[0].score <= results[1].score
    assert "cars" not in results[0].content