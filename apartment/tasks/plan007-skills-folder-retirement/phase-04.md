# Phase 04 — ai-nodes 메타 (workspace-structure 갱신 + AGENTS 1-1 비대칭 표 제거)

**Model**: sonnet
**Status**: pending

---

## 목표

ai-nodes 모노레포 메타 갱신 — 본 plan007이 *분리 표준* (ai-nodes ADR-006) 첫 적용 사례. 청사진·매트릭스·의도된 비대칭 표 모두 갱신:

- `ai-nodes/docs/workspace-structure.md` 2번 표준 디렉터리 트리 — 통합 → 분리
- `ai-nodes/docs/workspace-structure.md` 6번 skills/ 컨벤션 — 분리 패턴 명시
- `ai-nodes/docs/workspace-structure.md` 8번 의도된 비대칭 표 — career-os 항목 제거 (비대칭이 표준으로 격상)
- `ai-nodes/docs/workspace-structure.md` 9번 준수도 매트릭스 — apartment skills 항목 "적용 (plan007)"
- `ai-nodes/AGENTS.md` 1-1 career-os 한정 컨벤션 — 본문 제거 또는 "ADR-006로 표준 격상" 표기
- `ai-nodes/AGENTS.md` 3-1 apartment 진입점 — 새 path

**범위 외**: apartment 5문서 (phase-03), 코드 마이그 (phase-01/02), 검증 (phase-05). ADR 본문은 commit `5eb29a8`에 이미 박힘.

---

## 본 phase 강제 주의문

- 반드시 Edit 도구로 ai-nodes 메타 갱신. prose 응답만으로는 PHASE_FAILED.
- section sigil (section mark, U+00A7) 사용 금지.
- 본 phase commit 개수 self-check = 1.

---

## 사전 cwd 설정 (run-phases.py hotfix)

```bash
cd "$(git rev-parse --show-toplevel)"
pwd  # 기대: /home/bifos/ai-nodes
```

---

## 관련 docs

- ai-nodes ADR-006 (`docs/adr.md` line 251) — 워크스페이스 표준 패턴 변경: 통합 → 분리
- ai-nodes ADR-004 Status (Partially superseded by ADR-006) — skills/<name>/ 통합 표준 부분만
- career-os ADR-019 Status (Lifted to ai-nodes ADR-006) — 비대칭이 표준으로 격상

---

## 작업 항목

### 1. workspace-structure.md 2번 표준 디렉터리 트리 갱신

현재 본문 (line 165 추정):

```
1. 디렉터리 트리 — AGENTS.md / CLAUDE.md 심링크 / .env / .env.example / config/ / docs/ 5문서 / skills/<name>/{SKILL.md, references/, scripts/} / .claude/skills/<name>/ / tasks/plan{N}-<slug>/ / data/ / logs/.
```

→ 분리 패턴으로:

```
1. 디렉터리 트리 — AGENTS.md / CLAUDE.md 심링크 / .env / .env.example / config/ / docs/ 5문서 / scripts/<name>/ (실행 파일) / .claude/skills/<name>/{SKILL.md, references/} (컨텍스트 자산) / tasks/plan{N}-<slug>/ / data/ / logs/. (ADR-006: 통합 표준 폐기, 분리 표준 채택)
```

`Edit`로 갱신. 정확한 본문 grep으로 확인:

```bash
grep -n "skills/<name>/{SKILL.md\|scripts/<name>" docs/workspace-structure.md
```

### 2. workspace-structure.md 6번 skills/ 컨벤션 갱신

현재 *통합 패턴 표준*으로 적혀 있을 가능성:

```
6. skills/ 컨벤션 — `<workspace>/skills/<name>/{SKILL.md, references/, scripts/}` 통합 구조 + native skill 등록 (`.claude/skills/<name>/SKILL.md`).
```

→ 분리 패턴:

