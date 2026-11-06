from __future__ import annotations
from collections.abc import Sequence
from app.query.types import RetrievedChunk

def reciprocal_rank_fusion(rankings: Sequence[Sequence[RetrievedChunk]], *, k: int = 60, top_n: int | None = None) -> list[RetrievedChunk]:
    fused_scores: dict[int, float] = {}
    chunk_by_id: dict[int, RetrievedChunk] = {}

    for ranking in rankings:
        for rank, chunk in enumerate(ranking):
            cid = chunk.chunk_id
            fused_scores[cid] = fused_scores.get(cid, 0.0) + 1.0 / (k + rank)
            # keep first-seen chunk object (content/document_id identical)
            chunk_by_id.setdefault(cid, chunk)

    ordered_ids = sorted(fused_scores, key=lambda cid: fused_scores[cid], reverse=True)

    result = [chunk_by_id[cid] for cid in ordered_ids]
    return result[:top_n] if top_n is not None else result