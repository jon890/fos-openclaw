# Phase 2 — career-os/docs/adr.md + ai-nodes/docs/adr.md Quick Index 추가 + drift Status 일괄 갱신 (28 ADR 전수 audit)

**Model**: opus
**Status**: pending

---

## 목표

28 ADR (career-os 26 + ai-nodes 모노레포 2 + 신규 ADR-003 = 3) *전수 audit*. 각 ADR을:
1. **현재 코드 상태와 일치하는지 확인** (Decay 축 적용 — scripts/, .claude/skills/, config/, dispatcher case 매핑).
2. **Status 갱신** (Accepted / Superseded by ADR-N / Partially superseded by ADR-N / Deprecated).
3. **한 줄 요약 추출** (Quick Index 행에 박을 텍스트).

그 결과를 두 adr.md 상단에 **Quick Index 테이블** 추가 + 본문 첫 줄 *Status 라인* 갱신.

**Model: opus** (28 ADR 본문 + 코드 매핑 추론 + 한 줄 요약 작성 = deep analysis).

**범위 외**: docs-check skill 적용 (phase-03), docs 갱신 (phase-04).

## 관련 docs

- phase-01 commit — docs-check SKILL.md draft 작성 완료
- `career-os/docs/adr.md` (26 ADR / 637줄)
- `ai-nodes/docs/adr.md` (2 + 1 ADR / 82+ 줄)
- `career-os/.claude/skills/`, `career-os/scripts/`, `career-os/config/` (Decay 검사 대상)
- `skills/plan-and-build/references/common-pitfalls.md` 6-6

## 사전 검증

```bash
cd /home/bifos/ai-nodes

# 1-A. phase-01 commit 존재
git log -1 --format='%s' | grep -q "plan018 phase-01" \
  || { echo "PHASE_BLOCKED: phase-01 commit 없음"; exit 2; }

# 1-B. adr.md 파일 존재
test -f career-os/docs/adr.md \
  || { echo "PHASE_BLOCKED: career-os/docs/adr.md 부재"; exit 2; }
test -f docs/adr.md \
  || { echo "PHASE_BLOCKED: ai-nodes/docs/adr.md 부재"; exit 2; }

echo "사전 검증 OK"
```

## 작업 항목

### 1. 28 ADR 전수 audit (Read 단계)

Read 도구로 다음 자료 모두 로드:

- `career-os/docs/adr.md` (26 ADR 본문)
- `ai-nodes/docs/adr.md` (3 ADR 본문)
- `career-os/.claude/skills/` 디렉터리 목록 (현재 skill 매핑)
- `career-os/scripts/` 디렉터리 목록 (현재 script 매핑)
- `career-os/config/` 디렉터리 목록 (현재 config 매핑)
- `career-os/scripts/command-router/run_now.sh` (현재 dispatcher case 매핑)
- 최근 plan들 (`career-os/tasks/plan013*`, `plan014*`, `plan015*`, `plan016*`, `plan017*`) — Status 갱신 근거

각 ADR 본문을 읽고:
- 결정 키워드 추출 (skill 이름, scripts 파일명, config 파일명, dispatcher case 등)
- 현재 코드 상태와 매핑
- Status 추론:
  - 코드와 일치 → **Accepted** (현재 살아있음)
  - 코드 완전 X → **Superseded by ADR-N (date)** 또는 **Deprecated**
  - 코드 부분 X → **Partially superseded by ADR-N (어떤 부분)**
- 한 줄 요약 작성 (≤ 80자, 결정의 핵심)

### 2. Status 갱신 정확 매핑 (확정 + 추가 audit 결과)

본 phase에서 확정 가능한 Status (사용자 통찰 + 코드 추적):

