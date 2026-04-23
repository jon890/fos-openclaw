#!/usr/bin/env bash
set -euo pipefail

SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTDIR="${1:-$(mktemp -d)}"
RAW_JSON="$OUTDIR/raw-search.json"
SUMMARY_JSON="$OUTDIR/summary.json"
COLLECTOR="$SKILL_ROOT/scripts/collect_sources.py"
NORMALIZER="$SKILL_ROOT/scripts/normalize_results.py"

mkdir -p "$OUTDIR"

python3 "$COLLECTOR" "$RAW_JSON"
python3 "$NORMALIZER" "$RAW_JSON" "$SUMMARY_JSON"

python3 - "$RAW_JSON" "$SUMMARY_JSON" <<'PY'
import json
import sys
raw_path, summary_path = sys.argv[1], sys.argv[2]
with open(raw_path, 'r', encoding='utf-8') as f:
    raw = json.load(f)
with open(summary_path, 'r', encoding='utf-8') as f:
    summary = json.load(f)

sources = {src.get('name'): src for src in raw.get('sources', [])}
assert 'Naver Land' in sources, 'missing Naver Land source'
assert 'Hogangnono' in sources, 'missing Hogangnono source'
assert 'KB Land' in sources, 'missing KB Land source'
assert sources['Naver Land'].get('status') in {'legacy-map-redirect', 'complex-entry-ok', 'ok'}, 'unexpected Naver status'
assert isinstance((summary.get('recentTransactions') or []), list), 'recentTransactions must be a list'
assert isinstance((summary.get('listingSummary') or {}).get('notes', []), list), 'listingSummary.notes must be a list'
print('smoke ok')
print('naver status:', sources['Naver Land'].get('status'))
print('naver articleCounts:', (sources['Naver Land'].get('numericSignals') or {}).get('articleCounts'))
if 'Naver Land Browser' in sources:
    print('naver browser status:', sources['Naver Land Browser'].get('status'))
print('recentTransactions:', len(summary.get('recentTransactions') or []))
PY

echo "raw: $RAW_JSON"
echo "summary: $SUMMARY_JSON"
