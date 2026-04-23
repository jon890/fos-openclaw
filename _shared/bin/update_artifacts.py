#!/usr/bin/env python3
"""Update the generated-artifacts.json index after a successful publish.

Usage: update_artifacts.py <artifacts-json> <topic> <output-path> <commit-hash> [--kind KIND]

- <artifacts-json>: path to data/generated-artifacts.json (created if missing).
- <topic>: topic key identifying the artifact.
- <output-path>: relative path of the markdown artifact inside fos-study.
- <commit-hash>: latest commit hash for the artifact.
- --kind: override the artifact kind. Defaults to 'live-coding' when
  '/live-coding/' appears in <output-path>, otherwise 'study-pack'.

Shape:
    {
      "artifacts": [
        {
          "topic": str,
          "kind": str,           # "study-pack" | "live-coding" | "question-bank" | ...
          "outputPath": str,
          "createdAt": iso,
          "updatedAt": iso,
          "lastCommit": str
        },
        ...
      ]
    }
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def infer_kind(output_path: str) -> str:
    if "/live-coding/" in output_path:
        return "live-coding"
    return "study-pack"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts_json")
    parser.add_argument("topic")
    parser.add_argument("output_path")
    parser.add_argument("commit_hash")
    parser.add_argument(
        "--kind",
        default=None,
        help="override kind; defaults to 'live-coding' or 'study-pack' based on path",
    )
    args = parser.parse_args(argv[1:])

    path = Path(args.artifacts_json)
    kind = args.kind or infer_kind(args.output_path)
    now = datetime.now(timezone.utc).astimezone().isoformat()

    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"artifacts": []}

    artifacts = data.setdefault("artifacts", [])
    existing = next(
        (a for a in artifacts if a.get("outputPath") == args.output_path), None
    )
    if existing:
        existing["updatedAt"] = now
        existing["lastCommit"] = args.commit_hash
        existing["topic"] = args.topic
        existing["kind"] = kind
    else:
        artifacts.append(
            {
                "topic": args.topic,
                "kind": kind,
                "outputPath": args.output_path,
                "createdAt": now,
                "updatedAt": now,
                "lastCommit": args.commit_hash,
            }
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
