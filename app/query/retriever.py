from __future__ import annotations
from typing import Sequence
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.query.types import RetrievedChunk

# retrieveing k chunks from db closes to the query's vectors
class PgVectorRetriever:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def retrieve(self, query_embedding: Sequence[float], k: int) -> list[RetrievedChunk]:
        vec_literal = "[" + ",".join(str(x) for x in query_embedding) + "]"

        stmt = text(
            """
            SELECT id, document_id, content,
                   embedding <=> CAST(:vec AS vector) AS distance
            FROM document_chunks
            ORDER BY distance ASC
            LIMIT :k
            """
        )

        result = await self._session.execute(stmt, {"vec": vec_literal, "k": k})
        rows = result.mappings().all()

        return [
            RetrievedChunk(
                chunk_id=row["id"],
                document_id=row["document_id"],
                content=row["content"],
                score=row["distance"],
            )
            for row in rows
        ]