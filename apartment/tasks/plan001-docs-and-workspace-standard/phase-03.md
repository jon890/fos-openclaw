# Phase 03 — ai-nodes 메타 (workspace-structure + AGENTS /init 보강 + ADR-004 + career-os Status 격상)

**Model**: sonnet
**Status**: pending

---

## 목표

ai-nodes 모노레포 레벨의 워크스페이스 표준 정식화 — `workspace-structure.md` 신설 + `ai-nodes/AGENTS.md` /init 식 보강 + `ai-nodes/docs/adr.md` ADR-004 append (격상 표기) + `career-os/docs/adr.md` ADR-018/021 Status 격상 표기.

**범위 외**: apartment 자체 docs (phase-01/02 완료), 잔여 참조 (phase-04), 통합 검증 + push (phase-05).

---

## 본 phase 강제 주의문

- 반드시 Write/Edit 도구로 파일을 생성·수정해야 한다. prose 응답만으로는 PHASE_FAILED (common-pitfalls 6-6).
- 작성·수정하는 모든 문서에 section sigil (section mark, U+00A7) 특수문자 사용 금지.
- ADR Quick Index ↔ 본문 동기 유지 — ADR-004 append 시 Quick Index 행도 같이 추가.
- 본 phase 종료 시 commit 개수 self-check = 1.

---

## 관련 docs

- career-os ADR-018 (docs/ 운영 정책: 5문서 + adr.md 단일 누적)
- career-os ADR-019 (scripts/ 분리 — 의도된 비대칭)
- career-os ADR-021 (Discord 알림 openclaw 경유 + 워크스페이스 .env 격리)
- career-os AGENTS.md (5문서 라우팅 모범 사례, 132줄)
- ai-nodes/docs/adr.md ADR-001/002/003 (모노레포 기존 ADR)

---

## 작업 항목

### 1. ai-nodes/docs/workspace-structure.md 신설

`Write` 도구로 신설. 약 150-200줄.

섹션 구조:

1. 헤더 — 모든 워크스페이스 표준 구조 정식 명세 + ai-nodes ADR-004 결정 근거 링크
2. 워크스페이스 정의 — 격리 원칙 + 현재 4 워크스페이스 (apartment / career-os / stock-investment / travel)
3. 표준 디렉터리 트리 — code block (약 30줄). AGENTS.md / CLAUDE.md 심링크 / .env / .env.example / config/ / docs/ 5문서 / skills/<name>/{SKILL.md, references/, scripts/} / .claude/skills/<name>/ / tasks/plan{N}-<kebab-slug>/ / data/ (gitignored) / logs/ (gitignored).
4. AGENTS.md / CLAUDE.md 심링크 명세 — `ln -s AGENTS.md CLAUDE.md` 명령 + Claude Code 자동 로드 목적.
5. docs/ 5문서 컨벤션 — 표 (`| 번호 | 문서 | 책임 |`):
   - 1: prd.md (제품 범위 / MVP 타깃 / 기능 표 / 운영 정책 / 성공 기준 / 미연결 항목)
   - 2: data-schema.md (config / data / logs / .env 스키마)
   - 3: flow.md (명령별 데이터 흐름)
   - 4: code-architecture.md (디렉터리 트리 / skill 표준 / 외부 의존성 / Runner 패턴)
   - 5: adr.md (워크스페이스 한정 ADR 누적, 개별 파일 신설 금지)
6. tasks/plan{N}-<slug>/ 컨벤션 — 워크스페이스별 독립 번호 / kebab-case slug / index.json + phase-NN.md / 완료 후 history 보존 / draft/ 옵션 (common-pitfalls 6-6 방어용).
7. skills/ 컨벤션 — `skills/<name>/{SKILL.md, references/, scripts/}` 통합 + native skill 등록 (`.claude/skills/<name>/SKILL.md`) 우선.
8. .env 비밀 정보 — 워크스페이스 root 격리 (`.env` gitignored, `.env.example` git tracked). 키별 워크스페이스 격리, ai-nodes 루트 `.env` 생성 금지.
9. 의도된 비대칭 (예외) — 표 (워크스페이스 / 비대칭 / 근거):
   - career-os: `scripts/<name>/` 별도 + `.claude/skills/<name>/` 분리 / career-os adr.md ADR-019
   - apartment: 없음 (표준 따름)
   - stock-investment: TODO 별도 audit
   - travel: TODO 별도 audit
