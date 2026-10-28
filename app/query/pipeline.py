from __future__ import annotations
from dataclasses import dataclass
from app.embeddings.types import Embedder
from app.query.context import Citation, build_context
from app.query.embed import embed_query
from app.query.generator import AnswerGenerator
from app.query.types import Retriever
from app.query.rerank import Reranker

RETRIEVE_K = 20
RERANK_FLOOR = 0.0
NO_CONTEXT_ANSWER = "I Dont have enough context on this"

@dataclass(frozen=True, slots=True)
class QueryResult:
    answer: str
    citations: list[Citation]

class QueryPipeline:
    """Chains: embed -> retrieve -> rerank -> gate -> build_context -> generate."""

    def __init__(self, embedder: Embedder, retriever: Retriever, reranker: Reranker, generator: AnswerGenerator) -> None:
        self._embedder = embedder
        self._retriever = retriever
        self._reranker = reranker
        self._generator = generator

    async def run(self, question: str, k: int = 5) -> QueryResult:
        vector = await embed_query(self._embedder, question)
        candidates = await self._retriever.retrieve(vector, RETRIEVE_K)

        ranked = await self._reranker.rerank(question, candidates, top_n=k)
        relevant = [c for c in ranked if (c.rerank_score or 0.0) >= RERANK_FLOOR]

        if not relevant:
            return QueryResult(answer=NO_CONTEXT_ANSWER, citations=[])

        context = build_context(relevant)
        print(f"\n[CONTEXT prompt_block]:\n{context.prompt_block!r}\n")   # ← KEY

        answer = await self._generator.generate(question, context)
        print(f"[LLM ANSWER]: {answer!r}\n")
        used = [c for c in context.citations if f"[{c.label}]" in answer]

        return QueryResult(answer=answer, citations=used)