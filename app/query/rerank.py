from __future__ import annotations
from typing import Protocol, Sequence
from app.query.types import RetrievedChunk

class Reranker(Protocol):
    async def rerank(self, query: str, candidates: Sequence[RetrievedChunk], top_n: int) -> list[RetrievedChunk]:
        pass