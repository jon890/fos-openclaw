# Phase 1 — SKILL.md draft 작성 (~180줄, Append + 주석 마킹 + audit trail 명세)

**Model**: sonnet
**Status**: pending

---

## 목표

candidate-baseline-suggester native skill의 draft를 별도 파일에 작성. fos-study 전체 commit history + study-progress + interview-prep-analyzer baseline 산출물에서 추론한 자산 갱신 명세 (Append + 주석 마킹) + audit trail 명세.

draft를 phase 본문 코드 블록에 박지 않음 — common-pitfalls 6-6 회피.

**범위 외**: 실제 적용 (phase-02), docs 갱신 (phase-03).

## 관련 docs

- `career-os/docs/adr.md` ADR-028 — 본 plan 결정 출처
- `career-os/.claude/skills/study-pack-writer/SKILL.md` — native 명세 패턴
- `career-os/.claude/skills/interview-prep-analyzer/` (plan017 실행 후) — baseline 산출물 의존 (선택적)
- `skills/plan-and-build/references/common-pitfalls.md` 6-6 + 6-7

## 사전 검증

```bash
cd /home/bifos/ai-nodes

# 1-A. ADR-028 docs commit 존재
git log --oneline | grep -q "ADR-028.*candidate-baseline" \
  || { echo "PHASE_BLOCKED: ADR-028 commit 없음"; exit 2; }

# 1-B. draft 디렉터리 존재
test -d career-os/tasks/plan020-candidate-baseline-suggester/draft \
  || { echo "PHASE_BLOCKED: draft 디렉터리 없음"; exit 2; }

echo "사전 검증 OK"
```

## 작업 항목

### 1. SKILL.md draft 작성

저장: `career-os/tasks/plan020-candidate-baseline-suggester/draft/SKILL.md`

본문 구성 (~180줄):

#### Frontmatter
```yaml
---
name: candidate-baseline-suggester
description: career-os/config/ hand-crafted 자산 (candidate-profile.md, baseline-core-files.json, prd.md '약점·강점', data/study-progress.json weak_spots)을 fos-study 전체 commit history + study-progress + interview-prep-analyzer baseline 산출물 기반으로 자동 갱신. Append + 주석 마킹 패턴 — 기존 본문 보존 + 새 항목 추가 + outdated 항목 주석 마킹. audit trail (data/runtime/profile-refresh-suggestions/YYYY-MM-DD/ 안 before/after/diff/changes) 필수. 자연어 호출 — "후보자 프로필 갱신", "baseline 약점·강점 평가 업데이트", "/candidate-baseline-suggester" 슬래시.
---
```

#### 본문 섹션
1. **Overview** — 한 줄
2. **When to use** — 자연어 + 슬래시 + 호출 빈도 권장 (예: study-pack 누적 후 / 면접 시즌 시작 시)
3. **Inputs** — Read 대상:
   - `career-os/config/candidate-profile.md` (현재 본문)
   - `career-os/config/baseline-core-files.json` (현재 본문)
   - `career-os/docs/prd.md` (특히 "약점·강점" 섹션)
   - `career-os/data/study-progress.json` (sessions + weak_spots)
   - (선택) `career-os/data/reports/baseline/<latest>/report.md` — 있으면 Read, 없으면 skip
   - fos-study 전체 commit history — `git log` + 최근 N개 산출물 path
4. **Workflow** — 다음 순서:

   #### 4-1. Backup (audit trail before/)
   ```bash
   DATE=$(date +%F)
   AUDIT_DIR=career-os/data/runtime/profile-refresh-suggestions/$DATE
   mkdir -p $AUDIT_DIR/before $AUDIT_DIR/after
   cp candidate-profile.md baseline-core-files.json prd-weak-strong-section.md study-progress.json $AUDIT_DIR/before/
   ```

   #### 4-2. fos-study 분석 (Claude 자연어 추론)
   - `git -C career-os/sources/fos-study log --all --pretty=format:'%h %ad %s' --date=short`
   - 최근 학습 토픽 매핑 (study-pack / interview-asset 산출물 path → 강점 평가 근거)
   - 새 핵심 파일 후보 식별 (fos-study 최근 commit 중 baseline-core-files 미포함)

   #### 4-3. 자산 갱신 (Append + 주석 마킹)
   - **candidate-profile.md "입증된 강점" 섹션**: 새 학습 토픽 append. 형식: `- <강점 항목> (근거: fos-study/<path>)`
   - **candidate-profile.md "약점·학습 중인 영역" 섹션**: 학습 완료 약점에 주석 마킹. 형식: `<!-- suggester: outdated since YYYY-MM-DD, 근거 fos-study/<path> -->` 한 줄 추가
   - **baseline-core-files.json `files` 배열**: 새 핵심 파일 append. 형식: `{"path": "interview/...", "note": "suggester: added YYYY-MM-DD, 근거 ..."}`
   - **prd.md "약점·강점" 섹션** (짧은 두 줄): 대체 가능. 보강 필요 / 이미 갖춘 강점 평가 갱신
   - **data/study-progress.json `weak_spots`**: 평가 갱신 (각 weak_spot의 last_evaluated + status)

   #### 4-4. audit trail (after/ + diff + changes)
   - 갱신된 자산을 `$AUDIT_DIR/after/`에 복사
   - `diff -u $AUDIT_DIR/before/<f> $AUDIT_DIR/after/<f> > $AUDIT_DIR/diff/<f>.diff` (각 파일별)
   - `$AUDIT_DIR/changes.md` 작성: 각 변경의 *근거 fos-study path + 사유* 명시
