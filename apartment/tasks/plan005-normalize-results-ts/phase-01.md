# Phase 1 — normalize_results.ts 신설 + zod 입력/출력 스키마

apartment plan005 phase-01. `normalize_results.py`를 `normalize_results.ts`로 신설. 입력 (raw-search.json) + 출력 (summary.json) zod 스키마 자기방어 (ADR-007 후속 적용).

본 phase는 *신설*만 — run_report.sh / run_smoke_test.sh 호출 변경은 phase-02. Python 원본은 phase-02에서 git rm.

## 작업 위치 (cwd 정책)

run-phases.py가 본 phase를 `cwd=apartment/` (워크스페이스)로 실행한다. 모든 bash 블록 첫 줄은 다음으로 ai-nodes 루트 이동:

```bash
cd "$(git rev-parse --show-toplevel)"
```

이후 모든 path는 `apartment/scripts/apartment-daily-report/...` 형식.

## 관련 docs (먼저 읽기)

- `apartment/docs/adr.md` ADR-007 (zod) — 적용 패턴.
- `apartment/scripts/apartment-daily-report/normalize_results.py` — 마이그 원본 (167줄).
- `apartment/scripts/apartment-daily-report/collect_sources.ts` — 입력 JSON 출력 위치 + 키 형태 참고.
- `apartment/scripts/apartment-daily-report/naver_api_schemas.ts` — zod 스키마 적용 패턴 참고.

## 변경할 파일

신설:

- `apartment/scripts/apartment-daily-report/normalize_results.ts`

본 phase에서 *기존 파일 수정 금지* — Python 원본, run_report.sh, run_smoke_test.sh, collect_*.ts 모두 그대로.

## 명세

### normalize_results.ts

CLI 진입점:

```ts
#!/usr/bin/env bun
// CLI: bun run normalize_results.ts <input.json> <output.json>

if (import.meta.main) {
  const [, , inputPath, outputPath] = process.argv;
  if (!inputPath || !outputPath) {
    process.stderr.write("usage: normalize_results.ts <input> <output>\n");
    process.exit(1);
  }
  await normalizeResults(inputPath, outputPath);
}

export async function normalizeResults(inputPath: string, outputPath: string): Promise<void> { ... }
```

Python `normalize_results.py` 동작 정확히 보존:

- `TARGET_UNIT_ALIASES`: `{ "59A": new Set(["59a", "59-a", "59 a", "59", "전용59", "전용 59", "59㎡", "59.0", "59형"]) }`
- `AREA_TOLERANCE_M2 = 1.5`
- `ROOT_KEYS`: 9개 키 동일 순서
- 헬퍼: `compact`, `normalizeUnitText`, `asFloat`, `buildFocusNorms`, `findFocusAreaMatches`, `inferMatchStatus`
- 모든 regex Python → TS RegExp 1:1 매핑 (특히 `re.sub(r"[^0-9a-z가-힣.]+", "", text)` — 한글 문자 클래스 보존)
- `infer_match_status` 분기 순서 정확 보존 (unit_norm exact / supply_area 매칭 / sourceTypeProfile.exclusive / fallback unverified)
- output `focusSummary` 9 필드 + `notes`
- `setdefault` 패턴 → `out[key] ??= {}` 또는 `[]` 분기
- `datetime.now().isoformat()` → `new Date().toISOString()` (Python format은 microsecond 포함이지만 TS는 millisecond — 호환성 *허용*. 단 docs/검증에는 명시)

입력 처리:

- `Bun.file(inputPath).json()` 또는 `JSON.parse(await Bun.file(inputPath).text())`
- 입력 zod 스키마는 *passthrough 관대* — collect_sources.ts 출력 형태 + 추가 필드 허용

출력 처리:

- `Bun.write(outputPath, JSON.stringify(out, null, 2))`
- 출력 zod 스키마로 검증 (`OutputSchema.parse(out)`) 후 write

### zod 스키마

`normalize_results.ts` 안에 inline:

```ts
import { z } from "zod";

const RawSearchInputSchema = z.object({
  target: z.record(z.string(), z.unknown()).optional(),
  focusUnit: z.record(z.string(), z.unknown()).optional(),
  sources: z.array(z.unknown()).optional(),
  recentTransactions: z.array(z.unknown()).optional(),
  listingSummary: z.record(z.string(), z.unknown()).optional(),
  comparison: z.record(z.string(), z.unknown()).optional(),
  notes: z.array(z.unknown()).optional(),
  generatedAt: z.string().optional(),
}).passthrough();

const FocusSummarySchema = z.object({
  label: z.string(),
  exclusiveAreaM2: z.number().nullable(),
  recentTransactionExactMatches: z.number(),
  recentTransactionUnverified: z.number(),
  recentTransactionNonMatches: z.number(),
  hasExactMatchData: z.boolean(),
  kbTypeProfileCount: z.number(),
  kbFocusAreaMatchCount: z.number(),
  kbFocusAreaMatches: z.array(z.unknown()),
  notes: z.array(z.string()),
}).passthrough();

const SummaryOutputSchema = z.object({
  generatedAt: z.string(),
  target: z.record(z.string(), z.unknown()),
  focusUnit: z.record(z.string(), z.unknown()),
  sources: z.array(z.unknown()),
  recentTransactions: z.array(z.unknown()),
  listingSummary: z.record(z.string(), z.unknown()),
  comparison: z.record(z.string(), z.unknown()),
  notes: z.array(z.string()),
  focusSummary: FocusSummarySchema,
}).passthrough();
```

