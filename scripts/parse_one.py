"""Parse md file and return structure"""
from __future__ import annotations

import argparse
from pathlib import Path
from app.ingestion.loaders.markdown import MarkdownLoader

def main() -> None:
    parser = argparse.ArgumentParser() # parse md file
    parser.add_argument("path", type=Path) #path of the md file
    args = parser.parse_args()

    if not args.path.exists():
        raise SystemExit(f"File not found: {args.path}")

    doc = MarkdownLoader().load(args.path) # runs the parser and return ParsedDocument 

    # structurally, this ParsedDocumen has front matter and multiple sections 9along with title captured in ParsedDocument class we defined
    # metadata extraction
    doc_id = doc.front_matter.get("id", "—")
    title = doc.title or "(untitled)"
    doc_type = doc.front_matter.get("doc_type", "—")
    # header summary
    print(f"{doc_id} | {title} | {doc_type}")
    print()
    print(f"Sections ({len(doc.sections)}):")
    #section summary
    for section in doc.sections:
        path_str = str(section.heading_path)
        print(f"  {path_str:<50}  {len(section.content):>5} chars")


if __name__ == "__main__":
    main()