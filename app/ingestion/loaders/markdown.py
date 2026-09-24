from __future__ import annotations
import re
from pathlib import Path
from typing import Any
import yaml
from app.ingestion.loaders.base import ParsedDocument, Section

_FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL) # will detect an YAML front matter from md file, if present
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$") # capture the heading in md file (1 to 6)

class MarkdownLoader:
    '''Handling complete file parsing logic - reading it, extracting the metadata, sections and returning a parsed document'''
    def load(self, path: Path) -> ParsedDocument:
        text = path.read_text(encoding="utf-8")
        front_matter, body = self._extract_front_matter(text)
        sections = self._parse_sections(body)
        return ParsedDocument(
            source_path=path,
            front_matter=front_matter,
            sections=sections,
        )
    
    '''Use teh regex defined at top to capture the frint matter and return'''
    def _extract_front_matter(self, text: str) -> tuple[dict[str, Any], str]:
        match = _FRONT_MATTER_RE.match(text)
        if match is None:
            return {}, text
        try:
            # convert yaml strings to python dict b
            data = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError: 
            return {}, text
        if not isinstance(data, dict):
            return {}, text
        return data, text[match.end():] # return the dict and remaining data

    '''Convert the normal lines present in file to Section objects'''
    def _parse_sections(self, body: str) -> list[Section]:
    
        sections: list[Section] = []
        stack: list[tuple[int, str]] = []
        current_lines: list[str] = []
        current_level: int = 0

        def flush() -> None:
            if not stack:
                return
            content = "\n".join(current_lines).strip()
            if not content:
                return
            sections.append(
                Section(
                    heading_path=[text for _, text in stack],
                    heading_level=current_level,
                    content=content,
                )
            )

        for line in body.splitlines():
            match = _HEADING_RE.match(line)
            if match is None:
                current_lines.append(line)
                continue

            level = len(match.group(1))
            text = match.group(2).strip()

            # Skip the very first H1 — treat it as the document title, already
            # captured by front_matter or exposed via ParsedDocument.title.
            if level == 1 and not stack and not sections:
                continue

            # Close out whatever section we were building.
            flush()
            current_lines = []

            # Pop any headings at this level or deeper — they are siblings or
            # descendants of the incoming heading, not ancestors.
            while stack and stack[-1][0] >= level:
                stack.pop()

            stack.append((level, text))
            current_level = level

        flush()
        return sections