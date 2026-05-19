# Phase 1 — build_weekly_listing_trend.py git rm + 검증 + push

apartment plan006 phase-01 (마지막 phase). ADR-008에 따라 `build_weekly_listing_trend.py` git rm. 호출자 0 + Python 잔존 0 검증. index.json `status=completed`로 갱신. origin/main push.

## 작업 위치 (cwd 정책)

run-phases.py가 본 phase를 `cwd=apartment/` (워크스페이스)로 실행한다. 모든 bash 블록 첫 줄은 다음으로 ai-nodes 루트 이동:

```bash
cd "$(git rev-parse --show-toplevel)"
```

이후 모든 path는 `apartment/...` 형식.

## 관련 docs (먼저 읽기)

- `apartment/docs/adr.md` ADR-008 — 폐기 결정 본문.
- `apartment/docs/code-architecture.md` — 언어 통계 (Python 0 예상).
- `apartment/scripts/apartment-daily-report/build_weekly_listing_trend.py` — 폐기 대상.

## 변경할 파일

삭제:

- `apartment/scripts/apartment-daily-report/build_weekly_listing_trend.py`

본 phase에서 *새 파일 생성 / 다른 파일 수정 금지*. docs / ADR는 별도 commit (`f6bbf57`)으로 이미 처리.

## 검증 절차

```bash
cd "$(git rev-parse --show-toplevel)"

# 1. 호출자 0 재확인 — script 안 어디서도 호출 안 됨
! grep -rn "build_weekly_listing_trend\|weekly-price-trend\|monthly-price-trend" apartment/scripts/ apartment/config/ apartment/.claude/ 2>&1 | grep -v "^apartment/scripts/apartment-daily-report/build_weekly_listing_trend.py" || (echo "FAIL: 호출자 발견 — 폐기 전 정리 필요" && exit 1)

# (ADR + docs는 build_weekly_listing_trend를 *역사적 참조*로 언급 — apartment/docs/adr.md 또는 README 잔존은 OK)

# 2. git rm
git rm apartment/scripts/apartment-daily-report/build_weekly_listing_trend.py

# 3. Python collector 0 확인 (extract_claude_result.py는 _shared/bin/에 위치 — apartment/scripts 안 0이어야 함)
ls apartment/scripts/apartment-daily-report/*.py 2>&1
test ! -e apartment/scripts/apartment-daily-report/build_weekly_listing_trend.py || (echo "FAIL: 파일 잔존" && exit 1)

PYTHON_COUNT="$(find apartment/scripts/apartment-daily-report -maxdepth 1 -name '*.py' -type f | wc -l)"
test "$PYTHON_COUNT" -eq 0 || (echo "FAIL: apartment/scripts Python 잔존 ($PYTHON_COUNT 개)" && exit 1)

# 4. shell 호출 정합성 (run_report.sh / run_smoke_test.sh / run_guri_buy_search.sh가 python3 직접 호출 0)
grep -n "python3" apartment/scripts/apartment-daily-report/run_report.sh apartment/scripts/apartment-daily-report/run_smoke_test.sh apartment/scripts/apartment-daily-report/run_guri_buy_search.sh 2>&1 | grep -v "python3 - " | grep -v "PYTHON_BIN" || echo "OK: python3 직접 호출은 heredoc 검증 블록 + _shared/bin/extract_claude_result.py 호출만"

# (line 112 `python3 "$EXTRACT" "$CLAUDE_JSON"` + run_smoke_test.sh line 15 `python3 - <<'PY'` heredoc은 별도 정책. 본 plan 스코프 밖)
```

## index.json 갱신

```bash
cd "$(git rev-parse --show-toplevel)"

PHASE_01_SHA_FUTURE="" # 본 phase commit 후 가능 — 후기록은 phase commit 안에 통합
```

`apartment/tasks/plan006-weekly-trend-retire/index.json` Edit:

- `updated_at` → 현재 ISO-8601 UTC.
- `status` → `"completed"`.
- `current_phase` → `1`.
- `phases[0].status` → `"completed"` (commitSha는 본 commit 후 자동 follow-up — 단일 phase plan은 commit-after-record가 어려움. trailing cleanup 가능).

본 phase는 *단일 phase plan*이라 phase-01 자기 commitSha 후기록이 trailing cleanup 패턴 (common-pitfalls 6-2). 본 commit 안에 status=completed + commitSha 비워두고 push 후 cleanup follow-up 또는 status=completed만 적용 + commitSha 생략.

표준 채택: **status=completed만 본 commit에 적용 + commitSha 필드는 생략**. 추후 cleanup follow-up commit이 필요하면 사용자 직접 처리.

## commit + push

```bash
cd "$(git rev-parse --show-toplevel)"

git add apartment/tasks/plan006-weekly-trend-retire/index.json
# build_weekly_listing_trend.py는 git rm으로 이미 stage됨

git status --porcelain | grep -E "^(A|M|D|R) " | head
# 의도 외 staged 파일 0 — cross-session race 회피.

git commit -m "feat(apartment): build_weekly_listing_trend.py 폐기 + plan006 status=completed (ADR-008)

- dead code (호출자 0) + PIL 외부 pip 의존 동시 제거
- apartment Python collector 0개 도달 (plan003~005 TS 마이그 + plan006 폐기 시리즈 완료)
- _shared/bin/extract_claude_result.py만 ai-nodes 공용 잔존
- plan006 status=completed

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"

git push origin main
```

## 금지 사항

- 새 파일 생성.
- 다른 파일 수정 (build_weekly_listing_trend.py git rm + index.json Edit 외).
- ADR 본문 수정.
- 다른 워크스페이스 파일 stage.
- amend / force push.
- section mark (U+00A7) 직접 입력.

## PHASE_BLOCKED / PHASE_FAILED 조건

- 호출자 발견 (1번 검증 fail) — `PHASE_FAILED: 호출자 발견 — ADR-008 결정 전 정리 필요`.
- Python 잔존 (3번 검증 fail) — `PHASE_FAILED: apartment/scripts Python 잔존`.
- 의도 외 staged 파일 — `PHASE_BLOCKED: cross-session stage race — git status 확인 필요`.
- push 거절 — `PHASE_BLOCKED: push 거절 — 사용자 검토 필요`.