10. 현재 워크스페이스 준수도 매트릭스 — 2026-05-18 기준 표 (4 워크스페이스 × 7 항목):
    - AGENTS.md / CLAUDE.md 심링크
    - docs/ 5문서
    - tasks/plan{N}/ 영역
    - skills/<name>/scripts/ 통합 (career-os 비대칭)
    - .claude/skills/ native 등록
    - .env (workspace root)
    - data/ vs docs/ 분리
11. 새 워크스페이스 추가 체크리스트 — bash mkdir + AGENTS / CLAUDE / 5문서 / config/ / .env.example placeholder + 체크리스트 8개.
12. 참조 — ai-nodes/docs/adr.md ADR-004 / skills/planning/SKILL.md / skills/plan-and-build/.

### 2. ai-nodes/AGENTS.md /init 식 보강

`Edit` 도구로 4 위치 보강. 기존 148줄 + 50줄 추정.

#### 2-1. 1번 저장소 구조 — `공용 영역` 불릿에 workspace-structure.md 진입 추가

기존 본문 line 25:

```
- `docs/` — ai-nodes 모노레포 레벨 ADR (워크스페이스 간 공통 정책). 워크스페이스 한정 결정은 `<workspace>/docs/adr.md`.
```

다음으로 갱신:

```
- `docs/` — ai-nodes 모노레포 레벨 ADR + 워크스페이스 표준 청사진 (`docs/workspace-structure.md` 신설, plan001 — 새 워크스페이스 추가 진입점). 워크스페이스 한정 결정은 `<workspace>/docs/adr.md`.
```

#### 2-2. 3번 워크스페이스 진입점 끝에 새 3-4 추가

기존 `### 3-3. stock-investment / travel` 본문 끝(`참조. 본 모노레포 진입점은 그곳에 정의.` 줄) 다음에 추가:

```

### 3-4. 새 워크스페이스 추가

`ai-nodes/docs/workspace-structure.md` 11번 체크리스트 참조. mkdir + AGENTS.md + CLAUDE.md 심링크 + 5문서 placeholder + tasks/ + config/ + .env.example. 첫 plan은 5문서 본문 작성 + ADR-001 자리.
```

#### 2-3. 9번 외부 의존성에 Bun runtime 라인 보강 + Python / agent-browser 명시

기존 본문 line 143:

```
- Bun runtime — TS 헬퍼 실행. `bun` 명령 + npm install로 node_modules 보유.
```

다음으로 갱신:

```
- Bun runtime — TS 헬퍼 실행. 설치 후 ai-nodes 루트에서 `bun install` 1회 (root package.json: zod, fast-xml-parser, dotenv + @types/bun).
- Python 3 — `_shared/bin/extract_claude_result.py` + apartment Python collector 6개. 기본 stdlib만 사용 (외부 pip 의존 없음).
- `agent-browser` CLI — JS-heavy 페이지(Naver Land 등) 수집. 로컬 설치 필수 (apartment ADR-001).
```

#### 2-4. 10번 참고 문서 보강

기존 본문 10번 섹션 전체 (line 146-152) 다음으로 갱신:

