# Phase 2 — career-os/.claude/skills/candidate-baseline-suggester/ 생성 + SKILL.md Write 적용

**Model**: sonnet
**Status**: pending

---

## 목표

phase-01 draft의 SKILL.md를 `career-os/.claude/skills/candidate-baseline-suggester/SKILL.md`에 Write 적용. 디렉터리 생성 + byte-for-byte diff 검증.

**범위 외**: docs 갱신 (phase-03), 정적 검증·push (phase-03).

## 관련 docs

- phase-01 commit — SKILL.md draft 작성 완료
- `skills/plan-and-build/references/common-pitfalls.md` 6-6 (Write 위장)

## 사전 검증

```bash
cd /home/bifos/ai-nodes

# 1-A. phase-01 commit 존재
git log -1 --format='%s' | grep -q "plan020 phase-01" \
  || { echo "PHASE_BLOCKED: phase-01 commit 없음"; exit 2; }

# 1-B. draft 부재 시 abort
DRAFT=career-os/tasks/plan020-candidate-baseline-suggester/draft/SKILL.md
test -f "$DRAFT" || { echo "PHASE_BLOCKED: draft 부재"; exit 2; }

# 1-C. 신규 위치 (아직 부재)
test ! -d career-os/.claude/skills/candidate-baseline-suggester \
  || { echo "PHASE_BLOCKED: skill 디렉터리 이미 존재"; exit 2; }

echo "사전 검증 OK"
```

## 작업 항목

### 1. 디렉터리 생성 + SKILL.md Write

```bash
cd /home/bifos/ai-nodes
mkdir -p career-os/.claude/skills/candidate-baseline-suggester
```

`Read` 도구로 `career-os/tasks/plan020-candidate-baseline-suggester/draft/SKILL.md` 로드.

`Write` 도구로 `career-os/.claude/skills/candidate-baseline-suggester/SKILL.md`에 **draft 본문 그대로** 저장. prose 위장 금지 (6-6).

### 2. 검증

```bash
cd /home/bifos/ai-nodes
TARGET=career-os/.claude/skills/candidate-baseline-suggester/SKILL.md
DRAFT=career-os/tasks/plan020-candidate-baseline-suggester/draft/SKILL.md

# A. byte-for-byte diff
diff -q "$TARGET" "$DRAFT" > /dev/null \
  || { echo "PHASE_FAILED: target ↔ draft 불일치"; exit 1; }

# B. 라인 수
LINES=$(wc -l < "$TARGET")
[ "$LINES" -ge 120 ] || { echo "PHASE_FAILED: $LINES 줄 — Write 누락 의심"; exit 1; }

# C. 핵심 키워드
for kw in "When to use" "Inputs" "Workflow" "Self-check" "Error handling" \
          "Append" "audit trail\|before/\|after/" "candidate-profile" "fos-study"; do
  grep -qE "$kw" "$TARGET" || { echo "PHASE_FAILED: '$kw' 누락"; exit 1; }
done

# D. native invoke
grep -q "candidate-baseline-suggester\|claude -p" "$TARGET" \
  || { echo "PHASE_FAILED: native invoke 안내 누락"; exit 1; }

# E. 옛 subprocess 지시문 없음 (6-7)
for kw in "Output only valid JSON" "Do not output markdown" "claude --json-schema"; do
  grep -q "$kw" "$TARGET" && { echo "PHASE_FAILED: '$kw' 잔재"; exit 1; }
done

echo "[2] 검증 OK ($LINES 줄)"
```

### 3. 커밋 + commit 개수 강제

```bash
cd /home/bifos/ai-nodes
HEAD_BEFORE=$(git rev-parse HEAD)

git add career-os/.claude/skills/candidate-baseline-suggester/
git commit -m "$(cat <<'COMMIT_EOF'
feat(career-os): candidate-baseline-suggester skill 신규 (plan020 phase-02)

ADR-028 적용. draft 별도 파일 → byte-for-byte Write (common-pitfalls 6-6 회피).

위치: career-os/.claude/skills/candidate-baseline-suggester/SKILL.md
  (워크스페이스 한정 — 자산 모두 career-os 소속)

기능: fos-study 전체 commit history + study-progress + (선택)
interview-prep-analyzer baseline 산출물 분석 → candidate-profile.md +
baseline-core-files.json + prd.md "약점·강점" + data/study-progress.json
weak_spots Append + 주석 마킹 패턴으로 갱신.

audit trail: data/runtime/profile-refresh-suggestions/YYYY-MM-DD/ 안
before/ + after/ + diff/ + changes.md 보관 (수동 roll back 안전망).

호출: claude -p "/candidate-baseline-suggester" 또는 자연어
  "후보자 프로필 fos-study 학습 결과 반영해서 갱신해줘"
COMMIT_EOF
)" || { echo "PHASE_FAILED: commit"; exit 1; }

HEAD_AFTER=$(git rev-parse HEAD)
COMMITS=$(git rev-list "$HEAD_BEFORE..$HEAD_AFTER" --count)
[ "$COMMITS" = "1" ] || { echo "PHASE_FAILED: commit 수 $COMMITS"; exit 1; }
echo "[3] commit 1 OK"
```

## Critical Files

| 파일 | 변경 |
|---|---|
| `career-os/.claude/skills/candidate-baseline-suggester/SKILL.md` | 신규 (Write, draft 복제) |

## Blocked 조건

- phase-01 commit 없음 → `PHASE_BLOCKED` + `exit 2`
- draft 부재 → `PHASE_BLOCKED` + `exit 2`
- skill 디렉터리 이미 존재 → `PHASE_BLOCKED` + `exit 2`
- 검증 A~E 실패 → `PHASE_FAILED` + `exit 1`
- commit 수 ≠ 1 → `PHASE_FAILED: commit 위장 의심` + `exit 1`
