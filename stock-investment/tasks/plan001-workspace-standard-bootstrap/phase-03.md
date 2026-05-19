# Phase 3 — 통합 검증 + status=completed + push

stock-investment plan001 phase-03 (마지막). phase-01 + phase-02 산출 통합 검증, index.json `status=completed`로 갱신, origin/main push.

## 작업 위치 (cwd 정책)

run-phases.py가 본 phase를 `cwd=stock-investment/` (워크스페이스)로 실행. 첫 bash 블록:

```bash
cd "$(git rev-parse --show-toplevel)"
```

## 관련 docs (먼저 읽기)

- `stock-investment/tasks/plan001-workspace-standard-bootstrap/index.json` — 본 task index.
- phase-01 + phase-02 산출 — 검증 대상.

## 검증 절차

```bash
cd "$(git rev-parse --show-toplevel)"

# 1. phase-01 + phase-02 commit 분리 확인
git log --oneline -5
# phase-01 = "docs(stock-investment): 5문서 신설 — decisions/* 7 ADR 재분배 (plan001 phase-01)"
# phase-02 = "docs(stock-investment): AGENTS.md 한글화 + CLAUDE 심링크 + .env.example (plan001 phase-02)"
# 둘 분리. 통합돼 있으면 PHASE_FAILED.

# 2. 5문서 존재 + 본문 충실
for f in prd data-schema flow code-architecture adr; do
  test -s "stock-investment/docs/$f.md" || (echo "PHASE_FAILED: $f.md 부재" && exit 1)
  LINES=$(wc -l < "stock-investment/docs/$f.md")
  test "$LINES" -ge 30 || (echo "PHASE_FAILED: $f.md 부실 ($LINES 라인)" && exit 1)
done
echo "[5문서 충실] OK"

# 3. AGENTS.md 한글화 + 5문서 라우팅
grep -q "## 1. 5문서 라우팅" stock-investment/AGENTS.md
grep -q "## 6. 외부 의존성" stock-investment/AGENTS.md
HANGUL_LINES=$(grep -cP "[가-힣]" stock-investment/AGENTS.md)
test "$HANGUL_LINES" -ge 20 || (echo "PHASE_FAILED: AGENTS 한글화 부실" && exit 1)
echo "[AGENTS 한글화] OK"

# 4. CLAUDE.md 심링크
test -L stock-investment/CLAUDE.md
readlink stock-investment/CLAUDE.md | grep -q "^AGENTS.md$"
echo "[CLAUDE 심링크] OK"

# 5. .env.example
test -f stock-investment/.env.example
grep -q "^DISCORD_CHANNEL_ID=" stock-investment/.env.example
echo "[.env.example] OK"

# 6. tasks/ + plan001 디렉터리
test -d stock-investment/tasks/plan001-workspace-standard-bootstrap
echo "[tasks/plan001] OK"

# 7. docs/decisions/ 그대로 보존 확인 (plan003에서 폐기)
test -d stock-investment/docs/decisions
DECISIONS_COUNT=$(find stock-investment/docs/decisions -maxdepth 1 -name "*.md" | wc -l)
test "$DECISIONS_COUNT" -eq 7 || (echo "PHASE_FAILED: decisions/* 7개 보존 안됨 ($DECISIONS_COUNT)" && exit 1)
echo "[decisions/ 7개 보존] OK"

# 8. skill / config / data / scripts 변경 0 (본 plan은 docs only)
git diff HEAD~3 --name-only | grep -v "^stock-investment/docs/\|^stock-investment/AGENTS.md\|^stock-investment/CLAUDE.md\|^stock-investment/.env.example\|^stock-investment/tasks/plan001" && (echo "PHASE_FAILED: 의도 외 영역 변경 발견" && exit 1) || true
echo "[스코프 격리] OK"

# 9. ADR-001 본문 검증
grep -q "^## ADR-001 — 워크스페이스 ai-nodes 표준 구조 적용 시작" stock-investment/docs/adr.md
echo "[ADR-001 본문] OK"

# 10. docs-style 정합 (section mark 사용 0)
! grep -n "§" stock-investment/docs/*.md stock-investment/AGENTS.md
echo "[section mark 0] OK"
```

