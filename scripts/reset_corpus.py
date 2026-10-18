from __future__ import annotations

import asyncio

from sqlalchemy import text

from app.db.session import SessionLocal


async def reset() -> None:
    async with SessionLocal() as session:
        # children before parents (FK order)
        await session.execute(text("DELETE FROM document_chunks"))
        await session.execute(text("DELETE FROM documents"))
        await session.execute(text("DELETE FROM ingestion_jobs"))
        await session.commit()
    print("corpus wiped: document_chunks, documents, ingestion_jobs cleared")


if __name__ == "__main__":
    asyncio.run(reset())