| ADR | 현재 Status | 새 Status | 근거 |
|---|---|---|---|
| career-os ADR-004 | 폐기 명시 | (그대로 — 이미 표기) | 표기 정확 |
| career-os ADR-006 | Accepted | **Partially superseded by ai-nodes ADR-002 (plan013, 2026-05-14)** | study-pack 라우팅 → native skill 진입점 전환 |
| career-os ADR-007 | Accepted | **Superseded by ADR-027 (plan015, 2026-05-15)** | Q&A workflow → interview-asset-writer 통합 |
| career-os ADR-011 | Accepted | **Superseded by plan015 (2026-05-15)** | 자동 replenish → topic-pool-replenisher 폐기, study-topic-recommender 흡수 예정 (plan016) |
| career-os ADR-016 | Accepted | **Partially superseded by ADR-027 (plan017, 2026-05-15)** | config 통합 → topics.json 3 분리 |
| career-os ADR-023 | Accepted (본문 "사실상 무효화") | **Deprecated (2026-05-13, 실측 결과 출력 포맷 결정 무효)** | 본문에 메타 언급만, status 라인 정식 갱신 |

추가로 phase-02 audit에서 발견되는 drift도 같은 컨벤션으로 갱신. 발견 없으면 Accepted 유지.

### 3. Quick Index 테이블 작성

각 adr.md 파일 상단 (헤더 직후, ADR-001 시작 전)에 Quick Index 섹션 추가:

#### career-os/docs/adr.md (26 ADR)

```markdown
## Quick Index

빠른 ADR 탐색용 단일 출처. 본문 헤더의 ADR 번호 + 제목 + Status 라인과 동기 유지.

| ADR | 제목 | Status | 한 줄 요약 |
|---|---|---|---|
| ADR-001 | Daily 파일 선택 전략 | Accepted | <한 줄 요약> |
| ADR-002 | 학습 진도 추적 | Accepted | <한 줄 요약> |
| ADR-003 | Baseline 청킹 제거 | Accepted | <한 줄 요약> |
| ADR-004 | reports/ 디렉터리 컨벤션 | Superseded by no-action (2026-04-18) | <한 줄 요약> |
| ADR-005 | Study pack 출력 및 발행 정책 | Accepted | <한 줄 요약> |
| ADR-006 | Study-pack 엔트리포인트와 topic 라우팅 | Partially superseded by ai-nodes ADR-002 (plan013) | <한 줄 요약> |
| ADR-007 | Experience-based interview question bank workflow | Superseded by ADR-027 (plan015) | <한 줄 요약> |
| ADR-008 | Generation status notifications | Accepted | <한 줄 요약> |
| ADR-009 | Morning topic reservoir + recommendation pipeline | Accepted | <한 줄 요약> (plan016 ts 마이그 진행 중 — 알고리즘 유지) |
| ADR-010 | Recommendation scoring + mix targets | Accepted | <한 줄 요약> |
| ADR-011 | Study topic 자동 보충 (replenishment) | Superseded by plan015 (topic-pool-replenisher 폐기) | <한 줄 요약> |
| ADR-012 | Morning 추천을 10픽 + 오늘의 3선으로 확장 | Accepted | <한 줄 요약> |
| ADR-013 | RSS·Atom discovery 레이어 부착 | Accepted | <한 줄 요약> |
| ADR-014 | Claude usage 전파 패턴 통일 | Accepted | <한 줄 요약> |
| ADR-015 | docs/ 피드백 루프 + data/ 위치 정책 | Accepted | <한 줄 요약> |
| ADR-016 | config 디렉터리 통합 | Partially superseded by ADR-027 (plan017) | <한 줄 요약> |
| ADR-017 | cj-oliveyoung-java-backend-prep 분해 | Accepted | <한 줄 요약> |
| ADR-018 | docs/ 운영 정책: 휘발성 vs 영속 | Accepted | <한 줄 요약> |
| ADR-019 | scripts/ 폴더 분리 | Accepted | <한 줄 요약> |
| ADR-020 | 공용 헬퍼 TS(Bun) 마이그레이션 | Accepted | <한 줄 요약> |
| ADR-021 | Discord 알림 openclaw 경유 + 워크스페이스 .env | Accepted | <한 줄 요약> |
| ADR-022 | 도메인 헬퍼 TS(Bun) 마이그레이션 | Accepted | <한 줄 요약> |
| ADR-023 | Study-pack 생성 출력 포맷 | Deprecated (2026-05-13, 실측 무효) | <한 줄 요약> |
| ADR-025 | Skills 정리 + 한글화 정책 | Accepted | <한 줄 요약> |
| ADR-026 | study-topic-recommender native + ts 마이그 + replenish/promote/live-coding 흡수 | Accepted | <한 줄 요약> (plan016 실행 중) |
| ADR-027 | knowledge-gap-analyzer → interview-prep-analyzer + topics.json 분리 | Accepted | <한 줄 요약> (plan017 실행 중) |

(ADR-024는 번호 누락. ADR-007a/b 충돌은 prd.md "분해 대기 작업"에 기록.)

---
```

