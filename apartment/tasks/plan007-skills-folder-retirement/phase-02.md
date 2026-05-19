# Phase 02 — apartment-interior-reference-digest 마이그 + native 등록 + skills/ 디렉터리 폐기

**Model**: sonnet
**Status**: pending

---

## 목표

apartment-interior-reference-digest skill 마이그 + native 등록 (현재 `.claude/skills/` 미등록 상태) + apartment/skills/ 디렉터리 자체 폐기:

- `scripts/` → `apartment/scripts/apartment-interior-reference-digest/` (run_digest.sh 1개)
- `SKILL.md` + `references/` → `apartment/.claude/skills/apartment-interior-reference-digest/` (신규 native 등록)
- `apartment/skills/apartment-interior-reference-digest/` 디렉터리 폐기
- `apartment/skills/` 디렉터리 자체 폐기 (모든 skill 이동 완료)

**범위 외**: apartment-daily-report 마이그 (phase-01 완료 가정), 5문서 갱신 (phase-03), ai-nodes 메타 (phase-04), 검증 (phase-05).

---

## 본 phase 강제 주의문

- 반드시 Write/Edit/Bash 도구로 file 이동·수정·삭제 수행. prose 응답만으로는 PHASE_FAILED.
- 작성·수정하는 모든 문서에 section sigil (section mark, U+00A7) 사용 금지.
- destructive edit (디렉터리 폐기) 후 즉시 검증 (`test ! -e`).
- 본 phase commit 개수 self-check = 1.

---

## 사전 cwd 설정 (run-phases.py hotfix)

```bash
cd "$(git rev-parse --show-toplevel)"
pwd  # 기대: /home/bifos/ai-nodes
```

---

## 관련 docs

- apartment ADR-004 (`apartment/docs/adr.md`)
- ai-nodes ADR-006 (`docs/adr.md`)
- phase-01 산출: `apartment/scripts/apartment-daily-report/` + `apartment/.claude/skills/apartment-daily-report/` 본체화 완료

---

## 작업 항목

### 1. scripts/ 이동 — apartment/scripts/apartment-interior-reference-digest/

```bash
mkdir -p apartment/scripts/apartment-interior-reference-digest
git mv apartment/skills/apartment-interior-reference-digest/scripts/run_digest.sh apartment/scripts/apartment-interior-reference-digest/run_digest.sh
rmdir apartment/skills/apartment-interior-reference-digest/scripts
```

검증:

```bash
test -f apartment/scripts/apartment-interior-reference-digest/run_digest.sh && echo "[moved run_digest.sh] OK"
test ! -d apartment/skills/apartment-interior-reference-digest/scripts && echo "[옛 scripts/ 폐기] OK"
```

### 2. SKILL.md + references/ 이동 — apartment/.claude/skills/apartment-interior-reference-digest/ (신규 native 등록)

```bash
mkdir -p apartment/.claude/skills/apartment-interior-reference-digest
git mv apartment/skills/apartment-interior-reference-digest/SKILL.md apartment/.claude/skills/apartment-interior-reference-digest/SKILL.md
git mv apartment/skills/apartment-interior-reference-digest/references apartment/.claude/skills/apartment-interior-reference-digest/references
```

검증:

```bash
test -f apartment/.claude/skills/apartment-interior-reference-digest/SKILL.md && echo "[SKILL.md moved + native 등록] OK"
test -d apartment/.claude/skills/apartment-interior-reference-digest/references && echo "[references/ moved] OK"
```

### 3. apartment/skills/apartment-interior-reference-digest/ 디렉터리 폐기

```bash
rmdir apartment/skills/apartment-interior-reference-digest 2>/dev/null && echo "[interior-digest skills/<name>/ 폐기] OK" || echo "(빈 디렉터리 아님)"
test ! -d apartment/skills/apartment-interior-reference-digest && echo "[apartment/skills/apartment-interior-reference-digest 폐기] 확정"
```

### 4. apartment/skills/ 디렉터리 자체 폐기 (마지막 skill 이동 완료)

```bash
# 현 상태 확인 — 빈 디렉터리여야 함
ls apartment/skills/ 2>&1
COUNT=$(ls apartment/skills/ 2>/dev/null | wc -l)
echo "[apartment/skills/ 남은 entry] $COUNT"
[ "$COUNT" -eq 0 ] || { echo "PHASE_FAILED: skills/ 비어있지 않음 ($COUNT)"; ls apartment/skills/; exit 1; }

# 폐기
rmdir apartment/skills && echo "[apartment/skills/ 디렉터리 자체 폐기] OK"
test ! -e apartment/skills && echo "[apartment/skills/ 부재 확인] OK"
```

### 5. run_digest.sh 내부 path 인용 검증 (단순 thin runner라 path 인용 적음)

