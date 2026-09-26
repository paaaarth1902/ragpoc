import pytest
from app.embeddings.fake import FakeEmbedder, embed_chunks
from app.ingestion.chunker import Chunk

def _make_chunk(content: str, idx: int = 0) -> Chunk:
    return Chunk(
        content=content,
        heading_path=["Test"],
        heading_level=1,
        chunk_index=idx,
        token_count=len(content.split()),
    )

@pytest.mark.asyncio
async def test_fake_embedder_returns_correct_shape():
    embedder = FakeEmbedder(dim=1536)
    vectors = await embedder.embed(["hello", "world"])
    assert len(vectors) == 2
    assert all(len(v) == 1536 for v in vectors)
    assert all(isinstance(x, float) for x in vectors[0])

@pytest.mark.asyncio
async def test_fake_embedder_is_deterministic():
    embedder = FakeEmbedder(dim=32)
    a = await embedder.embed(["same text"])
    b = await embedder.embed(["same text"])
    assert a == b

@pytest.mark.asyncio
async def test_fake_embedder_distinguishes_texts():
    embedder = FakeEmbedder(dim=32)
    [v1, v2] = await embedder.embed(["alpha", "beta"])
    assert v1 != v2

@pytest.mark.asyncio
async def test_embed_chunks_preserves_order_and_metadata():
    chunks = [_make_chunk(f"chunk {i}", idx=i) for i in range(5)]
    embedded = await embed_chunks(FakeEmbedder(dim=32), chunks)
    assert len(embedded) == 5
    for orig, emb in zip(chunks, embedded, strict=True):
        assert emb.content == orig.content
        assert emb.chunk_index == orig.chunk_index
        assert emb.heading_path == orig.heading_path
        assert len(emb.vector) == 32