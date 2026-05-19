# Phase 2 — run_report.sh + run_smoke_test.sh 호출 변경 + Python git rm

apartment plan005 phase-02. phase-01에서 신설한 `normalize_results.ts`로 호출을 옮기고 Python 원본 git rm.

## 작업 위치 (cwd 정책)

run-phases.py가 본 phase를 `cwd=apartment/` (워크스페이스)로 실행한다. 모든 bash 블록 첫 줄은 다음으로 ai-nodes 루트 이동:

```bash
cd "$(git rev-parse --show-toplevel)"
```

이후 모든 path는 `apartment/scripts/apartment-daily-report/...` 형식.

## 관련 docs (먼저 읽기)

- `apartment/scripts/apartment-daily-report/run_report.sh` — 라인 61, 102 NORMALIZER 호출 위치.
- `apartment/scripts/apartment-daily-report/run_smoke_test.sh` — 라인 8, 13 NORMALIZER 호출 위치.
- `apartment/scripts/apartment-daily-report/normalize_results.ts` (phase-01 산출).

## 변경할 파일

수정:

- `apartment/scripts/apartment-daily-report/run_report.sh`
- `apartment/scripts/apartment-daily-report/run_smoke_test.sh`

삭제:

- `apartment/scripts/apartment-daily-report/normalize_results.py`

본 phase에서 *신규 파일 생성 금지*. *docs / ADR / collect_*.ts / extract_claude_result.py 호출부 수정 금지*.

## 명세

### run_report.sh

기준 상태:

```bash
# line 61
NORMALIZER="$(dirname "$0")/normalize_results.py"
# ...
# line 102
if ! python3 "$NORMALIZER" "$RAW_JSON" "$SUMMARY_JSON"; then
```

변경 후:

```bash
NORMALIZER="$(dirname "$0")/normalize_results.ts"
# ...
if ! bun run "$NORMALIZER" "$RAW_JSON" "$SUMMARY_JSON"; then
```

### run_smoke_test.sh

기준 상태:

```bash
# line 8
NORMALIZER="$(dirname "$0")/normalize_results.py"
# ...
# line 13
python3 "$NORMALIZER" "$RAW_JSON" "$SUMMARY_JSON"
```

변경 후:

```bash
NORMALIZER="$(dirname "$0")/normalize_results.ts"
# ...
bun run "$NORMALIZER" "$RAW_JSON" "$SUMMARY_JSON"
```

### Python git rm

```bash
cd "$(git rev-parse --show-toplevel)"
git rm apartment/scripts/apartment-daily-report/normalize_results.py
```

### 검증

```bash
cd "$(git rev-parse --show-toplevel)"

# 1. run_report.sh의 normalize_results.py 참조 0
! grep -n "normalize_results.py\|python3.*NORMALIZER" apartment/scripts/apartment-daily-report/run_report.sh

# 2. run_smoke_test.sh도 동일
! grep -n "normalize_results.py\|python3.*NORMALIZER" apartment/scripts/apartment-daily-report/run_smoke_test.sh

# 3. shell 구문 점검
bash -n apartment/scripts/apartment-daily-report/run_report.sh
bash -n apartment/scripts/apartment-daily-report/run_smoke_test.sh

# 4. smoke test 실행 (네트워크 의존 — 차단 시 PHASE_BLOCKED)
bash apartment/scripts/apartment-daily-report/run_smoke_test.sh
```

성공 기준: 1-3 모두 통과 + 4가 정상 종료 (network 차단 시 PHASE_BLOCKED 가능).

## 금지 사항

- 새 파일 생성 (phase-01 책임 완료).
- `normalize_results.ts` 또는 `collect_*.ts` 수정.
- `apartment/docs/` 수정.
- ADR 본문 수정.
- `run_report.sh` 기타 라인 변경 (NORMALIZER 호출 외 변경 금지) — line 112 EXTRACT (extract_claude_result.py)는 별도 ADR 정책 (apartment는 Python 버전 사용) — 변경 금지.
- run_smoke_test.sh의 line 15 `python3 - <<'PY'` heredoc 검증 블록 — summary.json 형식 검증 로직. 본 plan 스코프 밖. 유지.
- section mark (U+00A7) 직접 입력.

## commit

```bash
cd "$(git rev-parse --show-toplevel)"

git add apartment/scripts/apartment-daily-report/run_report.sh
git add apartment/scripts/apartment-daily-report/run_smoke_test.sh
# Python rm은 git rm으로 이미 stage됨

git status --porcelain | grep -E "^(A|M|D|R) " | head
# 의도 외 staged 파일 0 — cross-session race 회피.

git commit -m "refactor(apartment): normalize_results.ts 호출 전환 + Python git rm (plan005 phase-02)

- run_report.sh / run_smoke_test.sh의 python3 NORMALIZER → bun run NORMALIZER
- NORMALIZER path .py → .ts
- normalize_results.py git rm
- extract_claude_result.py (apartment Python 잔존) 호출은 별도 정책 — 변경 없음

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

push 없음 (phase-03 책임).

## PHASE_BLOCKED / PHASE_FAILED 조건

- shell 구문 오류 — `PHASE_FAILED: bash -n 실패 — diff 확인`.
- smoke_test 네트워크 차단 — `PHASE_BLOCKED: smoke_test 네트워크 차단`.
- smoke_test 결과 다름 (TS normalize 결과가 Python과 다른 summary.json) — `PHASE_FAILED: 기능 회귀 — diff 첨부`.
- 의도 외 staged 파일 — `PHASE_BLOCKED: stage drift`.
- run_report.sh / run_smoke_test.sh 외 의도하지 않은 라인 변경 — `PHASE_FAILED: scope creep — diff 확인`.
