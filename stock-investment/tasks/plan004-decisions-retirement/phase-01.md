# Phase 1 — decisions/* git rm + adr.md/code-architecture 정정 + workspace-structure 매트릭스 갱신

stock-investment plan004 phase-01. stock-investment 표준 적용 시리즈 마지막 작업.

## 작업 위치 (cwd 정책)

run-phases.py가 본 phase를 `cwd=stock-investment/` (워크스페이스)로 실행. 첫 bash 블록:

```bash
cd "$(git rev-parse --show-toplevel)"
```

## 관련 docs (먼저 읽기)

- `stock-investment/docs/decisions/*` — 7 파일 폐기 대상 (자료는 plan001 phase-01에서 5문서로 재분배 완료).
- `stock-investment/docs/adr.md` L10 / L19 / L52 / L56 / L72 — plan 번호 정정 대상.
- `stock-investment/docs/code-architecture.md` L37 — decisions 트리 라인 갱신.
- `ai-nodes/docs/workspace-structure.md` L159 / L173-179 / L181 — 매트릭스 갱신.

## 변경할 파일

**삭제 (git rm — 7개)**:
- `stock-investment/docs/decisions/001-stock-investing-workspace-and-morning-brief.md`
- `stock-investment/docs/decisions/002-google-nasdaq-first-class-and-issue-analysis.md`
- `stock-investment/docs/decisions/003-ai-semiconductor-infrastructure-monitoring.md`
- `stock-investment/docs/decisions/004-core-theme-report-structure.md`
- `stock-investment/docs/decisions/005-daily-ai-tech-stock-blog-note.md`
- `stock-investment/docs/decisions/006-anthropic-financial-services-reference.md`
- `stock-investment/docs/decisions/007-financial-services-adoption-plan.md`
- (이후 `decisions/` 빈 디렉터리 `rmdir`)

**수정 (Edit)**:
- `stock-investment/docs/adr.md` — History 라인 + Quick Index + ADR-001 본문 plan 번호 정정
- `stock-investment/docs/code-architecture.md` — L37 decisions/ 트리 라인 갱신
- `ai-nodes/docs/workspace-structure.md` — L159 / L173-179 매트릭스 + L181 안내

본 phase에서 *새 파일 생성 금지*. *scripts / config / .env / .claude/skills / AGENTS.md 수정 금지*.

## 명세

### 1. decisions/* 7 파일 git rm

```bash
cd "$(git rev-parse --show-toplevel)"

# 자료가 5문서로 재분배 완료됐는지 sanity 점검 (plan001 phase-01 산출)
for f in 001-stock-investing-workspace-and-morning-brief 002-google-nasdaq-first-class-and-issue-analysis 003-ai-semiconductor-infrastructure-monitoring 004-core-theme-report-structure 005-daily-ai-tech-stock-blog-note 006-anthropic-financial-services-reference 007-financial-services-adoption-plan; do
  test -f "stock-investment/docs/decisions/$f.md" || (echo "PHASE_BLOCKED: $f.md 부재 — git history 점검" && exit 1)
done

git rm stock-investment/docs/decisions/001-stock-investing-workspace-and-morning-brief.md
git rm stock-investment/docs/decisions/002-google-nasdaq-first-class-and-issue-analysis.md
git rm stock-investment/docs/decisions/003-ai-semiconductor-infrastructure-monitoring.md
git rm stock-investment/docs/decisions/004-core-theme-report-structure.md
git rm stock-investment/docs/decisions/005-daily-ai-tech-stock-blog-note.md
git rm stock-investment/docs/decisions/006-anthropic-financial-services-reference.md
git rm stock-investment/docs/decisions/007-financial-services-adoption-plan.md

# 빈 디렉터리 정리
rmdir stock-investment/docs/decisions
```

### 2. stock-investment/docs/adr.md 정정

**L10 History 라인**:

옛:
```
History: 기존 `docs/decisions/001~007.md` 는 plan003에서 폐기 예정.
```

새:
```
History: 기존 `docs/decisions/001~007.md` 는 plan004에서 git rm 완료 — 자료는 plan001 phase-01에서 5문서 (prd/data-schema/flow/code-architecture/adr)로 재분배됨.
```

**L19 Quick Index**:

옛:
```
| ADR-001 | 워크스페이스 ai-nodes 표준 구조 적용 시작 | Accepted | 5문서 + AGENTS 한글화 + CLAUDE 심링크 + tasks/ (plan001). 분리 패턴 + decisions 폐기는 plan002/003 후속 |
```