#### ai-nodes/docs/adr.md (3 ADR)

```markdown
## Quick Index

| ADR | 제목 | Status | 한 줄 요약 |
|---|---|---|---|
| ADR-001 | 공용 헬퍼 위치 분리: _shared/lib vs <workspace>/scripts/_lib | Accepted | <한 줄 요약> |
| ADR-002 | Claude Code native skill 패턴 채택 + .claude/skills/ 단일 위치 | Accepted | <한 줄 요약> |
| ADR-003 | docs-check skill + adr.md Quick Index + drift Status 컨벤션 | Accepted | <한 줄 요약> (plan018, 본 ADR) |

---
```

한 줄 요약은 audit 중 작성. 80자 이하.

### 4. 본문 Status 라인 갱신

각 drift된 ADR 본문의 첫 줄 (Status: ...)을 새 Status로 Edit. 예:

```markdown
## ADR-011 — Study topic 자동 보충 (replenishment)

- Status: Superseded by plan015 (2026-05-15) — topic-pool-replenisher 폐기, study-topic-recommender가 자동 흐름 흡수 예정 (plan016)
- Date: <원래 날짜>
```

Quick Index 행과 본문 Status 라인이 *완전 동일*해야 함 — Decay 검사 항목.

### 5. 자기 확인

```bash
cd /home/bifos/ai-nodes

# A. Quick Index 헤더 추가 확인
grep -q "^## Quick Index" career-os/docs/adr.md \
  || { echo "PHASE_FAILED: career-os/docs/adr.md Quick Index 누락"; exit 1; }
grep -q "^## Quick Index" docs/adr.md \
  || { echo "PHASE_FAILED: ai-nodes/docs/adr.md Quick Index 누락"; exit 1; }

# B. Quick Index 행 수 (career-os 26 + ai-nodes 3)
CAREER_ROWS=$(grep -cE "^\| ADR-[0-9]+" career-os/docs/adr.md)
[ "$CAREER_ROWS" -ge 26 ] || { echo "PHASE_FAILED: career-os Quick Index 행 $CAREER_ROWS (expected ≥26)"; exit 1; }

AI_ROWS=$(grep -cE "^\| ADR-[0-9]+" docs/adr.md)
[ "$AI_ROWS" -ge 3 ] || { echo "PHASE_FAILED: ai-nodes Quick Index 행 $AI_ROWS (expected ≥3)"; exit 1; }

# C. 확정 drift Status 5개 갱신 확인 (career-os)
for adr_status in "ADR-006.*Partially superseded\|ADR-006.*partially superseded" \
                   "ADR-007.*Superseded by ADR-027" \
                   "ADR-011.*Superseded by plan015" \
                   "ADR-016.*Partially superseded by ADR-027" \
                   "ADR-023.*Deprecated"; do
  grep -qE "$adr_status" career-os/docs/adr.md \
    || { echo "PHASE_FAILED: '$adr_status' Status 갱신 누락"; exit 1; }
done

# D. Quick Index ↔ 본문 sync (각 ADR 번호 두 곳)
python3 - <<'PY'
import re
from pathlib import Path
for f in ['career-os/docs/adr.md', 'docs/adr.md']:
    text = Path(f).read_text(encoding='utf-8')
    # Quick Index 행
    index_rows = re.findall(r'^\| (ADR-\d+) \|', text, re.M)
    # 본문 헤더
    body_headers = re.findall(r'^## (ADR-\d+) —', text, re.M)
    missing_in_body = set(index_rows) - set(body_headers)
    missing_in_index = set(body_headers) - set(index_rows)
    if missing_in_body or missing_in_index:
        print(f'PHASE_FAILED: {f} sync 위반')
        if missing_in_body:
            print(f'  Index에만 있음: {missing_in_body}')
        if missing_in_index:
            print(f'  Body에만 있음: {missing_in_index}')
        exit(1)
    print(f'[{f}] Index ↔ Body sync OK ({len(index_rows)} ADR)')
PY
[ $? -eq 0 ] || exit 1

echo "[5] Quick Index + Status audit OK"
```

