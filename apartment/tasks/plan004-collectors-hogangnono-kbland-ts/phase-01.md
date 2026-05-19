# Phase 1 — collect_hogangnono.ts + collect_kbland.ts 신설

apartment plan004 phase-01. Hogangnono + KB Land 두 HTML 파서 collector를 TypeScript로 신설한다. Bun.fetch (ADR-005) + HTML regex 보존 + zod 결과 스키마 (ADR-007) 적용.

본 phase는 *신설*만 — collect_sources.ts 통합은 phase-02에서. Python 두 파일은 phase-02에서 git rm.

## 작업 위치 (cwd 정책)

run-phases.py가 본 phase를 `cwd=apartment/` (워크스페이스)로 실행한다. 모든 bash 블록 첫 줄은 다음으로 ai-nodes 루트 이동:

```bash
cd "$(git rev-parse --show-toplevel)"
```

이후 모든 path는 `apartment/scripts/apartment-daily-report/...` 형식.

## 관련 docs (먼저 읽기)

- `apartment/docs/adr.md` ADR-005 (Bun.fetch) / ADR-006 (import 통합) / ADR-007 (zod) — 적용 패턴.
- `apartment/scripts/apartment-daily-report/collect_naver_api.ts` — plan003 phase-01 산출. Bun.fetch + retry + zod 패턴 참고.
- `apartment/scripts/apartment-daily-report/naver_api_schemas.ts` — zod 스키마 적용 참고.
- `apartment/scripts/apartment-daily-report/collect_hogangnono.py` — 마이그 원본 (Python regex 보존).
- `apartment/scripts/apartment-daily-report/collect_kbland.py` — 마이그 원본.

## 변경할 파일

신설:

- `apartment/scripts/apartment-daily-report/collect_hogangnono.ts`
- `apartment/scripts/apartment-daily-report/collect_kbland.ts`

본 phase에서 *기존 파일 수정 금지* — Python 원본, collect_sources.ts, run_report.sh 모두 그대로.

## 명세

### collect_hogangnono.ts

CLI 진입점 + library export 동시 제공:

```ts
#!/usr/bin/env bun
// 1. fetch HTML
// 2. extract description / signals / numericSignals / recentTransactions / snippets
// 3. zod 스키마 검증
// 4. CLI: stdout JSON / library: export { runHogangnono }

export async function runHogangnono(url: string): Promise<HogangnonoResult> { ... }

if (import.meta.main) {
  const url = process.argv[2];
  const result = await runHogangnono(url);
  console.log(JSON.stringify(result));
}
```

Python `collect_hogangnono.py` 동작을 정확히 보존:

- HTTP GET via `Bun.fetch` + User-Agent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
- timeout 20s (AbortSignal.timeout)
- HTML regex 파서 — Python 정규식을 TS RegExp로 그대로 옮긴다 (각 패턴 + 플래그 1:1 매핑).
  - `extract_description` (meta description / og:description)
  - `compact` (whitespace + HTML unescape)
  - `parse_amount_to_manwon` ("X억 Y" → 만원 정수)
  - `extract_complex_info` (세대수 / 준공 / 용적률 / 건폐율 / 주차)
  - `extract_area_trade_summary` (대표 평형 1개월 평균)
  - `extract_recent_transactions` (계약일 면적 가격 층, 최대 5개)
  - `build_text` (script/style 제거 + 태그 제거 + compact)
- 결과 JSON 동일 키: `name="Hogangnono"`, `url`, `finalUrl`, `status`, `host`, `title=""`, `description`, `signals[]`, `numericSignals`, `jsonLd=[]`, `note`, `recentTransactions?`, `snippets[]`.
- HTML unescape — `html-entities` 외부 의존성 *추가 금지*. 인라인 작은 unescape (`&amp;` / `&lt;` / `&gt;` / `&quot;` / `&#39;` / `&nbsp;` 6개) 또는 textarea-style replace 직접 작성.

zod 스키마는 **collector 결과 자기방어** 차원. inline `z.object({ ... }).passthrough()` 형태. 응답 schema 검증 실패 시 PHASE_FAILED.

### collect_kbland.ts

같은 패턴. Python `collect_kbland.py` 동작 보존:

- 동일 fetch 패턴.
- regex 파서 — Python 정규식 1:1 매핑.
  - `extract_title` / `extract_description`
  - `extract_json_ld_blocks` (최대 5개, 각 2000자 잘림)
  - `build_text`
  - `extract_type_profiles` (m² / 세대 / 공급-전용 / 방욕실 / 전용률 / 매물수)
  - `extract_price_block(text, label)` — 매매/전세/월세 각 KB시세 / 일반가 / 상위 / 하위 / 최근 실거래 / 매물평균가
- 결과 JSON 키 동일: `name="KB Land"`, `url`, `finalUrl`, `status`, `host`, `title`, `description`, `signals[]`, `numericSignals`, `jsonLd[]`, `note`, `snippets[]`.

