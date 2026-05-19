# Phase 3 — 통합 검증 + status=completed + push

apartment plan004 phase-03. phase-01 + phase-02 산출을 통합 검증, index.json `status=completed`로 갱신, origin/main push.

## 작업 위치 (cwd 정책)

run-phases.py가 본 phase를 `cwd=apartment/` (워크스페이스)로 실행한다. 모든 bash 블록 첫 줄은 다음으로 ai-nodes 루트 이동:

```bash
cd "$(git rev-parse --show-toplevel)"
```

이후 모든 path는 `apartment/...` 형식.

## 관련 docs (먼저 읽기)

- `apartment/tasks/plan004-collectors-hogangnono-kbland-ts/index.json` — 본 task index.
- `apartment/scripts/apartment-daily-report/collect_sources.ts` — phase-02 산출.
- `apartment/scripts/apartment-daily-report/collect_hogangnono.ts` (phase-01).
- `apartment/scripts/apartment-daily-report/collect_kbland.ts` (phase-01).

## 검증 절차

```bash
cd "$(git rev-parse --show-toplevel)"

# 1. phase-01/02 commit 분리 확인
git log --oneline -5
# phase-01 = "feat(apartment): collect_hogangnono.ts + collect_kbland.ts 신설 (plan004 phase-01)"
# phase-02 = "refactor(apartment): collect_sources.ts import 통합 + Python collector 2개 git rm (plan004 phase-02)"
# 두 commit이 분리되어 있어야 함 (common-pitfalls 5-2). 통합돼 있으면 PHASE_FAILED.

# 2. Python collector 0 확인
ls apartment/scripts/apartment-daily-report/collect_*.py 2>&1
# normalize_results.py 외 collect_*.py 0개여야 함 (collect_hogangnono.py / collect_kbland.py git rm 완료)

# 3. TS collector 5개 확인
ls apartment/scripts/apartment-daily-report/*.ts
# collect_naver_api.ts / naver_api_schemas.ts / collect_sources.ts / collect_hogangnono.ts / collect_kbland.ts

# 4. runPythonSource 흔적 0
! grep -rn "runPythonSource\|Bun.spawn.*python3" apartment/scripts/apartment-daily-report/ || (echo "FAIL: subprocess 흔적 잔존" && exit 1)

# 5. smoke test (네트워크 의존)
bash apartment/scripts/apartment-daily-report/run_smoke_test.sh
```

성공 기준: 1-5 모두 통과.

## index.json 갱신

phase-01 / phase-02의 commitSha를 후기록 (`git log` 결과 기반) + phase-03 status running → completed + 전체 status → completed.

```bash
cd "$(git rev-parse --show-toplevel)"

# 각 phase commitSha 추출 (commit message 매칭으로)
PHASE_01_SHA="$(git log --format='%H' --grep='plan004 phase-01' -n 1 | cut -c1-12)"
PHASE_02_SHA="$(git log --format='%H' --grep='plan004 phase-02' -n 1 | cut -c1-12)"

echo "phase-01 SHA = $PHASE_01_SHA"
echo "phase-02 SHA = $PHASE_02_SHA"

# 둘 다 비어있으면 PHASE_FAILED: commit 누락 또는 cross-session race로 흡수됨
test -n "$PHASE_01_SHA" -a -n "$PHASE_02_SHA" || (echo "PHASE_FAILED: phase commitSha 추출 실패 — git log 확인" && exit 1)
```

`apartment/tasks/plan004-collectors-hogangnono-kbland-ts/index.json` Edit:

- `updated_at` → 현재 시각 (ISO-8601 UTC).
- `status` → `"completed"`.
- `current_phase` → `3`.
- `phases[0].status` → `"completed"`, `phases[0].commitSha` 추가.
- `phases[1].status` → `"completed"`, `phases[1].commitSha` 추가.
- `phases[2].status` → `"completed"`, `phases[2].commitSha`는 본 phase commit 후 follow-up 또는 그대로 생략.

(phase-03 자기 자신의 commitSha 후기록은 common-pitfalls 6-2 패턴 — 본 phase에선 phase-03 commitSha 필드 생략 가능. 본 phase commit 후 별도 cleanup commit이 표준.)

## commit + push

```bash
cd "$(git rev-parse --show-toplevel)"

git add apartment/tasks/plan004-collectors-hogangnono-kbland-ts/index.json

git status --porcelain | head
# 의도 외 staged 파일 0 — 다른 워크스페이스 / docs 변경 흡수 금지. cross-session race 흔적 발견 시 PHASE_BLOCKED.

git commit -m "task(apartment): plan004 status=completed (phase-03)

- phase-01 / phase-02 commitSha 후기록
- collect_hogangnono.ts + collect_kbland.ts 신설 완료
- collect_sources.ts import 통합 완료 — runPythonSource 분기 폐기 (ADR-006)
- Python collector 2개 git rm 완료
- 남은 Python: normalize_results.py (plan005) + build_weekly_listing_trend.py (plan006)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"

git push origin main
```

## 금지 사항

- 새 파일 생성.
- `apartment/scripts/` 안 코드 수정 (phase-01 / phase-02 산출 변경 금지).
- `apartment/docs/` 수정.
- ADR 본문 수정.
- 다른 워크스페이스 (career-os / stock-investment / travel) 파일 stage — cross-session race 흡수 회피.
- amend / force push.
- section mark (U+00A7) 문자 직접 입력.

## PHASE_BLOCKED / PHASE_FAILED 조건

- phase commitSha 추출 실패 (commit message 매칭 0) — `PHASE_FAILED: phase commit 누락 또는 message 패턴 mismatch — cross-session race 가능성`.
- 의도 외 staged 파일 (다른 워크스페이스 / docs 흡수) — `PHASE_BLOCKED: cross-session stage race — git status 확인 필요`.
- smoke_test 실패 — `PHASE_FAILED: smoke_test 회귀`.
- push 실패 (origin 분기, branch protection) — `PHASE_BLOCKED: push 거절 — 사용자 검토 필요`.
