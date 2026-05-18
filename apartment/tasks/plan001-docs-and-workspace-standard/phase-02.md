# Phase 02 — AGENTS slim + CLAUDE 심링크 + .env 이동 + 기존 docs 정리

**Model**: sonnet
**Status**: pending

---

## 목표

apartment/AGENTS.md 슬림 재작성 + CLAUDE.md 심링크 생성 + `.env` + `.env.example` 워크스페이스 root 이동 + 4 caller 갱신 + 기존 docs git rm (WORKFLOW.md / TOOLS.md / docs-naver-browser-plan.md / docs/decisions/).

**범위 외**: 5문서 자체 작성 (phase-01 완료 가정), ai-nodes 메타 (phase-03), 잔여 참조 갱신 (phase-04).

---

## 본 phase 강제 주의문

- 반드시 Write/Edit/Bash 도구로 파일 갱신·이동·삭제를 수행해야 한다. prose 응답으로 작업 묘사만 출력하면 PHASE_FAILED (common-pitfalls 6-6).
- 작성·수정하는 모든 문서에 section sigil (section mark, U+00A7) 특수문자 사용 금지. 섹션 헤더는 `## 1. 제목` 형태. CLAUDE.md directive 준수.
- destructive edit (git rm) 후 즉시 검증 명령 (`git ls-files <path> | wc -l = 0`)으로 잔재 확인 (common-pitfalls 6-5).
- 본 phase 종료 시 *commit 개수 self-check* 통과: 본 phase가 만든 commit 수 = 1.

---

## 관련 docs

- 참조: `career-os/AGENTS.md` (slim 후 모범 사례, 132줄)
- 본 phase 진입 전 phase-01 산출 가정: `apartment/docs/{prd, data-schema, flow, code-architecture, adr}.md` 존재.

---

## 작업 항목

### 1. apartment/AGENTS.md slim 재작성

`Write` 도구로 `apartment/AGENTS.md` 전면 재작성. 약 60-90줄.

(기존 AGENTS.md = 29줄, 본 phase에서 5문서 라우팅 중심으로 재구성.)

섹션 구조:

1. 헤더 — `# AGENTS.md — apartment 워크스페이스`. 워크스페이스 정의 + CLAUDE.md 심링크 명시 + 5문서 분리 안내.
2. 5문서 라우팅 가이드 — 표 (`| 문서 | 무엇이 들어 있는지 | 언제 보는지 |`):
   - `docs/prd.md` — 제품 범위·MVP 타깃·기능 표·Guri buy-search 운영 정책·성공 기준 → 새 기능 추가 / 우선순위 결정
   - `docs/data-schema.md` — config (4 json) / data / logs / .env 스키마 → 데이터 파일 / 새 config 도입
   - `docs/flow.md` — 명령별 데이터 흐름 (daily-report 12 step + interior-digest 5 step) → 새 흐름 추가 / 디버깅
   - `docs/code-architecture.md` — 디렉터리 트리·skill 표준·외부 의존·Runner 패턴 → 코드 구조 변경 / 새 스킬 추가
   - `docs/adr.md` — apartment 한정 ADR 누적 (현재 ADR-001). 모노레포 레벨은 `../docs/adr.md`. → 결정의 *왜*
3. tasks/ 영역 안내 — planning + plan-and-build 운영, `tasks/plan{N}-<slug>/` 형태, 완료 후에도 history 보존.
4. 목적 — 부동산 시장 리포트 + 인테리어 레퍼런스 자동화 (단일 사용자, 매일 재실행 가능).
5. 현재 타깃 — 한 줄 요약 (엘지원앙아파트 LG원앙 + 포커스 59A + 구리 럭키아파트 5동 1004호 24평 + 광역 Guri buy-search). 상세는 prd.md 2번 + 6번.
6. 워크플로 진입점 — code block:
   ```bash
   claude -p "/apartment-daily-report"
   # 또는: bash apartment/skills/apartment-daily-report/scripts/run_report.sh
   bash apartment/skills/apartment-interior-reference-digest/scripts/run_digest.sh
   bash apartment/skills/apartment-daily-report/scripts/run_smoke_test.sh
   ```
