from __future__ import annotations
import re
from dataclasses import dataclass
from functools import lru_cache

import tiktoken
from app.ingestion.loaders.base import ParsedDocument, Section

DEFAULT_MAX_TOKENS = 600
DEFAULT_OVERLAP_TOKENS = 80
DEFAULT_MODEL = "text-embedding-3-small"

# stores content in Chunk
@dataclass(slots=True)
class Chunk:
    content: str
    heading_path: list[str]
    heading_level: int
    chunk_index: int
    token_count: int

# 
@lru_cache(maxsize=8)
def _get_encoder(model: str) -> tiktoken.Encoding:
    return tiktoken.encoding_for_model(model)

def _count_tokens(text: str, model: str) -> int:
    return len(_get_encoder(model).encode(text))

# Paragraph breaks
_PARAGRAPH_SPLIT = re.compile(r"\n\s*\n")

# Splits on sentence terminators followed by whitespace.
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

def _split_into_units(text: str) -> list[str]:
    """Split text into paragraphs; fall back to sentences for oversized paragraphs."""
    paragraphs = [p.strip() for p in _PARAGRAPH_SPLIT.split(text) if p.strip()]
    return paragraphs

def _split_paragraph_into_sentences(paragraph: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(paragraph) if s.strip()]

def _pack_units(
    units: list[str],
    max_tokens: int,
    overlap_tokens: int,
    model: str,
) -> list[str]:
    encoder = _get_encoder(model)
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for unit in units:
        unit_tokens = len(encoder.encode(unit))

        # A single unit larger than max_tokens — must further-split by sentences
        # or, as a last resort, by raw tokens.
        if unit_tokens > max_tokens:
            if current:
                chunks.append("\n\n".join(current))
                current = []
                current_tokens = 0
            chunks.extend(_hard_split(unit, max_tokens, overlap_tokens, encoder))
            continue

        # Would adding this unit exceed max? Emit current, start fresh with overlap.
        if current_tokens + unit_tokens > max_tokens and current:
            chunks.append("\n\n".join(current))
            tail = _tail_overlap(chunks[-1], overlap_tokens, encoder)
            current = [tail, unit] if tail else [unit]
            current_tokens = len(encoder.encode(tail)) + unit_tokens if tail else unit_tokens
        else:
            current.append(unit)
            current_tokens += unit_tokens

    if current:
        chunks.append("\n\n".join(current))
    return chunks

def _hard_split(
    text: str,
    max_tokens: int,
    overlap_tokens: int,
    encoder: tiktoken.Encoding,
) -> list[str]:
    """Fallback: split a giant paragraph by sentences, then by raw tokens if a sentence itself is too big."""
    sentences = _split_paragraph_into_sentences(text)
    if len(sentences) > 1:
        return _pack_units(sentences, max_tokens, overlap_tokens, encoder.name)

    # A single sentence exceeds max_tokens — chop at the token level.
    tokens = encoder.encode(text)
    chunks: list[str] = []
    step = max_tokens - overlap_tokens
    for i in range(0, len(tokens), step):
        window = tokens[i : i + max_tokens]
        chunks.append(encoder.decode(window))
        if i + max_tokens >= len(tokens):
            break
    return chunks

def _tail_overlap(text: str, overlap_tokens: int, encoder: tiktoken.Encoding) -> str:
    """Return the trailing ~overlap_tokens tokens of `text` as a decoded string."""
    if overlap_tokens <= 0:
        return ""
    tokens = encoder.encode(text)
    if len(tokens) <= overlap_tokens:
        return text
    return encoder.decode(tokens[-overlap_tokens:])

def chunk_section(
    section: Section,
    starting_index: int,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
    model: str = DEFAULT_MODEL,
) -> list[Chunk]:
    """Turn one Section into one or more Chunks."""
    total_tokens = _count_tokens(section.content, model)

    if total_tokens <= max_tokens:
        return [
            Chunk(
                content=section.content,
                heading_path=list(section.heading_path),
                heading_level=section.heading_level,
                chunk_index=starting_index,
                token_count=total_tokens,
            )
        ]

    units = _split_into_units(section.content)
    packed = _pack_units(units, max_tokens, overlap_tokens, model)
    return [
        Chunk(
            content=text,
            heading_path=list(section.heading_path),
            heading_level=section.heading_level,
            chunk_index=starting_index + i,
            token_count=_count_tokens(text, model),
        )
        for i, text in enumerate(packed)
    ]

def chunk_document(
    document: ParsedDocument,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
    model: str = DEFAULT_MODEL,
) -> list[Chunk]:
    """Turn a ParsedDocument into a list of Chunks with document-wide chunk_index."""
    chunks: list[Chunk] = []
    for section in document.sections:
        section_chunks = chunk_section(
            section,
            starting_index=len(chunks),
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
            model=model,
        )
        chunks.extend(section_chunks)
    return chunks