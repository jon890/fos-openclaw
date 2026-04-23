#!/usr/bin/env bash
set -euo pipefail

TASK_ROOT="${TASK_ROOT:-$HOME/ai-nodes/career-os}"
ENV_FILE="$TASK_ROOT/config/.env"
EXAMPLE_FILE="$TASK_ROOT/config/.env.example"

if [[ -f "$ENV_FILE" ]]; then
  echo "$ENV_FILE already exists"
  exit 0
fi

cp "$EXAMPLE_FILE" "$ENV_FILE"
echo "Created $ENV_FILE"
echo "Fill in GITHUB_TOKEN before running baseline collection."
