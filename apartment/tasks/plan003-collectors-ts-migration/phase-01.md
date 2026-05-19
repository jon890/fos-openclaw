# Phase 01 — naver_api_schemas.ts (zod) + collect_naver_api.ts (Bun.fetch)

**Model**: sonnet
**Status**: pending

---

## 목표

Naver Land API 수집기를 TypeScript로 마이그. 2 file 신설:

1. `apartment/scripts/apartment-daily-report/naver_api_schemas.ts` — Naver API 3 endpoint zod 스키마 (overview / prices / articles). ADR-007 적용.
2. `apartment/scripts/apartment-daily-report/collect_naver_api.ts` — Bun.fetch 기반 collector. ADR-005 + ADR-001 적용.

표준 출력 JSON schema는 기존 Python 동일 — phase-02 collect_sources.ts와 호환.

**범위 외**: collect_sources.ts (phase-02), run_report.sh 갱신 (phase-02), 옛 Python git rm (phase-02), 검증 + push (phase-03).

---

## 본 phase 강제 주의문

- Write 도구로 2 file 생성. prose 응답만으로는 PHASE_FAILED.
- section sigil (section mark, U+00A7) 사용 금지.
- 본 phase commit 개수 self-check = 1.
- Bun 미설치 시 `echo "PHASE_BLOCKED: bun 미설치" && exit 2` (Bash 도구로 직접 실행).

---

## 사전 cwd 설정 (run-phases.py hotfix)

```bash
cd "$(git rev-parse --show-toplevel)"
pwd  # 기대: /home/bifos/ai-nodes
```

---

## 사전 조건 검증

```bash
command -v bun >/dev/null || { echo "PHASE_BLOCKED: bun 미설치"; exit 2; }
grep -q '"zod"' package.json || { echo "PHASE_BLOCKED: zod 의존성 부재"; exit 2; }
test -f apartment/scripts/apartment-daily-report/collect_naver_api.py || { echo "PHASE_FAILED: Python 참조 본체 부재"; exit 1; }
echo "[사전 조건] OK"
```

---

## 관련 docs

- ADR-001 (Naver Land 쿠키+Bearer API, `apartment/docs/adr.md`): 3 endpoint + 호출 정책 (2s sleep + 2/4/8 백오프 + 폴백).
- ADR-005 (Bun.fetch): 외부 HTTP fetch 표준.
- ADR-007 (zod): 응답 스키마 검증. `passthrough()` 적극 사용.
- 참조 본체: `apartment/scripts/apartment-daily-report/collect_naver_api.py` (Python 기존, 약 160줄).
- zod 패턴 참조: `_shared/lib/mvp_target_schema.ts` (plan002 사례).

---

## 작업 항목

### 1. naver_api_schemas.ts 신설

`Write` 도구로 `apartment/scripts/apartment-daily-report/naver_api_schemas.ts` 작성.

스키마 3개:

| 스키마 | 엔드포인트 | 인증 | 핵심 필드 |
|---|---|---|---|
| `OverviewSchema` | `/api/complexes/overview/{id}` | 쿠키 | `complex.complexName`, `complex.pyeongs[]` |
| `PricesSchema` | `/api/complexes/{id}/prices?tradeType=A1\|B1&year=5&type=summary` | 쿠키+Bearer | 한국부동산원 시세 본문 (상/평균/하 + 전세가율) |
| `ArticlesSchema` | `/api/articles/complex/{id}?tradeType=A1\|B1` | 쿠키+Bearer | `articleList[]` (각 `articleNo`, `articlePrice.allWarrantPrice` 등 prd.md 6-4 필터 대상) |

작성 원칙:

- 미상 필드는 `passthrough()` 또는 `catchall(z.unknown())` (ADR-007). Naver 비공식 API라 schema drift 무시.
- 필수 필드만 명시 — `articleNo` (필터링용), `articlePrice` (필터링용).
- `z.infer<typeof X>` 타입 alias 3개 export (`Overview`, `Prices`, `Articles`).
- 정확한 필드 본문은 phase Claude가 Python 본체 + 실 응답 샘플 참조해 작성.

### 2. collect_naver_api.ts 신설

`Write` 도구로 `apartment/scripts/apartment-daily-report/collect_naver_api.ts` 작성.

Python → TypeScript 변환 매핑:

| Python | TypeScript |
|---|---|
| `import requests` | `Bun.fetch` (ADR-005) |
| `requests.get(url, cookies={...})` | `Bun.fetch(url, { headers: { Cookie, Authorization } })` |
| `time.sleep(2)` | `await new Promise(r => setTimeout(r, 2000))` |
| `subprocess.run(['agent-browser', ...])` | `Bun.spawn(['agent-browser', ...])` (ADR-001 적용 detail) |
| `json.loads(text)` | `await res.json()` + `Schema.parse(...)` (zod, ADR-007) |
| `tempfile.mkstemp` | `import { mkdtempSync } from "fs"` + `path.join(tmpdir, ...)` |
| `os.environ.get` | `process.env[]` |
| `subprocess.run(... capture_output=True, text=True)` | `Bun.spawn(...) + new Response(proc.stdout).text()` |