입력 schema mismatch → `PHASE_FAILED: 입력 raw-search 스키마 mismatch`. 출력 schema mismatch → `PHASE_FAILED: 출력 summary 스키마 mismatch — 로직 정합성 검토 필요`.

### import 통합 정책

본 plan은 *normalize_results.ts CLI 신설*만 책임. `collect_sources.ts`와 import 통합은 *플랜에 없음*. `run_report.sh`가 `collect_sources.ts` + `normalize_results.ts`를 순차 실행하는 패턴 유지. 후속 plan에서 통합 검토 (사용자 결정).

## 성공 기준

```bash
cd "$(git rev-parse --show-toplevel)"

# 1. TS 컴파일 점검
bun build --target=bun --outfile=/tmp/_chk_n.js apartment/scripts/apartment-daily-report/normalize_results.ts >/dev/null

# 2. CLI usage 점검 (인자 부족 시 exit 1)
bun run apartment/scripts/apartment-daily-report/normalize_results.ts 2>/dev/null
test $? -eq 1 || (echo "FAIL: usage exit code" && exit 1)

# 3. 기능 회귀 (Python vs TS 동일 출력)
#    임시 raw-search.json 샘플로 Python + TS 둘 다 실행 후 jq diff 비교.
#    raw 샘플은 apartment/data/YYYY-MM-DD/raw-search.json 중 가장 최근 또는 fixture 생성.
RAW_SAMPLE="$(find apartment/data -name 'raw-search.json' -type f | sort -r | head -1)"
test -n "$RAW_SAMPLE" || RAW_SAMPLE=""

if [ -n "$RAW_SAMPLE" ]; then
  python3 apartment/scripts/apartment-daily-report/normalize_results.py "$RAW_SAMPLE" /tmp/_n_py.json
  bun run apartment/scripts/apartment-daily-report/normalize_results.ts "$RAW_SAMPLE" /tmp/_n_ts.json
  # generatedAt은 시간 차이 무시 — 그 외 diff 0
  jq 'del(.generatedAt)' /tmp/_n_py.json > /tmp/_n_py_clean.json
  jq 'del(.generatedAt)' /tmp/_n_ts.json > /tmp/_n_ts_clean.json
  diff /tmp/_n_py_clean.json /tmp/_n_ts_clean.json && echo "OK: py vs ts diff 0"
else
  echo "WARN: raw-search.json 샘플 부재 — diff 검증 생략 (phase-02/03 smoke_test가 cover)"
fi
```

성공 기준: 1, 2 모두 통과. 3은 raw 샘플 있을 때 diff 0. 샘플 부재 시 warning + phase-02 smoke_test 의존.

## 금지 사항

- `run_report.sh` / `run_smoke_test.sh` 수정 (phase-02 책임).
- `normalize_results.py` 삭제 (phase-02 책임 — phase-01에서 동시 존재 필요, diff 검증).
- `collect_*.ts` 또는 `naver_api_schemas.ts` 수정.
- 새 외부 의존성 추가 — zod + Bun runtime이면 충분.
- ADR 본문 수정 — 신규 ADR 없음.
- `apartment/docs/` 수정 — 별도 commit (`250e541`)으로 이미 갱신 완료.
- section mark (U+00A7) 직접 입력.

## commit

```bash
cd "$(git rev-parse --show-toplevel)"

git add apartment/scripts/apartment-daily-report/normalize_results.ts

git status --porcelain | grep -E "^(A|M|D|R) " | head
# 의도 외 staged 파일 0 — cross-session race 회피.
# normalize_results.py + run_*.sh + collect_*.ts 변경 stage 0 확인.

git commit -m "feat(apartment): normalize_results.ts 신설 (plan005 phase-01)

- Python normalize_results.py 동작 1:1 보존 (59A alias / focus_area_matches / matchStatus 추론)
- zod 입력 (raw-search) + 출력 (summary) 스키마 자기방어 (ADR-007)
- Python 원본은 phase-02에서 git rm
- run_report.sh / run_smoke_test.sh 호출 변경은 phase-02

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

push 없음.

## PHASE_BLOCKED / PHASE_FAILED 조건

- zod 입력 스키마 mismatch (실제 raw 샘플로 parse 실패) — `PHASE_FAILED: 입력 schema mismatch — collect_sources.ts 출력 형태 검토 필요`.
- 출력 schema mismatch — `PHASE_FAILED: 출력 schema mismatch — TS 로직 정합 검토 필요`.
- TS RegExp 비호환 (특히 한글 문자 클래스) — `PHASE_BLOCKED: regex 비호환 — 사용자 검토 필요`.
- Python vs TS diff 0이 아닌 경우 — `PHASE_FAILED: 기능 회귀 발견 — diff 첨부`.
- 의도 외 staged 파일 — `PHASE_BLOCKED: stage drift`.
