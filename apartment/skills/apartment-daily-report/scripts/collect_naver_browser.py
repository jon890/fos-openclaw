#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
PROMPT_TEMPLATE = SKILL_ROOT / "references" / "naver-browser-prompt.md"
DEFAULT_URL = "https://new.land.naver.com/complexes/1649?tab=detail&rf=Y"


def build_prompt(url: str) -> str:
    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    return template.replace("{{NAVER_LAND_URL}}", url)


def run_ab(args, session: str):
    env = {**os.environ, "AGENT_BROWSER_SESSION_NAME": session}
    env.setdefault("AGENT_BROWSER_ARGS", "--no-sandbox")
    return subprocess.run(["agent-browser", *args], check=True, capture_output=True, text=True, env=env)


def run_agent_browser_probe(url: str) -> dict:
    # Keep this deterministic and lightweight: collect visible evidence first,
    # then let Claude summarize/shape it if desired.
    session = os.environ.get("NAVER_BROWSER_SESSION_NAME", "apartment-naver")

    run_ab(["open", "https://fin.land.naver.com/complexes/1649?tab=detail"], session)
    run_ab(["wait", "--load", "networkidle"], session)
    run_ab(["snapshot", "-i", "--json"], session)

    # Try the visible search flow so Claude gets a richer snapshot than the raw landing map.
    run_ab(["click", "@e10"], session)
    run_ab(["snapshot", "-i", "--json"], session)
    run_ab(["fill", "@e10", os.environ.get("TARGET_NAME", "엘지원앙아파트")], session)
    run_ab(["press", "Enter"], session)
    run_ab(["wait", "--load", "networkidle"], session)

    snap = run_ab(["snapshot", "-i", "--json"], session)
    current_url = run_ab(["get", "url"], session)
    return {
        "snapshotJson": json.loads(snap.stdout),
        "finalUrl": current_url.stdout.strip(),
    }


def run_claude_on_browser_probe(prompt: str, probe: dict) -> dict:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".json") as f:
        json.dump(probe, f, ensure_ascii=False, indent=2)
        probe_path = f.name

    full_prompt = (
        prompt
        + "\n\n다음은 agent-browser snapshot JSON 과 현재 URL이다.\n"
        + f"- snapshot 파일: {probe_path}\n"
        + "이 파일을 읽고 visible evidence만 바탕으로 JSON을 작성한다."
    )

    proc = subprocess.run(
        ["claude", "--permission-mode", "bypassPermissions", "--print", full_prompt],
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(proc.stdout.strip())


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    prompt = build_prompt(url)

    try:
        probe = run_agent_browser_probe(url)
        browser_result = run_claude_on_browser_probe(prompt, probe)
        result = {
            "name": "Naver Land Browser",
            "url": url,
            "status": browser_result.get("status", "partial"),
            "finalUrl": browser_result.get("finalUrl") or probe.get("finalUrl"),
            "numericSignals": {
                "listingCounts": browser_result.get("listingCounts") or {},
            },
            "visibleSnippets": browser_result.get("visibleSnippets") or [],
            "priceTexts": browser_result.get("priceTexts") or [],
            "notes": browser_result.get("notes") or [],
            "uncertainty": browser_result.get("uncertainty") or [],
            "note": "Claude + agent-browser assisted collection result",
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
