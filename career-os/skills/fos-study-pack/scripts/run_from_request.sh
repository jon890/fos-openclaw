#!/usr/bin/env bash
set -euo pipefail

TASK_ROOT="${TASK_ROOT:-$HOME/ai-nodes/career-os}"
REQUEST_TEXT="${1:-}"
if [[ -z "$REQUEST_TEXT" ]]; then
  echo "usage: run_from_request.sh '<freeform study-pack request>'" >&2
  exit 1
fi

RESOLVER="$TASK_ROOT/skills/fos-study-pack/scripts/resolve_freeform_study_pack.py"
STUDY_CFG="$TASK_ROOT/config/study-pack-topics.json"
MAINT_CFG="$TASK_ROOT/config/study-pack-maintainer-topics.json"
RUNNER="$TASK_ROOT/skills/cj-oliveyoung-java-backend-prep/scripts/run_now.sh"

RESOLUTION_JSON="$(python3 "$RESOLVER" "$STUDY_CFG" "$MAINT_CFG" "$REQUEST_TEXT")"
MODE="$(python3 - <<'PY' "$RESOLUTION_JSON"
import json, sys
print(json.loads(sys.argv[1])['mode'])
PY
)"
TOPIC="$(python3 - <<'PY' "$RESOLUTION_JSON"
import json, sys
print(json.loads(sys.argv[1])['topic'])
PY
)"

if [[ "$MODE" == "study-pack" ]]; then
  exec bash "$RUNNER" study-pack "$TOPIC"
fi

echo "unresolved study-pack request: $REQUEST_TEXT" >&2
python3 - <<'PY' "$RESOLUTION_JSON"
import json, sys
print(json.dumps(json.loads(sys.argv[1]), ensure_ascii=False, indent=2))
PY
exit 2
