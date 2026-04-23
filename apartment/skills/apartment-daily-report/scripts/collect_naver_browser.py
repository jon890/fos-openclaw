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
DIRECT_COMPLEX_URL = "https://fin.land.naver.com/complexes/1649?articleTradeTypes=A1&realEstateTypes=A01&space=69.4218-85.9508&tab=article&tradeTypes=A1"


def build_prompt(url: str) -> str:
    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    return template.replace("{{NAVER_LAND_URL}}", url)


def run_ab(args, session: str):
    env = {**os.environ, "AGENT_BROWSER_SESSION_NAME": session}
    env.setdefault("AGENT_BROWSER_ARGS", "--no-sandbox")
    return subprocess.run(["agent-browser", *args], check=True, capture_output=True, text=True, env=env)


def capture_snapshot(session: str, label: str):
    snap = run_ab(["snapshot", "-i", "--json"], session)
    return {
        "label": label,
        "snapshot": json.loads(snap.stdout),
    }


def try_step(session: str, snapshots: list, label: str, action_args: list):
    try:
        run_ab(action_args, session)
        run_ab(["wait", "1000"], session)
        snapshots.append(capture_snapshot(session, label))
        return True
    except Exception:
        return False


def run_agent_browser_probe(url: str) -> dict:
    session = os.environ.get("NAVER_BROWSER_SESSION_NAME", "apartment-naver")
    snapshots = []

    run_ab(["open", DIRECT_COMPLEX_URL], session)
    run_ab(["wait", "--load", "networkidle"], session)
    snapshots.append(capture_snapshot(session, "opened-direct-complex-url"))

    try_step(session, snapshots, "after-click-e19", ["click", "@e19"])
    try_step(session, snapshots, "after-click-e49", ["click", "@e49"])
    try_step(session, snapshots, "after-click-e17", ["click", "@e17"])
    try_step(session, snapshots, "after-click-e18", ["click", "@e18"])
    try_step(session, snapshots, "after-click-e37", ["click", "@e37"])
    try_step(session, snapshots, "after-click-e40", ["click", "@e40"])

    current_url = run_ab(["get", "url"], session)
    return {
        "finalUrl": current_url.stdout.strip(),
        "snapshots": snapshots,
    }


def run_claude_on_browser_probe(prompt: str, probe: dict) -> dict:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".json") as f:
        json.dump(probe, f, ensure_ascii=False, indent=2)
        probe_path = f.name

    full_prompt = (
        prompt
        + "\n\n다음은 agent-browser 단계별 snapshot JSON 과 현재 URL이다.\n"
        + f"- snapshot 파일: {probe_path}\n"
        + "이 파일을 읽고 각 단계에서 visible evidence가 어떻게 바뀌는지 본 뒤, 가장 정보가 많은 단계 기준으로 JSON을 작성한다.\n"
        + "특히 다음을 확인하려고 시도한다: 단지 상세 패널, 면적/평형 버튼, 매물 개수, 가격 텍스트, 59A 또는 전용 59㎡ 관련 표시."
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
