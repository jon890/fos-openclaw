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


def escape_tilde_ranges(content: str) -> str:
    """Escape bare tildes in prose to avoid accidental GFM strikethrough.

    GitHub Flavored Markdown treats multiple bare `~` characters in one paragraph
    as strikethrough delimiters. Study packs often contain ranges like `1~2분` or
    `60~100건`; when two ranges appear in one paragraph, rendering can be broken.

    Keep code fences and inline code unchanged, and skip already escaped tildes.
    """
    out: list[str] = []
    in_fence = False
    inline_code = False
    for line in content.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        chars: list[str] = []
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "`":
                inline_code = not inline_code
                chars.append(ch)
            elif ch == "~" and not inline_code:
                prev_ch = line[i - 1] if i > 0 else ""
                if prev_ch == "\\":
                    chars.append(ch)
                else:
                    chars.append("\\~")
            else:
                chars.append(ch)
            i += 1
        out.append("".join(chars))
    return "\n".join(out)


def validate_code_fence_languages(content: str) -> None:
    """Require a language tag on every opening fenced code block."""
    in_fence = False
    for line_no, line in enumerate(content.splitlines(), 1):
        stripped = line.lstrip()
        if not stripped.startswith("```"):
            continue
        if not in_fence:
            language = stripped[3:].strip()
            if not language:
                raise SystemExit(
                    "study-pack validation failed: code fence opened without language tag "
                    f"at line {line_no}"
                )
            in_fence = True
        else:
            in_fence = False


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
    validate_code_fence_languages(content)


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
    content = escape_tilde_ranges(content)

    out.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"Wrote study pack: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
