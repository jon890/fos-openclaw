# Phase 2 — 통합 검증 + status=completed + push

stock-investment plan004 phase-02 (마지막). phase-01 산출 검증, index.json status=completed, origin/main push.

## 작업 위치 (cwd 정책)

run-phases.py가 본 phase를 `cwd=stock-investment/` (워크스페이스)로 실행. 첫 bash 블록:

```bash
cd "$(git rev-parse --show-toplevel)"
```

## 검증 절차

```bash
cd "$(git rev-parse --show-toplevel)"

# 1. phase-01 commit 존재
PHASE_01_SHA="$(git log --format='%H' --grep='plan004.*phase-01' -n 1 | cut -c1-12)"
test -n "$PHASE_01_SHA" || (echo "PHASE_FAILED: phase-01 commit 누락" && exit 1)
echo "[phase-01 SHA] $PHASE_01_SHA"

# 2. decisions/ 부재
test ! -d stock-investment/docs/decisions || (echo "PHASE_FAILED: decisions/ 잔존" && exit 1)
echo "[decisions/ 폐기] OK"

# 3. adr.md plan 번호 정정 + History
grep -q "plan004에서 git rm 완료" stock-investment/docs/adr.md
! grep -q "plan003에서 폐기 예정" stock-investment/docs/adr.md
echo "[adr.md History 정정] OK"

# 4. code-architecture decisions 표기
grep -q "decisions/.*plan004" stock-investment/docs/code-architecture.md
echo "[code-architecture decisions 표기] OK"

# 5. workspace-structure 매트릭스 stock-investment 7행 O
ALL_O=$(grep -E "^\| (CLAUDE.md 심링크|docs/ 5문서|tasks/plan|skills/ 분리|\.claude/skills/|\.env|data/ vs docs/)" docs/workspace-structure.md | awk -F '|' '{print $4}' | grep -c "O")
test "$ALL_O" -ge 7 || (echo "PHASE_FAILED: matrix stock-investment O 카운트 $ALL_O" && exit 1)
echo "[매트릭스 stock-investment 7행 O] OK"

# 6. workspace-structure L159 / L181 안내 정정
grep -q "stock-investment | 적용 완료 (plan001~004)" docs/workspace-structure.md
grep -q "travel만 별도 workspace-audit" docs/workspace-structure.md
echo "[workspace-structure 안내] OK"

# 7. 다른 파일 변경 0
git log --format='%H' HEAD~2..HEAD --name-only | grep -vE "^stock-investment/docs/(adr|code-architecture)\.md$|^stock-investment/docs/decisions/|^stock-investment/tasks/plan004|^docs/workspace-structure\.md$|^[a-f0-9]\{40\}$|^$" && (echo "PHASE_FAILED: scope creep" && exit 1) || true
echo "[스코프 격리] OK"

# 8. docs-style 정합 (section mark 0)
! grep -n "§" stock-investment/docs/adr.md stock-investment/docs/code-architecture.md docs/workspace-structure.md
echo "[section mark 0] OK"
```

## index.json 갱신

```bash
cd "$(git rev-parse --show-toplevel)"

PHASE_01_SHA="$(git log --format='%H' --grep='plan004.*phase-01' -n 1 | cut -c1-12)"
test -n "$PHASE_01_SHA" || (echo "PHASE_FAILED: SHA 추출 실패" && exit 1)
```

`stock-investment/tasks/plan004-decisions-retirement/index.json` Edit:
- `updated_at` → 현재 ISO-8601 UTC.
- `status` → `"completed"`.
- `current_phase` → `2`.
- `phases[0].status` → `"completed"`, `phases[0].commitSha` 추가.
- `phases[1].status` → `"completed"` (commitSha는 trailing cleanup).

## commit + push

```bash
cd "$(git rev-parse --show-toplevel)"

git add stock-investment/tasks/plan004-decisions-retirement/index.json

git status --porcelain | grep -E "^(A|M|D|R) " | head
# 의도 외 staged 파일 0 — cross-session race 회피.

git commit -m "task(stock-investment): plan004 status=completed (phase-02) — 표준 적용 시리즈 완료

- phase-01 commitSha 후기록
- decisions/* 7 파일 git rm 완료
- adr.md / code-architecture.md plan 번호 정정
- ai-nodes/docs/workspace-structure.md 매트릭스 stock-investment 7행 ?→O
- stock-investment 표준 적용 시리즈 plan001~004 완전 완료

후속 (별도 plan 시리즈):
- travel 표준화 plan001 (5문서 + AGENTS 한글화 + CLAUDE 심링크 + tasks/)
- health-care 워크스페이스 audit (5번째 워크스페이스 발견, workspace-structure 매트릭스 보강 필요)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"

git push origin main
```

## 금지 사항

- 신규 파일 생성 (index.json Edit만).
- phase-01 산출 (decisions/* 폐기 + adr/code-architecture/workspace-structure) 수정.
- AGENTS.md / 5문서 / scripts / config / .env 수정.
- ADR 본문 수정.
- 다른 워크스페이스 파일 stage.
- amend / force push.

## PHASE_BLOCKED / PHASE_FAILED 조건

- phase-01 commit 부재 — `PHASE_FAILED: phase-01 누락 또는 cross-session race`.
- decisions/ 잔존 (검증 2) — `PHASE_FAILED: phase-01 회귀`.
- adr.md / code-architecture / workspace-structure 검증 fail — `PHASE_FAILED: 정정 부실`.
- 의도 외 staged 파일 — `PHASE_BLOCKED: cross-session stage race`.
- push 거절 — `PHASE_BLOCKED`.
