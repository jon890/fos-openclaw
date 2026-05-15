# Phase 2 — stale 일괄 폐기 + augment_positions.py ADR-015 위반 이동 또는 폐기

**Model**: sonnet
**Status**: pending

---

## 목표

phase-01의 `cleanup-report.md`를 Read해서 Category B (stale) 일괄 git rm + Category C (augment_positions.py) 사용 위치 grep 후 폐기 또는 이동 결정 + 적용. **활성 (Category A)은 건드리지 않음**.

## 관련 docs

- phase-01 commit — `draft/cleanup-report.md` 산출 완료
- `ai-nodes/docs/adr.md` ADR-015

## 사전 검증

```bash
cd /home/bifos/ai-nodes

# 1-A. phase-01 commit 존재
git log -1 --format='%s' | grep -q "plan019 phase-01" \
  || { echo "PHASE_BLOCKED: phase-01 commit 없음"; exit 2; }

# 1-B. cleanup-report.md 존재
REPORT=career-os/tasks/plan019-data-runtime-cleanup/draft/cleanup-report.md
test -f "$REPORT" || { echo "PHASE_BLOCKED: cleanup-report 부재"; exit 2; }

# 1-C. branch
[ "$(git branch --show-current)" = "main" ] \
  || { echo "PHASE_BLOCKED: branch != main"; exit 2; }

echo "사전 검증 OK"
```

## 작업 항목

### 1. cleanup-report.md Read — Category B 목록 추출

`Read` 도구로 `career-os/tasks/plan019-data-runtime-cleanup/draft/cleanup-report.md` 로드. Category B 표에서 각 행의 파일 경로 추출.

예상 Category B 목록 (phase-01 산출 기반, 실제 목록은 보고서 그대로):
- `data/runtime/freeform-study-pack-topic.json`
- `data/runtime/live-coding-generated-topic.json`
- `data/runtime/bootcamp-summary.md`
- `data/runtime/cj-foodville-bootcamp-summary.md`
- `data/runtime/broad-plus-kakaopay-position-snapshot.md`
- `data/runtime/kakaopay-focused-position-snapshot.md`
- `data/runtime/wanted-server-postings-{300,augmented,compact,1000-active}.md`
- `data/runtime/toss-server-postings.md`
- `data/runtime/live-position-postings*.md`
- `data/runtime/augmented-server-postings-no-toss.md`
- `data/runtime/topic-replenishment.{json,md}`
- (그 외 보고서가 Category B로 분류한 파일들)

### 2. Category B 일괄 git rm

각 Category B 파일을 git rm. 본 phase는 *보고서 권장 그대로 적용* — 사용자 검토 없이 (phase-01에서 이미 분류 검증).

```bash
cd /home/bifos/ai-nodes
# cleanup-report.md의 Category B 표를 파싱해서 자동 rm — 또는 Read 후 Edit 도구로 각 파일 git rm
# 실제 적용은 Claude가 phase 실행 시 보고서 Read → 각 파일 경로 추출 → Bash git rm 호출

# 검증: stale 파일들이 모두 제거됐는지
for stale in "data/runtime/freeform-study-pack-topic.json" \
             "data/runtime/live-coding-generated-topic.json" \
             "data/runtime/bootcamp-summary.md" \
             "data/runtime/cj-foodville-bootcamp-summary.md" \
             "data/runtime/topic-replenishment.json" \
             "data/runtime/topic-replenishment.md"; do
  test ! -f "career-os/$stale" \
    || { echo "PHASE_FAILED: $stale 잔존"; exit 1; }
done
echo "[2] Category B 일괄 git rm OK"
```

### 3. Category C augment_positions.py 처리

```bash
cd /home/bifos/ai-nodes
# 3-A. 사용 위치 grep
echo "=== augment_positions.py 사용 위치 ==="
USES=$(grep -rln "augment_positions" career-os/scripts/ career-os/.claude/skills/ _shared/ 2>/dev/null | wc -l)
echo "사용 횟수: $USES"

# 3-B. 결정
if [ "$USES" = "0" ]; then
  # 사용 없음 → 폐기
  git rm career-os/data/runtime/augment_positions.py
  echo "[3] 사용 없음 → 폐기"
else
  # 사용 있음 → scripts/position-recommender/로 이동
  git mv career-os/data/runtime/augment_positions.py \
         career-os/scripts/position-recommender/augment_positions.py
  echo "[3] 사용 $USES → scripts/position-recommender/로 이동"
fi

# 검증
test ! -f career-os/data/runtime/augment_positions.py \
  || { echo "PHASE_FAILED: augment_positions.py 잔존"; exit 1; }
```