5. **Self-check** — 갱신 후 정확성:
   - candidate-profile 본문 라인 수 *증가* (Append 모드라 줄어들면 안 됨)
   - baseline-core-files.json valid JSON + files 배열 길이 증가 (또는 동일)
   - audit trail 4 파일 모두 존재 (before/ + after/ + diff/ + changes.md)
   - 주석 마킹은 *기존 본문 그대로 두고 줄 추가*만 (기존 줄 삭제 금지)
6. **Error handling**:
   - fos-study git pull 실패 → stale data로 진행 + 사용자 알림
   - audit trail Write 실패 → skill 중단 (audit trail 없이는 절대 적용 X)
   - JSON 파싱 실패 → 해당 자산만 skip + stderr warn
7. **Why this design** — ADR-028 요약 3줄 (Append + 주석 마킹 + audit trail)

#### 호출 패턴

```bash
claude -p "/candidate-baseline-suggester"
# 또는 자연어
claude -p "후보자 프로필 fos-study 학습 결과 반영해서 갱신해줘"
```

### 2. draft 자기 확인

```bash
cd /home/bifos/ai-nodes
DRAFT=career-os/tasks/plan020-candidate-baseline-suggester/draft/SKILL.md

# A. draft 존재 + 라인 수
test -f "$DRAFT" || { echo "PHASE_FAILED: draft 부재"; exit 1; }
LINES=$(wc -l < "$DRAFT")
[ "$LINES" -ge 120 ] || { echo "PHASE_FAILED: draft $LINES 줄 (expected ≥120)"; exit 1; }

# B. 필수 섹션
for s in "When to use" "Inputs" "Workflow" "Self-check" "Error handling"; do
  grep -q "$s" "$DRAFT" || { echo "PHASE_FAILED: '$s' 누락"; exit 1; }
done

# C. 핵심 키워드 (Append + 주석 마킹 + audit trail)
for kw in "Append" "주석 마킹\|outdated" "audit trail\|before/\|after/\|diff" \
          "candidate-profile" "baseline-core-files" "fos-study"; do
  grep -qE "$kw" "$DRAFT" || { echo "PHASE_FAILED: '$kw' 누락"; exit 1; }
done

# D. 옛 subprocess 시대 지시문 없음 (6-7)
for kw in "Output only valid JSON" "Do not output markdown" "claude --json-schema"; do
  grep -q "$kw" "$DRAFT" && { echo "PHASE_FAILED: '$kw' 잔재"; exit 1; }
done

echo "[2] draft 자기 확인 OK ($LINES 줄)"
```

### 3. 커밋 + commit 개수 강제

```bash
cd /home/bifos/ai-nodes
HEAD_BEFORE=$(git rev-parse HEAD)

git add career-os/tasks/plan020-candidate-baseline-suggester/draft/
git commit -m "$(cat <<'COMMIT_EOF'
chore(career-os): plan020 phase-01 — candidate-baseline-suggester SKILL.md draft 작성

ADR-028 적용 준비. draft를 phase 본문 코드 블록이 아닌 별도 파일로 분리해
common-pitfalls 6-6 (Write 위장) 회피.

- draft/SKILL.md (~180줄): Append + 주석 마킹 + audit trail 명세
  - Workflow 4-1: Backup (before/)
  - Workflow 4-2: fos-study 전체 commit history 분석 (Claude 자연어 추론)
  - Workflow 4-3: 자산 갱신 (Append + outdated 주석 마킹)
  - Workflow 4-4: audit trail (after/ + diff/ + changes.md)
- 갱신 대상: candidate-profile.md + baseline-core-files.json + prd.md
  "약점·강점" 섹션 + data/study-progress.json weak_spots

phase-02에서 career-os/.claude/skills/candidate-baseline-suggester/ 적용.
COMMIT_EOF
)" || { echo "PHASE_FAILED: commit"; exit 1; }

HEAD_AFTER=$(git rev-parse HEAD)
COMMITS=$(git rev-list "$HEAD_BEFORE..$HEAD_AFTER" --count)
[ "$COMMITS" = "1" ] || { echo "PHASE_FAILED: commit 수 $COMMITS"; exit 1; }
echo "[3] commit 1 OK"
```

## Critical Files

| 파일 | 변경 |
|---|---|
| `career-os/tasks/plan020-candidate-baseline-suggester/draft/SKILL.md` | 신규 (~180줄) |

## Blocked 조건

- ADR-028 commit 없음 → `PHASE_BLOCKED` + `exit 2`
- draft 디렉터리 부재 → `PHASE_BLOCKED` + `exit 2`
- 자기 확인 A~D 실패 → `PHASE_FAILED` + `exit 1`
- commit 수 ≠ 1 → `PHASE_FAILED` + `exit 1`

## 의도 메모

- Append + 주석 마킹은 *hand-crafted 자산 보호* 핵심. self-check에서 *라인 수 감소* 발견 시 실패 — 본문 삭제 시도 즉시 잡힘.
- audit trail은 *roll back 안전망* — git revert로도 안 잡히는 환경별 변경 추적.
