# Phase 02 — collect_sources.ts (import 통합) + run_report.sh 갱신 + 옛 Python git rm

**Model**: sonnet
**Status**: pending

---

## 목표

apartment collect_sources 오케스트레이터 → TypeScript + run_report.sh가 Bun 호출 + 옛 Python 2개 git rm:

1. `apartment/scripts/apartment-daily-report/collect_sources.ts` 신설 — `import { runNaverApi }` (ADR-006). hogangnono / kb는 `Bun.spawn(python3)` 임시 (plan004까지).
2. `apartment/scripts/apartment-daily-report/run_report.sh` 갱신 — `python3 $COLLECTOR` → `bun run $COLLECTOR_TS`.
3. `collect_sources.py` + `collect_naver_api.py` 두 Python git rm.

**범위 외**: phase-01 산출 (collect_naver_api.ts + naver_api_schemas.ts), 검증 + push (phase-03), hogangnono / kb / normalize / weekly_trend (plan004~006).

---

## 본 phase 강제 주의문

- Write/Edit/Bash 도구로 file 생성·수정·삭제. prose 응답만으로는 PHASE_FAILED.
- section sigil (U+00A7) 사용 금지.
- destructive edit (git rm) 후 즉시 검증 (`test ! -e` + `git ls-files | wc -l`, common-pitfalls 6-5).
- 본 phase commit 개수 self-check = 1.

---

## 사전 cwd 설정 (run-phases.py hotfix)

```bash
cd "$(git rev-parse --show-toplevel)"
pwd  # 기대: /home/bifos/ai-nodes
```

---

## 사전 조건 검증

```bash
test -f apartment/scripts/apartment-daily-report/collect_naver_api.ts || { echo "PHASE_FAILED: phase-01 산출 누락"; exit 1; }
test -f apartment/scripts/apartment-daily-report/naver_api_schemas.ts || { echo "PHASE_FAILED: phase-01 산출 누락"; exit 1; }
test -f apartment/scripts/apartment-daily-report/collect_sources.py || { echo "PHASE_FAILED: collect_sources.py 부재"; exit 1; }
echo "[사전 조건] OK"
```

---

## 관련 docs

- ADR-006 (오케스트레이션 import 통합): `apartment/docs/adr.md`
- ADR-005 (Bun.fetch)
- 참조 본체: `apartment/scripts/apartment-daily-report/collect_sources.py` (Python 기존, 약 60줄)
- phase-01 산출: `collect_naver_api.ts` (`runNaverApi` export) + `naver_api_schemas.ts`

---

## 작업 항목

### 1. collect_sources.ts 신설

`Write` 도구로 `apartment/scripts/apartment-daily-report/collect_sources.ts` 작성.

Python → TypeScript 변환 매핑:

| Python | TypeScript |
|---|---|
| `subprocess.run([sys.executable, script, url])` (Naver) | `import { runNaverApi } from './collect_naver_api'` + `await runNaverApi(url)` (ADR-006) |
| `subprocess.run([sys.executable, script, url])` (Hogangnono/KB) | `Bun.spawn(['python3', script, url])` + `await new Response(proc.stdout).text()` + `JSON.parse(...)` (plan004까지 임시) |
| `os.path.dirname(os.path.abspath(__file__))` | `import.meta.dir` |
| `os.environ.get("TARGET_NAME", "default")` | `process.env.TARGET_NAME ?? "default"` |

핵심 흐름:

1. env 로드 (TARGET_NAME, TARGET_ALIAS, TARGET_LOCATION, TARGET_UNIT_LABEL, TARGET_UNIT_EXCLUSIVE_AREA_M2, NAVER_URL, HOGANGNONO_URL, KB_URL).
2. Naver = `runNaverApi(NAVER_URL)` (ts import).
3. Hogangnono = `Bun.spawn(['python3', 'collect_hogangnono.py', HOGANGNONO_URL])` (임시).
4. KB = `Bun.spawn(['python3', 'collect_kbland.py', KB_URL])` (임시).
5. focus-unit 매칭 (Python `classify_focus_against_profiles` 직역) — exclusiveAreaEstimateM2 ± 1.5.
6. `build_recent_transactions` 등 normalize 로직 직역.
7. CLI 인자: `bun run collect_sources.ts <raw-search.json-output-path>` (run_report.sh가 호출, 기존 Python 동일 인터페이스).
8. 출력: `Bun.write(outputPath, JSON.stringify(result, null, 2))`.

표준 출력 JSON schema 기존 Python 동일 — `target`, `sources[]`, `recentTransactions[]`, `listingSummary`, `comparison`, `focusSummary` 등. normalize_results.py (plan005 마이그 전)가 그대로 받음.

shebang: `#!/usr/bin/env bun`. chmod +x.

### 2. run_report.sh 갱신