```
6. skills/ 컨벤션 — `<workspace>/scripts/<name>/` 실행 파일 분리 + `<workspace>/.claude/skills/<name>/{SKILL.md, references/}` 컨텍스트 자산 본체 (ADR-006). native skill 등록 단일 출처.
```

### 3. workspace-structure.md 8번 의도된 비대칭 표 갱신

기존 표:

```
| 워크스페이스 | 비대칭 내용 | 근거 |
|---|---|---|
| career-os | `scripts/<skill-name>/` 별도 디렉터리 + `.claude/skills/<name>/` 분리. skills/는 SKILL.md + references/ 만. | career-os ADR-019 (scripts/ 분리, 컨텍스트 로드 효율) |
| apartment | 없음 (표준 따름) | — |
| ...
```

→ career-os 항목 제거 (비대칭이 표준으로 격상). 표 본문 갱신:

```
| 워크스페이스 | 비대칭 내용 | 근거 |
|---|---|---|
| (모든 워크스페이스 표준 따름 — career-os ADR-019 분리 패턴이 ADR-006로 격상되어 의도된 비대칭 없음) | — | — |
| stock-investment | TODO — 별도 audit 필요 | — |
| travel | TODO — 별도 audit 필요 | — |
```

또는 표 자체 간소화 — career-os 행 제거 + apartment 행 제거 + "현재 의도된 비대칭 없음" 한 줄.

### 4. workspace-structure.md 9번 준수도 매트릭스 갱신

apartment skills/ 항목을 *적용 (plan007)*으로:

```
| 항목 | apartment | career-os | stock-investment | travel |
|---|---|---|---|---|
| skills/ 분리 표준 (ADR-006) | 적용 (plan007) | 적용 (ADR-019 격상) | TODO | TODO |
```

기존 항목 갱신 — *통합* 또는 *비대칭*에서 *적용 (plan007)*으로.

### 5. ai-nodes/AGENTS.md 1-1 career-os 한정 컨벤션 갱신

현재 (line 32-36):

```
### 1-1. career-os 한정 컨벤션 (ADR-019)

career-os만 `scripts/<skill-name>/`(실행 파일) + `skills/<skill-name>/`(SKILL.md + references) 분리 구조. 다른 워크스페이스는 `<workspace>/skills/<name>/scripts/` 표준 구조 유지.

워크스페이스 격리 원칙상 이 비대칭은 의도된 것 — 다른 워크스페이스로 컨벤션 확산은 별도 결정 필요.
```

→ 본문 제거 또는 *격상 표기*. 옵션 (사용자 결정 영역):

옵션 A (본문 제거 + 한 줄 표기):

```
### 1-1. 분리 표준 (ADR-006)

`<workspace>/scripts/<name>/` 실행 파일 + `<workspace>/.claude/skills/<name>/{SKILL.md, references/}` 컨텍스트 자산 본체. career-os ADR-019 비대칭이 ADR-006로 표준 격상 (2026-05-19). apartment plan007 첫 적용. stock-investment / travel은 audit 시 본 표준 따름.
```

옵션 B (섹션 자체 제거):

1-1 섹션 자체 제거. 본 정보는 *workspace-structure.md 단일 출처*.

본 phase는 옵션 A 적용 권장 (정보 보존 + 격상 명시).

### 6. ai-nodes/AGENTS.md 3-1 apartment 진입점 갱신

현재 (line 53-57):

```
### 3-1. apartment

```bash
apartment/skills/apartment-daily-report/scripts/run_report.sh
```
```

→ 새 path + native skill 진입점 추가:

```
### 3-1. apartment

native skill 2개:

```bash
claude -p "/apartment-daily-report"
claude -p "/apartment-interior-reference-digest"
```

직접 호출:

```bash
bash apartment/scripts/apartment-daily-report/run_report.sh
bash apartment/scripts/apartment-interior-reference-digest/run_digest.sh
```
```

산출물 위치는 기존 그대로.

### 7. commit 생성

