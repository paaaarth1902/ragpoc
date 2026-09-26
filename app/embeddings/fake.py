import hashlib
import random
from dataclasses import asdict
from app.embeddings.types import EmbeddedChunk, Embedder
from app.ingestion.chunker import Chunk

class FakeEmbedder:
    dim: int

    def __init__(self, dim: int = 1536) -> None:
        self.dim = dim

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector_for(t) for t in texts]
    
    def _vector_for(self, text: str) -> list[float]:
        seed = int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big") # converts the text string into a unique 8-byte hash int and remains same every time we see same text
        rng = random.Random(seed) # since we want this to be deterministic and seed is fixed for one text
        return [rng.uniform(-1.0, 1.0) for _ in range(self.dim)] # generate dim floats between limits mentioned

async def embed_chunks(embedder: Embedder, chunks: list[Chunk]) -> list[EmbeddedChunk]:
    vectors = await embedder.embed([c.content for c in chunks])
    if len(vectors) != len(chunks):
        raise ValueError(f"embedder returned {len(vectors)} vectors for {len(chunks)} chunks")
    return [EmbeddedChunk(**asdict(c), vector=v) for c, v in zip(chunks, vectors, strict=True)]

    