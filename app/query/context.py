from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID
from app.query.types import RetrievedChunk

@dataclass(frozen=True, slots=True)
class Citation:
    label: int
    chunk_id: int
    document_id: UUID

@dataclass(frozen=True, slots=True)
class GroundedContext:
    prompt_block: str
    citations: list[Citation]

def build_context(chunks: list[RetrievedChunk]) -> GroundedContext:
    """Turn retrieved chunks into a numbered context block + citation map."""
    if not chunks:
        return GroundedContext(prompt_block="", citations=[])

    lines: list[str] = []
    citations: list[Citation] = []

    for i, chunk in enumerate(chunks, start=1):
        lines.append(f"[{i}] {chunk.content}")
        citations.append(
            Citation(label=i, chunk_id=chunk.chunk_id, document_id=chunk.document_id)
        )

    prompt_block = "\n\n".join(lines)
    return GroundedContext(prompt_block=prompt_block, citations=citations)
