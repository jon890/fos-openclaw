# Phase 2 — collect_sources.ts import 통합 + Python git rm

apartment plan004 phase-02. phase-01에서 신설한 두 TS collector를 `collect_sources.ts`에 import 통합. `runPythonSource` Bun.spawn 분기 폐기 (ADR-006 완료). Python 두 파일 git rm.

## 작업 위치 (cwd 정책)

run-phases.py가 본 phase를 `cwd=apartment/` (워크스페이스)로 실행한다. 모든 bash 블록 첫 줄은 다음으로 ai-nodes 루트 이동:

```bash
cd "$(git rev-parse --show-toplevel)"
```

이후 모든 path는 `apartment/scripts/apartment-daily-report/...` 형식.

## 관련 docs (먼저 읽기)

- `apartment/docs/adr.md` ADR-006 (import 통합) — runPythonSource 분기 폐기 의도.
- `apartment/scripts/apartment-daily-report/collect_sources.ts` — phase-01 기준 상태. `runPythonSource` 함수 + SOURCES 배열 `script` 키 + for loop 분기 폐기 대상.
- `apartment/scripts/apartment-daily-report/collect_hogangnono.ts` (phase-01 신설).
- `apartment/scripts/apartment-daily-report/collect_kbland.ts` (phase-01 신설).
- `apartment/scripts/apartment-daily-report/run_smoke_test.sh` — 검증 진입점.

## 변경할 파일

수정:

- `apartment/scripts/apartment-daily-report/collect_sources.ts`

삭제:

- `apartment/scripts/apartment-daily-report/collect_hogangnono.py`
- `apartment/scripts/apartment-daily-report/collect_kbland.py`

본 phase에서 *신규 파일 생성 금지*. *docs / ADR / run_report.sh 수정 금지*.

## 명세

### collect_sources.ts 통합

기준 상태 (phase-01 기준):

```ts
import { runNaverApi } from "./collect_naver_api";
// ...
const SOURCES: Source[] = [
  { name: "Naver Land", url: NAVER_URL },
  { name: "Hogangnono", url: HOGANGNONO_URL, script: `${SCRIPT_DIR}/collect_hogangnono.py` },
  { name: "KB Land", url: KB_URL, script: `${SCRIPT_DIR}/collect_kbland.py` },
];

async function runPythonSource(script: string, url: string): Promise<...> { ... }

// for loop:
if (!src.script) {
  result = (await runNaverApi(src.url)) as ...;
} else {
  result = await runPythonSource(src.script, src.url);
}
```

변경 후 상태:

```ts
import { runNaverApi } from "./collect_naver_api";
import { runHogangnono } from "./collect_hogangnono";
import { runKbland } from "./collect_kbland";
// ...
interface Source {
  name: string;
  url: string;
  fetcher: (url: string) => Promise<Record<string, unknown>>;
}

const SOURCES: Source[] = [
  { name: "Naver Land", url: NAVER_URL, fetcher: runNaverApi as unknown as (u: string) => Promise<Record<string, unknown>> },
  { name: "Hogangnono", url: HOGANGNONO_URL, fetcher: runHogangnono as unknown as (u: string) => Promise<Record<string, unknown>> },
  { name: "KB Land", url: KB_URL, fetcher: runKbland as unknown as (u: string) => Promise<Record<string, unknown>> },
];

// runPythonSource 함수 + SCRIPT_DIR 상수 + `script` 키 + `if (!src.script)` 분기 모두 폐기.

// for loop 본문:
try {
  const result = await src.fetcher(src.url);
  sourceResults.push(result);
} catch (e) { ... }
```

핵심 정리:

- `runPythonSource` 함수 제거.
- `SCRIPT_DIR` / `import.meta.dir` 상수 제거 (다른 곳에서 사용 안 함 확인 후 제거).
- `Source.script` 필드 제거 → `fetcher` 필드로 대체.
- `if (!src.script) ... else ...` 분기 → `src.fetcher(src.url)` 단일 호출.
- `Bun.spawn(["python3", ...])` 흔적 0.

`fetcher` 시그니처 통일은 `Promise<Record<string, unknown>>`로 좁힌다 — 각 collector가 `runX` 함수 export 시 호환되도록 phase-01 산출 점검.

