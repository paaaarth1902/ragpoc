from __future__ import annotations
from dataclasses import dataclass
from app.embeddings.types import Embedder
from app.query.context import Citation, build_context
from app.query.embed import embed_query
from app.query.generator import AnswerGenerator
from app.query.types import Retriever

@dataclass(frozen=True, slots=True)
class QueryResult:
    answer: str
    citations: list[Citation]

class QueryPipeline:
    """Chains: embed -> retrieve -> build_context -> generate."""

    def __init__(
        self,
        embedder: Embedder,
        retriever: Retriever,
        generator: AnswerGenerator,
    ) -> None:
        self._embedder = embedder
        self._retriever = retriever
        self._generator = generator

    async def run(self, question: str, k: int = 5) -> QueryResult:
        vector = await embed_query(self._embedder, question)
        chunks = await self._retriever.retrieve(vector, k)
        context = build_context(chunks)
        answer = await self._generator.generate(question, context)
        return QueryResult(answer=answer, citations=context.citations)