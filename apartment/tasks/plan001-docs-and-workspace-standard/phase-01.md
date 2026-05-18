# Phase 01 — apartment 5문서 작성

**Model**: sonnet
**Status**: pending

---

## 목표

apartment 워크스페이스에 5문서 (prd, data-schema, flow, code-architecture, adr)를 신설. career-os 5문서 컨벤션 정합 + ai-nodes ADR-004 워크스페이스 표준 적용 사례.

**범위 외**: AGENTS.md slim (phase-02), .env 이동 (phase-02), 기존 docs git rm (phase-02), ai-nodes 메타 (phase-03).

---

## 본 phase 강제 주의문

- 반드시 Write 도구로 5개 파일을 *생성*해야 한다. prose 응답으로 본문만 출력하고 종료하면 PHASE_FAILED (common-pitfalls 6-6).
- 작성하는 모든 문서에 section sigil (section mark, U+00A7) 특수문자 사용 금지. 섹션 헤더는 `## 1. 제목` 형태. cross-reference는 평문 (`1-4` 또는 `섹션 1-4`). CLAUDE.md directive 준수.
- 본 phase 종료 시 *commit 개수 self-check* 통과: 본 phase가 만든 commit 수 = 1.

---

## 관련 docs

- 참조 패턴: `career-os/docs/{prd,data-schema,flow,code-architecture,adr}.md` (5문서 구현 사례)
- 흡수 대상: `apartment/WORKFLOW.md` (Guri buy-search preferences 12 불릿) + `apartment/TOOLS.md` (target alias notes) + `apartment/docs/decisions/001-naver-api-integration.md` (54줄 ADR 본문)
- 작성 원칙: `skills/planning/SKILL.md` 7단계 (docs 영향 종합 + ADR 작성 원칙)

---

## 작업 항목

### 1. apartment/docs/prd.md 신설

`Write` 도구로 `apartment/docs/prd.md` 작성. 약 130-160줄.

섹션 구조:

1. 목적 — 부동산 시장 리포트 + 인테리어 레퍼런스 자동화 (단일 사용자, 매일 재실행).
2. 현재 MVP 타깃 — `apartment/TOOLS.md` 본문 흡수. 엘지원앙아파트(LG원앙) / 경기 구리시 수택동 854-2 / 포커스 평형 59A + 인테리어 타깃 (구리 럭키아파트 5동 1004호) + Naver Land / Hogangnono / KB Land 정확한 URL + 59A alias 매칭 정책 (exact / unverified / non-match 3단계).
3. 사용자 — 본인 1인. 매일 아침 시장 리포트 + 인테리어 레퍼런스.
4. 기능 목록 — 표 (`| 번호 | 명령 | 산출물 | 빈도 |`):
   - `apartment-daily-report` (skill, `scripts/run_report.sh`) — `data/YYYY-MM-DD/{report.md, raw-search.json, summary.json}` — 매일 08:00 cron
   - `apartment-interior-reference-digest` (skill, `scripts/run_digest.sh`) — `data/interior-reference-digest/YYYY-MM-DD/report.md` + Discord 요약 (3 결정 질문) — 매일
   - native skill 등록 상태: apartment-daily-report = 등록, apartment-interior-reference-digest = 미등록
   - (광역 매수 탐색은 6번 운영 정책 섹션 — Guri buy-search)
