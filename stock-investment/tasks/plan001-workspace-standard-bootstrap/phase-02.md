# Phase 2 — AGENTS.md 한글화 + 5문서 라우팅 + CLAUDE.md 심링크 + tasks/ + .env.example

stock-investment plan001 phase-02. AGENTS.md를 한글화 + 5문서 라우팅 표 추가 + CLAUDE.md 심링크 + tasks/ 디렉터리 + .env.example placeholder.

본 phase는 phase-01 산출 (5문서 신설) 후 *워크스페이스 진입점·인프라* 정합화. skill / config / data 변경 0.

## 작업 위치 (cwd 정책)

run-phases.py가 본 phase를 `cwd=stock-investment/` (워크스페이스)로 실행. 첫 bash 블록:

```bash
cd "$(git rev-parse --show-toplevel)"
```

이후 path는 `stock-investment/...` 형식.

## 관련 docs (먼저 읽기)

- `stock-investment/docs/{prd,data-schema,flow,code-architecture,adr}.md` (phase-01 신설) — 라우팅 표 작성용.
- `apartment/AGENTS.md` + `career-os/AGENTS.md` — 한글화 + 라우팅 표 + 외부 의존성 섹션 패턴.
- `ai-nodes/AGENTS.md` (모노레포 진입점) — stock-investment 진입점 라우팅 참조.
- `stock-investment/AGENTS.md` (현재 영문) — 변경 대상.

## 변경할 파일

수정:

- `stock-investment/AGENTS.md` (영문 → 한글 + 라우팅 + 외부 의존성 섹션 보강)

신설:

- `stock-investment/CLAUDE.md` (AGENTS.md 심링크)
- `stock-investment/tasks/.gitkeep` (디렉터리 마커)
- `stock-investment/.env.example` (template)

본 phase에서 *5문서 수정 금지* (phase-01 산출 보존). *skill / config / data 변경 금지*.

## 명세

### 1. AGENTS.md 한글화 + 구조 변경

기존 영문 26 라인 → 한글 표준 구조로 재작성. apartment/AGENTS.md (단순 패턴) 또는 career-os/AGENTS.md (복잡 패턴) 참고. stock-investment는 *중간 크기*라 apartment 패턴 적합.

새 AGENTS.md 골격:

