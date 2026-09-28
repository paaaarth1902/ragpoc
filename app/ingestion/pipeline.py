from pathlib import Path
from app.embeddings.fake import embed_chunks
from app.embeddings.types import EmbeddedChunk, Embedder
from app.ingestion.chunker import chunk_document
from app.ingestion.loaders.base import ParsedDocument
from app.ingestion.loaders.markdown import MarkdownLoader

async def ingest_parsed(parsed: ParsedDocument, embedder: Embedder) -> list[EmbeddedChunk]:
    return await embed_chunks(embedder, chunk_document(parsed))

async def ingest_document(path: Path, embedder: Embedder,) -> list[EmbeddedChunk]:
    return await ingest_parsed(MarkdownLoader().load(path), embedder)