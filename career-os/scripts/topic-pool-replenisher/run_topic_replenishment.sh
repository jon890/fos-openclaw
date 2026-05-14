#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="${TASK_ROOT:-$HOME/ai-nodes/career-os}"
SCRIPT="$TASK_ROOT/scripts/topic-pool-replenisher/replenish_topic_reservoir.ts"
"$SCRIPT"
cat "$TASK_ROOT/data/runtime/topic-replenishment.md"