`grep -n "python3\|COLLECTOR" apartment/scripts/apartment-daily-report/run_report.sh` 로 정확한 줄 식별 후 `Edit` 갱신.

변경 항목:

- `COLLECTOR="$SKILL_ROOT/scripts/collect_sources.py"` → `COLLECTOR="$WS_ROOT/scripts/apartment-daily-report/collect_sources.ts"` (또는 `$(dirname "$0")/collect_sources.ts` 자기 위치 기준).
- `python3 "$COLLECTOR" "$RAW_JSON"` → `bun run "$COLLECTOR" "$RAW_JSON"`.

`bash -n` 검증 + 옛 `python3 collect_sources.py` 인용 0 검증.

### 3. 옛 Python git rm

```bash
git rm apartment/scripts/apartment-daily-report/collect_sources.py
git rm apartment/scripts/apartment-daily-report/collect_naver_api.py
test ! -e apartment/scripts/apartment-daily-report/collect_sources.py
test ! -e apartment/scripts/apartment-daily-report/collect_naver_api.py
```

### 4. commit 생성

```bash
git add apartment/scripts/apartment-daily-report/collect_sources.ts apartment/scripts/apartment-daily-report/run_report.sh
git commit -m "$(cat <<'EOF'
refactor(apartment): collect_sources.ts (import 통합) + run_report.sh bun 호출 + 옛 Python 2개 git rm (plan003 phase-02)

ADR-006 (import 통합) 첫 적용:
- collect_sources.ts: import { runNaverApi } (Naver = ts 직접). hogangnono/kb는 Bun.spawn(python3) 임시 (plan004까지).
- run_report.sh: python3 $COLLECTOR → bun run $COLLECTOR_TS.
- collect_sources.py + collect_naver_api.py git rm — Python collector 2개 폐기.

표준 출력 JSON schema 기존 Python 동일 — normalize_results.py 호환 (plan005까지).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## 검증 (phase 종료 직전)

```bash
SIGIL_CHAR=$(printf '\xc2\xa7')

# 1. ts file 신설
test -f apartment/scripts/apartment-daily-report/collect_sources.ts || { echo "PHASE_FAILED"; exit 1; }

# 2. type/syntax
bun build --no-bundle apartment/scripts/apartment-daily-report/collect_sources.ts > /dev/null 2>&1 || { echo "PHASE_FAILED: ts type"; exit 1; }
bash -n apartment/scripts/apartment-daily-report/run_report.sh || { echo "PHASE_FAILED: shell syntax"; exit 1; }

# 3. ADR-006 import 통합 + Bun.spawn(python3) 적용
grep -q "from \"./collect_naver_api\"\|from './collect_naver_api'" apartment/scripts/apartment-daily-report/collect_sources.ts || { echo "PHASE_FAILED: import 통합 누락"; exit 1; }
grep -q "Bun.spawn" apartment/scripts/apartment-daily-report/collect_sources.ts || { echo "PHASE_FAILED: Bun.spawn 누락"; exit 1; }

# 4. run_report.sh bun run 호출
grep -q "bun run.*collect_sources" apartment/scripts/apartment-daily-report/run_report.sh || { echo "PHASE_FAILED: bun run 누락"; exit 1; }

# 5. 옛 Python file git rm
test ! -e apartment/scripts/apartment-daily-report/collect_sources.py || { echo "PHASE_FAILED: collect_sources.py 잔존"; exit 1; }
test ! -e apartment/scripts/apartment-daily-report/collect_naver_api.py || { echo "PHASE_FAILED: collect_naver_api.py 잔존"; exit 1; }

# 6. sigil
for f in apartment/scripts/apartment-daily-report/collect_sources.ts apartment/scripts/apartment-daily-report/run_report.sh; do
  COUNT=$(grep -c "$SIGIL_CHAR" "$f" 2>/dev/null || echo 0)
  [ "$COUNT" -eq 0 ] || { echo "PHASE_FAILED: $f sigil $COUNT"; exit 1; }
done

# 7. commit 개수
COMMITS=$(git log --format='%H' HEAD~1..HEAD | wc -l)
[ "$COMMITS" -eq 1 ] || { echo "PHASE_FAILED: commit $COMMITS != 1"; exit 1; }

echo "✓ Phase 02 검증 통과"
```

---

## 의도 메모

- phase-01 산출 `collect_naver_api.ts`에 `export async function runNaverApi` 권장 — 없으면 phase-02 Edit으로 보강.
- 표준 출력 JSON schema 기존 Python 동일 — `normalize_results.py` (plan005까지 Python) 호환 핵심.
- hogangnono / kb Python 임시 호출 = plan004 마이그 후 import 통합 교체.
- run_report.sh `$COLLECTOR` 변수명 유지 — 값만 `.ts`로 변경.
- 본 phase 후 apartment Python = 4 (hogangnono/kbland/normalize/weekly_trend) + Shell 5 + TS 4.
