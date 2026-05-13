#!/usr/bin/env bash
set -euo pipefail

TASK_ROOT="${TASK_ROOT:-$HOME/ai-nodes/apartment}"
SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$TASK_ROOT/config/interior-reference-digest.json}"
DECISION_FILE="${DECISION_FILE:-$TASK_ROOT/docs/interior/lucky-5-1004-interior-decisions.md}"
REFERENCE_FILE="${REFERENCE_FILE:-$TASK_ROOT/docs/interior/interior-references.md}"
REPORT_DATE="${REPORT_DATE:-$(date +%F)}"
OUTDIR="${OUTPUT_ROOT:-$TASK_ROOT/data/interior-reference-digest}/$REPORT_DATE"
REQUEST_MD="$OUTDIR/request.md"
REPORT_MD="$OUTDIR/report.md"

mkdir -p "$OUTDIR"

cat > "$REQUEST_MD" <<EOF
# apartment-interior-reference-digest request

Run the apartment interior reference digest workflow.

Inputs:
- Config: $CONFIG_FILE
- Decision note: $DECISION_FILE
- Reference notebook: $REFERENCE_FILE
- Output report: $REPORT_MD

Required behavior:
1. Read the config and decision note.
2. Use web_search/web_fetch to find current interior references.
3. Prioritize 오늘의집, 네이버 블로그, and local/interior portfolio pages.
4. Score candidates against the config rubric.
5. Write the markdown digest to $REPORT_MD.
6. Append strong reference candidates to the reference notebook with stable R-00X IDs.
7. Do not auto-confirm decisions in the decision note; only list decision candidates unless the user explicitly confirmed.
8. If delivering to Discord, send only a concise summary with 3-5 recommendations and one decision question.

Do not contact vendors or request quotes.
EOF

cat > "$REPORT_MD" <<EOF
# 인테리어 레퍼런스 다이제스트

- 날짜: $REPORT_DATE
- 상태: 준비됨

이 파일은 runner가 만든 자리표시자입니다. 실제 다이제스트는 OpenClaw agent가 $REQUEST_MD 를 읽고 web_search/web_fetch로 후보를 조사한 뒤 덮어써야 합니다.
EOF

echo "$REQUEST_MD"
echo "$REPORT_MD"
