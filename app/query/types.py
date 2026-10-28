from dataclasses import dataclass
from typing import Protocol, Sequence
from uuid import UUID

@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    chunk_id: int
    document_id: UUID
    content: str
    score: float
    rerank_score: float | None = None

class Retriever(Protocol):
    async def retrieve(self, query_embedding: Sequence[float], k: int) -> list[RetrievedChunk]:
        pass
    