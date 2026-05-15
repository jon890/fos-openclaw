# Phase 1 — data/runtime + config 전수 audit (Read만, 폐기 후보 매핑 보고서 산출)

**Model**: sonnet
**Status**: pending

---

## 목표

`career-os/data/runtime/` + `career-os/config/` 전수 audit. 각 파일을 활성/stale/위치 위반 3 카테고리로 분류. 폐기 후보 매핑 보고서를 별도 파일에 산출. **본 phase는 Read·분석만 — 폐기·이동 적용 X (phase-02)**.

## 관련 docs

- `ai-nodes/docs/adr.md` ADR-015 — `data/` 위치 정책 (코드는 scripts/, 데이터만 data/)

## 사전 검증

```bash
cd /home/bifos/ai-nodes

# 1-A. data/runtime + config 디렉터리 존재
test -d career-os/data/runtime && test -d career-os/config \
  || { echo "PHASE_BLOCKED: 디렉터리 부재"; exit 2; }

# 1-B. plan019 draft 디렉터리
test -d career-os/tasks/plan019-data-runtime-cleanup/draft \
  || { echo "PHASE_BLOCKED: draft 디렉터리 부재"; exit 2; }

echo "사전 검증 OK"
```

## 작업 항목

### 1. data/runtime 전수 인벤토리

```bash
cd /home/bifos/ai-nodes
echo "=== data/runtime 전수 ==="
ls -la career-os/data/runtime/
echo ""
echo "=== 각 파일 수정 시각 ==="
find career-os/data/runtime/ -maxdepth 1 -type f -printf '%T@ %p\n' | sort -n | awk '{
  cmd="date -d @"$1" \"+%Y-%m-%d\""; cmd | getline date; close(cmd);
  print date, $2
}'
```

### 2. config 전수 인벤토리

```bash
cd /home/bifos/ai-nodes
echo "=== config/ 전수 ==="
ls -la career-os/config/
echo ""
echo "=== 각 config 파일 ↔ 사용 위치 grep ==="
for f in career-os/config/*.json career-os/config/*.md; do
  [ -e "$f" ] || continue
  BASENAME=$(basename "$f")
  HITS=$(grep -rln "config/$BASENAME" career-os/.claude/skills/ career-os/scripts/ _shared/ 2>/dev/null | grep -v "career-os/tasks/" | wc -l)
  echo "$BASENAME: $HITS 위치에서 read"
done
```

### 3. 분류 (Read + 분석)

각 파일을 다음 3 카테고리로 분류:

#### Category A: 활성 (현재 사용 중, 최근 7일 갱신)

예상 항목:
- `data/runtime/position-recommendation.md` (recommend-positions 출력)
- `data/runtime/wanted-server-postings.md`
- `data/runtime/position-postings-augmented.md`
- 모든 `config/*.json` (study-pack-writer / interview-asset-writer / interview-prep-analyzer / study-topic-recommender가 Read)

#### Category B: stale (한 달+ 미갱신 또는 폐기된 skill 잔재)

예상 항목:
- `data/runtime/freeform-study-pack-topic.json` (4/24, 한 달 전)
- `data/runtime/live-coding-generated-topic.json` (5/4, plan016이 흡수 — 의미 변경)
- `data/runtime/bootcamp-summary.md` (plan014 폐기 skill 산출물)
- `data/runtime/cj-foodville-bootcamp-summary.md` (동일)
- `data/runtime/broad-plus-kakaopay-position-snapshot.md`
- `data/runtime/kakaopay-focused-position-snapshot.md`
- `data/runtime/wanted-server-postings-{300,augmented,compact,1000-active}.md` (변형)
- `data/runtime/toss-server-postings.md`
- `data/runtime/live-position-postings*.md`
- `data/runtime/augmented-server-postings-no-toss.md`
- `data/runtime/2026-05-13-*-scan.md` (1회성 분석)
- `data/runtime/verified-company-postings-raw.md`, `-with-links.md`
- `data/runtime/topic-replenishment.json` / `.md` (plan015 폐기)

#### Category C: 위치 위반 (ADR-015)

예상 항목:
- `data/runtime/augment_positions.py` (Python script가 data/ 안)

