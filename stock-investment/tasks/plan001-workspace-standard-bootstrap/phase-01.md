# Phase 1 — 5문서 신설 (decisions/* 7 ADR 자료 재분배)

stock-investment plan001 phase-01. ai-nodes 표준 5문서 (`prd/data-schema/flow/code-architecture/adr`)를 stock-investment/docs/에 신설. docs/decisions/* 7 ADR 자료를 의미에 맞게 재분배. adr.md에 ADR-001 신설.

본 phase는 *docs 신설*만. AGENTS.md / CLAUDE.md / tasks/ / .env는 phase-02 책임. skill / scripts / config 코드 변경 0.

## 작업 위치 (cwd 정책)

run-phases.py가 본 phase를 `cwd=stock-investment/` (워크스페이스)로 실행. 첫 bash 블록:

```bash
cd "$(git rev-parse --show-toplevel)"
```

이후 path는 `stock-investment/...` 형식.

## 관련 docs (먼저 읽기)

**5문서 작성 표준**:
- `docs/docs-style.md` — 6 패턴 + 한자어 회피 + 거울 구조 (ADR-005). 모든 stock-investment docs가 본 형식 따름.
- `docs/workspace-structure.md` 2번·6번 — 5문서 책임 영역 청사진.
- `skills/planning/SKILL.md` "5문서 공통 작성 원칙" 섹션 — 각 문서 *책임 영역* + *넣지 않는다* 목록.

**참고 패턴 (다른 워크스페이스)**:
- `career-os/docs/{prd,data-schema,flow,code-architecture,adr}.md` — 가장 성숙한 5문서 예시.
- `apartment/docs/{prd,data-schema,flow,code-architecture,adr}.md` — 작은 워크스페이스 5문서 예시.

**stock-investment 재분배 원본**:
- `stock-investment/docs/decisions/001-stock-investing-workspace-and-morning-brief.md`
- `stock-investment/docs/decisions/002-google-nasdaq-first-class-and-issue-analysis.md`
- `stock-investment/docs/decisions/003-ai-semiconductor-infrastructure-monitoring.md`
- `stock-investment/docs/decisions/004-core-theme-report-structure.md`
- `stock-investment/docs/decisions/005-daily-ai-tech-stock-blog-note.md`
- `stock-investment/docs/decisions/006-anthropic-financial-services-reference.md`
- `stock-investment/docs/decisions/007-financial-services-adoption-plan.md`

**워크스페이스 현황** (재분배 시 참조):
- 3 skill: `stock-investing-morning-brief` / `current-issue-analysis` / `daily-stock-analysis-note` (`stock-investment/skills/<name>/SKILL.md` 위치).
- 6 config json: `catalysts.json`, `current-issues.json`, `daily-stock-universe.json`, `sources.json`, `theme-reports.json`, `watchlist.json`.
- data/: 일자별 디렉터리 (`YYYY-MM-DD/`) + `daily-notes/` + `issues/` + `audit/` + `thesis-tracker/`.

## 신설할 파일

5개 신설:

- `stock-investment/docs/prd.md`
- `stock-investment/docs/data-schema.md`
- `stock-investment/docs/flow.md`
- `stock-investment/docs/code-architecture.md`
- `stock-investment/docs/adr.md`

본 phase에서 *기존 파일 수정 금지*. decisions/* 7 파일 *읽기만*, 폐기는 plan003 책임.

## decisions/* → 5문서 재분배 매핑

각 decisions ADR의 *content*를 분석해 책임 영역에 맞춰 분배. 단순 복사 ❌ — *의미 재구성*.

| decisions | 5문서 재분배 |
|---|---|
| 001 stock-investing-workspace and morning brief | **prd**: 워크스페이스 목적 + 첫 skill 명세 + 타깃 (CRCL/BTC/QQQ/GOOGL). **flow**: morning-brief 수집→Claude→Discord 흐름. |
| 002 google-nasdaq first-class and issue-analysis | **prd**: 기능 확장 (Nasdaq/QQQ/Google + issue-analysis skill). **flow**: issue-analysis 흐름. |
| 003 ai-semiconductor-infrastructure-monitoring | **prd**: 테마 추가 (AI 반도체/인프라). **data-schema**: theme-reports.json 스키마 일부. |
| 004 core-theme-report-structure | **data-schema**: theme-reports.json 정식 스키마. **flow**: theme report 생성 흐름. |
| 005 daily-ai-tech-stock-blog-note | **prd**: daily-stock-analysis-note skill. **flow**: blog note 생성 + fos-study git push 흐름. **code-architecture**: career-os/sources/fos-study 의존 (cross-workspace 예외, 발행 목적). |
| 006 anthropic-financial-services-reference | **prd** *미연결 항목* 또는 **adr**: reference material 인용 (미실행 계획 자료). |
| 007 financial-services-adoption-plan | **prd** *미연결 항목* — 미실행 plan. 또는 *분해 대기 작업* 섹션. |

재분배 원칙:
- 결정의 *왜* + trade-off 거절 대안 → adr.md (단 7 decisions 본문 자체는 plan003에서 폐기 — adr.md에는 *요약만*)
- 제품 범위·기능 명세·타깃 → prd.md
- JSON 스키마·산출물 형식 → data-schema.md
- 명령별 데이터 흐름 (입력 → runner → 산출물) → flow.md
- 디렉터리 트리·skill 위치·외부 의존성 → code-architecture.md

## 명세

### 1. prd.md 신설

ai-nodes 표준 (`career-os/docs/prd.md` 또는 `apartment/docs/prd.md` 참고). 섹션:

- 목적 (워크스페이스 1 줄 의도)
- 현재 MVP 타깃 (CRCL / BTC / GOOGL / QQQ / AI 반도체 + 금융 서비스 reference)
- 사용자 (단일 사용자 = 본인)
- 기능 목록 (표): 3 skill — 산출물 + Discord 발행 여부 + 빈도
- 산출물 경로 정책 (data/YYYY-MM-DD/ + daily-notes/ + issues/ + thesis-tracker/ + audit/)
- 비기능 요구사항 (재실행 가능성 / 비용 추적 / Discord 알림 / 격리 / 비밀)
- 의도적으로 안 하는 것 (실시간 거래 / 실 거래 자동화 / 광범위 풀-리포 분석 / 재무 자문 등)
- 미연결 / 보류 항목 (decisions/006/007 자료)
- 성공 기준 (3 skill 매일 정상 도는지)

### 2. data-schema.md 신설

6 config json 스키마 명세 — `Read` 도구로 각 config json 본문 점검 후 작성:

- `config/catalysts.json` (테마별 catalyst 이벤트)
- `config/current-issues.json` (issue-analysis 토픽 큐)
- `config/daily-stock-universe.json` (daily-note 후보 종목)
- `config/sources.json` (수집 source 정의)
- `config/theme-reports.json` (테마 리포트 스키마, decisions/004 기반)
- `config/watchlist.json` (CRCL/BTC/등 기본 watch)

산출물 스키마:
- `data/YYYY-MM-DD/<topic-or-mode>/` 디렉터리 구조
- `data/daily-notes/<YYYY-MM-DD>/<slug>/` — daily-stock-analysis-note 산출
- `data/issues/<YYYY-MM-DD>/<slug>/` — current-issue-analysis 산출
- `data/thesis-tracker/` — 시계열 thesis 추적
- `data/audit/` — workspace-audit 결과

logs/:
- `logs/task-runs.jsonl` 스키마 (`_shared/bin/track_task.sh`가 사용)
- `logs/token-usage.jsonl`

.env 스키마 (plan001은 .env.example placeholder만, 실 .env는 plan003 또는 사용자 작업):
- `DISCORD_CHANNEL_ID` (필수, openclaw 알림)
- `TZ=Asia/Seoul` (현재 run_daily_note.sh L14에 하드코드 — .env로 끌어올림 검토)

### 3. flow.md 신설

3 skill 각각 데이터 흐름 (입력 → runner → Claude → 산출물). career-os/flow.md L37~290 패턴 참고.

각 skill에 대해:
- 호출 방식 (현재: `bash skills/<name>/scripts/<runner>.sh`. plan002 후: `claude -p "/<skill>"` 또는 native)
- 입력 (config + data 의존)
- runner 단계 (track_task.sh wrap → 수집 → Claude → extract → notify)
- 산출물 위치
- Discord 알림 (`DISCORD_CHANNEL_ID`)
- git push (daily-stock-analysis-note만 — career-os/sources/fos-study로)

또 통과 시점 항상 일어나는 일 (track_task.sh + Discord 알림 + extract_claude_result.ts) 섹션.

### 4. code-architecture.md 신설

디렉터리 트리 + 계층 책임 + 외부 의존성. career-os/code-architecture.md L120~170 패턴 참고.

- stock-investment/ 트리:
  - skills/ (3 skill, *현재 통합 패턴* — plan002에서 분리 패턴으로)
  - config/ (6 json)
  - data/ (일자별)
  - docs/ (5문서 + plan003까지 decisions/ 잔존)
  - logs/
  - tasks/ (plan001 신설, plan002~ 후속)

- 외부 의존성:
  - `_shared/bin/track_task.sh` (load-bearing)
  - `_shared/lib/extract_claude_result.ts` (ai-nodes plan001 통합)
  - `claude` CLI
  - career-os/sources/fos-study (cross-workspace 발행 목적 — decisions/005 예외, ADR-001 미위반 — 발행 대상 git repo)

- 분리 패턴 적용 상태 (plan002 대기 표기):
  - 현재: `skills/<name>/{SKILL.md, references/, scripts/}` (통합 패턴, ai-nodes ADR-006 *미적용 — 의도된 비대칭 종료 예정*)
  - plan002 후: `scripts/<name>/` + `.claude/skills/<name>/{SKILL.md, references/}` (분리 표준)

### 5. adr.md 신설

Quick Index + ADR-001 본문. decisions/* 7개 본문은 *plan003에서 폐기 예정*이므로 adr.md에는 *현재 결정* 1개만:

```
# ADR — stock-investment

stock-investment 워크스페이스 아키텍처 결정 누적. 새 결정은 가장 아래에 추가.

형식: `## ADR-N — 제목` + Status / Date 라인 + 맥락 / 결정 / 결과 3섹션.

모노레포 레벨 ADR: ../docs/adr.md.

History: 옛 docs/decisions/001~007.md는 plan003에서 폐기 + 5문서 (prd/data-schema/flow/code-architecture)로 재분배 완료.

---

## Quick Index

| ADR | 제목 | Status | 한 줄 요약 |
|---|---|---|---|
| ADR-001 | 워크스페이스 ai-nodes 표준 구조 적용 시작 | Accepted | 5문서 + AGENTS 한글화 + CLAUDE 심링크 + tasks/ (plan001). 분리 패턴 + decisions 폐기는 plan002/003 후속 |

---

## ADR-001 — 워크스페이스 ai-nodes 표준 구조 적용 시작

**Status**: Accepted
**Date**: 2026-05-20

### 맥락

stock-investment는 2026-05-05 운영 시작 이후 ai-nodes 표준 구조 (ADR-004) 미적용 상태로 유지. 발견 시점 (2026-05-20 audit):

- 5문서 부재 (docs/decisions/* 7개만 — 옛 시점 ADR 형식, 모노레포 표준 ADR-006 미적용)
- AGENTS.md 영문 짧음 (라우팅 / 외부 의존성 명세 미흡)
- CLAUDE.md 심링크 부재 (Claude Code 자동 로드 미활용)
- tasks/ 부재 (plan 시스템 미운영)
- .claude/skills/ 부재 (3 skill native 진입점 미등록)
- skills/<name>/scripts/ 통합 패턴 (ai-nodes ADR-006 분리 표준 미적용)

워크스페이스 격리 원칙상 stock-investment를 *의도된 비대칭*으로 둘 수 있으나, 활성 운영 (매일 data 누적) 워크스페이스가 표준 부재 상태로 *반복 audit drift* 발생 — 표준화로 전환.

### 결정

ai-nodes 표준 구조 적용 시리즈 시작. 3 plan 분할:

1. **plan001 (본 plan)**: docs 영역. 5문서 신설 + AGENTS.md 한글화 + CLAUDE.md 심링크 + tasks/. decisions/* 7개는 *5문서로 재분배 후 plan003에서 폐기*.
2. **plan002**: ADR-006 분리 패턴 마이그. `skills/<name>/scripts/` → `scripts/<name>/` + `.claude/skills/<name>/{SKILL.md, references/}`. 3 skill 모두.
3. **plan003**: decisions/* 7 파일 git rm + workspace-structure.md 매트릭스 stock-investment ?→✓ 갱신 + .env 도입.

**거절한 대안**:

- 의도된 비대칭 공식화 ADR — 활성 운영 + audit drift 누적 상태에서 비표준 유지 비용 > 표준화 비용.
- 단일 큰 plan — 4-5 phase 한 번에 처리. rollback 복잡 + cron 영향 phase 안에 섞임. 시리즈가 안전.
- decisions/* 그대로 유지 + adr.md만 신규 — ai-nodes ADR-018 (개별 ADR 파일 신설 금지) 위반.

### 결과

- 워크스페이스 5문서 활성화 — drift 추적 단일 출처.
- Claude Code 자동 로드 → `claude -p "/<skill>"` 진입점 (plan002 후).
- ai-nodes/docs/workspace-structure.md 매트릭스에서 stock-investment ✓ (plan003 완료 후).
- 향후 plan 사이클 (`tasks/plan{N}-<slug>/`) 운영 가능.
- cron 운영 중단 없음 — plan001은 docs only. plan002 분리 마이그 시 cron 호출 path 갱신 필요 (별도 plan에서 결정).

**적용**: plan001 (5문서 + AGENTS) → plan002 (분리 패턴) → plan003 (decisions/ 폐기 + workspace-structure ✓).
```

## 성공 기준

```bash
cd "$(git rev-parse --show-toplevel)"

# 1. 5문서 모두 존재 + 비어있지 않음
for f in prd data-schema flow code-architecture adr; do
  test -s "stock-investment/docs/$f.md" || (echo "FAIL: stock-investment/docs/$f.md 부재 또는 빈 파일" && exit 1)
done
echo "[5문서 존재] OK"

# 2. 각 문서 최소 본문 라인 (50+ 라인 기대)
for f in prd data-schema flow code-architecture adr; do
  LINES=$(wc -l < "stock-investment/docs/$f.md")
  test "$LINES" -ge 30 || (echo "FAIL: stock-investment/docs/$f.md 만 $LINES 라인 — 부실" && exit 1)
done
echo "[최소 본문 라인] OK"

# 3. adr.md ADR-001 본문 + Quick Index 존재
grep -q "^## ADR-001" stock-investment/docs/adr.md
grep -q "Quick Index" stock-investment/docs/adr.md
echo "[ADR-001 + Quick Index] OK"

# 4. prd.md MVP 타깃 (CRCL, BTC, GOOGL, QQQ) 명시 — 핵심 키워드 grep
grep -q "CRCL\|Circle" stock-investment/docs/prd.md
grep -q "Bitcoin\|BTC" stock-investment/docs/prd.md
echo "[prd 핵심 타깃 명시] OK"

# 5. data-schema.md 6 config 모두 명시
for c in catalysts current-issues daily-stock-universe sources theme-reports watchlist; do
  grep -q "$c.json" stock-investment/docs/data-schema.md || (echo "FAIL: data-schema $c.json 명세 누락" && exit 1)
done
echo "[6 config 명세] OK"

# 6. flow.md 3 skill 모두 명시
for s in stock-investing-morning-brief current-issue-analysis daily-stock-analysis-note; do
  grep -q "$s" stock-investment/docs/flow.md || (echo "FAIL: flow $s 누락" && exit 1)
done
echo "[3 skill flow] OK"

# 7. code-architecture.md 외부 의존성 (track_task.sh + extract_claude_result.ts) 명시
grep -q "track_task.sh" stock-investment/docs/code-architecture.md
grep -q "extract_claude_result.ts" stock-investment/docs/code-architecture.md
echo "[외부 의존성] OK"

# 8. docs-style 정합 검증 — § 사용 0
! grep -n "§" stock-investment/docs/*.md
echo "[section mark 사용 0] OK"
```

## 금지 사항

- 기존 파일 수정 (decisions/* / AGENTS.md / SKILL.md / scripts/*.sh / config/*.json).
- decisions/* git rm — plan003 책임.
- AGENTS.md / CLAUDE.md / tasks/ — phase-02 책임.
- skill 분리 패턴 마이그 — plan002 책임.
- 신규 ADR (ADR-002+) — 본 plan은 ADR-001만 신설.
- section mark (U+00A7) 문자 직접 입력 (5문서 본문 + 본 phase 산출 둘 다).

## commit

```bash
cd "$(git rev-parse --show-toplevel)"

git add stock-investment/docs/prd.md stock-investment/docs/data-schema.md stock-investment/docs/flow.md stock-investment/docs/code-architecture.md stock-investment/docs/adr.md

git status --porcelain | grep -E "^(A|M|D|R) " | head
# 의도 외 staged 파일 0 — cross-session race 회피.

git commit -m "docs(stock-investment): 5문서 신설 — decisions/* 7 ADR 재분배 (plan001 phase-01)

ai-nodes 표준 5문서 (prd/data-schema/flow/code-architecture/adr) 신설:
- prd.md: 워크스페이스 목적 + MVP 타깃 (CRCL/BTC/GOOGL/QQQ/AI 반도체) + 3 skill 기능 표 + 미연결 항목
- data-schema.md: 6 config json + data/ 산출물 + logs/ + .env 스키마
- flow.md: 3 skill 데이터 흐름 (수집 → Claude → extract → Discord/git push)
- code-architecture.md: 디렉터리 트리 + 외부 의존성 + 분리 패턴 plan002 대기 표기
- adr.md: Quick Index + ADR-001 (워크스페이스 표준 적용 시작, plan001~003 시리즈)

decisions/* 7개는 plan003에서 폐기 예정 — 자료는 5문서로 재분배 완료.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

push 없음 (phase-03 책임).

## PHASE_BLOCKED / PHASE_FAILED 조건

- 5문서 중 1개 이상 부재 (성공 기준 1) — `PHASE_FAILED: docs 신설 누락`.
- 본문 부실 (성공 기준 2, 30 라인 미만) — `PHASE_FAILED: docs 부실 — 재작성 필요`.
- decisions/* 자료를 *그대로 복사*만 한 경우 — *재분배 의미*가 없음. `PHASE_FAILED: 의미 재분배 검토 필요`.
- 의도 외 staged 파일 — `PHASE_BLOCKED: cross-session stage race`.
- section mark 직접 사용 발견 (성공 기준 8) — `PHASE_FAILED: docs-style 위반`.
