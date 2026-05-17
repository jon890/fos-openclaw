#!/usr/bin/env bash
# run_now.sh — entry point for all task runs.
# Requires: ~/ai-nodes/_shared/bin/track_task.sh (external dependency, see AGENTS.md)
set -euo pipefail

TASK_ROOT="${TASK_ROOT:-$HOME/ai-nodes/career-os}"
TRACKER="${TRACKER:-$HOME/ai-nodes/_shared/bin/track_task.sh}"
NOTIFY_SCRIPT="bun --env-file=$HOME/ai-nodes/career-os/.env run $HOME/ai-nodes/_shared/lib/notify_discord.ts"
FORMAT_COST="$HOME/ai-nodes/_shared/lib/format_cost_summary.ts"
LOCK_DIR="$TASK_ROOT/data/runtime/locks"
MODE="${1:-}"

mkdir -p "$LOCK_DIR"

# run_tracked <task-name> <label> <runner-cmd...>
#
# Wraps the runner with track_task.sh, captures the exit code, and sends a Discord
# completion / failure notification with a one-line cost summary (from
# `_shared/lib/format_cost_summary.ts`) appended. Exits with the runner's code.
#
# `label` is the human-readable subject for the notification, e.g. "${TOPIC}
# 스터디팩". The verb is auto-added: "[완료] ${label}" or "[실패] ${label} (exit N)".
run_tracked() {
  local task_name="$1"; shift
  local label="$1"; shift

  set +e
  "$TRACKER" "$TASK_ROOT" "$task_name" "$@"
  local code=$?
  set -e

  local cost_line=""
  cost_line="$(bun run "$FORMAT_COST" "$TASK_ROOT" "$task_name" 2>/dev/null || true)"

  if (( code == 0 )); then
    $NOTIFY_SCRIPT "[완료] ${label}${cost_line}" || true
  else
    $NOTIFY_SCRIPT "[실패] ${label} (exit ${code})${cost_line}" || true
  fi

  exit "$code"
}

case "$MODE" in
  *)
    echo "usage: run_now.sh (dispatcher case 0개 — plan023에서 디렉터리 폐기 예정)" >&2
    echo "모든 진입점은 native skill 직접 호출:" >&2
    echo "  claude -p '/position-recommender [args]' — ADR-030, plan022" >&2
    echo "  claude -p '/interview-prep-analyzer [args]' — ADR-002, plan017" >&2
    echo "  claude -p '/study-pack-writer <topic>' — ADR-002, plan013" >&2
    echo "  claude -p '/interview-asset-writer <topic>' — ADR-002, plan014" >&2
    echo "  claude -p '/study-topic-recommender' — ADR-002, plan016" >&2
    exit 1
    ;;
esac