### 6. 커밋 + commit 개수 강제

```bash
cd /home/bifos/ai-nodes
HEAD_BEFORE=$(git rev-parse HEAD)

git add career-os/docs/adr.md docs/adr.md
git commit -m "$(cat <<'COMMIT_EOF'
docs(ai-nodes): adr.md Quick Index 추가 + drift Status 일괄 갱신 (plan018 phase-02)

ADR-003 적용. 28 ADR 전수 audit + Quick Index 테이블 + Status 라인 갱신.

career-os/docs/adr.md (26 ADR):
- ADR-006: Accepted → Partially superseded by ai-nodes ADR-002 (plan013
  native skill 전환 — study-pack 라우팅 부분)
- ADR-007: Accepted → Superseded by ADR-027 (plan015 interview-asset-writer
  통합)
- ADR-011: Accepted → Superseded by plan015 (topic-pool-replenisher 폐기)
- ADR-016: Accepted → Partially superseded by ADR-027 (plan017 topics.json
  3 분리)
- ADR-023: Accepted (본문 "사실상 무효화") → Deprecated (2026-05-13 실측 무효)
- ADR-026/027: Accepted, 진행 중 plan016/017 명시

ai-nodes/docs/adr.md (3 ADR, ADR-003 포함):
- ADR-001/002: Accepted
- ADR-003: 본 plan 신규

Quick Index 형식: `| ADR | 제목 | Status | 한 줄 요약 |`.
AI 에이전트가 본문 637줄 Read 없이 결정 매핑 가능.

검증:
- Quick Index 행 수: career-os 26 + ai-nodes 3
- 본문 헤더 ↔ Index 행 양방향 sync (Python 검사)
- 5 drift Status 라인 갱신 확인
COMMIT_EOF
)" || { echo "PHASE_FAILED: commit"; exit 1; }

HEAD_AFTER=$(git rev-parse HEAD)
COMMITS=$(git rev-list "$HEAD_BEFORE..$HEAD_AFTER" --count)
[ "$COMMITS" = "1" ] \
  || { echo "PHASE_FAILED: 본 phase commit 수 $COMMITS (expected 1)"; exit 1; }
echo "[6] commit 1 OK"
```

push는 phase-04.

## Critical Files

| 파일 | 변경 |
|---|---|
| `career-os/docs/adr.md` | Quick Index 추가 + 5+ ADR Status 갱신 |
| `ai-nodes/docs/adr.md` | Quick Index 추가 + Status 명시 |

## Blocked 조건

- phase-01 commit 없음 → `PHASE_BLOCKED` + `exit 2`
- adr.md 파일 부재 → `PHASE_BLOCKED` + `exit 2`
- Quick Index 누락 → `PHASE_FAILED` + `exit 1`
- Index ↔ Body sync 위반 → `PHASE_FAILED` + `exit 1`
- 확정 drift 5개 Status 갱신 누락 → `PHASE_FAILED` + `exit 1`
- commit 수 ≠ 1 → `PHASE_FAILED: commit 위장 의심` + `exit 1`

## 의도 메모

- *Model: opus* — 28 ADR 본문 + 코드 매핑 + 한 줄 요약 추론 = deep analysis. sonnet은 부족.
- Quick Index 본문 ↔ 헤더 *양방향 sync* 검사는 Decay 축의 첫 자동화 검사 (skill phase-03에서 명시).
- ADR-024 누락은 *기록*만 (별도 cleanup plan). 본 phase 범위 외.
- 확정 5 drift는 사용자 통찰 + 코드 추적 결과 — 그 외 발견되면 같은 컨벤션 적용.
