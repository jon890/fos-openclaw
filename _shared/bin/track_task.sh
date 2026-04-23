#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: track_task.sh <task-root> <task-name> <command...>" >&2
  exit 1
fi

TASK_ROOT="$1"
shift
TASK_NAME="$1"
shift

LOG_DIR="$TASK_ROOT/logs"
mkdir -p "$LOG_DIR"

RUN_ID="$(date +%Y%m%dT%H%M%S)-$$"
START_TS="$(date --iso-8601=seconds)"
START_EPOCH="$(date +%s)"
STATUS="success"
EXIT_CODE=0

TOKEN_LOG="$LOG_DIR/token-usage.jsonl"
RUN_LOG="$LOG_DIR/task-runs.jsonl"
STATUS_DIR="$LOG_DIR/.usage-status"
mkdir -p "$STATUS_DIR"
START_STATUS="$STATUS_DIR/${RUN_ID}.start.status"
END_STATUS="$STATUS_DIR/${RUN_ID}.end.status"
COMMAND_FILE="$STATUS_DIR/${RUN_ID}.command.txt"
FILE_METRICS_JSON="$STATUS_DIR/${RUN_ID}.file-metrics.json"
CLAUDE_USAGE_FILE="$STATUS_DIR/${RUN_ID}.claude-usage.json"

export TRACK_TASK_RUN_ID="$RUN_ID"
export TRACK_TASK_LOG_DIR="$LOG_DIR"
export TRACK_TASK_STATUS_DIR="$STATUS_DIR"
export TRACK_TASK_CLAUDE_USAGE_FILE="$CLAUDE_USAGE_FILE"

printf '%q ' "$@" > "$COMMAND_FILE"
printf '\n' >> "$COMMAND_FILE"

openclaw status > "$START_STATUS" 2>/dev/null || true

capture_file_metrics() {
  python3 - "$TASK_ROOT" <<'PY'
import json
import os
import sys
from pathlib import Path

root = Path(sys.argv[1])
metrics = {
    "report_files": [],
    "input_files": [],
    "target_list_files": [],
    "report_bytes": 0,
    "input_bytes": 0,
    "target_list_bytes": 0,
    "target_list_line_count": 0,
}
if root.exists():
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        name = path.name
        rel = str(path.relative_to(root))
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if name == 'report.md':
            metrics['report_files'].append(rel)
            metrics['report_bytes'] += size
        elif name == 'analysis-input.md':
            metrics['input_files'].append(rel)
            metrics['input_bytes'] += size
        elif name == 'target-files.txt':
            metrics['target_list_files'].append(rel)
            metrics['target_list_bytes'] += size
            try:
                with path.open('r', encoding='utf-8') as f:
                    metrics['target_list_line_count'] += sum(1 for line in f if line.strip())
            except OSError:
                pass
print(json.dumps(metrics, ensure_ascii=False))
PY
}

START_METRICS="$(capture_file_metrics)"
printf '%s\n' "$START_METRICS" > "$FILE_METRICS_JSON"

set +e
"$@"
EXIT_CODE=$?
set -e
if [[ $EXIT_CODE -ne 0 ]]; then
  STATUS="failed"
fi

END_TS="$(date --iso-8601=seconds)"
END_EPOCH="$(date +%s)"
DURATION_SEC=$((END_EPOCH - START_EPOCH))

openclaw status > "$END_STATUS" 2>/dev/null || true
END_METRICS="$(capture_file_metrics)"

python3 - "$TASK_NAME" "$RUN_ID" "$START_TS" "$END_TS" "$STATUS" "$EXIT_CODE" "$DURATION_SEC" "$START_STATUS" "$END_STATUS" "$COMMAND_FILE" "$TOKEN_LOG" "$RUN_LOG" "$START_METRICS" "$END_METRICS" "$CLAUDE_USAGE_FILE" <<'PY'
import json
import re
import sys
from pathlib import Path

(
    task_name,
    run_id,
    start_ts,
    end_ts,
    status,
    exit_code,
    duration_sec,
    start_status_path,
    end_status_path,
    command_file,
    token_log,
    run_log,
    start_metrics_json,
    end_metrics_json,
    claude_usage_path,
) = sys.argv[1:]