새:
```
| ADR-001 | 워크스페이스 ai-nodes 표준 구조 적용 시작 | Accepted | 5문서 + AGENTS 한글화 + CLAUDE 심링크 + tasks/ (plan001). 분리 패턴 (plan002) + AGENTS 강화 (plan003) + decisions 폐기 (plan004) 시리즈 완료 |
```

**L52 ADR-001 본문**:

옛:
```
   - `decisions/*` 7개는 5문서로 재분배 후 plan003에서 폐기.
```

새:
```
   - `decisions/*` 7개는 5문서로 재분배 후 plan004에서 git rm 완료.
```

**L56 ADR-001 본문**:

옛:
```
3. **plan003**: `decisions/*` 7 파일 git rm + workspace-structure.md 표 stock-investment 항목 갱신 + .env 도입.
```

새:
```
3. **plan003**: AGENTS.md 강화 (4-1 진실 출처 + 4-2 투자 컨텍스트 + cron 시점 표).
4. **plan004**: `decisions/*` 7 파일 git rm + workspace-structure.md 매트릭스 stock-investment 항목 ?→O 갱신. .env는 plan001 phase-02 시점에 사용자 직접 신설 완료.
```

**L72 ADR-001 본문**:

옛:
```
적용: plan001 (5문서 + AGENTS) → plan002 (분리 패턴) → plan003 (decisions/ 폐기 + workspace-structure 갱신).
```

새:
```
적용: plan001 (5문서 + AGENTS) → plan002 (분리 패턴) → plan003 (AGENTS 강화) → plan004 (decisions/ git rm + workspace-structure ✓).
```

### 3. stock-investment/docs/code-architecture.md L37 갱신

옛:
```
│   └── decisions/                    # 기존 결정 파일 7개 (plan003에서 폐기 예정)
```

새:
```
│   # docs/decisions/ — plan004에서 git rm 완료 (자료는 plan001 phase-01에서 5문서로 재분배됨, history는 git log 참조)
```

### 4. ai-nodes/docs/workspace-structure.md 매트릭스 갱신

**L159 (옛)**:
```
| stock-investment | TODO — 별도 audit 필요 | — |
```

**L159 (새)**:
```
| stock-investment | 적용 완료 (plan001~004) | 본 표준 적용 시리즈 마지막 plan004로 decisions/ 폐기 + 매트릭스 갱신 |
```

**L170 표 — stock-investment 컬럼 모두 ?→O**:

L173-179 컬럼 7개를 모두 ?→O. 표 본문 일괄 Edit 또는 한 행씩:

옛 (각 행):
```
| CLAUDE.md 심링크 | O | O | ? | ? |
| docs/ 5문서 | O | O | ? | ? |
| tasks/plan{N}/ 영역 | O | O | ? | ? |
| skills/ 분리 표준 (ADR-006) | 적용 (plan007) | 적용 (ADR-019 → ADR-006 격상) | ? | ? |
| .claude/skills/ native 등록 | O | O | ? | ? |
| .env (workspace root) | O | O | ? | ? |
| data/ vs docs/ 분리 | O | O | ? | ? |
```

새:
```
| CLAUDE.md 심링크 | O | O | O (plan001) | ? |
| docs/ 5문서 | O | O | O (plan001) | ? |
| tasks/plan{N}/ 영역 | O | O | O (plan001~004) | ? |
| skills/ 분리 표준 (ADR-006) | 적용 (plan007) | 적용 (ADR-019 → ADR-006 격상) | 적용 (plan002) | ? |
| .claude/skills/ native 등록 | O | O | O (plan002) | ? |
| .env (workspace root) | O | O | O | ? |
| data/ vs docs/ 분리 | O | O | O | ? |
```

**L181 (옛)**:
```
stock-investment / travel은 별도 workspace-audit 실행 후 갱신 예정.
```

**L181 (새)**:
```
travel만 별도 workspace-audit 실행 후 갱신 예정. stock-investment는 plan001~004 시리즈로 완료.
```

## 성공 기준

```bash
cd "$(git rev-parse --show-toplevel)"

# 1. decisions/ 부재
test ! -d stock-investment/docs/decisions || (echo "FAIL: decisions/ 잔존" && exit 1)
echo "[decisions/ 폐기] OK"

# 2. adr.md History 라인 갱신
grep -q "plan004에서 git rm 완료" stock-investment/docs/adr.md
! grep -q "plan003에서 폐기 예정" stock-investment/docs/adr.md
echo "[adr.md History] OK"

# 3. adr.md plan003 / plan004 본문 명시
grep -q "plan004: \`decisions/" stock-investment/docs/adr.md
grep -q "plan003.*AGENTS.md 강화\|plan003.*AGENTS 강화" stock-investment/docs/adr.md
echo "[adr.md plan003/004 본문] OK"

# 4. code-architecture.md decisions 트리 갱신
! grep -q "decisions/.*plan003에서 폐기" stock-investment/docs/code-architecture.md
grep -q "decisions/.*plan004" stock-investment/docs/code-architecture.md
echo "[code-architecture decisions 표기] OK"

# 5. workspace-structure.md 매트릭스 stock-investment 7행 모두 O
ALL_O=$(grep -E "^\| (CLAUDE.md 심링크|docs/ 5문서|tasks/plan|skills/ 분리|\.claude/skills/|\.env|data/ vs docs/)" docs/workspace-structure.md | awk -F '|' '{print $4}' | grep -c "O")
test "$ALL_O" -ge 7 || (echo "FAIL: matrix stock-investment 컬럼 O 카운트 $ALL_O (7 기대)" && exit 1)
echo "[매트릭스 stock-investment O] OK"

# 6. workspace-structure L159 stock-investment 적용 완료
grep -q "stock-investment | 적용 완료 (plan001~004)" docs/workspace-structure.md
echo "[L159 적용 완료] OK"

# 7. workspace-structure L181 travel만 남음 표기
grep -q "travel만 별도 workspace-audit" docs/workspace-structure.md
echo "[L181 travel만 잔존] OK"

# 8. scripts / config / .env / .claude/skills / AGENTS.md 변경 0
git diff HEAD --name-only | grep -vE "^stock-investment/docs/(adr|code-architecture)\.md$|^stock-investment/docs/decisions/|^stock-investment/tasks/plan004|^docs/workspace-structure\.md$" && (echo "FAIL: scope creep" && exit 1) || true
echo "[스코프 격리] OK"
```

## 금지 사항

- 새 파일 생성.
- AGENTS.md / 5문서 (prd/data-schema/flow) 수정 — phase-01/02/03 산출 보존.
- scripts / config / .env / .claude/skills 수정.
- ADR 신설.
- ADR 본문 *plan 번호 외 변경*.
- 다른 워크스페이스 (apartment / career-os / travel / health-care) 파일 수정 — workspace-structure.md 모노레포 docs는 *예외 허용* (본 plan 의도).
- ai-nodes/docs/workspace-structure.md *5번째 워크스페이스 (health-care) 행 추가* — 별도 plan 책임.
- amend / force push.
- section mark (U+00A7) 직접 입력.

## commit

```bash
cd "$(git rev-parse --show-toplevel)"

git add stock-investment/docs/adr.md stock-investment/docs/code-architecture.md docs/workspace-structure.md
# decisions/* git rm은 이미 stage됨

git status --porcelain | grep -E "^(A|M|D|R) " | head -15
# 의도 외 staged 파일 0 — cross-session race 회피.

git commit -m "docs(stock-investment, ai-nodes): plan004 decisions/ 폐기 + workspace-structure 매트릭스 ✓ (phase-01)

- stock-investment/docs/decisions/* 7 파일 git rm — 자료는 plan001 phase-01에서 5문서 재분배 완료
- stock-investment/docs/adr.md History / Quick Index / ADR-001 본문 plan 번호 정정 (plan003 → plan004)
- stock-investment/docs/code-architecture.md decisions 트리 라인 갱신
- ai-nodes/docs/workspace-structure.md 매트릭스 stock-investment 7행 ?→O + L159 적용 완료 + L181 travel만 잔존 표기

stock-investment 표준 적용 시리즈 완료 (plan001~004). 다음은 travel + health-care.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

push 없음 (phase-02 책임).

## PHASE_BLOCKED / PHASE_FAILED 조건

- decisions/* 7 파일 중 부재 (sanity 점검) — `PHASE_BLOCKED: 자료 부재 — git history 점검`.
- adr.md plan 번호 정정 실패 (성공 기준 2/3) — `PHASE_FAILED: adr 정정 누락`.
- workspace-structure 매트릭스 O 부족 (성공 기준 5) — `PHASE_FAILED: 매트릭스 갱신 부실`.
- scope creep — `PHASE_FAILED`.
- 의도 외 staged 파일 — `PHASE_BLOCKED`.
