# Phase 3 — 통합 검증 + status=completed + push

apartment plan005 phase-03. phase-01 + phase-02 산출 통합 검증, index.json `status=completed`로 갱신, origin/main push.

## 작업 위치 (cwd 정책)

run-phases.py가 본 phase를 `cwd=apartment/` (워크스페이스)로 실행한다. 모든 bash 블록 첫 줄은 다음으로 ai-nodes 루트 이동:

```bash
cd "$(git rev-parse --show-toplevel)"
```

이후 모든 path는 `apartment/...` 형식.

## 관련 docs (먼저 읽기)

- `apartment/tasks/plan005-normalize-results-ts/index.json` — 본 task index.
- `apartment/scripts/apartment-daily-report/normalize_results.ts` (phase-01).
- `apartment/scripts/apartment-daily-report/run_report.sh` / `run_smoke_test.sh` (phase-02).

## 검증 절차

```bash
cd "$(git rev-parse --show-toplevel)"

# 1. phase-01/02 commit 분리 확인
git log --oneline -5
# phase-01 = "feat(apartment): normalize_results.ts 신설 (plan005 phase-01)"
# phase-02 = "refactor(apartment): normalize_results.ts 호출 전환 + Python git rm (plan005 phase-02)"
# 두 commit 분리. 통합돼 있으면 PHASE_FAILED.

# 2. Python normalize 0 확인
test ! -f apartment/scripts/apartment-daily-report/normalize_results.py || (echo "FAIL: Python 잔존" && exit 1)

# 3. TS normalize 존재 확인
test -f apartment/scripts/apartment-daily-report/normalize_results.ts || (echo "FAIL: TS 부재" && exit 1)

# 4. shell 호출 정합성
grep -q "bun run.*NORMALIZER\|bun run.*normalize_results.ts" apartment/scripts/apartment-daily-report/run_report.sh
grep -q "bun run.*NORMALIZER\|bun run.*normalize_results.ts" apartment/scripts/apartment-daily-report/run_smoke_test.sh
! grep -n "normalize_results.py\|python3.*NORMALIZER" apartment/scripts/apartment-daily-report/run_report.sh apartment/scripts/apartment-daily-report/run_smoke_test.sh

# 5. smoke test
bash apartment/scripts/apartment-daily-report/run_smoke_test.sh
```

성공 기준: 1-5 모두 통과.

## index.json 갱신

phase-01 / phase-02 commitSha 후기록 + status 갱신.

```bash
cd "$(git rev-parse --show-toplevel)"

PHASE_01_SHA="$(git log --format='%H' --grep='plan005 phase-01' -n 1 | cut -c1-12)"
PHASE_02_SHA="$(git log --format='%H' --grep='plan005 phase-02' -n 1 | cut -c1-12)"

echo "phase-01 SHA = $PHASE_01_SHA"
echo "phase-02 SHA = $PHASE_02_SHA"

test -n "$PHASE_01_SHA" -a -n "$PHASE_02_SHA" || (echo "PHASE_FAILED: phase commitSha 추출 실패 — git log 확인" && exit 1)
```

`apartment/tasks/plan005-normalize-results-ts/index.json` Edit:

- `updated_at` → 현재 ISO-8601 UTC.
- `status` → `"completed"`.
- `current_phase` → `3`.
- `phases[0].status` / `phases[1].status` → `"completed"`, 각 `commitSha` 추가.
- `phases[2].status` → `"completed"` (commitSha는 본 commit 후 follow-up cleanup).

## commit + push

```bash
cd "$(git rev-parse --show-toplevel)"

git add apartment/tasks/plan005-normalize-results-ts/index.json

git status --porcelain | grep -E "^(A|M|D|R) " | head
# 의도 외 staged 파일 0 — 다른 워크스페이스 / docs 흡수 회피.
# 발견 시 PHASE_BLOCKED.

git commit -m "task(apartment): plan005 status=completed (phase-03)

- phase-01 / phase-02 commitSha 후기록
- normalize_results.ts 신설 완료
- run_report.sh / run_smoke_test.sh 호출 전환 완료
- normalize_results.py git rm 완료
- 남은 Python: build_weekly_listing_trend.py (plan006) + extract_claude_result.py (별도 정책)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"

git push origin main
```

## 금지 사항

- 새 파일 생성.
- `apartment/scripts/` 안 코드 수정 (phase-01 / phase-02 산출 변경 금지).
- `apartment/docs/` 수정.
- ADR 본문 수정.
- 다른 워크스페이스 파일 stage — cross-session race 흡수 회피.
- amend / force push.
- section mark (U+00A7) 직접 입력.

## PHASE_BLOCKED / PHASE_FAILED 조건

- phase commitSha 추출 실패 — `PHASE_FAILED: phase commit 누락 또는 cross-session race`.
- 의도 외 staged 파일 — `PHASE_BLOCKED: cross-session stage race — git status 확인 필요`.
- smoke_test 실패 — `PHASE_FAILED: smoke_test 회귀`.
- push 거절 — `PHASE_BLOCKED: push 거절 — 사용자 검토 필요`.
