#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
PROMPT_TEMPLATE = SKILL_ROOT / "references" / "naver-browser-prompt.md"
DEFAULT_URL = "https://new.land.naver.com/complexes/1649?tab=detail&rf=Y"


def build_prompt(url: str) -> str:
    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    return template.replace("{{NAVER_LAND_URL}}", url)


def run_claude_browser(prompt: str) -> dict:
    # Assumption: the local Claude/browser-capable setup is exposed through the user's Claude CLI environment.
    # This script intentionally stays thin and fails loudly until the exact browser invocation is settled.
    command = os.environ.get("NAVER_BROWSER_CLAUDE_COMMAND")
    if not command:
        raise RuntimeError("NAVER_BROWSER_CLAUDE_COMMAND is not set")

    proc = subprocess.run(
        command,
        input=prompt,
        text=True,
        shell=True,
        capture_output=True,
        check=True,
    )
    stdout = proc.stdout.strip()
    return json.loads(stdout)


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    prompt = build_prompt(url)

    try:
        browser_result = run_claude_browser(prompt)
        result = {
            "name": "Naver Land Browser",
            "url": url,
            "status": browser_result.get("status", "partial"),
            "finalUrl": browser_result.get("finalUrl"),
            "numericSignals": {
                "listingCounts": browser_result.get("listingCounts") or {},
            },
            "visibleSnippets": browser_result.get("visibleSnippets") or [],
            "priceTexts": browser_result.get("priceTexts") or [],
            "notes": browser_result.get("notes") or [],
            "uncertainty": browser_result.get("uncertainty") or [],
            "note": "Claude browser-assisted collection result",
        }
    except Exception as e:
        result = {
            "name": "Naver Land Browser",
            "url": url,
            "status": "error",
            "note": f"browser collection failed: {type(e).__name__}: {e}",
            "numericSignals": {},
            "visibleSnippets": [],
            "priceTexts": [],
            "notes": [],
            "uncertainty": ["browser fallback unavailable"],
        }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
