from __future__ import annotations
from app.query.types import RetrievedChunk

def hit_at_k(retrieved: list[RetrievedChunk], expected: set[int], k: int) -> bool:
    """Did ANY expected chunk land in the top-k? (recall-style)"""
    top_ids = {c.chunk_id for c in retrieved[:k]}
    return bool(expected & top_ids)


def mrr(retrieved: list[RetrievedChunk], expected: set[int]) -> float:
    """Mean Reciprocal Rank: 1/rank of first expected chunk, else 0.
    Rewards ranking the right chunk HIGH, not just retrieving it."""
    for rank, chunk in enumerate(retrieved, start=1):
        if chunk.chunk_id in expected:
            return 1.0 / rank
    return 0.0