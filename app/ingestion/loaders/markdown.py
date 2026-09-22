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
        stack: list[str] = []                    
        current_level = 0                        
        buffer: list[str] = []                   

        # call this utlity every time we're about to move to new section - basically save and reset
        
        def flush() -> None:
            if not stack:
                return
            content = "\n".join(buffer).strip()
            if not content:
                return
            sections.append(
                Section(
                    heading_path=list(stack),    # copy: stack keeps mutating
                    heading_level=current_level,
                    content=content,
                )
            )
        # if its regular line, append it to buffer. Keep accumulating buffer and as soon as heading is encoutered, package the accumulated text and start working under new heading
        for line in body.splitlines():
            heading = _HEADING_RE.match(line)
            if heading is None:
                buffer.append(line)
                continue
            
            # if its heading, wat level it is
            level = len(heading.group(1))
            title = heading.group(2).strip()

            # First H1 is the document title. Skip it.
            if level == 1 and not stack and not sections:
                continue
            
            flush()
            buffer.clear() # clear buffer
            del stack[level - 1:]    # trim to depth level-1
            stack.append(title) # add new heading to stack
            current_level = level   # update active level

        flush()
        return sections