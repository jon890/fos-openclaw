# Phase 03 — apartment 5문서 + AGENTS.md 본문 갱신

**Model**: sonnet
**Status**: pending

---

## 목표

phase-01/02에서 코드 마이그 완료된 새 디렉터리 구조 (`apartment/scripts/<name>/` + `apartment/.claude/skills/<name>/`)를 apartment 5문서 + AGENTS.md 본문에 반영:

- `apartment/docs/code-architecture.md` — 디렉터리 트리 + skill 표준 갱신
- `apartment/docs/prd.md` — 워크플로 진입점 path
- `apartment/docs/flow.md` — 진입점 path + runner 내부 path
- `apartment/docs/data-schema.md` — 영향 작음 (config / data path 동일). 단 *진입점 인용*이 있다면 갱신
- `apartment/AGENTS.md` — 워크플로 진입점 5번 갱신

**범위 외**: 코드 마이그 (phase-01/02), ai-nodes 메타 (phase-04), 통합 검증 (phase-05). ADR 본문은 docs commit `5eb29a8`에 이미 박힘 — 본 phase에서 갱신 안 함.

---

## 본 phase 강제 주의문

- 반드시 Edit 도구로 5문서 + AGENTS.md를 갱신. prose 응답만으로는 PHASE_FAILED.
- 작성·수정하는 모든 문서에 section sigil (section mark, U+00A7) 사용 금지.
- 본 phase commit 개수 self-check = 1.

---

## 사전 cwd 설정 (run-phases.py hotfix)

```bash
cd "$(git rev-parse --show-toplevel)"
pwd  # 기대: /home/bifos/ai-nodes
```

---

## 관련 docs

- apartment ADR-004 (docs commit `5eb29a8`) — skills/ 폐기 + .claude/skills/ 본체화 결정의 *왜*.
- phase-01/02 산출: `apartment/scripts/{apartment-daily-report, apartment-interior-reference-digest}/` + `apartment/.claude/skills/{...}/`.

---

## 작업 항목

### 1. apartment/docs/code-architecture.md 디렉터리 트리 갱신

기존 트리에서 `skills/<name>/{SKILL.md, references/, scripts/}` 통합 표현 → 분리 표현으로 변경:

- `apartment/skills/` 디렉터리 자체 제거 (또는 `폐기 (plan007, ADR-004)` 표시)
- `apartment/scripts/<name>/` 추가 (실행 파일 분리)
- `apartment/.claude/skills/<name>/{SKILL.md, references/}` 추가 (컨텍스트 자산 본체)
- skill 표준 설명 갱신 — 분리 패턴 (ai-nodes ADR-006 표준)
- native skill 등록 표 갱신 — apartment-interior-reference-digest 미등록 → 등록

`Edit` 도구로 정확한 본문 갱신. 본문 위치 확인:

```bash
grep -n "skills/<name>\|skills/apartment\|apartment/skills" apartment/docs/code-architecture.md
```

검증:

```bash
LEFT=$(grep -c "apartment/skills/" apartment/docs/code-architecture.md || echo 0)
echo "[옛 apartment/skills/ 인용] $LEFT"
[ "$LEFT" -eq 0 ] || { echo "PHASE_FAILED: code-architecture.md에 옛 인용 잔존 $LEFT"; exit 1; }

grep -q "apartment/scripts/" apartment/docs/code-architecture.md || { echo "PHASE_FAILED: scripts/ 분리 명시 누락"; exit 1; }
grep -q "apartment/.claude/skills/" apartment/docs/code-architecture.md || { echo "PHASE_FAILED: .claude/skills/ 본체 명시 누락"; exit 1; }
echo "[code-architecture 갱신] OK"
```

### 2. apartment/docs/prd.md 워크플로 진입점 갱신

기존 진입점 표 또는 본문에 `apartment/skills/apartment-daily-report/scripts/run_report.sh` 등 인용 → 새 path로:

- `bash apartment/scripts/apartment-daily-report/run_report.sh` (직접)
- `claude -p "/apartment-daily-report"` (native)
- `bash apartment/scripts/apartment-interior-reference-digest/run_digest.sh`
- `claude -p "/apartment-interior-reference-digest"` (신규 native)

```bash
grep -n "apartment/skills\|run_report.sh\|run_digest.sh" apartment/docs/prd.md
```

검증:

```bash
LEFT=$(grep -c "apartment/skills/" apartment/docs/prd.md || echo 0)
[ "$LEFT" -eq 0 ] || { echo "PHASE_FAILED: prd.md 옛 인용 잔존 $LEFT"; exit 1; }
grep -q "/apartment-interior-reference-digest" apartment/docs/prd.md || { echo "PHASE_FAILED: native interior 인용 누락"; exit 1; }
echo "[prd.md 갱신] OK"
```

### 3. apartment/docs/flow.md 진입점 + runner path 갱신

flow.md는 진입점 + runner 내부 path 인용 다수 — phase-01/02 마이그 결과 반영.

```bash
grep -n "apartment/skills" apartment/docs/flow.md
```

각 인용을 새 path로 `Edit`:

