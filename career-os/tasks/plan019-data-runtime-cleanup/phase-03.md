# Phase 3 — 정적 검증 + push + trailing + index.json completed

**Model**: sonnet
**Status**: pending

---

## 목표

phase-01/02 누적 결과 정적 검증. 모든 commit push + index.json status=completed + trailing.

## 사전 검증

```bash
cd /home/bifos/ai-nodes

# 1-A. phase-02 commit 존재
git log -1 --format='%s' | grep -q "plan019 phase-02" \
  || { echo "PHASE_BLOCKED: phase-02 commit 없음"; exit 2; }

# 1-B. branch
[ "$(git branch --show-current)" = "main" ] \
  || { echo "PHASE_BLOCKED: branch != main"; exit 2; }

echo "사전 검증 OK"
```

## 작업 항목

### 1. 정적 검증

```bash
cd /home/bifos/ai-nodes

# A. data/runtime/ Python 잔재 0
HITS=$(find career-os/data/runtime/ -name "*.py" 2>/dev/null | wc -l)
[ "$HITS" = "0" ] || { echo "PHASE_FAILED: data/runtime Python $HITS 잔존"; exit 1; }

# B. 옛 폐기 skill 잔재 0
for f in "bootcamp-summary.md" "cj-foodville-bootcamp-summary.md" \
         "topic-replenishment.json" "topic-replenishment.md" \
         "freeform-study-pack-topic.json" "live-coding-generated-topic.json"; do
  test ! -f "career-os/data/runtime/$f" \
    || { echo "PHASE_FAILED: $f 잔존"; exit 1; }
done

# C. 활성 파일 보존 (Category A — 건드리면 안 됨)
for active in "position-recommendation.md" "wanted-server-postings.md" \
              "position-postings-augmented.md" "topic-inventory.json" \
              "morning-topic-recommendation.md"; do
  test -f "career-os/data/runtime/$active" \
    || { echo "PHASE_FAILED: 활성 파일 $active 누락 (실수 삭제 의심)"; exit 1; }
done

# D. plan019 phase commit history
PLAN_COMMITS=$(git log --oneline | grep -c "plan019 phase-")
[ "$PLAN_COMMITS" -ge 2 ] || { echo "PHASE_FAILED: phase commit $PLAN_COMMITS (expected ≥2)"; exit 1; }

echo "=== 정적 검증 전부 통과 ==="
```

### 2. index.json status=completed

```bash
cd /home/bifos/ai-nodes
python3 - <<'PY'
import json
from pathlib import Path
p = Path("career-os/tasks/plan019-data-runtime-cleanup/index.json")
data = json.loads(p.read_text(encoding="utf-8"))
data["status"] = "completed"
data["current_phase"] = 3
for phase in data["phases"]:
    phase["status"] = "completed"
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("[index.json] completed")
PY
```

### 3. 최종 commit + push

```bash
cd /home/bifos/ai-nodes
HEAD_BEFORE=$(git rev-parse HEAD)

git add career-os/tasks/plan019-data-runtime-cleanup/index.json

git commit -m "$(cat <<'COMMIT_EOF'
task(career-os): plan019 index.json status=completed (phase-03)

plan019 단계 1~3 통과:
- phase-01: data/runtime + config audit 보고서 산출
- phase-02: stale 일괄 폐기 + augment_positions.py 위치 정리
- phase-03: 정적 검증 통과

정적 검증 4 항목:
- data/runtime Python 잔재 0
- 폐기 skill 산출물 잔재 0 (bootcamp/replenishment/freeform/live-coding)
- 활성 파일 (Category A) 보존 확인
- plan019 phase commit history ≥2

plan020 (candidate-baseline-suggester skill) 계획은 별도 /planning 세션.
COMMIT_EOF
)" || { echo "PHASE_FAILED: commit"; exit 1; }

HEAD_AFTER=$(git rev-parse HEAD)
COMMITS=$(git rev-list "$HEAD_BEFORE..$HEAD_AFTER" --count)
[ "$COMMITS" = "1" ] || { echo "PHASE_FAILED: commit 수 $COMMITS"; exit 1; }

git push origin main || { echo "PHASE_FAILED: push"; exit 1; }
echo "[3] commit + push OK"
```

### 4. trailing cleanup

```bash
cd /home/bifos/ai-nodes
if [ -n "$(git status --porcelain career-os/tasks/plan019-data-runtime-cleanup/index.json)" ]; then
  git add career-os/tasks/plan019-data-runtime-cleanup/index.json
  git commit -m "task(career-os): plan019 index.json commitSha 후기록"
  git push origin main
fi

DIRTY=$(git status --porcelain career-os/tasks/plan019-data-runtime-cleanup/ | wc -l)
[ "$DIRTY" = "0" ] || { echo "PHASE_FAILED: trailing dirty"; exit 1; }
echo "trailing cleanup OK"
```

## Blocked 조건

- phase-02 commit 없음 → `PHASE_BLOCKED` + `exit 2`
- branch != main → `PHASE_BLOCKED` + `exit 2`
- 정적 검증 A~D 실패 → `PHASE_FAILED` + `exit 1`
- commit 수 ≠ 1 → `PHASE_FAILED` + `exit 1`
- push 실패 → `PHASE_FAILED` + `exit 1`

## 의도 메모

- Category A 보존 검증 (활성 파일이 실수로 삭제됐는지) — phase-02 안전망.
- plan020 (candidate-baseline-suggester)은 본 plan019 외 — 별도 /planning 세션에서.