```
## 10. 참고 문서

- 워크스페이스 표준 청사진: `docs/workspace-structure.md` (새 워크스페이스 추가 진입점).
- 모노레포 ADR: `docs/adr.md` (ADR-001~004 누적).
- 워크스페이스별 상세: `<workspace>/AGENTS.md`.
- career-os 5문서: `career-os/docs/{prd, data-schema, flow, code-architecture, adr}.md`.
- apartment 5문서: `apartment/docs/{prd, data-schema, flow, code-architecture, adr}.md` (plan001 신설).
- planning skill: `skills/planning/SKILL.md` (8단계 워크플로 + 5문서 공통 작성 원칙).
- plan-and-build skill: `skills/plan-and-build/` (자동 phase 실행 + common-pitfalls 축적).
- workspace-audit skill: `skills/workspace-audit/SKILL.md` (워크스페이스 건전성 감사).
- docs-check skill: `skills/docs-check/SKILL.md` (5문서 + ADR 건전성 감사).
```

### 3. ai-nodes/docs/adr.md ADR-004 append

먼저 본문 마지막 ADR (ADR-003) 위치 확인:

```bash
grep -n "^## ADR-" ai-nodes/docs/adr.md
```

ADR-003 본문 끝 다음에 `Edit` 도구로 ADR-004 append. 본문 약 50줄.

본문:

```markdown


---

## ADR-004 — 워크스페이스 표준 구조 정식화

- Status: Accepted
- Date: 2026-05-18

### 맥락

career-os와 apartment 두 워크스페이스가 5문서 컨벤션 + AGENTS.md/CLAUDE.md 심링크 + tasks/plan{N}-<slug>/ 영역 + .env 워크스페이스 root + docs vs data 분리 패턴으로 수렴. 다른 워크스페이스(stock-investment, travel) 신규 추가 시 동일 청사진 필요.

기존 워크스페이스 정책 분산:

- career-os ADR-018: docs/ 운영 정책 (5문서 + adr.md 단일 누적). 워크스페이스 한정 결정.
- career-os ADR-021: Discord 알림 openclaw 경유 + .env 워크스페이스 root 격리. 워크스페이스 한정 결정.
- career-os ADR-019: scripts/ 분리. 워크스페이스 한정 예외로 보존.

분산된 워크스페이스 ADR 중 모든 워크스페이스 공통 적용 부분은 모노레포 레벨로 격상 필요.

### 결정

ai-nodes 모노레포의 워크스페이스 표준 구조를 `ai-nodes/docs/workspace-structure.md`에 정식화. 본 문서가 현재 구조 단일 출처, ADR-004는 결정의 *왜* 책임.

표준 내용:

1. 디렉터리 트리 — AGENTS.md / CLAUDE.md 심링크 / .env / .env.example / config/ / docs/ 5문서 / skills/<name>/{SKILL.md, references/, scripts/} / .claude/skills/<name>/ / tasks/plan{N}-<slug>/ / data/ / logs/.
2. AGENTS.md + CLAUDE.md 심링크 — Claude Code 자동 로드.
3. docs/ 5문서 — prd / data-schema / flow / code-architecture / adr.md. ADR 누적 (개별 파일 신설 금지).
4. .env 워크스페이스 root + .env.example 템플릿 — 워크스페이스별 격리.
5. tasks/plan{N}-<kebab-slug>/ — planning + plan-and-build 영구 보관.
6. skills/<name>/ 통합 구조 + native skill 우선 등록.

career-os ADR-018 (docs/ 운영 정책) / ADR-021 (.env 워크스페이스 root 부분)을 본 ADR-004로 모노레포 격상. career-os ADR 본문 Status 라인에 `Lifted to ai-nodes ADR-004 (2026-05-18)` 표기.

거절한 대안:

- 워크스페이스별 독립 ADR 유지 (격상 안 함) — 같은 결정이 4 워크스페이스 ADR에 중복 표기 → drift 위험.
- 단일 거대 ADR 대신 디렉터리·5문서·.env·docs vs data·tasks/plan 별 분리 ADR — 새 워크스페이스 추가 시 N개 ADR 동시 적용. UX 나쁨.

### 결과

- 새 워크스페이스 추가 시 `workspace-structure.md` 청사진만 따르면 됨. ADR-004는 청사진 정당화.
- career-os ADR-018/021의 공통 적용 부분은 ADR-004로 격상. 워크스페이스 한정 부분 (career-os ADR-019 scripts/ 분리, ADR-021 Discord openclaw 부분)은 워크스페이스 ADR에 남음.
- workspace-structure.md 10번 매트릭스로 각 워크스페이스 표준 준수도 추적.
- 의도된 비대칭 (career-os ADR-019)도 명시되어 표준 이탈 결정 자체로 가시화.

### 적용

- `ai-nodes/docs/workspace-structure.md` (신설, 본 ADR의 적용 청사진)
- `ai-nodes/AGENTS.md` 1번 / 3-4 / 9번 / 10번 갱신
- `career-os/docs/adr.md` ADR-018 / ADR-021 Status 라인 격상 표기
- apartment 워크스페이스가 plan001에서 본 표준의 적용 첫 사례 (career-os는 plan023까지 진행으로 이미 표준 준수)
```