7. 외부 의존성 — `_shared/bin/track_task.sh` (load-bearing), `_shared/bin/extract_claude_result.py`, `claude` CLI, `agent-browser` CLI (ADR-001). 상세는 `docs/code-architecture.md` 5번.
8. 운영 원칙 — focus-unit 위장 금지, raw fetched untrusted, 검증 안 된 입주 가능 단정 금지, 매물 가격 발명 금지. `.env` 워크스페이스 root (ai-nodes ADR-004). 영구 자산은 `~/.openclaw/workspace` 아닌 워크스페이스 내부.
9. 규칙 — 다른 워크스페이스(career-os, stock-investment, travel) 격리, 재실행 가능 + 날짜 단위 멱등, 불확실성 명시 (source 실패 raw 보존), 새 결정은 `docs/adr.md` 누적 (개별 ADR 파일 신설 금지, ai-nodes ADR-004).

런타임 상태(어느 명령이 최근에 잘 도는지)는 본 문서에 박지 않는다 — `logs/task-runs.jsonl` 단일 출처.

### 2. apartment/CLAUDE.md 심링크 생성

```bash
cd /home/bifos/ai-nodes/apartment
ln -s AGENTS.md CLAUDE.md
```

검증:

```bash
test -L /home/bifos/ai-nodes/apartment/CLAUDE.md && echo "[CLAUDE.md] symlink OK" || { echo "PHASE_FAILED: CLAUDE.md not symlink"; exit 1; }
TARGET=$(readlink /home/bifos/ai-nodes/apartment/CLAUDE.md)
echo "[CLAUDE.md target] $TARGET"
[ "$TARGET" = "AGENTS.md" ] || { echo "PHASE_FAILED: symlink target $TARGET != AGENTS.md"; exit 1; }
```

### 3. .env 워크스페이스 root 이동

```bash
cd /home/bifos/ai-nodes/apartment

# .env.example은 git tracked
git mv config/.env.example .env.example

# .env는 gitignored — plain mv
mv config/.env .env
```

검증:

```bash
test -f /home/bifos/ai-nodes/apartment/.env && echo "[.env root] OK" || { echo "PHASE_FAILED: .env 이동 실패"; exit 1; }
test -f /home/bifos/ai-nodes/apartment/.env.example && echo "[.env.example root] OK" || { echo "PHASE_FAILED: .env.example 이동 실패"; exit 1; }
test ! -e /home/bifos/ai-nodes/apartment/config/.env && echo "[config/.env removed] OK" || { echo "PHASE_FAILED: 옛 config/.env 잔존"; exit 1; }
test ! -e /home/bifos/ai-nodes/apartment/config/.env.example && echo "[config/.env.example removed] OK" || { echo "PHASE_FAILED: 옛 config/.env.example 잔존"; exit 1; }
```

### 4. .env caller 갱신 (live code 4건)

먼저 정확한 줄 확인:

```bash
grep -n "config/.env\|docs/decisions" \
  apartment/skills/apartment-daily-report/scripts/run_report.sh \
  apartment/skills/apartment-daily-report/scripts/collect_sources.py \
  apartment/skills/apartment-daily-report/scripts/collect_naver_api.py
```

`Edit` 도구로 갱신:

#### 4-1. `apartment/skills/apartment-daily-report/scripts/run_report.sh` line 12-13

- line 12 주석: `# ADR-001 참조: apartment/docs/decisions/001-naver-api-integration.md` → `# ADR-001 참조: apartment/docs/adr.md`
- line 13: `ENV_FILE="${APARTMENT_ENV_FILE:-$HOME/ai-nodes/apartment/config/.env}"` → `ENV_FILE="${APARTMENT_ENV_FILE:-$HOME/ai-nodes/apartment/.env}"`

