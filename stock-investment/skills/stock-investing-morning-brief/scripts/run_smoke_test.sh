#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="${TASK_ROOT:-$HOME/ai-nodes/stock-investment}"
REPORT_DATE="${REPORT_DATE:-smoke-$(date +%Y%m%dT%H%M%S)}" \
SKIP_NOTIFY=1 \
CLAUDE_TIMEOUT_SECONDS=90 \
"$TASK_ROOT/skills/stock-investing-morning-brief/scripts/run_report.sh"