```bash
git add docs/workspace-structure.md AGENTS.md
git commit -m "$(cat <<'EOF'
docs(ai-nodes): workspace-structure + AGENTS 갱신 — 분리 표준 적용 (plan007 phase-04, ADR-006)

ai-nodes ADR-006 적용 (workspace-structure.md 청사진 갱신):
- 2번 표준 디렉터리 트리: 통합 (skills/<name>/{SKILL,refs,scripts}) → 분리 (scripts/<name>/ + .claude/skills/<name>/{SKILL,refs})
- 6번 skills/ 컨벤션: 분리 패턴 명시
- 8번 의도된 비대칭 표: career-os 항목 제거 (격상)
- 9번 준수도 매트릭스: apartment skills/ → "적용 (plan007)"

ai-nodes/AGENTS.md:
- 1-1 career-os 한정 컨벤션 → 분리 표준 (ADR-006 격상)으로 본문 갱신
- 3-1 apartment 진입점: 새 path (scripts/ + .claude/skills/) + interior native 진입점 추가

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## 검증 (phase 종료 직전)

```bash
SIGIL_CHAR=$(printf '\xc2\xa7')

# 1. workspace-structure.md 청사진 갱신
grep -q "ADR-006" docs/workspace-structure.md || { echo "PHASE_FAILED: ADR-006 인용 누락"; exit 1; }
grep -q "scripts/<name>/.*\.claude/skills/<name>" docs/workspace-structure.md || grep -q "scripts/<name>" docs/workspace-structure.md && grep -q ".claude/skills/<name>/{SKILL.md, references/}" docs/workspace-structure.md || { echo "PHASE_FAILED: 분리 트리 명시 누락"; exit 1; }
echo "[1 workspace-structure 분리 트리] OK"

# 2. 의도된 비대칭 표에서 career-os scripts/ 분리 본문 제거 (격상)
LEFT=$(grep -c "career-os.*scripts/<skill-name>/.*별도 디렉터리" docs/workspace-structure.md || echo 0)
[ "$LEFT" -eq 0 ] || { echo "PHASE_FAILED: career-os 비대칭 본문 잔존"; exit 1; }
echo "[2 비대칭 표 제거] OK"

# 3. ai-nodes/AGENTS.md 1-1 갱신 + 3-1 새 path
grep -q "ADR-006" AGENTS.md || { echo "PHASE_FAILED: AGENTS.md ADR-006 인용 누락"; exit 1; }
LEFT=$(grep -c "apartment/skills/apartment-daily-report/scripts/run_report.sh" AGENTS.md || echo 0)
[ "$LEFT" -eq 0 ] || { echo "PHASE_FAILED: AGENTS.md 옛 apartment 진입점 잔존"; exit 1; }
echo "[3 AGENTS 갱신] OK"

# 4. section sigil
for f in docs/workspace-structure.md AGENTS.md; do
  COUNT=$(grep -c "$SIGIL_CHAR" "$f" 2>/dev/null || echo 0)
  [ "$COUNT" -eq 0 ] || { echo "PHASE_FAILED: $f sigil 잔재 $COUNT"; exit 1; }
done
echo "[4 sigil] 0건"

# 5. commit 개수
COMMITS=$(git log --format='%H' HEAD~1..HEAD | wc -l)
echo "[5 commit count] $COMMITS"
[ "$COMMITS" -eq 1 ] || { echo "PHASE_FAILED: phase commit $COMMITS != 1"; exit 1; }

echo "✓ Phase 04 검증 통과"
```

---

## 의도 메모

- workspace-structure.md = 청사진 단일 출처. ADR-006 결정 적용.
- 1-1 career-os 한정 컨벤션 → *분리 표준* 본문으로 — 정보 보존 + 격상 명시.
- 매트릭스 9번 *apartment 적용 (plan007)* = 본 plan의 실 결과 기록.
- stock-investment / travel은 *audit TODO* 유지 — 별도 사이클.
