#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.request
from urllib.parse import quote

IGNORE_PREFIXES = [".claude/", ".git/", "node_modules/"]


def load_env(env_path):
    data = {}
    if not os.path.exists(env_path):
        return data
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip()
    return data


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../.."))
ENV_PATH = os.path.join(TASK_ROOT, "config", ".env")
ENV = load_env(ENV_PATH)

OWNER = ENV.get("GITHUB_REPO_OWNER", "jon890")
REPO = ENV.get("GITHUB_REPO_NAME", "fos-study")
BRANCH = ENV.get("GITHUB_REPO_BRANCH", "main")
GITHUB_TOKEN = ENV.get("GITHUB_TOKEN", "")

TREE_API = f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees/{BRANCH}?recursive=1"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}"


def request_headers():
    headers = {"User-Agent": "openclaw-career-os", "Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def get_json(url):
    req = urllib.request.Request(url, headers=request_headers())
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_text(url):
    req = urllib.request.Request(url, headers=request_headers())
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def ignored(path):
    return any(path == p[:-1] or path.startswith(p) for p in IGNORE_PREFIXES)


def walk():
    payload = get_json(TREE_API)
    out = []
    for item in payload.get("tree", []):
        item_path = item.get("path", "")
        if ignored(item_path):
            continue
        if item.get("type") == "blob" and item_path.lower().endswith(".md"):
            out.append(item_path)
    return out


def title_from_text(text, path):
    for line in text.splitlines():
        if line.strip().startswith("#"):
            return re.sub(r"^#+\s*", "", line.strip())
    return os.path.basename(path)


def main():
    if len(sys.argv) != 2:
        print("usage: collect_fos_study.py <output-json>", file=sys.stderr)
        sys.exit(1)
    if not GITHUB_TOKEN:
        print(f"error: missing GITHUB_TOKEN in {ENV_PATH}", file=sys.stderr)
        sys.exit(2)
    out_path = sys.argv[1]
    md_paths = walk()
    docs = []
    for path in md_paths:
        text = get_text(f"{RAW_BASE}/{quote(path)}")
        docs.append({
            "path": path,
            "title": title_from_text(text, path),
            "content": text,
            "chars": len(text)
        })
    payload = {
        "repo": f"{OWNER}/{REPO}",
        "branch": BRANCH,
        "count": len(docs),
        "documents": docs,
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
