# Phase 3 — 5문서 + AGENTS.md 갱신 + 정적 검증 + push + trailing + index.json completed

**Model**: sonnet
**Status**: pending

---

## 목표

plan020 변경 (candidate-baseline-suggester skill 신규)을 5문서 + AGENTS.md에 반영. 정적 검증 + push + trailing + index.json completed 마킹.

## 사전 검증

```bash
cd /home/bifos/ai-nodes

# 1-A. phase-02 commit 존재
git log -1 --format='%s' | grep -q "plan020 phase-02" \
  || { echo "PHASE_BLOCKED: phase-02 commit 없음"; exit 2; }

# 1-B. skill 위치 존재
test -f career-os/.claude/skills/candidate-baseline-suggester/SKILL.md \
  || { echo "PHASE_BLOCKED: SKILL.md 부재"; exit 2; }

# 1-C. branch
[ "$(git branch --show-current)" = "main" ] \
  || { echo "PHASE_BLOCKED: branch != main"; exit 2; }

echo "사전 검증 OK"
```

## 작업 항목

### 1. docs 갱신

#### 1-A. prd.md "기능 목록" 표

`/candidate-baseline-suggester` (native) 행 추가:
- 산출물: `data/runtime/profile-refresh-suggestions/YYYY-MM-DD/` audit trail + config 자산 직접 갱신
- 외부 git push: 없음 (career-os 내부)
- 빈도: study-pack 누적 후 / 면접 시즌 시작 시

#### 1-B. flow.md

`/candidate-baseline-suggester` 섹션 추가. ASCII flow:

```
호출: claude -p "/candidate-baseline-suggester"
  ↓
Read: candidate-profile.md + baseline-core-files.json + prd.md "약점·강점"
      + data/study-progress.json + (선택) data/reports/baseline/<latest>/
      + fos-study git log (전체 history)
  ↓
Backup → data/runtime/profile-refresh-suggestions/YYYY-MM-DD/before/
  ↓
Claude 자연어 분석:
  - 강점 추가 후보 (fos-study 학습 증거)
  - 약점 outdated 후보 (학습 완료 → 주석 마킹)
  - baseline-core-files 추가 후보 (fos-study 새 핵심 파일)
  - weak_spots 평가 갱신
  ↓
Edit 적용 (Append + 주석 마킹):
  candidate-profile.md / baseline-core-files.json / prd.md / study-progress.json
  ↓
audit trail Write → after/ + diff/ + changes.md
  ↓
Discord 알림 [완료]
```

#### 1-C. code-architecture.md

`.claude/skills/candidate-baseline-suggester/` 트리 라인 추가 (SKILL.md만, references 없음).

#### 1-D. data-schema.md

`data/runtime/profile-refresh-suggestions/YYYY-MM-DD/` 구조 추가:
- `before/<asset>` — 갱신 전 사본
- `after/<asset>` — 갱신 후 사본
- `diff/<asset>.diff` — unified diff
- `changes.md` — 변경 사유 + fos-study path 출처

#### 1-E. AGENTS.md

native skill 진입점 목록에 `claude -p "/candidate-baseline-suggester"` 추가.

### 2. 정적 검증

```bash
cd /home/bifos/ai-nodes

# A. SKILL.md 필수 섹션
SKILL=career-os/.claude/skills/candidate-baseline-suggester/SKILL.md
test -f "$SKILL" || { echo "PHASE_FAILED: SKILL.md 부재"; exit 1; }
for s in "When to use" "Inputs" "Workflow" "Self-check" "Error handling" \
         "Append" "audit trail\|before/\|after/" "candidate-profile" "fos-study"; do
  grep -qE "$s" "$SKILL" || { echo "PHASE_FAILED: '$s' 누락"; exit 1; }
done
echo "[A] SKILL.md 검증 OK"

# B. 5문서 + AGENTS.md candidate-baseline-suggester 안내 추가
for d in prd flow code-architecture data-schema; do
  grep -q "candidate-baseline-suggester" "career-os/docs/$d.md" \
    || { echo "PHASE_FAILED: docs/$d.md candidate-baseline-suggester 안내 누락"; exit 1; }
done
grep -q "candidate-baseline-suggester" career-os/AGENTS.md \
  || { echo "PHASE_FAILED: AGENTS.md 안내 누락"; exit 1; }
echo "[B] docs 갱신 OK"

# C. 옛 subprocess 지시문 잔재 0 (6-7)
for kw in "Output only valid JSON" "Do not output markdown" "claude --json-schema"; do
  HITS=$(grep -rln "$kw" career-os/.claude/skills/candidate-baseline-suggester/ 2>/dev/null | wc -l)
  [ "$HITS" = "0" ] || { echo "PHASE_FAILED: '$kw' 잔재"; exit 1; }
done
echo "[C] 6-7 잔재 0 OK"

# D. plan020 phase commit history
PLAN_COMMITS=$(git log --oneline | grep -c "plan020 phase-")
[ "$PLAN_COMMITS" -ge 2 ] || { echo "PHASE_FAILED: plan020 commit $PLAN_COMMITS"; exit 1; }
echo "[D] plan020 commit history OK"

echo "=== 정적 검증 전부 통과 ==="
```

