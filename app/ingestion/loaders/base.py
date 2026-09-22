"""Loader contract"""
from  __future__  import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

@dataclass(slots=True)
class Section:
    heading_path: list[str]
    heading_level: int
    content: str

@dataclass(slots=True)
class ParsedDocument:
    source_path: Path
    front_matter: dict[str, Any] = field(default_factory=dict)
    sections: list[Section] = field(default_factory=list)

    @property
    def title(self) -> str | None:
        return self.front_matter.get("title")
    
class Loader(Protocol):
    def load(self, path: Path) -> ParsedDocument:
        pass