- `apartment/skills/apartment-daily-report/scripts/run_report.sh` → `apartment/scripts/apartment-daily-report/run_report.sh`
- `apartment/skills/apartment-daily-report/scripts/collect_sources.py` → `apartment/scripts/apartment-daily-report/collect_sources.py`
- `apartment/skills/apartment-daily-report/scripts/notify_discord.sh` → `apartment/scripts/apartment-daily-report/notify_discord.sh`
- `apartment/skills/apartment-interior-reference-digest/scripts/run_digest.sh` → `apartment/scripts/apartment-interior-reference-digest/run_digest.sh`

검증:

```bash
LEFT=$(grep -c "apartment/skills/" apartment/docs/flow.md || echo 0)
[ "$LEFT" -eq 0 ] || { echo "PHASE_FAILED: flow.md 옛 인용 잔존"; exit 1; }
echo "[flow.md 갱신] OK"
```

### 4. apartment/docs/data-schema.md 점검 (영향 작음)

```bash
grep -n "apartment/skills" apartment/docs/data-schema.md || echo "(인용 없음)"
```

인용 발견 시 `Edit`로 갱신. 보통 data-schema.md는 config / data path 위주이므로 영향 작음.

### 5. apartment/AGENTS.md 워크플로 진입점 갱신

기존 (line 53-58 추정):

```bash
claude -p "/apartment-daily-report"
bash apartment/skills/apartment-daily-report/scripts/run_report.sh
bash apartment/skills/apartment-interior-reference-digest/scripts/run_digest.sh
bash apartment/skills/apartment-daily-report/scripts/run_smoke_test.sh
```

→ 새 path로 + interior native 진입점 추가:

```bash
# native skill 진입점
claude -p "/apartment-daily-report"
claude -p "/apartment-interior-reference-digest"

# 또는 직접 호출
bash apartment/scripts/apartment-daily-report/run_report.sh
bash apartment/scripts/apartment-interior-reference-digest/run_digest.sh
bash apartment/scripts/apartment-daily-report/run_smoke_test.sh
```

검증:

```bash
LEFT=$(grep -c "apartment/skills/" apartment/AGENTS.md || echo 0)
[ "$LEFT" -eq 0 ] || { echo "PHASE_FAILED: AGENTS.md 옛 인용 잔존"; exit 1; }
grep -q "/apartment-interior-reference-digest" apartment/AGENTS.md || { echo "PHASE_FAILED: AGENTS.md interior native 진입점 누락"; exit 1; }
echo "[AGENTS.md 갱신] OK"
```

### 6. commit 생성

```bash
git add apartment/docs apartment/AGENTS.md
git commit -m "$(cat <<'EOF'
docs(apartment): 5문서 + AGENTS.md skills/ → scripts/ + .claude/skills/ 분리 path 갱신 (plan007 phase-03)

phase-01/02에서 코드 마이그 완료된 새 구조 (ADR-004) 반영:
- code-architecture.md: 디렉터리 트리 + skill 표준 (분리 패턴)
- prd.md: 워크플로 진입점 (native + 직접 호출)
- flow.md: 진입점 + runner 내부 path
- data-schema.md: 영향 작음 (인용 있을 시만)
- AGENTS.md: 워크플로 진입점 native skill 2개 + 직접 호출 path

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## 검증 (phase 종료 직전)

```bash
SIGIL_CHAR=$(printf '\xc2\xa7')

# 1. 5문서 + AGENTS.md 모두 옛 path 인용 0건
for f in apartment/docs/prd.md apartment/docs/data-schema.md apartment/docs/flow.md apartment/docs/code-architecture.md apartment/AGENTS.md; do
  LEFT=$(grep -c "apartment/skills/apartment" "$f" 2>/dev/null || echo 0)
  echo "[$f 옛 인용] $LEFT"
  [ "$LEFT" -eq 0 ] || { echo "PHASE_FAILED: $f 옛 path 잔존 $LEFT"; exit 1; }
done

# 2. native skill 진입점 2개 모두 문서화
grep -q "/apartment-daily-report" apartment/AGENTS.md && grep -q "/apartment-interior-reference-digest" apartment/AGENTS.md || { echo "PHASE_FAILED: native 진입점 누락"; exit 1; }
echo "[2 native 진입점] OK"

# 3. section sigil
for f in apartment/docs/prd.md apartment/docs/data-schema.md apartment/docs/flow.md apartment/docs/code-architecture.md apartment/AGENTS.md; do
  COUNT=$(grep -c "$SIGIL_CHAR" "$f" 2>/dev/null || echo 0)
  [ "$COUNT" -eq 0 ] || { echo "PHASE_FAILED: $f sigil 잔재 $COUNT"; exit 1; }
done
echo "[3 sigil] 0건"

# 4. commit 개수
COMMITS=$(git log --format='%H' HEAD~1..HEAD | wc -l)
echo "[4 commit count] $COMMITS"
[ "$COMMITS" -eq 1 ] || { echo "PHASE_FAILED: phase commit $COMMITS != 1"; exit 1; }

echo "✓ Phase 03 검증 통과"
```

---

## 의도 메모

- ADR 본문은 docs commit `5eb29a8`에 이미 박힘 — 본 phase는 *5문서 본문 갱신*만.
- 5문서 갱신은 *코드 마이그 결과 반영* (phase-01/02 산출).
- AGENTS.md 갱신에 interior-reference-digest native 진입점 추가 — 사용자가 자연어 호출 가능 (`claude -p "/apartment-interior-reference-digest"`).
