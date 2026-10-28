# app/query/rerank_fake.py
from __future__ import annotations

from typing import Sequence

from app.query.types import RetrievedChunk


class FakeReranker:
    """Deterministic, model-free reranker for tests.

    Scores each chunk by how many query words appear in its content,
    then returns the top_n by that score. No real model involved.
    """

    async def rerank(
        self,
        query: str,
        candidates: Sequence[RetrievedChunk],
        top_n: int,
    ) -> list[RetrievedChunk]:
        query_words = set(query.lower().split())

        def overlap(chunk: RetrievedChunk) -> int:
            chunk_words = set(chunk.content.lower().split())
            return len(query_words & chunk_words)   # count shared words

        ranked = sorted(candidates, key=overlap, reverse=True)  # most overlap first
        return list(ranked[:top_n])