```bash
# run_digest.sh 본문 path 패턴 확인
grep -n "apartment/skills\|SKILL_ROOT\|TASK_ROOT" apartment/scripts/apartment-interior-reference-digest/run_digest.sh | head -10

# 옛 apartment/skills/ 인용 잔존 시 갱신 필요
LEFT=$(grep -c "apartment/skills/" apartment/scripts/apartment-interior-reference-digest/run_digest.sh || echo 0)
echo "[옛 apartment/skills 인용] $LEFT"
[ "$LEFT" -eq 0 ] || { echo "WARN: run_digest.sh에 옛 apartment/skills 인용 $LEFT 건 — Edit 도구로 갱신 필요"; }
```

run_digest.sh 본문이 *thin runner*이고 `TASK_ROOT="${TASK_ROOT:-$HOME/ai-nodes/apartment}"` 같은 절대 경로 위주라 *옛 apartment/skills 인용 없을 가능성 높음*. 단 있으면 `Edit` 도구로 새 path (`apartment/scripts/apartment-interior-reference-digest/`)로 갱신.

### 6. commit 생성

```bash
git add apartment/scripts/apartment-interior-reference-digest apartment/.claude/skills/apartment-interior-reference-digest apartment/skills
git commit -m "$(cat <<'EOF'
refactor(apartment): apartment-interior-reference-digest 마이그 + native 등록 + skills/ 디렉터리 폐기 (plan007 phase-02)

apartment ADR-004 + ai-nodes ADR-006 적용:
- apartment/skills/apartment-interior-reference-digest/ 폐기
- apartment/scripts/apartment-interior-reference-digest/ 신설 (run_digest.sh)
- apartment/.claude/skills/apartment-interior-reference-digest/ 신규 native 등록 (SKILL.md + references/)
- apartment/skills/ 디렉터리 자체 폐기 — 모든 skill 분리 완료
- claude -p "/apartment-interior-reference-digest" 호출 가능

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## 검증 (phase 종료 직전)

```bash
SIGIL_CHAR=$(printf '\xc2\xa7')

# 1. 새 위치 자산 존재
test -f apartment/.claude/skills/apartment-interior-reference-digest/SKILL.md || { echo "PHASE_FAILED: SKILL.md missing"; exit 1; }
test -d apartment/.claude/skills/apartment-interior-reference-digest/references || { echo "PHASE_FAILED: references missing"; exit 1; }
test -f apartment/scripts/apartment-interior-reference-digest/run_digest.sh || { echo "PHASE_FAILED: run_digest.sh missing"; exit 1; }
echo "[1 새 위치 자산] OK"

# 2. apartment/skills/ 디렉터리 자체 폐기
test ! -e apartment/skills || { echo "PHASE_FAILED: apartment/skills/ 잔존"; exit 1; }
echo "[2 apartment/skills/ 폐기] OK"

# 3. native skill 등록 (.claude/skills/<name>/) 두 개 모두
test -f apartment/.claude/skills/apartment-daily-report/SKILL.md || { echo "PHASE_FAILED: daily-report SKILL absent"; exit 1; }
test -f apartment/.claude/skills/apartment-interior-reference-digest/SKILL.md || { echo "PHASE_FAILED: interior-digest SKILL absent"; exit 1; }
echo "[3 native skill 2개 등록] OK"

# 4. apartment/scripts/ 두 skill 디렉터리 모두
test -d apartment/scripts/apartment-daily-report || { echo "PHASE_FAILED: scripts daily-report missing"; exit 1; }
test -d apartment/scripts/apartment-interior-reference-digest || { echo "PHASE_FAILED: scripts interior-digest missing"; exit 1; }
echo "[4 scripts 분리 2개] OK"

# 5. shell syntax
bash -n apartment/scripts/apartment-interior-reference-digest/run_digest.sh || { echo "PHASE_FAILED: run_digest syntax"; exit 1; }
echo "[5 run_digest syntax] OK"

# 6. section sigil
for f in apartment/.claude/skills/apartment-interior-reference-digest/SKILL.md; do
  COUNT=$(grep -c "$SIGIL_CHAR" "$f" 2>/dev/null || echo 0)
  [ "$COUNT" -eq 0 ] || { echo "PHASE_FAILED: $f sigil 잔재"; exit 1; }
done
echo "[6 sigil] 0건"

# 7. commit 개수
COMMITS=$(git log --format='%H' HEAD~1..HEAD | wc -l)
echo "[7 commit count] $COMMITS"
[ "$COMMITS" -eq 1 ] || { echo "PHASE_FAILED: phase commit $COMMITS != 1"; exit 1; }

echo "✓ Phase 02 검증 통과"
```

---

## 의도 메모

- apartment-interior-reference-digest는 *현재 native 미등록* — 본 phase에서 동시 native 등록 (`claude -p "/apartment-interior-reference-digest"` 가능).
- apartment/skills/ 디렉터리 자체 폐기 = *마지막 skill 이동 완료 신호*. workspace-structure.md 분리 표준 정합.
- run_digest.sh는 thin (53줄) — path 인용 적음. Edit 작업 작음.
- 본 phase 후 apartment는 *완전 분리 패턴* — career-os와 같은 패턴.
