# Phase 3 — ~/ai-nodes/skills/docs-check/ 디렉터리 생성 + SKILL.md Write 적용

**Model**: sonnet
**Status**: pending

---

## 목표

phase-01 draft의 SKILL.md를 `~/ai-nodes/skills/docs-check/SKILL.md`에 Write 적용. ai-nodes 모노레포 전역 skill — 워크스페이스가 아닌 *루트 skills/* 위치 (apartment의 `agent-browser`, planning, plan-and-build와 같은 위치 — 모노레포 공용).

**범위 외**: AGENTS.md 갱신 (phase-04), 정적 검증·push (phase-04).

## 관련 docs

- phase-02 commit — adr.md Quick Index + Status 갱신 완료
- `career-os/tasks/plan018-docs-check-and-adr-health/draft/SKILL.md` — Write 원본
- `skills/plan-and-build/references/common-pitfalls.md` 6-6 (Write 위장)

## 사전 검증

```bash
cd /home/bifos/ai-nodes

# 1-A. phase-02 commit 존재
git log -1 --format='%s' | grep -q "plan018 phase-02" \
  || { echo "PHASE_BLOCKED: phase-02 commit 없음"; exit 2; }

# 1-B. draft SKILL.md 존재
DRAFT=career-os/tasks/plan018-docs-check-and-adr-health/draft/SKILL.md
test -f "$DRAFT" || { echo "PHASE_BLOCKED: draft 부재"; exit 2; }

# 1-C. skill 위치 (아직 부재)
test ! -d skills/docs-check \
  || { echo "PHASE_BLOCKED: skills/docs-check 이미 존재"; exit 2; }

# 1-D. 모노레포 skills/ 디렉터리 위치 확인
test -d skills \
  || { echo "PHASE_BLOCKED: ~/ai-nodes/skills/ 부재"; exit 2; }

echo "사전 검증 OK"
```

## 작업 항목

### 1. skill 디렉터리 + SKILL.md Write

```bash
cd /home/bifos/ai-nodes
mkdir -p skills/docs-check
```

`Read` 도구로 `career-os/tasks/plan018-docs-check-and-adr-health/draft/SKILL.md` 로드.

`Write` 도구로 `skills/docs-check/SKILL.md`에 **draft 본문 그대로** 저장.

### 2. SKILL.md 적용 검증

```bash
cd /home/bifos/ai-nodes
TARGET=skills/docs-check/SKILL.md
DRAFT=career-os/tasks/plan018-docs-check-and-adr-health/draft/SKILL.md

# A. byte-for-byte 동일
diff -q "$TARGET" "$DRAFT" > /dev/null \
  || { echo "PHASE_FAILED: target ↔ draft 불일치"; exit 1; }

# B. 라인 수
LINES=$(wc -l < "$TARGET")
[ "$LINES" -ge 120 ] || { echo "PHASE_FAILED: target $LINES 줄 — Write 누락 의심"; exit 1; }

# C. 5축 + 자동화 검사 + 필수 섹션
for kw in "Decay" "Bloat" "Clarity" "Duplication" "Self-Evidence" \
          "Quick Index" "When to use" "Inputs" "Workflow" "Error handling"; do
  grep -q "$kw" "$TARGET" || { echo "PHASE_FAILED: '$kw' 누락"; exit 1; }
done

# D. native invoke 안내
grep -q "docs-check\|claude -p" "$TARGET" \
  || { echo "PHASE_FAILED: native invoke 안내 누락"; exit 1; }

# E. 옛 subprocess 지시문 *없음* (6-7)
for kw in "Output only valid JSON" "Do not output markdown" "claude --json-schema"; do
  grep -q "$kw" "$TARGET" && { echo "PHASE_FAILED: '$kw' 잔재"; exit 1; }
done

echo "[2] SKILL.md 적용 검증 OK ($LINES 줄)"
```

### 3. skill 위치 자동 로드 검증

```bash
cd /home/bifos/ai-nodes
# Claude Code skill discovery 패턴 — skills/<name>/SKILL.md
# 또는 .claude/skills/<name>/SKILL.md
# 본 skill은 ~/ai-nodes/skills/docs-check/SKILL.md — 모노레포 공용 (agent-browser, planning, plan-and-build와 같은 위치)

# 같은 위치의 기존 skill 확인
ls skills/ | head -10
echo ""
# 자동 로드 검사 — 기존 패턴 따름
for existing in agent-browser planning plan-and-build workspace-audit; do
  test -f "skills/$existing/SKILL.md" \
    && echo "[참고] skills/$existing/SKILL.md 정상" \
    || echo "[참고] skills/$existing/ 부재 (정상일 수 있음)"
done
echo "[3] skill 위치 정합성 OK"
```

### 4. 커밋 + commit 개수 강제

```bash
cd /home/bifos/ai-nodes
HEAD_BEFORE=$(git rev-parse HEAD)

git add skills/docs-check/
git commit -m "$(cat <<'COMMIT_EOF'
feat(ai-nodes): docs-check skill 신규 (plan018 phase-03)

ai-nodes ADR-003 적용. fos-blog docs-check 5축 차용 + ai-nodes 도메인
변형 + native skill 명세.

위치: ~/ai-nodes/skills/docs-check/SKILL.md (모노레포 전역 — agent-browser
+ planning + plan-and-build + workspace-audit와 같은 위치)

5축 검사:
- A. Decay (Code ↔ Docs Sync, stale ADR/path/skill)
- B. Bloat (ADR 30줄 + 코드 블록 + 파일 path 열거)
- C. Clarity (why + alternative + rejection)
- D. Duplication (5문서 단일 출처)
- E. Self-Evidence (자명한 ADR 폐기)

ai-nodes 자동화 검사 5개:
1. ADR Quick Index ↔ 본문 sync (heading ↔ index 행)
2. 30줄 threshold (ADR 본문 줄 수 ≥30 → bloat 후보)
3. Config schema alignment (data-schema.md ↔ config json 키)
4. Dispatcher case coverage (run_now.sh case ↔ prd.md + flow.md 섹션)
5. Prohibited terms (§ / 옛 subprocess 지시문 / outdated skill 이름)

draft 별도 파일 → byte-for-byte Write (common-pitfalls 6-6 회피).

호출: `claude -p "/docs-check [scope]"` (scope: 워크스페이스 이름 또는 all).
발견 사항을 Critical/Warning/Safe 3단계 분류. 수정은 사용자 승인 후.
COMMIT_EOF
)" || { echo "PHASE_FAILED: commit"; exit 1; }

HEAD_AFTER=$(git rev-parse HEAD)
COMMITS=$(git rev-list "$HEAD_BEFORE..$HEAD_AFTER" --count)
[ "$COMMITS" = "1" ] \
  || { echo "PHASE_FAILED: 본 phase commit 수 $COMMITS (expected 1)"; exit 1; }
echo "[4] commit 1 OK"
```

push는 phase-04.

## Critical Files

| 파일 | 변경 |
|---|---|
| `~/ai-nodes/skills/docs-check/SKILL.md` | 신규 (Write, draft 복제) |

## Blocked 조건

- phase-02 commit 없음 → `PHASE_BLOCKED` + `exit 2`
- draft 부재 → `PHASE_BLOCKED` + `exit 2`
- skill 위치 이미 존재 → `PHASE_BLOCKED` + `exit 2`
- 검증 A~E 실패 → `PHASE_FAILED` + `exit 1`
- commit 수 ≠ 1 → `PHASE_FAILED: commit 위장 의심` + `exit 1`

## 의도 메모

- skill 위치 `~/ai-nodes/skills/docs-check/`는 *워크스페이스 격리 원칙 예외* — ADR-003에서 정당화 (ADR 검사 자체는 모노레포 공용).
- SKILL.md byte diff 검증이 6-6 방어선.