성공 기준: 1-10 모두 통과.

## index.json 갱신

phase-01 + phase-02 commitSha 후기록 + 전체 status 갱신.

```bash
cd "$(git rev-parse --show-toplevel)"

PHASE_01_SHA="$(git log --format='%H' --grep='plan001 phase-01' -n 1 | cut -c1-12)"
PHASE_02_SHA="$(git log --format='%H' --grep='plan001 phase-02' -n 1 | cut -c1-12)"

echo "phase-01 SHA = $PHASE_01_SHA"
echo "phase-02 SHA = $PHASE_02_SHA"

test -n "$PHASE_01_SHA" -a -n "$PHASE_02_SHA" || (echo "PHASE_FAILED: phase commitSha 추출 실패 — git log 확인" && exit 1)

# stock-investment는 첫 plan이라 다른 workspace plan과 메시지 패턴 충돌 가능성 — workspace prefix 추가 검증
git log --format='%s' --grep='plan001 phase-01' -n 5 | grep "stock-investment" -q || echo "WARN: phase-01 commit에 stock-investment scope 명시 권장"
```

`stock-investment/tasks/plan001-workspace-standard-bootstrap/index.json` Edit:

- `updated_at` → 현재 ISO-8601 UTC.
- `status` → `"completed"`.
- `current_phase` → `3`.
- `phases[0].status` + `phases[0].commitSha` 후기록.
- `phases[1].status` + `phases[1].commitSha` 후기록.
- `phases[2].status` → `"completed"` (commitSha는 본 commit 후 trailing cleanup).

## commit + push

```bash
cd "$(git rev-parse --show-toplevel)"

git add stock-investment/tasks/plan001-workspace-standard-bootstrap/index.json

git status --porcelain | grep -E "^(A|M|D|R) " | head
# 의도 외 staged 파일 0 — cross-session race 회피.

git commit -m "task(stock-investment): plan001 status=completed (phase-03)

- phase-01 / phase-02 commitSha 후기록
- 5문서 신설 완료 (prd / data-schema / flow / code-architecture / adr)
- AGENTS.md 한글화 + CLAUDE.md 심링크 + .env.example placeholder
- decisions/* 7 파일 보존 (plan003에서 폐기 예정)

후속: plan002 (ADR-006 분리 패턴 마이그) → plan003 (decisions/ 폐기 + workspace-structure ✓ 갱신).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"

git push origin main
```

## 금지 사항

- 신규 파일 생성 (index.json Edit만).
- 5문서 / AGENTS.md / CLAUDE.md / .env.example 수정 (phase-01/02 산출 보존).
- decisions/* 폐기 — plan003 책임.
- skill / config / data / scripts 변경.
- ADR 본문 수정.
- 다른 워크스페이스 파일 stage.
- amend / force push.
- section mark (U+00A7) 직접 입력.

## PHASE_BLOCKED / PHASE_FAILED 조건

- phase-01 또는 phase-02 commit 부재 — `PHASE_FAILED: phase commit 누락 또는 cross-session race`.
- 5문서 부실 (성공 기준 2) — `PHASE_FAILED: 5문서 부실`.
- AGENTS 한글화 부실 (성공 기준 3) — `PHASE_FAILED: AGENTS 한글화 부실`.
- 의도 외 staged 파일 — `PHASE_BLOCKED: cross-session stage race — git status 확인`.
- push 거절 — `PHASE_BLOCKED: push 거절 — 사용자 검토 필요`.
- 의도 외 영역 변경 발견 (성공 기준 8) — `PHASE_FAILED: scope creep`.
