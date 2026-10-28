from __future__ import annotations

from dataclasses import replace
from typing import Sequence

from sentence_transformers import CrossEncoder

from app.query.types import RetrievedChunk


class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
        self._model = CrossEncoder(model_name)

    async def rerank(
        self, query: str, candidates: Sequence[RetrievedChunk], top_n: int
    ) -> list[RetrievedChunk]:
        if not candidates:
            return []

        pairs = [(query, c.content) for c in candidates]
        scores = self._model.predict(pairs)

        scored = [replace(c, rerank_score=float(s)) for c, s in zip(candidates, scores)]
        scored.sort(key=lambda c: c.rerank_score, reverse=True)
        return scored[:top_n]