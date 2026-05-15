# Phase 1 — docs-check SKILL.md draft 작성 (5축 + ai-nodes 도메인 변형 + 자동화 검사 명세)

**Model**: sonnet
**Status**: pending

---

## 목표

ai-nodes 전역 docs-check skill의 native 명세 draft를 별도 파일에 작성. fos-blog `docs-check` 5축 차용 + ai-nodes 도메인 변형 (Drizzle schema → config json / page.tsx → dispatcher case / SKILL.md trigger pattern).

draft를 phase 본문 코드 블록에 박지 않음 — common-pitfalls 6-6 회피.

**범위 외**: adr.md Quick Index 추가 (phase-02), skill 적용 (phase-03), docs 갱신 (phase-04).

## 관련 docs (실행 전 필수 읽기)

- `ai-nodes/docs/adr.md` ADR-003 — 본 plan 결정 출처
- fos-blog repo의 `.claude/skills/docs-check/SKILL.md` (참고용):
  - `gh api -H 'Accept: application/vnd.github.raw' repos/jon890/fos-blog/contents/.claude/skills/docs-check/SKILL.md`
- `career-os/.claude/skills/study-pack-writer/SKILL.md` — native 명세 패턴
- `career-os/.claude/skills/interview-asset-writer/SKILL.md` — native 명세 + 분기 패턴
- `skills/plan-and-build/references/common-pitfalls.md` 6-6 + 6-7

## 사전 검증

```bash
cd /home/bifos/ai-nodes

# 1-A. ADR-003 docs commit 존재
git log --oneline | grep -q "ADR-003.*docs-check" \
  || { echo "PHASE_BLOCKED: ADR-003 commit 없음"; exit 2; }

# 1-B. draft 디렉터리 존재
test -d career-os/tasks/plan018-docs-check-and-adr-health/draft \
  || { echo "PHASE_BLOCKED: draft 디렉터리 없음"; exit 2; }

# 1-C. gh CLI 가용 (참고 자료 fetch용)
which gh >/dev/null || { echo "PHASE_BLOCKED: gh 미설치"; exit 2; }

echo "사전 검증 OK"
```

## 작업 항목

### 1. fos-blog docs-check 참고 자료 fetch

```bash
cd /home/bifos/ai-nodes
# gh api로 fos-blog/.claude/skills/docs-check/SKILL.md raw 가져오기 (글로벌 CLAUDE.md github_query directive)
gh api -H 'Accept: application/vnd.github.raw' \
  repos/jon890/fos-blog/contents/.claude/skills/docs-check/SKILL.md \
  > /tmp/plan018-fos-blog-docs-check.md 2>&1
test -s /tmp/plan018-fos-blog-docs-check.md \
  || { echo "PHASE_FAILED: fos-blog docs-check fetch 실패"; cat /tmp/plan018-fos-blog-docs-check.md; exit 1; }
echo "[1] fos-blog docs-check fetch OK ($(wc -l < /tmp/plan018-fos-blog-docs-check.md) 줄)"
```

### 2. docs-check SKILL.md draft 작성

저장: `career-os/tasks/plan018-docs-check-and-adr-health/draft/SKILL.md`

본문 구성 (~180줄):

#### Frontmatter
```yaml
---
name: docs-check
description: ai-nodes 모노레포의 docs 건전성을 5축으로 종합 감사한다. Decay (Code↔Docs drift, stale ADR), Bloat (ADR 30줄 초과 / 코드 블록 / 파일 path 열거), Clarity (why + alternative + rejection 명시), Duplication (5문서 단일 출처), Self-Evidence (자명한 ADR 폐기 후보). 자연어 호출 — "ADR 건전성 점검", "docs 감사", "stale ADR 찾기", "/docs-check" 슬래시. 본 skill은 *발견*만 — 수정은 사용자 승인 후 별도 진행.
---
```

#### 본문 섹션
1. **Overview** — 한 줄
2. **When to use** — 슬래시 + 자연어 패턴 (감사·점검 키워드)
3. **Inputs** — Read 대상 (career-os/docs/adr.md + ai-nodes/docs/adr.md + 워크스페이스 docs/ + scripts/ + .claude/skills/)
4. **Workflow** — 5축 검사 순서:
   - **A. Decay** (Code ↔ Docs Sync):
     - ADR 본문 + Quick Index ↔ 실제 코드 (scripts/, .claude/skills/, config/) 매핑
     - Stale 키워드 grep: skill 이름·dispatcher case·config 경로 ADR 안에 있는데 코드엔 없음
     - ADR Quick Index ↔ 본문 헤더 sync (양쪽 모두 같은 ADR 번호 + 제목)
     - Status 라인이 *Accepted*인데 실제 코드 없음 → drift 의심
   - **B. Bloat** (Over-specification):
     - ADR 본문 30줄 초과 → bloat 의심
     - 코드 블록 >10줄 → 본문이 아닌 코드 책임
     - 파일 path 열거 ≥3 → code-architecture.md 책임
     - 변경 이력 → git log 책임
   - **C. Clarity** (Decision Rationale):
     - "맥락" 섹션 존재 + 길이 ≥3줄
     - "결정" 섹션 + 거절한 대안 ≥1
     - "결과" 섹션 + 단점 또는 trade-off ≥1
   - **D. Duplication** (Single Source of Truth):
     - 5문서 (prd / data-schema / flow / code-architecture / adr) 간 동일 정보 grep
     - 예: config 스키마 = data-schema.md만, 흐름 = flow.md만
   - **E. Self-Evidence** (ADR Necessity Filter):
     - ADR이 *코드/config로 self-evident*한 내용만 담고 있으면 폐기 후보
     - 예: "package.json 변경" 자체는 ADR 가치 없음 — *왜 그 선택인지* 없으면 폐기 후보