def parse_status(path_str):
    text = Path(path_str).read_text(encoding='utf-8', errors='ignore') if Path(path_str).exists() else ''
    result = {
        'raw': text,
        'model': None,
        'tokens_in': None,
        'tokens_out': None,
        'cached_tokens': None,
        'cache_hit_percent': None,
    }
    m = re.search(r'Model:\s*([^·\n]+)', text)
    if m:
        result['model'] = m.group(1).strip()
    m = re.search(r'Tokens:\s*([0-9.]+)([kKmM]?)\s+in\s*/\s*([0-9.]+)([kKmM]?)\s+out', text)
    if m:
        def expand(num, suffix):
            value = float(num)
            suffix = suffix.lower()
            if suffix == 'k':
                value *= 1000
            elif suffix == 'm':
                value *= 1000000
            return int(value)
        result['tokens_in'] = expand(m.group(1), m.group(2))
        result['tokens_out'] = expand(m.group(3), m.group(4))
    m = re.search(r'Cache:\s*([0-9]+)%\s+hit\s+·\s+([0-9.]+)([kKmM]?)\s+cached', text)
    if m:
        result['cache_hit_percent'] = int(m.group(1))
        cached = float(m.group(2))
        suffix = m.group(3).lower()
        if suffix == 'k':
            cached *= 1000
        elif suffix == 'm':
            cached *= 1000000
        result['cached_tokens'] = int(cached)
    return result

start = parse_status(start_status_path)
end = parse_status(end_status_path)

# Diagnostic: if openclaw status text is present but none of Model/Tokens/Cache
# regexes matched, the output schema has likely drifted. Warn once so silent
# null-only jsonl rows are traceable instead of invisibly broken.
def _parsed_any(r):
    return any(r.get(k) is not None for k in ('model', 'tokens_in', 'tokens_out', 'cached_tokens', 'cache_hit_percent'))

for label, r in (('start', start), ('end', end)):
    if r['raw'] and not _parsed_any(r):
        preview = r['raw'].strip().splitlines()[:3]
        sys.stderr.write(
            f"[track_task] WARN: openclaw {label}-status parse matched 0 fields "
            f"(run_id={run_id}); first lines: {preview!r}\n"
        )
        break
start_metrics = json.loads(start_metrics_json)
end_metrics = json.loads(end_metrics_json)
claude_usage = {}
claude_usage_file = Path(claude_usage_path)
if claude_usage_file.exists():
    try:
        claude_usage = json.loads(claude_usage_file.read_text(encoding='utf-8', errors='ignore'))
    except Exception:
        claude_usage = {}

def delta(a, b):
    if a is None or b is None:
        return None
    return b - a

command = Path(command_file).read_text(encoding='utf-8', errors='ignore').strip()
usage = claude_usage.get('usage', {}) if isinstance(claude_usage, dict) else {}
model_usage = claude_usage.get('modelUsage', {}) if isinstance(claude_usage, dict) else {}
primary_model = None
if isinstance(model_usage, dict) and model_usage:
    primary_model = next(iter(model_usage.keys()))
model_usage_entry = model_usage.get(primary_model, {}) if primary_model else {}

entry = {
    'run_id': run_id,
    'task_name': task_name,
    'start_time': start_ts,
    'end_time': end_ts,
    'duration_sec': int(duration_sec),
    'status': status,
    'exit_code': int(exit_code),
    'command': command,
    'model': primary_model or end.get('model') or start.get('model'),
    'tokens_in_start': start.get('tokens_in'),
    'tokens_in_end': end.get('tokens_in'),
    'tokens_in_delta': usage.get('input_tokens', delta(start.get('tokens_in'), end.get('tokens_in'))),
    'tokens_out_start': start.get('tokens_out'),
    'tokens_out_end': end.get('tokens_out'),
    'tokens_out_delta': usage.get('output_tokens', delta(start.get('tokens_out'), end.get('tokens_out'))),
    'cached_tokens_start': start.get('cached_tokens'),
    'cached_tokens_end': end.get('cached_tokens'),
    'cached_tokens_delta': usage.get('cache_creation_input_tokens') if usage.get('cache_creation_input_tokens') is not None else delta(start.get('cached_tokens'), end.get('cached_tokens')),
    'cache_read_input_tokens': usage.get('cache_read_input_tokens'),
    'cache_hit_percent_start': start.get('cache_hit_percent'),
    'cache_hit_percent_end': end.get('cache_hit_percent'),
    'cost_usd': claude_usage.get('total_cost_usd') if isinstance(claude_usage, dict) else None,
    'claude_session_id': claude_usage.get('session_id') if isinstance(claude_usage, dict) else None,
    'claude_result_uuid': claude_usage.get('uuid') if isinstance(claude_usage, dict) else None,
    'service_tier': usage.get('service_tier'),
    'usage_raw': claude_usage,
    'model_usage': model_usage_entry,
    'file_metrics_before': start_metrics,
    'file_metrics_after': end_metrics,
    'report_bytes_delta': end_metrics.get('report_bytes', 0) - start_metrics.get('report_bytes', 0),
    'input_bytes_delta': end_metrics.get('input_bytes', 0) - start_metrics.get('input_bytes', 0),
    'target_list_bytes_delta': end_metrics.get('target_list_bytes', 0) - start_metrics.get('target_list_bytes', 0),
    'target_list_line_count_delta': end_metrics.get('target_list_line_count', 0) - start_metrics.get('target_list_line_count', 0),
}

for path in [token_log, run_log]:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
PY

exit "$EXIT_CODE"