### 공용 헬퍼 정책

`compact` / `parse_amount_to_manwon` / `extract_description` / `build_text` 등은 *두 collector 각각에 inline 중복*. plan005 normalize 마이그 시점에 통합 재검토 — 본 plan 스코프 최소화 (사용자 결정).

### zod 결과 스키마

각 collector ts 파일 안에 inline:

```ts
import { z } from "zod";

const HogangnonoResultSchema = z.object({
  name: z.literal("Hogangnono"),
  url: z.string(),
  finalUrl: z.string(),
  status: z.string(),
  host: z.string(),
  title: z.string(),
  description: z.string(),
  signals: z.array(z.string()),
  numericSignals: z.record(z.string(), z.unknown()),
  jsonLd: z.array(z.string()),
  note: z.string(),
  recentTransactions: z.array(z.unknown()).optional(),
  snippets: z.array(z.string()),
}).passthrough();

export type HogangnonoResult = z.infer<typeof HogangnonoResultSchema>;
```

KB Land도 동일 패턴 (`name: z.literal("KB Land")`).

각 collector 함수 끝에 `return Schema.parse(raw)` 또는 `Schema.passthrough().parse(raw)`로 *자기 결과* 검증.

## 성공 기준

```bash
cd "$(git rev-parse --show-toplevel)"

# 1. TS 컴파일 점검 (bun --no-install 통과)
bun build --target=bun --outfile=/tmp/_chk_h.js apartment/scripts/apartment-daily-report/collect_hogangnono.ts >/dev/null
bun build --target=bun --outfile=/tmp/_chk_k.js apartment/scripts/apartment-daily-report/collect_kbland.ts >/dev/null

# 2. CLI 실행 점검 (실제 HTTP 호출 + zod parse 통과)
bun run apartment/scripts/apartment-daily-report/collect_hogangnono.ts https://hogangnono.com/apt/5V184 | jq '.name + " status=" + .status'
bun run apartment/scripts/apartment-daily-report/collect_kbland.ts https://kbland.kr/se/c/2906 | jq '.name + " status=" + .status'

# 3. zod schema mismatch 확인 — 위 명령이 throw 없이 종료해야 통과
```

성공 기준 모두 통과 + Hogangnono 결과의 `recentTransactions` 또는 `numericSignals.areaTradeSummary` 둘 중 하나 존재 + KB Land 결과의 `numericSignals.pricing` 또는 `typeProfiles` 둘 중 하나 존재.

## 금지 사항

- `collect_sources.ts` 수정 (phase-02 책임).
- `collect_hogangnono.py` / `collect_kbland.py` 삭제 (phase-02 책임).
- `run_report.sh` 수정 (변경 불필요).
- 새 외부 의존성 추가 (html-entities / cheerio / fast-html-parser 등). 인라인 작은 unescape로 충분.
- HTML 파싱 라이브러리 도입 — Python 원본이 regex만 사용. 동일 보존.
- ADR 본문 수정 — plan003 ADR-005/006/007 후속 적용일 뿐. 신규 ADR 없음.
- `apartment/docs/` 수정 — docs는 본 task 작성 전 별도 commit으로 이미 갱신 완료 (`91779dd`).
- section mark (U+00A7) 문자 본 phase 본문에 직접 입력 — 평문 표기로 대체.

## commit

phase 끝에 본 phase 산출만 commit (push 없음 — phase-03에서 push):

```bash
cd "$(git rev-parse --show-toplevel)"

git add apartment/scripts/apartment-daily-report/collect_hogangnono.ts
git add apartment/scripts/apartment-daily-report/collect_kbland.ts

git status --porcelain | grep -E "^(A|M|D) " | head
# 의도 외 staged 파일이 있으면 PHASE_BLOCKED: stage drift

git commit -m "feat(apartment): collect_hogangnono.ts + collect_kbland.ts 신설 (plan004 phase-01)

- Bun.fetch + HTML regex 파서 (Python 원본 동작 보존)
- zod 결과 스키마 자기방어 (ADR-007)
- 공용 헬퍼는 각 collector inline 중복 (plan005에서 통합 재검토)
- Python 원본은 phase-02에서 git rm

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

push 없음.

## PHASE_BLOCKED / PHASE_FAILED 조건

- CLI 실행 시 HTTP 차단 / DNS 실패 — `PHASE_BLOCKED: hogangnono.com 또는 kbland.kr 차단 — 네트워크 확인 필요`.
- zod schema mismatch + 해결 불가 — `PHASE_FAILED: zod schema mismatch 진단 필요 — 응답 샘플 첨부`.
- Python regex 1:1 매핑 중 TS RegExp 비호환 발견 (예: lookbehind 미지원 환경) — `PHASE_BLOCKED: regex 비호환 — 사용자 검토 필요`.
- 의도 외 staged 파일 발견 (cross-session race) — `PHASE_BLOCKED: stage drift — git status 확인 필요`.
