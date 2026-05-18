# Phase 04 — 잔여 참조 갱신 + grep 검증

**Model**: sonnet
**Status**: pending

---

## 목표

apartment 워크스페이스 안 옛 path 인용 (옛 `WORKFLOW.md`, `TOOLS.md`, `docs/decisions/`, `apartment/config/.env`, `docs-naver-browser-plan.md`) 잔재가 SKILL.md / scripts / 기타 docs 안에 남아 있는지 grep + Edit으로 정리. phase-01/02의 safety net.

**범위 외**: 5문서 + AGENTS.md / 메타 작업 (phase-01~03 완료), 통합 검증 + push (phase-05). README.md stale 영역은 plan001 범위 외 (별도 chore).

---

## 본 phase 강제 주의문

- Edit/Bash 도구로 잔재 갱신해야 함. 잔재 0건 시 commit 없이 정상 종료 (exit 0).
- 작성·수정하는 모든 문서에 section sigil (U+00A7) 사용 금지.
- 본 phase commit 개수 = 0 (잔재 없음 시) 또는 1 (잔재 발견 + 갱신 시). 정확히 명시.

---

## 관련 docs

- phase-01 산출: apartment/docs/{prd,data-schema,flow,code-architecture,adr}.md
- phase-02 산출: apartment/AGENTS.md (slim), apartment/CLAUDE.md (심링크), apartment/.env (root)
- phase-03 산출: ai-nodes/docs/workspace-structure.md, ai-nodes ADR-004, career-os Status 격상

---

## 작업 항목

### 1. 잔재 grep — 옛 path 인용

```bash
echo "=== 옛 path 잔재 grep ==="

# A. WORKFLOW.md 인용 (apartment/WORKFLOW.md 폐기됨, flow.md로 흡수)
A_HITS=$(grep -rln "WORKFLOW.md\|apartment/WORKFLOW" \
  apartment/skills/ apartment/.claude/ apartment/AGENTS.md \
  2>/dev/null || true)
echo "[A WORKFLOW.md 인용]"
echo "$A_HITS"

# B. TOOLS.md 인용 (apartment/TOOLS.md 폐기됨, prd.md로 흡수)
B_HITS=$(grep -rln "apartment/TOOLS\|TOOLS.md" \
  apartment/skills/ apartment/.claude/ apartment/AGENTS.md \
  2>/dev/null || true)
echo "[B TOOLS.md 인용]"
echo "$B_HITS"

# C. docs/decisions/ 인용 (decisions/ 폐기됨, adr.md ADR-001로 흡수)
C_HITS=$(grep -rln "docs/decisions\|001-naver-api-integration" \
  apartment/skills/ apartment/.claude/ apartment/AGENTS.md \
  2>/dev/null || true)
echo "[C docs/decisions/ 인용]"
echo "$C_HITS"

# D. apartment/config/.env 인용 (phase-02에서 갱신됐어야 함)
D_HITS=$(grep -rln "apartment/config/.env\|config/.env" \
  apartment/skills/ apartment/.claude/ apartment/AGENTS.md \
  2>/dev/null || true)
echo "[D apartment/config/.env 인용]"
echo "$D_HITS"

# E. docs-naver-browser-plan.md 인용 (적용된 plan note, 폐기됨)
E_HITS=$(grep -rln "docs-naver-browser-plan" \
  apartment/skills/ apartment/.claude/ apartment/AGENTS.md \
  2>/dev/null || true)
echo "[E docs-naver-browser-plan.md 인용]"
echo "$E_HITS"
```

### 2. 잔재별 Edit 갱신 (발견 시)

위 grep 결과 파일별로 `Edit` 도구로 갱신:

| 잔재 | 갱신 방향 |
|---|---|
| A. WORKFLOW.md | `docs/flow.md` (워크플로 인용) 또는 `docs/prd.md` (Guri buy-search 정책 인용) |
| B. TOOLS.md | `docs/prd.md` 2번 (현재 MVP 타깃) |
| C. docs/decisions/ | `docs/adr.md` 또는 `docs/adr.md ADR-001` (Naver 인용) |
| D. apartment/config/.env | `apartment/.env` (phase-02 갱신 누락 보완) |
| E. docs-naver-browser-plan.md | 인용 자체 제거 또는 `docs/adr.md ADR-001`로 redirect |

### 3. ai-nodes 레벨 잔재 점검 (정보용, 갱신은 plan001 범위 외)

```bash
echo "=== ai-nodes 레벨 옛 apartment path 인용 (정보만) ==="
grep -rn "apartment/WORKFLOW\|apartment/TOOLS\|apartment/docs/decisions\|apartment/config/.env\|docs-naver-browser-plan" \
  ai-nodes/AGENTS.md ai-nodes/README.md ai-nodes/docs/ 2>/dev/null \
  | grep -v "^Binary" || echo "(없음)"

# README.md stale 영역 (career-os command-router, _shared/lib invoke_claude_skills 등)은
# 별도 chore commit 대상이라 본 phase에서 갱신하지 않음.
```

### 4. 갱신 후 재검증

