#!/usr/bin/env python3
"""Extract the markdown body from Claude CLI JSON, validate it, and write it out.

Usage: extract_and_validate_study_pack.py <raw-json> <output-md>

Validations:
- JSON payload must be non-empty.
- After trimming a trailing code fence and any preamble before the first
  markdown heading, the body must start with '#'.
- The body must not begin with any of the known bad prefixes that indicate
  the model wrote a summary instead of the full document.
- Final body must be at least 80 non-empty lines to count as a full study pack.
"""
import json
import re
import sys
from pathlib import Path

BAD_PREFIXES = (
    "The hook warning",
    "The file is at",
    "파일이 생성되었다",
    "문서 구성",
    "문서 구성 요약",
    "다음과 같다",
    "아래와 같다",
    "`database/",
)
MIN_LINES = 80


def strip_to_markdown_body(raw_text: str) -> str:
    content = raw_text.strip()
    content = re.sub(r"\n```\s*$", "", content)
    for i, line in enumerate(content.splitlines()):
        if line.lstrip().startswith("#"):
            content = "\n".join(content.splitlines()[i:]).strip()
            break
    return content


def validate(content: str) -> None:
    if not content:
        raise SystemExit("study-pack validation failed: generated file is empty")
    if not content.startswith("#"):
        raise SystemExit(
            "study-pack validation failed: generated file does not start with markdown heading"
        )
    if any(content.startswith(prefix) for prefix in BAD_PREFIXES):
        raise SystemExit(
            "study-pack validation failed: generated file looks like a summary report, not the full document"
        )
    if len(content.splitlines()) < MIN_LINES:
        raise SystemExit(
            "study-pack validation failed: generated file is too short, likely not a full study pack"
        )


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(
            "usage: extract_and_validate_study_pack.py <raw-json> <output-md>",
            file=sys.stderr,
        )
        return 1

    src = Path(argv[1])
    out = Path(argv[2])

    raw = src.read_text(encoding="utf-8", errors="replace").strip()
    if not raw:
        raise SystemExit("study-pack validation failed: claude JSON output is empty")

    payload = json.loads(raw)
    text = payload.get("result", "")
    content = strip_to_markdown_body(text)
    validate(content)

    out.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"Wrote study pack: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
