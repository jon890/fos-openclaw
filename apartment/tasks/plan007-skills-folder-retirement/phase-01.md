# Phase 01 — apartment-daily-report 마이그 (scripts + SKILL/references + symlink 폐기)

**Model**: sonnet
**Status**: pending

---

## 목표

apartment-daily-report skill의 본체를 `apartment/skills/apartment-daily-report/`에서 분리 패턴으로 이동:

- `scripts/` → `apartment/scripts/apartment-daily-report/` (실행 파일 분리)
- `SKILL.md` + `references/` → `apartment/.claude/skills/apartment-daily-report/` (컨텍스트 자산 본체)
- 기존 `apartment/.claude/skills/apartment-daily-report` symlink 폐기 (본체화)
- runner의 `SKILL_ROOT` 패턴 정정 — 자기 위치 기준 `apartment/scripts/<name>/` → `apartment/.claude/skills/<name>/` 참조

**범위 외**: apartment-interior-reference-digest 마이그 (phase-02), 5문서 갱신 (phase-03), ai-nodes 메타 (phase-04), 검증 (phase-05).

---

## 본 phase 강제 주의문

- 반드시 Write/Edit/Bash 도구로 file 이동·수정·삭제를 수행. prose 응답만으로는 PHASE_FAILED (common-pitfalls 6-6).
- 작성·수정하는 모든 문서에 section sigil (section mark, U+00A7) 특수문자 사용 금지.
- destructive edit (symlink 폐기, file 이동) 후 즉시 검증 (`test -e`, `git ls-files | wc -l`).
- 본 phase commit 개수 self-check = 1.

---

## 사전 cwd 설정 (run-phases.py hotfix)

run-phases.py는 cwd=apartment로 phase 실행. 본 phase는 ai-nodes 루트 기준 `apartment/...` path 다수 인용 — 첫 bash 호출에서 cwd=ai-nodes 루트로 변경. Claude Code Bash 도구 cwd 보존 → 후속 자동 유지.

```bash
cd "$(git rev-parse --show-toplevel)"
pwd  # 기대: /home/bifos/ai-nodes
```

---

## 관련 docs

- apartment ADR-004 (`apartment/docs/adr.md` line 141)
- ai-nodes ADR-006 (`docs/adr.md` line 251)
- 현재 구조 참조: `apartment/skills/apartment-daily-report/` (SKILL.md + references/ + scripts/ 통합)

---

## 작업 항목

### 1. apartment/.claude/skills/apartment-daily-report symlink 폐기

```bash
test -L apartment/.claude/skills/apartment-daily-report && rm apartment/.claude/skills/apartment-daily-report
test ! -e apartment/.claude/skills/apartment-daily-report && echo "[symlink removed] OK"
```

### 2. scripts/ 이동 — apartment/scripts/apartment-daily-report/

```bash
mkdir -p apartment/scripts/apartment-daily-report
git mv apartment/skills/apartment-daily-report/scripts/* apartment/scripts/apartment-daily-report/
rmdir apartment/skills/apartment-daily-report/scripts
```

검증:

```bash
COUNT=$(ls apartment/scripts/apartment-daily-report/ | wc -l)
echo "[moved scripts] $COUNT files"
[ "$COUNT" -ge 7 ] || { echo "PHASE_FAILED: scripts $COUNT < 7"; exit 1; }
test ! -d apartment/skills/apartment-daily-report/scripts && echo "[옛 scripts/ 디렉터리 폐기] OK"
```

### 3. SKILL.md + references/ 이동 — apartment/.claude/skills/apartment-daily-report/

```bash
mkdir -p apartment/.claude/skills/apartment-daily-report
git mv apartment/skills/apartment-daily-report/SKILL.md apartment/.claude/skills/apartment-daily-report/SKILL.md
git mv apartment/skills/apartment-daily-report/references apartment/.claude/skills/apartment-daily-report/references
```

검증:

```bash
test -f apartment/.claude/skills/apartment-daily-report/SKILL.md && echo "[SKILL.md moved] OK"
test -d apartment/.claude/skills/apartment-daily-report/references && echo "[references/ moved] OK"
REFS=$(ls apartment/.claude/skills/apartment-daily-report/references | wc -l)
echo "[references] $REFS files"
[ "$REFS" -ge 2 ] || { echo "PHASE_FAILED: references $REFS < 2"; exit 1; }
```

### 4. apartment/skills/apartment-daily-report/ 디렉터리 폐기 (빈 디렉터리)

```bash
rmdir apartment/skills/apartment-daily-report 2>/dev/null && echo "[skills/<name>/ removed] OK" || echo "(여전히 비어있지 않음)"
test ! -d apartment/skills/apartment-daily-report && echo "[apartment/skills/apartment-daily-report 폐기] 확정"
```

### 5. runner SKILL_ROOT 정정 (apartment/scripts/apartment-daily-report/run_report.sh)

`Edit` 도구로 `apartment/scripts/apartment-daily-report/run_report.sh`의 `SKILL_ROOT` 라인 갱신.

기존 패턴 (line 22):

```bash
SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
```

