from pathlib import Path
from dataclasses import asdict
from app.embeddings.types import EmbeddedChunk, Embedder
from app.ingestion.chunker import chunk_document, Chunk
from app.ingestion.loaders.base import ParsedDocument
from app.ingestion.loaders.markdown import MarkdownLoader

async def embed_chunks(embedder: Embedder, chunks: list[Chunk]) -> list[EmbeddedChunk]:
    """Generic helper: works with ANY Embedder implementation (OpenAI or Fake)."""
    if not chunks:
        return []

    # Calls .embed() on whatever object was passed in
    vectors = await embedder.embed([c.content for c in chunks])

    if len(vectors) != len(chunks):
        raise ValueError(f"embedder returned {len(vectors)} vectors for {len(chunks)} chunks")

    return [
        EmbeddedChunk(**asdict(c), vector=v)
        for c, v in zip(chunks, vectors, strict=True)
    ]

async def ingest_parsed(parsed: ParsedDocument, embedder: Embedder) -> list[EmbeddedChunk]:
    return await embed_chunks(embedder, chunk_document(parsed))

async def ingest_document(path: Path, embedder: Embedder,) -> list[EmbeddedChunk]:
    return await ingest_parsed(MarkdownLoader().load(path), embedder)