5. 산출물 경로 정책 — `data/YYYY-MM-DD/`, `data/interior-reference-digest/YYYY-MM-DD/`, `data/YYYY-MM-DD-HHMM-guri-buy-search/`, `logs/task-runs.jsonl`, `data/audit/YYYY-MM-DD.md`. ai-nodes ADR-004 docs vs data 분리 정합.
6. 운영 정책 — Guri buy-search — `apartment/WORKFLOW.md`의 "Guri buy-search preferences" 12 불릿을 다음 8 sub-section으로 재구성:
   - 6-1. 입지 우선 (수택주공 언덕 페널티)
   - 6-2. 후보 단지 포함 (LG원앙 49/52, 대림한숲 51, 구리럭키 complexNo 24858, 인창동 주공 1659/1660/1661/1662)
   - 6-3. 후보 제외 정책 (쌍용 1648 + 우림 1650 + 수택주공 8575, `selectionRules.minHouseholdsForRecommendation = 501`)
   - 6-4. 입주 가능성 필터 (세안고/전세안고/전세승계/월세승계/갭투자/임차인 거주/갱신권/2027~2028 후반 입주 제외. `articlePrice.allWarrantPrice > 0` 필터)
   - 6-5. 통근 시간 가산 (NHN 판교 사옥 `경기 성남시 분당구 대왕판교로645번길 16`)
   - 6-6. Discord 출력 포맷 (30개 매물 + 1~10/11~20/21~30 그룹 + raw verification 라벨 숨김)
   - 6-7. user-facing 노출 정책 (내부 path 미노출)
   - 6-8. 알림 패턴 (시작/완료/실패 + task 직접 호출, ai-nodes 표준)
7. 비기능 요구사항 — 재실행 가능성, 불확실성 명시, 알림, 격리, 비밀 정보 (`.env` 워크스페이스 root, ai-nodes ADR-004).
8. 의도적으로 안 하는 것 — focus-unit 위장 금지, raw fetched untrusted, chat-only 요약, 검증 안 된 입주 가능 단정, 매물 가격 발명.
9. 성공 기준 — 매일 3 source 교차검증, Guri buy-search 정책 충족, 인테리어 디제스트 3 질문 + 7일 dedupe, `logs/task-runs.jsonl` cost 추적, source 실패 raw 보존.
10. 미연결 / 보류 항목:
    - Naver 수집 후속 (NID_SES 만료 감지, JWT 자동 추출 PoC, 국토부 실거래가 등 추가 source) — ADR-001 후속
    - smoke-test 확장 (`scripts/run_smoke_test.sh`를 routine health check로)
    - (env defaults → 명시 config 파일 이전은 별도 코드 정리 백로그 — `jon890/fos-claw#3`. 본 문서는 미연결 기능만.)

### 2. apartment/docs/data-schema.md 신설

`Write` 도구로 `apartment/docs/data-schema.md` 작성. 약 120-140줄.

섹션 구조:

1. config/ (4 파일)
   - 1-1. focus-unit.json — `complexName, complexAlias, primaryFocusUnit {label, exclusiveAreaM2, aliases[]}, notes[]`
   - 1-2. guri-buy-complexes.json — `purpose, budgetManwon {target, nearBudgetCeiling}, candidateComplexes[] {name, aliases[], complexNo, focusAreasM2[], lifeArea, notes[]}, commuteTarget, excludedComplexes[], selectionRules {minHouseholdsForRecommendation, excludeNonFlatDailyAccess}`
   - 1-3. interior-reference-digest.json — `target, stylePreferences[], currentDecisionNote, outputRoot, sourcePriority[], searchQueries {exactComplex, nearbyAndSimilar, topicFocused}, scoringRubric, dailyReport {maxRecommendations, preferredRecommendations, includeTodayDecisionQuestion, todayDecisionQuestionCount, discordSafe, autoAppendReferenceCandidates, autoAppendDecisions, scheduleRecommendation}, referenceNotebook, evaluationFocus[]`
   - 1-4. lucky-24-floorplan.json — `target, source, visibleDimensionsMm, laundryInterpretation, applianceModels, fieldCheckQuestions[]`
   - 1-5. .env (워크스페이스 root, ai-nodes ADR-004) — `NAVER_COOKIE`, `NAVER_BEARER` (선택), `DISCORD_WEBHOOK_URL`. 템플릿 `.env.example`.
