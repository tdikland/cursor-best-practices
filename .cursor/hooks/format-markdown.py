#!/usr/bin/env python3
"""
Cursor afterFileEdit hook: format and clean Markdown files after creation or modification.

Applies common Markdown best practices:
- Single trailing newline at end of file
- No trailing whitespace on lines
- Blank line before and after ATX headings (# ## ...)
- Space between # and heading text
- At most one consecutive blank line
"""

from pathlib import Path
import json
import re
import sys


def is_markdown_file(path: Path) -> bool:
    """Return True if path has a Markdown extension."""
    return path.suffix.lower() in (".md", ".markdown")


def clean_markdown(content: str) -> str:
    """
    Apply Markdown best-practices formatting to content.

    - Trim trailing whitespace on each line
    - Ensure blank line before and after ATX headings
    - Ensure space between # and heading text
    - Collapse multiple consecutive blank lines to one
    - Ensure exactly one trailing newline
    """
    lines = [line.rstrip() for line in content.splitlines()]
    out: list[str] = []
    prev_blank = False

    for i, line in enumerate(lines):
        is_blank = len(line) == 0
        is_atx = bool(re.match(r"^#{1,6}(?:[ \t]|$)", line))

        if is_blank:
            if not prev_blank:
                out.append("")
            prev_blank = True
            continue

        if is_atx:
            normalized = re.sub(r"^(#{1,6})[ \t]*", r"\1 ", line)
            if out and out[-1] != "":
                out.append("")
            out.append(normalized)
            next_non_blank = i + 1
            while next_non_blank < len(lines) and lines[next_non_blank] == "":
                next_non_blank += 1
            if next_non_blank < len(lines):
                out.append("")
            prev_blank = False
            continue

        out.append(line)
        prev_blank = False

    result = "\n".join(out)
    if result and not result.endswith("\n"):
        result += "\n"
    return result


def main() -> None:
    """Read hook JSON from stdin and format the edited file if it is Markdown."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    file_path = payload.get("file_path")
    if not file_path:
        sys.exit(0)

    path = Path(file_path)
    if not path.is_file() or not is_markdown_file(path):
        sys.exit(0)

    text = path.read_text(encoding="utf-8", errors="replace")
    cleaned = clean_markdown(text)
    if cleaned != text:
        path.write_text(cleaned, encoding="utf-8")

    sys.exit(0)


if __name__ == "__main__":
    main()
