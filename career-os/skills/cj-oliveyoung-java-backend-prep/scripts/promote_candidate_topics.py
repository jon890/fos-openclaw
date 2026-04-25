#!/usr/bin/env python3
import json
import sys
from pathlib import Path
TASK_ROOT = Path.home() / "ai-nodes" / "career-os"
CONFIG = TASK_ROOT / "config"
if len(sys.argv) != 3:
    print("usage: promote_candidate_topics.py <study|live-coding> <key-or-slug>", file=sys.stderr)
    sys.exit(1)
mode, target = sys.argv[1], sys.argv[2]
if mode == "study":
    candidates = json.loads((CONFIG / "study-topic-candidates.json").read_text(encoding="utf-8")).get("topics", [])
    main_cfg = json.loads((CONFIG / "study-pack-topics.json").read_text(encoding="utf-8"))
    for item in candidates:
        if item.get("key") != target:
            continue
        promotion = item.get("promotionTarget")
        if not promotion:
            raise SystemExit(f"candidate has no promotionTarget: {target}")
        main_cfg[target] = promotion
        (CONFIG / "study-pack-topics.json").write_text(json.dumps(main_cfg, ensure_ascii=False, indent=2) + "
", encoding="utf-8")
        print(f"promoted study candidate: {target}")
        raise SystemExit(0)
    raise SystemExit(f"study candidate not found: {target}")
if mode == "live-coding":
    candidates = json.loads((CONFIG / "live-coding-seed-candidates.json").read_text(encoding="utf-8")).get("seeds", [])
    main_cfg = json.loads((CONFIG / "live-coding-seed-pool.json").read_text(encoding="utf-8"))
    for item in candidates:
        if item.get("slug") != target:
            continue
        if any(seed.get("slug") == target for seed in main_cfg.get("seeds", [])):
            raise SystemExit(f"live-coding seed already exists in primary pool: {target}")
        main_cfg.setdefault("seeds", []).append(item)
        (CONFIG / "live-coding-seed-pool.json").write_text(json.dumps(main_cfg, ensure_ascii=False, indent=2) + "
", encoding="utf-8")
        print(f"promoted live-coding candidate: {target}")
        raise SystemExit(0)
    raise SystemExit(f"live-coding candidate not found: {target}")
raise SystemExit(f"unsupported mode: {mode}")