(만약 phase-01 산출 `runHogangnono` / `runKbland`가 더 구체적 zod-infer 타입을 반환하면 SOURCES 배열 타입 캐스팅 또는 fetcher 호출부 캐스팅이 필요. type 호환 issue 발생 시 `Record<string, unknown>` 캐스팅으로 통일 — 본 단계는 *오케스트레이션 단순화* 우선, 타입 narrow는 후속.)

### Python 두 파일 git rm

```bash
cd "$(git rev-parse --show-toplevel)"
git rm apartment/scripts/apartment-daily-report/collect_hogangnono.py
git rm apartment/scripts/apartment-daily-report/collect_kbland.py
```

### 검증

```bash
cd "$(git rev-parse --show-toplevel)"

# 1. TS 컴파일 점검
bun build --target=bun --outfile=/tmp/_chk_sources.js apartment/scripts/apartment-daily-report/collect_sources.ts >/dev/null

# 2. runPythonSource 흔적 0 확인
! grep -n "runPythonSource\|Bun.spawn.*python3\|collect_hogangnono.py\|collect_kbland.py" apartment/scripts/apartment-daily-report/collect_sources.ts

# 3. run_report.sh가 python3 호출하지 않는지 (Python collector 파일 ref 0)
! grep -n "collect_hogangnono\|collect_kbland" apartment/scripts/apartment-daily-report/run_report.sh || echo "WARN: run_report.sh에 Python 참조 잔존"

# 4. smoke test (네트워크 의존 — 차단 시 PHASE_BLOCKED)
bash apartment/scripts/apartment-daily-report/run_smoke_test.sh
```

성공 기준: 1-3 모두 통과 + 4가 정상 종료 (network 차단 시 PHASE_BLOCKED 가능).

## 금지 사항

- 새 파일 생성 (phase-01 책임 완료).
- `apartment/docs/` 수정 — 별도 commit (`91779dd`)으로 완료.
- `apartment/scripts/apartment-daily-report/run_report.sh` 수정 — 변경 불필요 (Python 호출 없음).
- `apartment/scripts/apartment-daily-report/collect_naver_api.ts` 또는 `naver_api_schemas.ts` 수정 — plan003 산출 보존.
- normalize_results.py 수정 — plan005 책임.
- ADR 본문 수정 — plan004 = 후속 적용. 신규 ADR 없음.
- section mark (U+00A7) 문자 본 phase 본문에 직접 입력 — 평문 표기로 대체.

## commit

```bash
cd "$(git rev-parse --show-toplevel)"

git add apartment/scripts/apartment-daily-report/collect_sources.ts
# Python rm은 git rm으로 이미 stage됨

git status --porcelain | head
# 의도 외 staged 파일이 있으면 PHASE_BLOCKED: stage drift

git commit -m "refactor(apartment): collect_sources.ts import 통합 + Python collector 2개 git rm (plan004 phase-02)

- runPythonSource (Bun.spawn python3) 분기 폐기 — ADR-006 완료
- Source.script → Source.fetcher 통일, for loop 단일 호출
- collect_hogangnono.py + collect_kbland.py git rm
- run_report.sh 변경 없음 (이미 Python 직접 호출 없음)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

push 없음 (phase-03 책임).

## PHASE_BLOCKED / PHASE_FAILED 조건

- TypeScript 타입 호환 실패 (runX 반환 타입 narrow vs SOURCES `fetcher` Record 시그니처) — `Record<string, unknown>` 캐스팅으로 통일 후에도 컴파일 실패 시 `PHASE_BLOCKED: ts type 호환 — 사용자 검토 필요`.
- smoke_test 실패 (네트워크) — `PHASE_BLOCKED: smoke_test 네트워크 차단`.
- smoke_test 실패 (collector 로직) — `PHASE_FAILED: collector 결과 불일치 — diff 첨부`.
- 의도 외 staged 파일 (cross-session race) — `PHASE_BLOCKED: stage drift`.
- run_report.sh에 Python collector 참조 잔존 — `PHASE_FAILED: run_report.sh drift 확인 필요`.