#### 4-2. `apartment/skills/apartment-daily-report/scripts/collect_sources.py` line 156

- `notes.append("Naver API 수집은 NAVER_COOKIE 부재로 건너뛰었다 — apartment/config/.env에 쿠키를 설정하라.")` → `notes.append("Naver API 수집은 NAVER_COOKIE 부재로 건너뛰었다 — apartment/.env에 쿠키를 설정하라.")`

#### 4-3. `apartment/skills/apartment-daily-report/scripts/collect_naver_api.py`

`grep -n "config/.env" apartment/skills/apartment-daily-report/scripts/collect_naver_api.py` 결과의 모든 줄에서 `apartment/config/.env` → `apartment/.env` 갱신. `replace_all` 사용 가능.

검증:

```bash
LEFT_CONFIG_ENV=$(grep -rn "config/.env\|apartment/config/.env" apartment/skills/ apartment/AGENTS.md 2>/dev/null | wc -l)
echo "[옛 config/.env 참조] $LEFT_CONFIG_ENV"
[ "$LEFT_CONFIG_ENV" -eq 0 ] || { echo "PHASE_FAILED: 옛 config/.env 참조 잔존"; grep -rn "config/.env" apartment/skills/ apartment/AGENTS.md; exit 1; }

LEFT_DECISIONS=$(grep -rn "docs/decisions" apartment/skills/ apartment/AGENTS.md 2>/dev/null | wc -l)
echo "[옛 docs/decisions 참조] $LEFT_DECISIONS"
[ "$LEFT_DECISIONS" -eq 0 ] || { echo "PHASE_FAILED: 옛 docs/decisions 참조 잔존"; grep -rn "docs/decisions" apartment/skills/ apartment/AGENTS.md; exit 1; }
```

### 5. 기존 docs git rm

```bash
cd /home/bifos/ai-nodes

git rm apartment/WORKFLOW.md
git rm apartment/TOOLS.md
git rm apartment/docs-naver-browser-plan.md
git rm -r apartment/docs/decisions/
```

검증 (destructive edit 안전 보장, common-pitfalls 6-5):

```bash
LEFT_FILES=$(git ls-files \
  apartment/WORKFLOW.md \
  apartment/TOOLS.md \
  apartment/docs-naver-browser-plan.md \
  apartment/docs/decisions/ 2>/dev/null | wc -l)
echo "[옛 docs git tracked 잔존] $LEFT_FILES"
[ "$LEFT_FILES" -eq 0 ] || { echo "PHASE_FAILED: 옛 docs git tracked 잔존: $LEFT_FILES"; exit 1; }

# filesystem 잔존 확인
LEFT_FS=$(ls apartment/WORKFLOW.md apartment/TOOLS.md apartment/docs-naver-browser-plan.md 2>/dev/null | wc -l)
LEFT_DEC_DIR=$(test -d apartment/docs/decisions && echo 1 || echo 0)
echo "[filesystem 잔존 files] $LEFT_FS"
echo "[filesystem 잔존 decisions dir] $LEFT_DEC_DIR"
[ "$LEFT_FS" -eq 0 ] && [ "$LEFT_DEC_DIR" -eq 0 ] || { echo "PHASE_FAILED: filesystem 잔존"; exit 1; }
```

### 6. commit 생성

