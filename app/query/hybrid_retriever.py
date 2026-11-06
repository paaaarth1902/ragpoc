from __future__ import annotations
from collections.abc import Sequence
from app.query.keyword_retriever import KeywordRetriever
from app.query.retriever import PgVectorRetriever
from app.query.rrf import reciprocal_rank_fusion
from app.query.types import RetrievedChunk

class HybridRetriever:
    def __init__( self,vector_retriever: PgVectorRetriever,keyword_retriever: KeywordRetriever,*,pool_k: int = 20) -> None:
        self._vector = vector_retriever
        self._keyword = keyword_retriever
        self._pool_k = pool_k

    async def retrieve_hybrid(self, query_text: str, query_embedding: Sequence[float], k: int) -> list[RetrievedChunk]:
        vector_hits = await self._vector.retrieve(query_embedding, self._pool_k)
        keyword_hits = await self._keyword.retrieve(query_text, self._pool_k)

        return reciprocal_rank_fusion([vector_hits, keyword_hits], top_n=k)