핵심 함수:

- `extractBearerViaHar(cookie, complexNo): Promise<string | null>` — agent-browser HAR 캡처 + Authorization 헤더 회수.
- `fetchWithRetry(url, headers): Promise<Response>` — 2s sleep + 2/4/8 백오프 3회 + 마지막 성공 fallback (ADR-001).
- `main()` — env load → bearer 추출 → 3 endpoint 호출 + zod parse → JSON 출력.

환경변수: `NAVER_COOKIE` (필수), `NAVER_BEARER` (선택), `COMPLEX_NO` (기본 1649).

표준 출력 JSON: `{name: "Naver Land", status: "api-ok"|"skipped-no-cookie"|"auth-failed"|"rate-limited"|"no-data", numericSignals?, prices?, articles?, note?}`. 기존 Python 동일 schema.

CLI 인터페이스: `bun run collect_naver_api.ts <url>` — url 인자 받음 (collect_sources가 호출).

shebang: `#!/usr/bin/env bun`. chmod +x.

phase-02 import 호환 위해 main 외에 `export async function runNaverApi(url: string): Promise<SourceResult>` 함수 export 권장.

### 3. commit 생성

```bash
git add apartment/scripts/apartment-daily-report/naver_api_schemas.ts apartment/scripts/apartment-daily-report/collect_naver_api.ts
git commit -m "$(cat <<'EOF'
feat(apartment): collect_naver_api.ts + naver_api_schemas.ts 신설 (plan003 phase-01)

ADR-001 (Naver Land 쿠키+Bearer API) Python → TypeScript 마이그.
ADR-005 (Bun.fetch) + ADR-007 (zod) 첫 적용.

- naver_api_schemas.ts: 3 endpoint zod 스키마 (Overview/Prices/Articles, passthrough())
- collect_naver_api.ts: Bun.fetch + 2/4/8 백오프 + Bun.spawn(agent-browser) Bearer JWT 자동 추출
- 표준 출력 JSON schema 기존 Python 동일 (phase-02 collect_sources.ts 호환)

옛 collect_naver_api.py는 phase-02에서 git rm.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## 검증 (phase 종료 직전)

```bash
SIGIL_CHAR=$(printf '\xc2\xa7')

# 1. file 신설
test -f apartment/scripts/apartment-daily-report/naver_api_schemas.ts || { echo "PHASE_FAILED: schemas missing"; exit 1; }
test -f apartment/scripts/apartment-daily-report/collect_naver_api.ts || { echo "PHASE_FAILED: collect_naver_api missing"; exit 1; }

# 2. type/syntax
bun build --no-bundle apartment/scripts/apartment-daily-report/naver_api_schemas.ts > /dev/null 2>&1 || { echo "PHASE_FAILED: schemas type"; exit 1; }
bun build --no-bundle apartment/scripts/apartment-daily-report/collect_naver_api.ts > /dev/null 2>&1 || { echo "PHASE_FAILED: collect_naver_api type"; exit 1; }

# 3. ADR-005/007 패턴 적용 grep
grep -q "from \"zod\"\|from 'zod'" apartment/scripts/apartment-daily-report/naver_api_schemas.ts || { echo "PHASE_FAILED: zod import 누락"; exit 1; }
grep -q "Bun.fetch" apartment/scripts/apartment-daily-report/collect_naver_api.ts || { echo "PHASE_FAILED: Bun.fetch 미사용"; exit 1; }
grep -q "Bun.spawn" apartment/scripts/apartment-daily-report/collect_naver_api.ts || { echo "PHASE_FAILED: Bun.spawn(agent-browser) 미사용"; exit 1; }

# 4. sigil
for f in apartment/scripts/apartment-daily-report/naver_api_schemas.ts apartment/scripts/apartment-daily-report/collect_naver_api.ts; do
  COUNT=$(grep -c "$SIGIL_CHAR" "$f" 2>/dev/null || echo 0)
  [ "$COUNT" -eq 0 ] || { echo "PHASE_FAILED: $f sigil $COUNT"; exit 1; }
done

# 5. commit 개수
COMMITS=$(git log --format='%H' HEAD~1..HEAD | wc -l)
[ "$COMMITS" -eq 1 ] || { echo "PHASE_FAILED: commit $COMMITS != 1"; exit 1; }

echo "✓ Phase 01 검증 통과"
```

---

## 의도 메모

- naver_api_schemas.ts 분리 — collect_naver_api.ts 본문 압축 + 응답 schema 변경 시 단일 위치 갱신.
- `passthrough()` 적극 사용 (ADR-007) — 비공식 API drift 흡수.
- agent-browser CLI 호출은 Bun.spawn — ADR-001 적용 detail (Bearer JWT 자동 추출 유지).
- 옛 collect_naver_api.py는 phase-02에서 git rm — 본 phase는 *Python 본체 보존* (collect_sources.py 호출 중).
