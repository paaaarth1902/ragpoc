from __future__ import annotations
from app.embeddings.types import Embedder

async def embed_query(embedder: Embedder, question: str) -> list[float]:
    if not question.strip():
        raise ValueError("Question must not be empty. Please pass something")
    vectors = await embedder.embed([question])
    return vectors[0]