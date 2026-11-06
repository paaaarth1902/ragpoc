from __future__ import annotations
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.query.types import RetrievedChunk

class KeywordRetriever:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def retrieve(self, query_text: str, k: int) -> list[RetrievedChunk]:
        stmt = text(
            """
            SELECT id, document_id, content,
                   ts_rank(
                       to_tsvector('english', content),
                       plainto_tsquery('english', :q)
                   ) AS rank
            FROM document_chunks
            WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :q)
            ORDER BY rank DESC
            LIMIT :k
            """
        )

        result = await self._session.execute(stmt, {"q": query_text, "k": k})
        rows = result.mappings().all()

        return [
            RetrievedChunk(chunk_id=row["id"], document_id=row["document_id"], content=row["content"], score=float(row["rank"])) for row in rows
        ]