```bash
git add apartment/
git commit -m "$(cat <<'EOF'
chore(apartment): AGENTS slim + CLAUDE 심링크 + .env 워크스페이스 root 이동 + 옛 docs 정리 (plan001 phase-02)

- apartment/AGENTS.md: 5문서 라우팅 + 슬림 본문 (career-os AGENTS.md mirror 패턴, 60-90줄)
- apartment/CLAUDE.md → AGENTS.md (신규 심링크)
- apartment/.env + .env.example: config/ → 워크스페이스 root (ai-nodes ADR-004 표준)
- caller 4 갱신: run_report.sh (env path + ADR 인용), collect_sources.py 에러 메시지, collect_naver_api.py
- 옛 docs git rm:
  - WORKFLOW.md (flow.md 흡수, plan001 phase-01)
  - TOOLS.md (prd.md 2번 흡수)
  - docs-naver-browser-plan.md (이미 적용된 plan note)
  - docs/decisions/ (adr.md 단일 파일로 흡수, ai-nodes ADR-004 정합)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## 검증 (phase 종료 직전)

```bash
# 1. 핵심 산출물 존재
test -f apartment/AGENTS.md && echo "[AGENTS.md] OK" || { echo "PHASE_FAILED: AGENTS.md absent"; exit 1; }
test -L apartment/CLAUDE.md && echo "[CLAUDE.md] symlink OK" || { echo "PHASE_FAILED: CLAUDE.md symlink absent"; exit 1; }
test -f apartment/.env && echo "[.env root] OK" || { echo "PHASE_FAILED: .env root absent"; exit 1; }
test -f apartment/.env.example && echo "[.env.example root] OK" || { echo "PHASE_FAILED: .env.example root absent"; exit 1; }

# 2. section sigil 미사용 (AGENTS.md, U+00A7)
SIGIL_CHAR=$(printf '\xc2\xa7')
COUNT=$(grep -c "$SIGIL_CHAR" apartment/AGENTS.md || echo 0)
echo "[sigil AGENTS.md] $COUNT"
[ "$COUNT" -eq 0 ] || { echo "PHASE_FAILED: AGENTS.md sigil 잔재"; exit 1; }

# 3. AGENTS.md 분량 (50-100줄)
LINES=$(wc -l < apartment/AGENTS.md)
echo "[AGENTS.md] $LINES lines"
[ "$LINES" -ge 50 ] && [ "$LINES" -le 100 ] || { echo "PHASE_FAILED: AGENTS.md $LINES 범위 (50-100) 밖"; exit 1; }

# 4. 5문서 링크 존재 (AGENTS.md 안)
for f in prd data-schema flow code-architecture adr; do
  grep -q "docs/$f.md" apartment/AGENTS.md || { echo "PHASE_FAILED: AGENTS.md docs/$f.md 라우팅 누락"; exit 1; }
done
echo "[5문서 라우팅] OK"

# 5. commit 개수 self-check
COMMITS=$(git log --format='%H' HEAD~1..HEAD | wc -l)
echo "[commit count] $COMMITS"
[ "$COMMITS" -eq 1 ] || { echo "PHASE_FAILED: phase commit $COMMITS != 1"; exit 1; }

# 6. working tree clean (apartment 영역)
DIRTY=$(git status --porcelain apartment/ | wc -l)
echo "[apartment dirty] $DIRTY lines"
[ "$DIRTY" -eq 0 ] || { echo "PHASE_FAILED: apartment/ working tree dirty"; git status --porcelain apartment/; exit 1; }

echo "✓ Phase 02 검증 통과"
```

---

## 의도 메모

- AGENTS.md slim 분량 50-100줄 — career-os 132줄 mirror하되 apartment 도메인이 작음. tasks/ 영역 안내 포함 (planning + plan-and-build).
- `.env` 자체는 gitignored이라 plain `mv`. `.env.example`만 `git mv` (tracked).
- caller 4건 = run_report.sh (2 위치) + collect_sources.py + collect_naver_api.py.
- destructive edit (git rm) 안전 — common-pitfalls 6-5 방어로 `git ls-files | wc -l` + `ls / test -d` 이중 검증.
- 본 phase 후 apartment/ 디렉터리 구조 = workspace-structure.md 표준 형태로 정착. phase-03이 *그 표준 자체를 ai-nodes 메타에 정식화*.