5. **자동화 검사 5개 (ai-nodes 변형)**:
   - 1) ADR Quick Index ↔ 본문 sync (헤더 ADR 번호 = Index 행 ADR 번호)
   - 2) 30줄 threshold (ADR 본문 줄 수 ≥30 → bloat 후보 리스트)
   - 3) Config schema alignment (data-schema.md 본문 스키마 ↔ 실제 config json 키)
   - 4) Dispatcher case coverage (run_now.sh case ↔ prd.md 기능 표 + flow.md 섹션)
   - 5) Prohibited terms (§ 기호 / 옛 subprocess 지시문 / outdated skill 이름 등)
6. **호출 방법**:
   - native invoke: `claude -p "/docs-check [scope]"` (scope: 워크스페이스 이름 또는 `all`)
   - 발견 사항을 *Critical / Warning / Safe* 3단계로 분류
   - 사용자 승인 전 *수정 안 함* — 발견만 보고
7. **Error handling** — git pull 실패 / 워크스페이스 없음 / ADR 파일 없음
8. **Why this design** — ADR-003 요약 3줄

### 3. draft 자기 확인

```bash
cd /home/bifos/ai-nodes
DRAFT=career-os/tasks/plan018-docs-check-and-adr-health/draft/SKILL.md

# A. draft 존재 + 라인 수
test -f "$DRAFT" || { echo "PHASE_FAILED: draft 부재"; exit 1; }
LINES=$(wc -l < "$DRAFT")
[ "$LINES" -ge 120 ] || { echo "PHASE_FAILED: draft $LINES 줄 (expected ≥120)"; exit 1; }

# B. 5축 키워드
for axis in "Decay" "Bloat" "Clarity" "Duplication" "Self-Evidence"; do
  grep -q "$axis" "$DRAFT" || { echo "PHASE_FAILED: 5축 '$axis' 누락"; exit 1; }
done

# C. ai-nodes 도메인 변형 키워드
for kw in "dispatcher" "Quick Index" "ADR" "config" "SKILL.md"; do
  grep -q "$kw" "$DRAFT" || { echo "PHASE_FAILED: 도메인 키워드 '$kw' 누락"; exit 1; }
done

# D. native skill 패턴 키워드
for s in "When to use" "Inputs" "Workflow" "Error handling"; do
  grep -q "$s" "$DRAFT" || { echo "PHASE_FAILED: 섹션 '$s' 누락"; exit 1; }
done

# E. 옛 subprocess 지시문 *없음* (6-7)
for kw in "Output only valid JSON" "Do not output markdown" "claude --json-schema"; do
  grep -q "$kw" "$DRAFT" && { echo "PHASE_FAILED: 옛 subprocess 지시문 '$kw' 잔재"; exit 1; }
done

echo "[3] draft 자기 확인 OK ($LINES 줄)"
```

### 4. 커밋 + commit 개수 강제

```bash
cd /home/bifos/ai-nodes
HEAD_BEFORE=$(git rev-parse HEAD)

git add career-os/tasks/plan018-docs-check-and-adr-health/draft/
git commit -m "$(cat <<'COMMIT_EOF'
chore(career-os): plan018 phase-01 — docs-check SKILL.md draft 작성

ai-nodes 모노레포 ADR-003 적용 준비. draft를 phase 본문 코드 블록이 아닌
별도 파일로 분리해 common-pitfalls 6-6 (Write 위장) 회피.

- draft/SKILL.md (~180줄): fos-blog docs-check 5축 차용 + ai-nodes
  도메인 변형
  - Decay / Bloat / Clarity / Duplication / Self-Evidence
  - ai-nodes 자동화 검사 5개 (Quick Index sync / 30줄 threshold / config
    schema alignment / dispatcher case coverage / prohibited terms)
- fos-blog 원본 참고: gh api로 raw fetch (글로벌 CLAUDE.md github_query
  directive 적용)

phase-02에서 28 ADR 전수 audit + Quick Index 추가 + Status 일괄 갱신.
phase-03에서 ~/ai-nodes/skills/docs-check/ 디렉터리 생성 + SKILL.md 적용.
COMMIT_EOF
)" || { echo "PHASE_FAILED: commit"; exit 1; }

HEAD_AFTER=$(git rev-parse HEAD)
COMMITS=$(git rev-list "$HEAD_BEFORE..$HEAD_AFTER" --count)
[ "$COMMITS" = "1" ] \
  || { echo "PHASE_FAILED: 본 phase commit 수 $COMMITS (expected 1)"; exit 1; }
echo "[4] commit 1 OK"
```

push는 phase-04.

## Critical Files

| 파일 | 변경 |
|---|---|
| `career-os/tasks/plan018-docs-check-and-adr-health/draft/SKILL.md` | 신규 (~180줄) |

## Blocked 조건

- ADR-003 commit 없음 → `PHASE_BLOCKED` + `exit 2`
- draft 디렉터리 부재 → `PHASE_BLOCKED` + `exit 2`
- gh CLI 미설치 → `PHASE_BLOCKED` + `exit 2`
- fos-blog fetch 실패 → `PHASE_FAILED` + `exit 1`
- 자기 확인 A~E 실패 → `PHASE_FAILED: <항목>` + `exit 1`
- commit 수 ≠ 1 → `PHASE_FAILED: commit 위장 의심` + `exit 1`

## 의도 메모

- `gh api` 사용은 글로벌 CLAUDE.md `<github_query>` directive 적용 (WebFetch 회피).
- 5축 + 자동화 검사 5개는 fos-blog 원본과 *동일 구조 + ai-nodes 변형*. ai-nodes 자동화 검사는 Drizzle/Next 도메인이 아닌 config json + dispatcher + SKILL.md trigger 도메인.