2. data/ (산출물)
   - 2-1. data/YYYY-MM-DD/ — `raw-search.json`, `summary.json` (9 key: generatedAt, target, focusUnit, sources, recentTransactions, listingSummary, comparison, notes, focusSummary), `claude.result.json`, `report.md`, `report.fallback.md`
   - 2-2. data/YYYY-MM-DD-HHMM-guri-buy-search/ — Guri 광역 산출
   - 2-3. data/interior-reference-digest/YYYY-MM-DD/ — `request.md`, `report.md`
   - 2-4. data/audit/YYYY-MM-DD.md — 감사 노트
3. logs/ — `task-runs.jsonl` (run_id, task, started_at, finished_at, exit_code, model, cost_usd, tokens_input, tokens_output), `token-usage.jsonl`, `.usage-status/`. 상세는 `_shared/bin/track_task.sh` 단일 출처.
4. docs/interior/ — 인테리어 결정 영역 (skill 도메인 자산, 5문서와 별도). 6 파일: `interior-references.md`, `lucky-5-1004-{interior-decisions, decision-queue, decision-summary, field-checklist, contractor-brief}.md`. **결정은 docs/**, 디제스트 산출물은 data/. ai-nodes ADR-004 docs vs data 분리 절충 정합.

### 3. apartment/docs/flow.md 신설

`Write` 도구로 `apartment/docs/flow.md` 작성. 약 100-120줄.

섹션:

1. 전체 흐름 개요 — code block (사용자/cron → runner self-wrap → track_task.sh → collector → normalize → Claude CLI → extract → notify_discord → logs)
2. apartment-daily-report 흐름 — 12 step (self-wrap → env load → target 변수 → mkdir → Discord 시작 → collect_sources.py → normalize_results.py → Claude 90s timeout → extract → fallback → Discord 완료 → logs)
   - 2-1. smoke 흐름 — `scripts/run_smoke_test.sh` 헬스 체크 (Claude 호출 없음)
3. apartment-interior-reference-digest 흐름 — 5 step (CONFIG/DECISION/QUEUE/REFERENCE 경로 → mkdir → request.md 작성 → report.md placeholder → agent 외부 실행). 현재 runner는 thin — 실제 Claude 호출은 사용자 또는 cron 외부.
4. 알림 흐름 — `notify_discord.sh` 단일 진입점 (시작/완료/실패, ai-nodes 표준)
5. 트래커 + logs — `_shared/bin/track_task.sh` self-wrap (TRACK_TASK_WRAPPED guard). 종료 시 task-runs.jsonl + token-usage.jsonl append.
6. 직접 호출 진입점 — code block (`bash apartment/skills/.../run_report.sh`, `bash apartment/skills/.../run_digest.sh`, `bash apartment/skills/.../run_smoke_test.sh`). cron 진입 동일.

### 4. apartment/docs/code-architecture.md 신설

`Write` 도구로 `apartment/docs/code-architecture.md` 작성. 약 100-130줄.

섹션:

1. 디렉터리 트리 — code block. apartment/ 하위 전체:
   - `AGENTS.md`, `CLAUDE.md → AGENTS.md` 심링크, `.env`, `.env.example`
   - `config/{focus-unit, guri-buy-complexes, interior-reference-digest, lucky-24-floorplan}.json`
   - `docs/{prd, data-schema, flow, code-architecture, adr}.md` + `docs/interior/` (6 파일)
   - `skills/<name>/{SKILL.md, references/, scripts/}` 통합 구조
   - `.claude/skills/<name>/`
   - `tasks/plan{N}-<slug>/{index.json, phase-NN.md}`
   - `data/` (gitignored), `logs/` (gitignored)
2. skills/ 구조 표준 — `skills/<name>/{SKILL.md, references/, scripts/}` 통합 (ai-nodes 표준). 의도된 비대칭: career-os ADR-019 (scripts/<name>/ 분리, career-os 한정).
3. native skill 등록 (.claude/skills/) — 표:
   - apartment-daily-report — 등록, `claude -p "/apartment-daily-report"` 또는 `scripts/run_report.sh`
   - apartment-interior-reference-digest — 미등록, `scripts/run_digest.sh`
4. Runner 패턴 — self-wrap code block (`TRACK_TASK_WRAPPED` guard + `track_task.sh exec`). `logs/task-runs.jsonl` 기록 보장 + `<task-id>` = `apartment:daily-report` 형태.
5. 외부 의존성 — `_shared/bin/track_task.sh` (load-bearing), `_shared/bin/extract_claude_result.py` (Claude CLI JSON → report.md), `claude` CLI, `agent-browser` CLI (Naver Bearer JWT 자동 추출, ADR-001), (미사용) `_shared/lib/notify_discord.ts`, (미사용) `_shared/lib/extract_claude_result.ts`.
6. 언어 분포 — 표 (Shell 5 + Python 6 + TypeScript 0). career-os 표준 (ADR-020 TypeScript)과 격차. apartment는 현재 Python·Shell 표준.

(plan002~005 시리즈 정보는 본 문서에 박지 않음 — current state 원칙. 추가 plan 작성 시 docs 실시간 갱신.)

### 5. apartment/docs/adr.md 신설

`Write` 도구로 `apartment/docs/adr.md` 작성. 약 50-60줄.

기존 `apartment/docs/decisions/001-naver-api-integration.md` (54줄) 본문을 흡수 + 슬림화 (코드 블록·전수 목록·변경 이력 제거, 거절한 대안 2줄 추가).

섹션:

1. 헤더 — `# ADR — apartment` + apartment 한정 ADR 누적 + 모노레포 레벨 ADR은 `../../docs/adr.md` 링크.
2. Quick Index — 표 (`| ADR | 제목 | Status | 한 줄 요약 |`). 현재 ADR-001만.
3. ADR-001 — Naver Land 쿠키+Bearer API 통합
   - Status: Accepted / Date: 2026-04-24
   - 맥락 — 2026-04 Naver Land SPA 우회 차단 (SSR /404, fin.land 리다이렉트, SPA UI/검색/지도 인터랙션 /404, DevTools 감지). API 채널 조건부 열림 (overview / prices / articles 3 endpoint + 쿠키 + Bearer JWT). 쿠키 = NID_AUT/NID_SES 수주~수개월, Bearer = SPA 발급 JWT (exp-iat=3h).
   - 결정 — (1) SPA 우회 포기 (2) 3 API endpoint만 정식 수집 (3) 쿠키 사용자 수동 갱신 (`.env` `NAVER_COOKIE=`) (4) Bearer JWT agent-browser 자동 추출 + `NAVER_BEARER` fallback (5) 호출 정책 (2초 sleep, 429 백오프 2/4/8s 3회, 폴백 + Discord)
   - 거절한 대안 — Puppeteer/Playwright (`/404` 차단 + DevTools 감지로 불가) / 비공식 unofficial API 직 호출 (인증 우회 불가)
   - 결과 — 3축 (공식 시세 + 매물 호가 + 단지 개요) 확장 / 사용자 개입: NID_SES 만료 시 (실측 수주~수개월) 쿠키 수동 갱신 — 복사·붙여넣기 / `.env` 부재 시 Hogangnono+KB 폴백 / 리스크: Naver API 엔드포인트·인증 구조 변경 시 수집기 수정 필요 (비공식 API SLA 없음)
   - 적용 — `apartment/skills/apartment-daily-report/scripts/collect_naver_api.py` (3 API endpoint + 인증 + 폴백), `apartment/.env` (NAVER_COOKIE, NAVER_BEARER), 진단 세션(2026-04-24) 상세는 git history.

---

## 검증 (phase 종료 직전 실행)

```bash
# 1. 5문서 모두 존재
for f in prd data-schema flow code-architecture adr; do
  test -f apartment/docs/$f.md && echo "[$f.md] OK" || { echo "PHASE_FAILED: $f.md absent"; exit 1; }
done

# 2. 분량 검증
for f in prd data-schema flow code-architecture; do
  LINES=$(wc -l < apartment/docs/$f.md)
  echo "[$f.md] $LINES lines"
  [ "$LINES" -ge 90 ] || { echo "PHASE_FAILED: apartment/docs/$f.md $LINES < 90 lines"; exit 1; }
done
ADR_LINES=$(wc -l < apartment/docs/adr.md)
echo "[adr.md] $ADR_LINES lines"
[ "$ADR_LINES" -ge 40 ] || { echo "PHASE_FAILED: apartment/docs/adr.md $ADR_LINES < 40 lines"; exit 1; }

# 3. section sigil 미사용 검증 (U+00A7, CLAUDE.md directive 정합)
SIGIL_CHAR=$(printf '\xc2\xa7')
for f in prd data-schema flow code-architecture adr; do
  COUNT=$(grep -c "$SIGIL_CHAR" apartment/docs/$f.md 2>/dev/null || echo 0)
  [ "$COUNT" -eq 0 ] || { echo "PHASE_FAILED: apartment/docs/$f.md sigil 잔재 $COUNT"; exit 1; }
done
echo "[sigil check] 0건"

# 4. 핵심 키워드 (각 문서 책임 영역)
grep -q "Guri buy-search" apartment/docs/prd.md || { echo "PHASE_FAILED: prd.md Guri buy-search 흡수 누락"; exit 1; }
grep -q "59A" apartment/docs/prd.md || { echo "PHASE_FAILED: prd.md 59A 누락"; exit 1; }
grep -q "interior-reference-digest" apartment/docs/data-schema.md || { echo "PHASE_FAILED: data-schema.md interior 누락"; exit 1; }
grep -q "track_task.sh" apartment/docs/flow.md || { echo "PHASE_FAILED: flow.md tracker 누락"; exit 1; }
grep -q "ADR-001" apartment/docs/adr.md || { echo "PHASE_FAILED: adr.md ADR-001 누락"; exit 1; }
echo "[keyword check] OK"

# 5. commit 생성
git add apartment/docs/
git commit -m "$(cat <<'EOF'
docs(apartment): 5문서 (prd / data-schema / flow / code-architecture / adr) 신설 (plan001 phase-01)

career-os 5문서 컨벤션 정합 + ai-nodes ADR-004 워크스페이스 표준 적용.
WORKFLOW.md / TOOLS.md / docs/decisions/001 본문 흡수 (실제 파일 제거는 phase-02).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"

# 6. commit 개수 self-check (본 phase = 1 commit)
COMMITS=$(git log --format='%H' HEAD~1..HEAD | wc -l)
echo "[commit count] $COMMITS"
[ "$COMMITS" -eq 1 ] || { echo "PHASE_FAILED: phase commit $COMMITS != 1"; exit 1; }

echo "✓ Phase 01 검증 통과"
```

---

## 의도 메모

- draft 패턴 폐기 (사용자 결정 2026-05-18) — phase가 직접 작성. common-pitfalls 6-6 방어선은 강제 주의문 + commit 개수 self-check + 핵심 키워드 grep.
- 사용자 결정 보존 (phase 작성 시 반영):
  - ADR-001 거절 대안 유지 (Puppeteer/Playwright + 비공식 API)
  - ADR-001 쿠키 갱신 빈도 원본 보존 ("수주~수개월")
  - interior 영역 = 결정 docs/, 산출물 data/ 절충
  - prd.md 10번 = Naver 후속 + smoke 확장 + GitHub issue `jon890/fos-claw#3` 인용
  - plan002~005 시리즈 정보 docs에 박지 않음 (current state 원칙)
- 본 phase 산출 5문서는 phase-02 (AGENTS slim에서 5문서 라우팅), phase-03 (ai-nodes adr.md ADR-004 인용), phase-04 (잔여 참조 갱신) 모두의 기반.