ADR-004 append 후 ai-nodes/docs/adr.md 상단에 Quick Index가 있는지 확인:

```bash
grep -n "Quick Index\|^| ADR" ai-nodes/docs/adr.md | head -10
```

Quick Index가 있으면 ADR-004 행 추가:

```
| ADR-004 | 워크스페이스 표준 구조 정식화 | Accepted | 5문서 + .env workspace root + tasks/plan + skills/<name>/ 통합 + AGENTS 심링크 표준화, career-os ADR-018/021 격상 |
```

Quick Index 부재 시 append만 (별도 cleanup으로 추후 Quick Index 도입).

### 4. career-os/docs/adr.md ADR-018 / ADR-021 Status 격상

먼저 본문 위치 확인:

```bash
grep -n "^## ADR-018\|^## ADR-021" career-os/docs/adr.md
grep -n "^- Status:" career-os/docs/adr.md | head -25
```

#### 4-1. ADR-018 Status 라인 갱신

`Edit` 도구로 ADR-018 본문 Status 라인 갱신. 현재 본문에 `Partially superseded by ADR-032 (2026-05-17)` 표기되어 있음.

old:

```
- Status: Partially superseded by ADR-032 (2026-05-17)
```

new:

```
- Status: Partially superseded by ADR-032 (2026-05-17) — 5문서 + docs/data 분리 부분은 ai-nodes ADR-004 (2026-05-18)로 모노레포 격상 (Lifted)
```

#### 4-2. ADR-021 Status 라인 갱신

ADR-021 본문 Status 라인 갱신. (Status가 `Accepted`일 가능성 — 정확한 본문 확인 후 갱신.)

old (예상):

```
- Status: Accepted
```

new:

```
- Status: Lifted to ai-nodes ADR-004 (2026-05-18) — .env 워크스페이스 root 격리 부분. Discord 알림 openclaw 부분은 career-os 한정 유지.
```

(만약 본문 Status 표기가 다르면 그 표현 보존 + `, Lifted to ai-nodes ADR-004` 추가.)

#### 4-3. career-os/docs/adr.md Quick Index 동기

career-os/docs/adr.md 상단 Quick Index 표 (ADR-018/021 행)의 Status 컬럼을 위와 동일 형태로 갱신.

```bash
grep -n "^| ADR-018\|^| ADR-021" career-os/docs/adr.md
```

해당 행의 Status 컬럼만 `Edit`으로 갱신.

### 5. commit 생성

```bash
git add ai-nodes/docs/workspace-structure.md ai-nodes/docs/adr.md ai-nodes/AGENTS.md career-os/docs/adr.md
git commit -m "$(cat <<'EOF'
docs(ai-nodes, career-os): 워크스페이스 표준 정식화 + ADR-004 격상 (plan001 phase-03)

ai-nodes 메타:
- ai-nodes/docs/workspace-structure.md 신설 — 모든 워크스페이스 표준 구조 청사진 (디렉터리 트리 + 5문서 + tasks/ + 의도된 비대칭 + 준수도 매트릭스 + 새 워크스페이스 체크리스트)
- ai-nodes/docs/adr.md ADR-004 append — 워크스페이스 표준 구조 정식화 + 격상 표기
- ai-nodes/AGENTS.md /init 식 보강 — 1번 (workspace-structure.md 링크), 3-4 (새 워크스페이스 추가 절차), 9번 (Bun/Python/agent-browser 보강), 10번 (참고 문서)

career-os 격상:
- career-os/docs/adr.md ADR-018 Status: 본문 일부 ai-nodes ADR-004로 격상 (5문서 + docs/data 분리)
- career-os/docs/adr.md ADR-021 Status: .env 부분 ai-nodes ADR-004로 격상, Discord 부분 career-os 한정 유지
- Quick Index 동기

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## 검증

```bash
SIGIL_CHAR=$(printf '\xc2\xa7')