### 4. 보고서 산출

저장: `career-os/tasks/plan019-data-runtime-cleanup/draft/cleanup-report.md`

본문 구조:

```markdown
# data/runtime + config Cleanup Audit Report (plan019 phase-01)

## 요약

- 총 파일: <N>
- Category A (활성, 유지): <N>
- Category B (stale, 폐기 후보): <N>
- Category C (위치 위반, 이동): <N>

## Category A — 유지 (활성)

| 파일 | 최근 수정 | 사용 위치 | 비고 |
|---|---|---|---|
| ... | YYYY-MM-DD | ... | ... |

## Category B — 폐기 후보 (stale)

| 파일 | 최근 수정 | 폐기 근거 | 영향 |
|---|---|---|---|
| ... | YYYY-MM-DD | plan014 bootcamp 폐기 잔재 등 | 없음 |

## Category C — 이동/조치 (ADR-015 위반)

| 파일 | 위반 사유 | 권장 처리 |
|---|---|---|
| `data/runtime/augment_positions.py` | data/에 Python script | scripts/position-recommender/로 이동 또는 폐기 (사용 여부 확인) |

## 결정 (phase-02에 적용)

- Category B 일괄 git rm
- Category C augment_positions.py:
  - 사용 위치 grep 결과: <0건 / N건>
  - 권장: <폐기 / scripts/position-recommender/로 이동>
```

### 5. 자기 확인

```bash
cd /home/bifos/ai-nodes
REPORT=career-os/tasks/plan019-data-runtime-cleanup/draft/cleanup-report.md

# A. 보고서 존재
test -f "$REPORT" || { echo "PHASE_FAILED: cleanup-report.md 부재"; exit 1; }

# B. 3 카테고리 모두 포함
for cat in "Category A" "Category B" "Category C"; do
  grep -q "$cat" "$REPORT" || { echo "PHASE_FAILED: '$cat' 누락"; exit 1; }
done

# C. augment_positions.py 명시
grep -q "augment_positions\.py" "$REPORT" \
  || { echo "PHASE_FAILED: augment_positions.py 명시 누락"; exit 1; }

echo "[5] 보고서 자기 확인 OK"
```

### 6. 커밋 + commit 개수 강제

```bash
cd /home/bifos/ai-nodes
HEAD_BEFORE=$(git rev-parse HEAD)

git add career-os/tasks/plan019-data-runtime-cleanup/draft/
git commit -m "$(cat <<'COMMIT_EOF'
chore(career-os): plan019 phase-01 — data/runtime + config audit 보고서 산출

ai-nodes ADR-015 적용 준비. data/runtime 33+ 파일 + config 8 파일 전수
분류:
- Category A (활성, 유지)
- Category B (stale, 폐기 후보) — plan014 bootcamp / plan015 replenisher /
  plan016 흡수 잔재 + 한 달+ 미갱신 변형 파일
- Category C (위치 위반) — augment_positions.py Python script가 data/에

phase-02에서 Category B 일괄 git rm + Category C 이동/폐기 적용.

본 phase는 분석만 — 폐기·이동 X.
COMMIT_EOF
)" || { echo "PHASE_FAILED: commit"; exit 1; }

HEAD_AFTER=$(git rev-parse HEAD)
COMMITS=$(git rev-list "$HEAD_BEFORE..$HEAD_AFTER" --count)
[ "$COMMITS" = "1" ] || { echo "PHASE_FAILED: commit 수 $COMMITS"; exit 1; }
echo "[6] commit 1 OK"
```

## Critical Files

| 파일 | 변경 |
|---|---|
| `career-os/tasks/plan019-data-runtime-cleanup/draft/cleanup-report.md` | 신규 |

## Blocked 조건

- 디렉터리 부재 → `PHASE_BLOCKED` + `exit 2`
- 보고서 자기 확인 실패 → `PHASE_FAILED` + `exit 1`
- commit 수 ≠ 1 → `PHASE_FAILED` + `exit 1`

## 의도 메모

- *audit 분리* 패턴 — Read만, 적용은 phase-02. 안전.
- augment_positions.py 처리는 phase-02에서 사용 위치 grep 후 폐기 vs 이동 결정.