```bash
SIGIL_CHAR=$(printf '\xc2\xa7')

# 잔재 카운트 재집계
A=$(grep -rln "WORKFLOW.md" apartment/skills/ apartment/.claude/ apartment/AGENTS.md 2>/dev/null | wc -l)
B=$(grep -rln "apartment/TOOLS\|TOOLS.md" apartment/skills/ apartment/.claude/ apartment/AGENTS.md 2>/dev/null | wc -l)
C=$(grep -rln "docs/decisions\|001-naver-api-integration" apartment/skills/ apartment/.claude/ apartment/AGENTS.md 2>/dev/null | wc -l)
D=$(grep -rln "apartment/config/.env\|config/.env" apartment/skills/ apartment/.claude/ apartment/AGENTS.md 2>/dev/null | wc -l)
E=$(grep -rln "docs-naver-browser-plan" apartment/skills/ apartment/.claude/ apartment/AGENTS.md 2>/dev/null | wc -l)

TOTAL=$((A + B + C + D + E))
echo "[잔재 합계] A=$A B=$B C=$C D=$D E=$E TOTAL=$TOTAL"
[ "$TOTAL" -eq 0 ] || { echo "PHASE_FAILED: 잔재 $TOTAL건 남음"; exit 1; }

echo "[잔재 합계] 0건 — Phase 04 통과 조건 충족"

# section sigil 검증
DIRTY_SIGIL=$(git diff --name-only HEAD 2>/dev/null | xargs grep -l "$SIGIL_CHAR" 2>/dev/null | wc -l)
echo "[diff sigil] $DIRTY_SIGIL files"
[ "$DIRTY_SIGIL" -eq 0 ] || { echo "PHASE_FAILED: diff에 sigil 잔재"; exit 1; }
```

### 5. commit 생성 (잔재 발견 + 갱신 시만)

```bash
if [ "$(git status --porcelain apartment/ | wc -l)" -gt 0 ]; then
  git add apartment/
  git commit -m "$(cat <<'EOF'
docs(apartment): 잔여 참조 갱신 — plan001 phase-01/02 후속 (phase-04)

옛 path 인용 정리:
- WORKFLOW.md → docs/flow.md / docs/prd.md
- TOOLS.md → docs/prd.md
- docs/decisions/ → docs/adr.md ADR-001
- apartment/config/.env → apartment/.env (phase-02 누락 보완)
- docs-naver-browser-plan.md → docs/adr.md ADR-001 redirect 또는 인용 제거

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
  echo "[commit] 잔재 갱신 commit 생성"
else
  echo "[commit] 잔재 없음 — commit 생성 건너뜀 (정상)"
fi
```

---

## 검증 (phase 종료 직전)

```bash
SIGIL_CHAR=$(printf '\xc2\xa7')

# 1. 모든 잔재 0건
A=$(grep -rln "WORKFLOW.md" apartment/skills/ apartment/.claude/ apartment/AGENTS.md 2>/dev/null | wc -l)
B=$(grep -rln "apartment/TOOLS\|TOOLS.md" apartment/skills/ apartment/.claude/ apartment/AGENTS.md 2>/dev/null | wc -l)
C=$(grep -rln "docs/decisions\|001-naver-api-integration" apartment/skills/ apartment/.claude/ apartment/AGENTS.md 2>/dev/null | wc -l)
D=$(grep -rln "apartment/config/.env\|config/.env" apartment/skills/ apartment/.claude/ apartment/AGENTS.md 2>/dev/null | wc -l)
E=$(grep -rln "docs-naver-browser-plan" apartment/skills/ apartment/.claude/ apartment/AGENTS.md 2>/dev/null | wc -l)
TOTAL=$((A + B + C + D + E))
echo "[잔재] $TOTAL"
[ "$TOTAL" -eq 0 ] || { echo "PHASE_FAILED: 잔재 $TOTAL건"; exit 1; }

# 2. working tree clean (apartment 영역)
DIRTY=$(git status --porcelain apartment/ | wc -l)
echo "[apartment dirty] $DIRTY lines"
[ "$DIRTY" -eq 0 ] || { echo "PHASE_FAILED: working tree dirty"; git status --porcelain apartment/; exit 1; }

# 3. commit 개수 self-check (0 또는 1)
COMMITS=$(git log --format='%H' HEAD~1..HEAD | wc -l)
echo "[commit count] $COMMITS"
[ "$COMMITS" -le 1 ] || { echo "PHASE_FAILED: phase commit $COMMITS > 1"; exit 1; }

echo "✓ Phase 04 검증 통과"
```

---

## 의도 메모

- 잔재 0건이 기본 기대 — phase-01/02가 정확히 잔재 정리했다면. 본 phase는 safety net (common-pitfalls 6-5 destructive edit 회피).
- 잔재 발견 시 명시적 Edit 갱신. 옛 path 인용은 phase-01/02 누락 신호.
- README.md stale 영역 (career-os command-router, _shared/lib invoke_claude_skills 등)은 본 plan001 범위 밖 — 별도 chore commit.
- commit 개수 0 또는 1 모두 정상 — 잔재 유무에 따라.
