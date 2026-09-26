from dataclasses import dataclass, field
from typing import Protocol
from app.ingestion.chunker import Chunk

@dataclass(frozen=True, slots=True) # minimizing mem overhead with slots
class EmbeddedChunk(Chunk):
    vector: list[float] = field(default_factory=list)


class Embedder(Protocol):
    dim: int

    async def embed(self, texts: list[str]) -> list[list[float]]:
        pass