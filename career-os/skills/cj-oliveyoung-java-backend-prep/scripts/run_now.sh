#!/usr/bin/env bash
# run_now.sh — entry point for all task runs.
# Requires: ~/ai-nodes/_shared/bin/track_task.sh (external dependency, see AGENTS.md)
set -euo pipefail

TASK_ROOT="${TASK_ROOT:-$HOME/ai-nodes/career-os}"
TRACKER="${TRACKER:-$HOME/ai-nodes/_shared/bin/track_task.sh}"
NOTIFY_SCRIPT="$TASK_ROOT/skills/cj-oliveyoung-java-backend-prep/scripts/notify_discord.sh"
MODE="${1:-baseline}"

case "$MODE" in
  baseline)
    exec "$TRACKER" "$TASK_ROOT" "career-os:baseline" \
      "$TASK_ROOT/skills/cj-oliveyoung-java-backend-prep/scripts/run_baseline.sh"
    ;;
  daily)
    # Optional second arg: topic key from config/topic-file-map.json
    # e.g.  run_now.sh daily jpa-n+1
    # Omit to auto-select the most overdue weak spot from data/study-progress.json
    DAILY_TOPIC="${2:-}" exec "$TRACKER" "$TASK_ROOT" "career-os:daily" \
      "$TASK_ROOT/skills/cj-oliveyoung-java-backend-prep/scripts/run_daily.sh"
    ;;
  study-pack)
    TOPIC="${2:-}"
    if [[ -z "$TOPIC" ]]; then
      echo "usage: run_now.sh study-pack <topic>" >&2
      echo "  topic keys: see config/study-pack-topics.json" >&2
      exit 1
    fi

    "$NOTIFY_SCRIPT" "[시작] ${TOPIC} 스터디팩 생성 시작"

    MAINTAINER_CONFIG="$TASK_ROOT/config/study-pack-maintainer-topics.json"
    if [[ -z "${TOPIC_CONFIG_OVERRIDE:-}" && -f "$MAINTAINER_CONFIG" ]] && python3 - <<'PY' "$MAINTAINER_CONFIG" "$TOPIC"
import json, sys
from pathlib import Path
cfg = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
sys.exit(0 if sys.argv[2] in cfg else 1)
PY
    then
      RESOLVER="$TASK_ROOT/skills/study-pack-maintainer/scripts/resolve_maintainer_topic.py"
      eval "$(python3 "$RESOLVER" "$MAINTAINER_CONFIG" "$TOPIC")"

      set +e
      "$TRACKER" "$TASK_ROOT" "career-os:study-pack:$TOPIC" \
        "$TASK_ROOT/skills/study-pack-maintainer/scripts/run_maintainer.sh"
      code=$?
      set -e

      if (( code == 0 )); then
        "$NOTIFY_SCRIPT" "[완료] ${TOPIC} 스터디팩 생성 완료"
      else
        "$NOTIFY_SCRIPT" "[실패] ${TOPIC} 스터디팩 생성 실패 (exit ${code})" || true
      fi
      exit "$code"
    fi

    RESOLVER="$TASK_ROOT/skills/study-pack-writer/scripts/resolve_study_pack_topic.py"
    TOPIC_CONFIG="${TOPIC_CONFIG_OVERRIDE:-$TASK_ROOT/config/study-pack-topics.json}"
    eval "$(python3 "$RESOLVER" "$TOPIC_CONFIG" "$TOPIC")"

    set +e
    "$TRACKER" "$TASK_ROOT" "career-os:study-pack:$TOPIC" \
      "$TASK_ROOT/skills/study-pack-writer/scripts/run_study_pack.sh"
    code=$?
    set -e

    if (( code == 0 )); then
      "$NOTIFY_SCRIPT" "[완료] ${TOPIC} 스터디팩 생성 완료"
    else
      "$NOTIFY_SCRIPT" "[실패] ${TOPIC} 스터디팩 생성 실패 (exit ${code})" || true
    fi
    exit "$code"
    ;;
  question-bank)
    TOPIC="${2:-}"
    if [[ -z "$TOPIC" ]]; then
      echo "usage: run_now.sh question-bank <topic>" >&2
      echo "  topic keys: see config/experience-question-bank-topics.json" >&2
      exit 1
    fi

    RESOLVER="$TASK_ROOT/skills/experience-question-bank-writer/scripts/resolve_question_bank_topic.py"
    TOPIC_CONFIG="$TASK_ROOT/config/experience-question-bank-topics.json"
    eval "$(python3 "$RESOLVER" "$TOPIC_CONFIG" "$TOPIC")"

    exec "$TRACKER" "$TASK_ROOT" "career-os:question-bank:$TOPIC" \
      "$TASK_ROOT/skills/experience-question-bank-writer/scripts/run_question_bank.sh"
    ;;
  maintain-study-pack)
    TOPIC="${2:-}"
    if [[ -z "$TOPIC" ]]; then
      echo "usage: run_now.sh maintain-study-pack <topic>" >&2
      echo "  topic keys: see config/study-pack-maintainer-topics.json" >&2
      exit 1
    fi

    RESOLVER="$TASK_ROOT/skills/study-pack-maintainer/scripts/resolve_maintainer_topic.py"
    TOPIC_CONFIG="$TASK_ROOT/config/study-pack-maintainer-topics.json"
    eval "$(python3 "$RESOLVER" "$TOPIC_CONFIG" "$TOPIC")"

    exec "$TRACKER" "$TASK_ROOT" "career-os:maintain-study-pack:$TOPIC" \
      "$TASK_ROOT/skills/study-pack-maintainer/scripts/run_maintainer.sh"
    ;;
  master)
    TOPIC="${2:-senior-backend-master-playbook}"

    RESOLVER="$TASK_ROOT/skills/interview-master-writer/scripts/resolve_master_topic.py"
    TOPIC_CONFIG="$TASK_ROOT/config/interview-master-topics.json"
    eval "$(python3 "$RESOLVER" "$TOPIC_CONFIG" "$TOPIC")"

    exec "$TRACKER" "$TASK_ROOT" "career-os:master:$TOPIC" \
      "$TASK_ROOT/skills/interview-master-writer/scripts/run_master.sh"
    ;;
  smoke)
    exec "$TRACKER" "$TASK_ROOT" "career-os:smoke" \
      "$TASK_ROOT/skills/cj-oliveyoung-java-backend-prep/scripts/run_smoke_test.sh"
    ;;
  *)
    echo "usage: run_now.sh [baseline | daily [topic] | study-pack <topic> | question-bank <topic> | maintain-study-pack <topic> | master [topic] | smoke]" >&2
    echo "  daily topic keys: see config/topic-file-map.json" >&2
    echo "  study-pack topic keys: see config/study-pack-topics.json" >&2
    echo "  question-bank topic keys: see config/experience-question-bank-topics.json" >&2
    echo "  maintain-study-pack topic keys: see config/study-pack-maintainer-topics.json" >&2
    echo "  master topic keys: see config/interview-master-topics.json (default: senior-backend-master-playbook)" >&2
    exit 1
    ;;
esac
