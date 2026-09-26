
from __future__ import annotations
from pathlib import Path
from app.ingestion.chunker import (DEFAULT_MAX_TOKENS, DEFAULT_MODEL, DEFAULT_OVERLAP_TOKENS, _get_encoder, chunk_document, chunk_section)
from app.ingestion.loaders.base import ParsedDocument, Section

def _make_section(
    heading_path: list[str],
    content: str,
    heading_level: int = 2,
) -> Section:
    return Section(
        heading_path=heading_path,
        heading_level=heading_level,
        content=content,
    )

def _make_doc(sections: list[Section]) -> ParsedDocument:
    return ParsedDocument(
        source_path=Path("test://in-memory.md"),
        front_matter={"title": "Test Doc"},
        sections=sections,
    )

def _oversized_paragraph(target_tokens: int) -> str:
    """Deterministic paragraph that exceeds target_tokens after BPE encoding."""
    enc = _get_encoder(DEFAULT_MODEL)
    sentence = "The service was paused for maintenance and then resumed. "
    text = ""
    while len(enc.encode(text)) < target_tokens:
        text += sentence
    return text.strip()

def test_no_chunk_exceeds_max_tokens() -> None:
    section = _make_section(
        heading_path=["Large Section"],
        content=_oversized_paragraph(DEFAULT_MAX_TOKENS * 3),
    )
    chunks = chunk_document(_make_doc([section]))

    assert len(chunks) > 1, "oversized section should split"
    for c in chunks:
        assert c.token_count <= DEFAULT_MAX_TOKENS, (
            f"chunk {c.chunk_index} has {c.token_count} tokens, cap is {DEFAULT_MAX_TOKENS}"
        )

def test_small_section_stays_single_chunk() -> None:
    section = _make_section(
        heading_path=["Overview"],
        content="This is a short section. It should not be split.",
    )
    chunks = chunk_document(_make_doc([section]))

    assert len(chunks) == 1
    assert chunks[0].content.strip() == section.content.strip()
    assert chunks[0].chunk_index == 0

def test_consecutive_chunks_share_overlap_tokens() -> None:
    section = _make_section(
        heading_path=["Large Section"],
        content=_oversized_paragraph(DEFAULT_MAX_TOKENS * 2),
    )
    chunks = chunk_section(section, starting_index=0)

    assert len(chunks) >= 2, "need at least 2 chunks to check overlap"

    enc = _get_encoder(DEFAULT_MODEL)
    for prev, curr in zip(chunks, chunks[1:]):
        prev_tokens = enc.encode(prev.content)
        curr_tokens = enc.encode(curr.content)
        window = min(DEFAULT_OVERLAP_TOKENS // 2, len(prev_tokens), len(curr_tokens))
        assert window > 0

        prev_tail = enc.decode(prev_tokens[-window:]).strip()
        curr_head = enc.decode(curr_tokens[: window * 2])
        assert prev_tail in curr_head, (
            f"overlap not found.\nprev tail: {prev_tail!r}\ncurr head: {curr_head!r}"
        )

def test_heading_path_preserved_on_every_chunk() -> None:
    small = _make_section(
        heading_path=["Procedure", "Step 1"],
        content="Do the thing.",
    )
    big = _make_section(
        heading_path=["Procedure", "Step 2"],
        content=_oversized_paragraph(DEFAULT_MAX_TOKENS * 2),
    )
    chunks = chunk_document(_make_doc([small, big]))

    step1 = [c for c in chunks if c.heading_path == ["Procedure", "Step 1"]]
    step2 = [c for c in chunks if c.heading_path == ["Procedure", "Step 2"]]

    assert len(step1) == 1
    assert len(step2) >= 2, "big section should split"
    for c in chunks:
        assert c.heading_path, f"chunk {c.chunk_index} has empty heading_path"
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))