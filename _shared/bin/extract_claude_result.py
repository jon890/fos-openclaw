#!/usr/bin/env python3
"""Extract Claude CLI `--output-format json` result into a markdown report.

Usage: extract_claude_result.py <claude-json> <report-md> [usage-json]

- Reads the Claude CLI JSON payload from <claude-json>.
- Writes payload['result'] as markdown to <report-md>.
- If <usage-json> is provided (non-empty), writes the full payload to that path
  so track_task.sh can ingest token/cost metrics.
"""
import json
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) < 3 or len(argv) > 4:
        print(
            "usage: extract_claude_result.py <claude-json> <report-md> [usage-json]",
            file=sys.stderr,
        )
        return 1

    src = Path(argv[1])
    report = Path(argv[2])
    usage = Path(argv[3]) if len(argv) == 4 and argv[3] else None

    payload = json.loads(src.read_text(encoding="utf-8"))
    report.write_text((payload.get("result") or "").rstrip() + "\n", encoding="utf-8")
    if usage is not None:
        usage.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