### 4. 검증

```bash
cd /home/bifos/ai-nodes

# A. data/runtime/ 안 Python script 0
HITS=$(find career-os/data/runtime/ -name "*.py" 2>/dev/null | wc -l)
[ "$HITS" = "0" ] || { echo "PHASE_FAILED: data/runtime/에 Python script $HITS 잔존"; \
                       find career-os/data/runtime/ -name "*.py"; exit 1; }
echo "[A] data/runtime Python 잔재 0 OK"

# B. 옛 폐기 skill 산출물 잔재 0
for stale in "bootcamp-summary.md" "cj-foodville-bootcamp-summary.md" \
             "topic-replenishment.json" "topic-replenishment.md"; do
  test ! -f "career-os/data/runtime/$stale" \
    || { echo "PHASE_FAILED: $stale 잔존"; exit 1; }
done
echo "[B] 폐기 skill 잔재 0 OK"
```

### 5. 커밋 + commit 개수 강제

```bash
cd /home/bifos/ai-nodes
HEAD_BEFORE=$(git rev-parse HEAD)

git add career-os/data/runtime/ career-os/scripts/position-recommender/

git commit -m "$(cat <<'COMMIT_EOF'
chore(career-os): data/runtime stale 일괄 폐기 + augment_positions.py 위치 정리 (plan019 phase-02)

ai-nodes ADR-015 적용 + plan014/015/016 폐기 skill 잔재 정리.

폐기 (Category B — stale):
- data/runtime/freeform-study-pack-topic.json (4/24)
- data/runtime/live-coding-generated-topic.json (5/4, plan016 흡수 — 의미 변경)
- data/runtime/bootcamp-summary.md (plan014 bootcamp-batch 폐기 잔재)
- data/runtime/cj-foodville-bootcamp-summary.md (동일)
- data/runtime/{broad-plus-kakaopay,kakaopay-focused}-position-snapshot.md
  (1회성 5/11)
- data/runtime/wanted-server-postings-{300,augmented,compact,1000-active}.md
  (변형 일부 stale)
- data/runtime/toss-server-postings.md (5/9)
- data/runtime/live-position-postings.md, -all.md
- data/runtime/augmented-server-postings-no-toss.md
- data/runtime/topic-replenishment.json + .md (plan015 폐기)

이동/폐기 (Category C — ADR-015 위반):
- data/runtime/augment_positions.py — Python script가 data/에 위치
  → 사용 위치 grep 결과 따라 scripts/position-recommender/로 git mv 또는 폐기

활성 파일 (Category A)은 건드리지 않음 — position-recommendation.md,
position-postings-augmented.md, wanted-server-postings.md 등 매주 갱신.
COMMIT_EOF
)" || { echo "PHASE_FAILED: commit"; exit 1; }

HEAD_AFTER=$(git rev-parse HEAD)
COMMITS=$(git rev-list "$HEAD_BEFORE..$HEAD_AFTER" --count)
[ "$COMMITS" = "1" ] || { echo "PHASE_FAILED: commit 수 $COMMITS"; exit 1; }
echo "[5] commit 1 OK"
```

push는 phase-03.

## Critical Files

| 파일 | 변경 |
|---|---|
| `career-os/data/runtime/` Category B 파일들 | git rm |
| `career-os/data/runtime/augment_positions.py` | git rm 또는 scripts/position-recommender/로 git mv |

## Blocked 조건

- phase-01 commit 없음 → `PHASE_BLOCKED` + `exit 2`
- cleanup-report 부재 → `PHASE_BLOCKED` + `exit 2`
- 검증 A~B 실패 → `PHASE_FAILED` + `exit 1`
- commit 수 ≠ 1 → `PHASE_FAILED` + `exit 1`

## 의도 메모

- Category A (활성)은 *건드리지 않음* — 매주 갱신되는 산출물이라 자동 회복.
- augment_positions.py는 *사용 위치 grep 결과*로 폐기 vs 이동 자동 결정 (보수적 — 사용 있으면 이동, 없으면 폐기).