### 3. index.json status=completed

```bash
cd /home/bifos/ai-nodes
python3 - <<'PY'
import json
from pathlib import Path
p = Path("career-os/tasks/plan020-candidate-baseline-suggester/index.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["status"] = "completed"
d["current_phase"] = 3
for ph in d["phases"]:
    ph["status"] = "completed"
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("[index.json] completed")
PY
```

### 4. 최종 commit + push

```bash
cd /home/bifos/ai-nodes
HEAD_BEFORE=$(git rev-parse HEAD)

git add career-os/AGENTS.md \
        career-os/docs/ \
        career-os/tasks/plan020-candidate-baseline-suggester/index.json

git commit -m "$(cat <<'COMMIT_EOF'
docs(career-os): candidate-baseline-suggester 5문서 + AGENTS.md 갱신 + plan020 완료 (phase-03)

ADR-028 적용 마무리. plan020 phase-01~02 완료 후:
- prd.md 기능 표: /candidate-baseline-suggester native 진입점 추가
- flow.md: ASCII flow 박기 (Backup → 분석 → Edit → audit trail)
- code-architecture.md: .claude/skills/candidate-baseline-suggester/ 트리 추가
- data-schema.md: data/runtime/profile-refresh-suggestions/YYYY-MM-DD/
  구조 추가
- AGENTS.md: native 진입점 목록 갱신

정적 검증 4 항목:
- SKILL.md 필수 섹션 + 핵심 키워드
- 5문서 + AGENTS.md 안내
- 6-7 잔재 0
- plan020 phase commit history ≥2

native 진입점 누적 5개: study-pack / interview-asset / study-topic-recommender
(plan016) / interview-prep-analyzer (plan017) / candidate-baseline-suggester
(plan020).
COMMIT_EOF
)" || { echo "PHASE_FAILED: commit"; exit 1; }

HEAD_AFTER=$(git rev-parse HEAD)
COMMITS=$(git rev-list "$HEAD_BEFORE..$HEAD_AFTER" --count)
[ "$COMMITS" = "1" ] || { echo "PHASE_FAILED: commit 수 $COMMITS"; exit 1; }

git push origin main || { echo "PHASE_FAILED: push"; exit 1; }
echo "[4] commit + push OK"
```

### 5. trailing cleanup

```bash
cd /home/bifos/ai-nodes
if [ -n "$(git status --porcelain career-os/tasks/plan020-candidate-baseline-suggester/index.json)" ]; then
  git add career-os/tasks/plan020-candidate-baseline-suggester/index.json
  git commit -m "task(career-os): plan020 index.json commitSha 후기록"
  git push origin main
fi

DIRTY=$(git status --porcelain career-os/tasks/plan020-candidate-baseline-suggester/ | wc -l)
[ "$DIRTY" = "0" ] || { echo "PHASE_FAILED: trailing dirty"; exit 1; }
echo "trailing cleanup OK"
```

## 사용자 직접 처리 안내 (phase 외)

phase 종료 후 사용자가 환경에서 수행:

```bash
# 첫 실행 — backup 안전망 있어서 안전
claude -p "/candidate-baseline-suggester"

# 결과 확인
git status                                            # 갱신된 자산 확인
ls career-os/data/runtime/profile-refresh-suggestions/<date>/  # audit trail
cat career-os/data/runtime/profile-refresh-suggestions/<date>/changes.md
git diff career-os/config/candidate-profile.md       # 검토 후 git add + commit
```

## Blocked 조건

- phase-02 commit 없음 → `PHASE_BLOCKED` + `exit 2`
- SKILL.md 부재 → `PHASE_BLOCKED` + `exit 2`
- branch != main → `PHASE_BLOCKED` + `exit 2`
- 정적 검증 A~D 실패 → `PHASE_FAILED` + `exit 1`
- commit 수 ≠ 1 → `PHASE_FAILED` + `exit 1`
- push 실패 → `PHASE_FAILED` + `exit 1`
- trailing 후 dirty → `PHASE_FAILED` + `exit 1`

## 의도 메모

- 사용자 *수동 첫 실행*이 안전 — backup 안전망이 작동하는지 확인. cron 자동화는 별도 결정.
- 5문서 갱신은 4 문서 (prd / flow / code-architecture / data-schema). adr.md는 ADR-028 docs-first commit에서 이미 추가.