# 1. workspace-structure.md 신설 + 분량
test -f ai-nodes/docs/workspace-structure.md || { echo "PHASE_FAILED: workspace-structure.md absent"; exit 1; }
LINES=$(wc -l < ai-nodes/docs/workspace-structure.md)
echo "[workspace-structure.md] $LINES lines"
[ "$LINES" -ge 120 ] || { echo "PHASE_FAILED: workspace-structure.md $LINES < 120 lines"; exit 1; }

# 2. ADR-004 본문 존재
grep -q "^## ADR-004" ai-nodes/docs/adr.md || { echo "PHASE_FAILED: ai-nodes ADR-004 누락"; exit 1; }
echo "[ai-nodes ADR-004] OK"

# 3. career-os Status 격상
grep -q "Lifted to ai-nodes ADR-004" career-os/docs/adr.md || { echo "PHASE_FAILED: career-os Status 격상 누락"; exit 1; }
echo "[career-os Status 격상] OK"

# 4. ai-nodes/AGENTS.md workspace-structure 링크
grep -q "workspace-structure.md" ai-nodes/AGENTS.md || { echo "PHASE_FAILED: AGENTS.md workspace-structure 링크 누락"; exit 1; }
echo "[AGENTS.md 보강] OK"

# 5. section sigil 미사용 검증
for f in ai-nodes/docs/workspace-structure.md ai-nodes/docs/adr.md ai-nodes/AGENTS.md career-os/docs/adr.md; do
  COUNT=$(grep -c "$SIGIL_CHAR" "$f" 2>/dev/null || echo 0)
  [ "$COUNT" -eq 0 ] || { echo "PHASE_FAILED: $f sigil 잔재 $COUNT"; exit 1; }
done
echo "[sigil check] 0건"

# 6. 준수도 매트릭스 + 의도된 비대칭 표 존재
grep -q "준수도 매트릭스\|준수도" ai-nodes/docs/workspace-structure.md || { echo "PHASE_FAILED: 준수도 매트릭스 누락"; exit 1; }
grep -q "ADR-019" ai-nodes/docs/workspace-structure.md || { echo "PHASE_FAILED: ADR-019 비대칭 인용 누락"; exit 1; }
echo "[매트릭스 + 비대칭] OK"

# 7. commit 개수 self-check
COMMITS=$(git log --format='%H' HEAD~1..HEAD | wc -l)
echo "[commit count] $COMMITS"
[ "$COMMITS" -eq 1 ] || { echo "PHASE_FAILED: phase commit $COMMITS != 1"; exit 1; }

echo "✓ Phase 03 검증 통과"
```

---

## 의도 메모

- ADR-004는 결정의 *왜*, workspace-structure.md는 *현재 구조*. 책임 분리 (single source 원칙).
- career-os ADR-018/021 격상 — Partially / Lifted 표기. 워크스페이스 한정 부분 (Discord openclaw, learn/ 영역 폐기 등) 은 career-os 보존.
- 격상은 기존 결정 부정 아님 — 같은 결정의 모노레포 정식화. drift 방지.
- workspace-structure.md 10번 준수도 매트릭스 = 향후 audit 단일 출처. stock-investment / travel은 TODO audit로 보존.
- AGENTS.md /init 보강은 최소 침습 — 1번 / 3-4 / 9번 / 10번 4 위치만. 큰 재구성 안 함.