```markdown
# AGENTS.md — stock-investment 워크스페이스

`~/ai-nodes` 아래 독립 작업 워크스페이스. 모든 에이전트(Claude / Codex / Gemini 등)를 위한 정식 가이드 진입점. `CLAUDE.md`는 이 파일의 심볼릭 링크.

상세 결정·스키마·흐름은 `docs/` 5문서에 분리. 이 파일은 진입점·운영 원칙만 담는다.

## 1. 5문서 라우팅

| 문서 | 무엇이 들어 있는지 | 언제 보는지 |
|---|---|---|
| `docs/prd.md` | 제품 범위·MVP 타깃·기능 표·미연결 항목 | 새 기능 추가 / 우선순위 |
| `docs/data-schema.md` | config (6 json) / data / logs / .env 스키마 | 데이터 파일 변경 |
| `docs/flow.md` | 3 skill 데이터 흐름 (수집→Claude→Discord/git) | 흐름 추가 / 디버깅 |
| `docs/code-architecture.md` | 디렉터리 트리·skill 표준·외부 의존 | 코드 구조 변경 |
| `docs/adr.md` | stock-investment 한정 ADR 누적 (현재 ADR-001). 모노레포 레벨: `../docs/adr.md` | 결정의 *왜* |

## 2. tasks/ 영역

planning + plan-and-build 스킬로 운영. 형태: `tasks/plan{N}-<slug>/`.
완료된 plan도 history 보존.

## 3. 목적

주식·암호화폐 모닝 브리핑 + 일일 분석 자동화 (단일 사용자).

## 4. 현재 타깃

CRCL (Circle) + BTC + GOOGL/GOOG + QQQ + AI 반도체/인프라. 상세는 `docs/prd.md` 2번·4번.

## 5. 워크플로 진입점

3 skill — 현재는 *옛 통합 패턴* (`skills/<name>/scripts/*.sh`). plan002 후 *분리 패턴* (`scripts/<name>/` + `.claude/skills/<name>/`) + native skill 진입점:

```bash
# 현재 (plan001 시점)
bash stock-investment/skills/stock-investing-morning-brief/scripts/run_report.sh
bash stock-investment/skills/current-issue-analysis/scripts/run_issue_report.sh
bash stock-investment/skills/daily-stock-analysis-note/scripts/run_daily_note.sh

# plan002 후 (계획)
claude -p "/stock-investing-morning-brief"
claude -p "/current-issue-analysis"
claude -p "/daily-stock-analysis-note"
```

## 6. 외부 의존성

- `_shared/bin/track_task.sh` — 모든 runner self-wrap. **load-bearing**.
- `_shared/lib/extract_claude_result.ts` — claude JSON envelope 파싱 (ai-nodes plan001 통합).
- `claude` CLI — 모든 Claude 호출 의존.
- `career-os/sources/fos-study` — daily-stock-analysis-note만 발행 대상 (cross-workspace 예외, 발행 git repo).

상세는 `docs/code-architecture.md` 외부 의존성 섹션.

## 7. 운영 원칙

- 실시간 거래 / 실 자동화 금지 — 모니터링·브리핑 자동화 한정.
- 광범위 풀-리포 분석 금지 — config json 명시 큐 한정.
- 재무 자문 아님 — 불확실성 명시.
- 수집 데이터·해석 분리 — config / data / docs 책임 분리.
- 모닝 Discord 메시지는 간결 — 상세 자산은 `data/YYYY-MM-DD/`.
- 영구 자산은 워크스페이스 내부 (`~/.openclaw/workspace` 사용 안 함).

## 8. 규칙

- 다른 워크스페이스 (apartment, career-os, travel) 격리 — 교차 참조 금지 (단 career-os/sources/fos-study 발행 예외).
- 재실행 가능 + 날짜 단위 멱등.
- 불확실성 명시 — 검증된 사실 + 해석 분리.
- 새 결정은 `docs/adr.md` 누적 (개별 ADR 파일 신설 금지, ai-nodes ADR-018).
- 비밀 정보 (`DISCORD_CHANNEL_ID`)는 `.env` (워크스페이스 root, ADR-021 예정 — plan003에서 실 .env 도입).
```

내용 보존 의무 (현재 AGENTS.md 영문에서 가져올 항목):
- "Daily stock/crypto investment monitoring and morning briefing automation" → 3. 목적
- "Initial focus: CRCL, BTC. Planned: Nasdaq, QQQ, Google, crypto-adjacent" → 4. 현재 타깃 (확장 표기)
- "Keep this task reusable and isolated" → 8. 규칙
- "Prefer storing durable assets here, not in ~/.openclaw/workspace" → 7. 운영 원칙
- "Be explicit about uncertainty; this is not financial advice" → 7. 운영 원칙
- "Separate verified facts/data from interpretation" → 8. 규칙

### 2. CLAUDE.md 심링크

```bash
cd "$(git rev-parse --show-toplevel)"
cd stock-investment
ln -sf AGENTS.md CLAUDE.md
cd "$(git rev-parse --show-toplevel)"

# 검증
test -L stock-investment/CLAUDE.md && readlink stock-investment/CLAUDE.md | grep -q "^AGENTS.md$"
```

### 3. tasks/ 디렉터리 (.gitkeep)

plan001 task 디렉터리가 이미 `tasks/plan001-workspace-standard-bootstrap/`에 존재하므로 `tasks/` 자체는 이미 생성. 단 *비어있는 tasks/* 케이스 대비 `.gitkeep` 추가 불필요 — 본 phase는 *기존 tasks/* 유지만.

대신 tasks/ 명시화: AGENTS.md에 "2. tasks/ 영역" 섹션이 포함되어 있어 처리 완료.

### 4. .env.example placeholder

```bash
cat > stock-investment/.env.example <<'EOF'
# stock-investment 워크스페이스 환경 변수 template.
# 실 .env는 워크스페이스 root에 위치 (ai-nodes ADR-021 예정).
# plan001 시점에는 placeholder만 — 실 도입은 plan003.

# Discord 알림 (openclaw message send 경유)
DISCORD_CHANNEL_ID=
# 예: 주식토크 채널 id

# 타임존 — 현재 run_daily_note.sh L14 하드코드. plan002/003에서 .env로 끌어올림 검토.
TZ=Asia/Seoul
EOF
```

## 성공 기준

```bash
cd "$(git rev-parse --show-toplevel)"

# 1. AGENTS.md 한글화 + 5문서 라우팅 + 외부 의존성 섹션
grep -q "## 1. 5문서 라우팅" stock-investment/AGENTS.md
grep -q "## 6. 외부 의존성" stock-investment/AGENTS.md
grep -q "track_task.sh" stock-investment/AGENTS.md
grep -q "extract_claude_result.ts" stock-investment/AGENTS.md

# 2. 한글 영역 비율 충분 (영문만 26 라인 → 한글 표준 + 비율)
HANGUL_LINES=$(grep -cP "[가-힣]" stock-investment/AGENTS.md)
test "$HANGUL_LINES" -ge 20 || (echo "FAIL: AGENTS.md 한글화 부실 — $HANGUL_LINES 라인" && exit 1)

# 3. CLAUDE.md 심링크 존재 + 정확한 타깃
test -L stock-investment/CLAUDE.md
readlink stock-investment/CLAUDE.md | grep -q "^AGENTS.md$"

# 4. tasks/ 디렉터리 존재 (이미 plan001 디렉터리로 생성됨)
test -d stock-investment/tasks/plan001-workspace-standard-bootstrap

# 5. .env.example 존재 + DISCORD_CHANNEL_ID + TZ 명시
test -f stock-investment/.env.example
grep -q "^DISCORD_CHANNEL_ID=" stock-investment/.env.example
grep -q "^TZ=Asia/Seoul" stock-investment/.env.example

# 6. AGENTS.md 영문 잔존 0 (기존 영문 키워드 검증)
! grep -q "^# AGENTS.md - stock-investment task workspace$" stock-investment/AGENTS.md
! grep -q "^## Purpose$" stock-investment/AGENTS.md  # 옛 영문 섹션 헤더 제거됨

echo "✓ Phase 02 통과"
```

## 금지 사항

- 5문서 수정 (phase-01 산출 보존).
- skill / config / data / scripts 변경.
- ADR 본문 수정 — adr.md ADR-001은 phase-01 산출.
- 다른 워크스페이스 파일 수정.
- amend / force push.
- section mark (U+00A7) 직접 입력 (AGENTS.md 본문 + 본 phase 산출 둘 다).

## commit

```bash
cd "$(git rev-parse --show-toplevel)"

git add stock-investment/AGENTS.md stock-investment/CLAUDE.md stock-investment/.env.example

git status --porcelain | grep -E "^(A|M|D|R) " | head
# 의도 외 staged 파일 0 — cross-session race 회피.

git commit -m "docs(stock-investment): AGENTS.md 한글화 + CLAUDE 심링크 + .env.example (plan001 phase-02)

- AGENTS.md: 영문 26줄 → 한글 표준 (5문서 라우팅 + 외부 의존성 + 운영 원칙 섹션)
- CLAUDE.md: AGENTS.md 심링크 (Claude Code 자동 로드 활성화)
- .env.example: DISCORD_CHANNEL_ID + TZ placeholder (실 .env 도입은 plan003)

tasks/ 디렉터리는 plan001 자체로 생성됨 — .gitkeep 불필요.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

push 없음 (phase-03 책임).

## PHASE_BLOCKED / PHASE_FAILED 조건

- AGENTS.md 한글화 부실 (한글 라인 20 미만) — `PHASE_FAILED: 한글화 부실 — 재작성`.
- CLAUDE.md 심링크 타깃 mismatch — `PHASE_FAILED: 심링크 타깃 점검`.
- 5문서 라우팅 섹션 누락 — `PHASE_FAILED: 라우팅 표 부재`.
- 의도 외 staged 파일 — `PHASE_BLOCKED: cross-session stage race`.
- section mark 직접 사용 발견 — `PHASE_FAILED: docs-style 위반`.