이건 `apartment/skills/apartment-daily-report/`을 가리킴 (이전 구조). 마이그 후 *.scripts/apartment-daily-report/* 위치에서 *.claude/skills/apartment-daily-report/* 참조 필요:

```bash
WS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SKILL_ROOT="$WS_ROOT/.claude/skills/apartment-daily-report"
```

기존 `SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"` → 위 2줄로 교체.

이후 `$SKILL_ROOT/scripts/...` 인용은 *.claude/skills/apartment-daily-report/scripts/...* 였으나 scripts 이동되어 *.claude/skills/<name>/scripts/* 부재. 대신 *apartment/scripts/apartment-daily-report/* 가 실제 위치 — `$(dirname "$0")` 또는 `$WS_ROOT/scripts/apartment-daily-report/`.

`run_report.sh` 본문에 `$SKILL_ROOT/scripts/notify_discord.sh`, `$SKILL_ROOT/scripts/normalize_results.py`, `$SKILL_ROOT/scripts/collect_sources.py` 등 인용 다수 — 모두 `$(dirname "$0")/` 또는 `$WS_ROOT/scripts/apartment-daily-report/`로 변경.

정확한 갱신은 phase Claude가 `Edit` 도구로 처리. 검증:

```bash
bash -n apartment/scripts/apartment-daily-report/run_report.sh && echo "[shell syntax] OK" || { echo "PHASE_FAILED: shell syntax 오류"; exit 1; }
grep -q "apartment/skills/" apartment/scripts/apartment-daily-report/run_report.sh && { echo "PHASE_FAILED: 옛 apartment/skills/ 인용 잔존"; exit 1; }
echo "[runner SKILL_ROOT 정정] OK"
```

### 6. commit 생성

```bash
git add apartment/scripts/apartment-daily-report apartment/.claude/skills/apartment-daily-report apartment/skills/apartment-daily-report
git commit -m "$(cat <<'EOF'
refactor(apartment): apartment-daily-report skills/ 폐기 + .claude/skills/ 본체화 (plan007 phase-01)

apartment ADR-004 + ai-nodes ADR-006 적용:
- apartment/skills/apartment-daily-report/ 폐기
- apartment/scripts/apartment-daily-report/ 신설 (실행 파일 분리, 7+ scripts)
- apartment/.claude/skills/apartment-daily-report/ 본체화 (SKILL.md + references/)
- 기존 .claude/skills/apartment-daily-report symlink 폐기 (mirror → 본체)
- run_report.sh SKILL_ROOT 정정: 자기 위치 기준 상대 ($(dirname "$0")/../.. 패턴)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## 검증 (phase 종료 직전)

```bash
SIGIL_CHAR=$(printf '\xc2\xa7')

# 1. 새 위치 자산 존재
test -f apartment/.claude/skills/apartment-daily-report/SKILL.md || { echo "PHASE_FAILED: SKILL.md missing"; exit 1; }
test -d apartment/.claude/skills/apartment-daily-report/references || { echo "PHASE_FAILED: references missing"; exit 1; }
test -f apartment/scripts/apartment-daily-report/run_report.sh || { echo "PHASE_FAILED: run_report.sh missing"; exit 1; }
echo "[1 새 위치 자산] OK"

# 2. 옛 위치 폐기
test ! -e apartment/skills/apartment-daily-report || { echo "PHASE_FAILED: 옛 skills/ 잔존"; exit 1; }
echo "[2 옛 위치 폐기] OK"

# 3. symlink 부재 확인 (본체화)
test ! -L apartment/.claude/skills/apartment-daily-report || { echo "PHASE_FAILED: symlink 잔존"; exit 1; }
echo "[3 symlink 폐기 + 본체화] OK"

# 4. shell syntax
bash -n apartment/scripts/apartment-daily-report/run_report.sh || { echo "PHASE_FAILED: shell syntax"; exit 1; }
bash -n apartment/scripts/apartment-daily-report/run_smoke_test.sh || { echo "PHASE_FAILED: smoke syntax"; exit 1; }
echo "[4 shell syntax] OK"

# 5. 옛 apartment/skills/ 참조 잔존 (phase-03 책임이지만 본 phase 산출물 자체는 검증)
LEFT=$(grep -r "apartment/skills/apartment-daily-report" apartment/scripts/apartment-daily-report 2>/dev/null | wc -l)
echo "[5 옛 path 인용 in 본 phase 산출] $LEFT"
[ "$LEFT" -eq 0 ] || { echo "PHASE_FAILED: 옛 apartment/skills 인용 잔존 $LEFT"; exit 1; }

# 6. section sigil
COUNT=$(grep -c "$SIGIL_CHAR" apartment/.claude/skills/apartment-daily-report/SKILL.md 2>/dev/null || echo 0)
[ "$COUNT" -eq 0 ] || { echo "PHASE_FAILED: SKILL.md sigil 잔재"; exit 1; }
echo "[6 sigil] 0건"

# 7. commit 개수
COMMITS=$(git log --format='%H' HEAD~1..HEAD | wc -l)
echo "[7 commit count] $COMMITS"
[ "$COMMITS" -eq 1 ] || { echo "PHASE_FAILED: phase commit $COMMITS != 1"; exit 1; }

echo "✓ Phase 01 검증 통과"
```

---

## 의도 메모

- `git mv`로 history 보존 — file 이동 추적 가능.
- runner `SKILL_ROOT` 정정 — apartment ADR-004 결정 (자기 위치 기준 상대 path, A안).
- symlink 폐기 = 본체화 완료. `.claude/skills/<name>/`가 단일 출처.
- 본 phase 후 apartment-daily-report 호출:
  - native: `claude -p "/apartment-daily-report"` (기존 동작 유지 — symlink 폐기 후 본체로 직접)
  - direct: `bash apartment/scripts/apartment-daily-report/run_report.sh`
- 5문서 본문 path 갱신은 phase-03 책임. 본 phase는 코드 이동 + runner 정정에 집중.
