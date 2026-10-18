from __future__ import annotations
import pytest
from app.embeddings.fake import FakeEmbedder
from app.query.embed import embed_query

@pytest.mark.asyncio
async def test_embed_query_returns_one_vector():
    embedder = FakeEmbedder(dim=1536)
    vec = await embed_query(embedder, "how do I reset my password?")

    assert isinstance(vec, list)
    assert len(vec) == embedder.dim
    assert all(isinstance(x, float) for x in vec)


@pytest.mark.asyncio
async def test_embed_query_rejects_empty():
    embedder = FakeEmbedder()
    with pytest.raises(ValueError):
        await embed_query(embedder, "   ")  # whitespace == empty