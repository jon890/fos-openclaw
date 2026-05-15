# Phase 4 — ai-nodes/AGENTS.md 갱신 + 정적 검증 + push + trailing + index.json completed

**Model**: sonnet
**Status**: pending

---

## 목표

ai-nodes/AGENTS.md에 docs-check skill 안내 추가. 정적 검증 (5축 키워드 + Quick Index sync + commit history). 모든 commit push + index.json status=completed + trailing.

**범위 외**: 추가 코드/docs 변경.

## 관련 docs

- phase-03 commit — docs-check skill 적용 완료
- `~/ai-nodes/AGENTS.md` (모노레포 진입점)
- `skills/plan-and-build/references/common-pitfalls.md` 6-2

## 사전 검증

```bash
cd /home/bifos/ai-nodes

# 1-A. phase-03 commit 존재
git log -1 --format='%s' | grep -q "plan018 phase-03" \
  || { echo "PHASE_BLOCKED: phase-03 commit 없음"; exit 2; }

# 1-B. branch
[ "$(git branch --show-current)" = "main" ] \
  || { echo "PHASE_BLOCKED: branch != main"; exit 2; }

# 1-C. skill 위치 존재
test -f skills/docs-check/SKILL.md \
  || { echo "PHASE_BLOCKED: skill 부재"; exit 2; }

echo "사전 검증 OK"
```

## 작업 항목

### 1. ai-nodes/AGENTS.md 갱신

`ai-nodes/AGENTS.md`에서 `skills/` 섹션 (저장소 구조 안에서 모노레포 공용 skills 안내) 갱신:
- `agent-browser`, `planning`, `plan-and-build`, `workspace-audit` 옆에 `docs-check` 추가
- 짧은 한 줄 설명 (ai-nodes 5문서 + ADR 건전성 감사)

### 2. 정적 검증

```bash
cd /home/bifos/ai-nodes

# A. skill 위치 + 5축 키워드
SKILL=skills/docs-check/SKILL.md
test -f "$SKILL" || { echo "PHASE_FAILED: skill 부재"; exit 1; }
for kw in "Decay" "Bloat" "Clarity" "Duplication" "Self-Evidence" "Quick Index"; do
  grep -q "$kw" "$SKILL" || { echo "PHASE_FAILED: '$kw' 누락"; exit 1; }
done
echo "[A] skill 5축 + Quick Index OK"

# B. Quick Index 양방향 sync (phase-02 결과 유지)
python3 - <<'PY'
import re
from pathlib import Path
for f in ['career-os/docs/adr.md', 'docs/adr.md']:
    text = Path(f).read_text(encoding='utf-8')
    index_rows = re.findall(r'^\| (ADR-\d+) \|', text, re.M)
    body_headers = re.findall(r'^## (ADR-\d+) —', text, re.M)
    diff = set(index_rows) ^ set(body_headers)
    if diff:
        print(f'PHASE_FAILED: {f} Quick Index ↔ Body sync 위반 — {diff}')
        exit(1)
print('[B] Quick Index sync OK')
PY
[ $? -eq 0 ] || exit 1

# C. drift Status 5개 갱신 유지 (phase-02 결과)
for status in "ADR-006.*Partially superseded\|ADR-006.*partially superseded" \
              "ADR-007.*Superseded by ADR-027" \
              "ADR-011.*Superseded by plan015" \
              "ADR-016.*Partially superseded by ADR-027" \
              "ADR-023.*Deprecated"; do
  grep -qE "$status" career-os/docs/adr.md \
    || { echo "PHASE_FAILED: '$status' 누락"; exit 1; }
done
echo "[C] drift Status 5개 OK"

# D. AGENTS.md 갱신 확인
grep -q "docs-check" AGENTS.md \
  || { echo "PHASE_FAILED: AGENTS.md에 docs-check 안내 누락"; exit 1; }
echo "[D] AGENTS.md OK"

# E. 옛 subprocess 지시문 잔재 0
HITS=$(grep -rln "Output only valid JSON\|Do not output markdown" skills/docs-check/ 2>/dev/null | wc -l)
[ "$HITS" = "0" ] || { echo "PHASE_FAILED: 6-7 잔재"; exit 1; }
echo "[E] 6-7 잔재 0 OK"

# F. plan018 phase commit history (4 commits)
PLAN_COMMITS=$(git log --oneline | grep -c "plan018 phase-")
[ "$PLAN_COMMITS" -ge 3 ] \
  || { echo "PHASE_FAILED: plan018 commit history $PLAN_COMMITS (expected ≥3)"; exit 1; }
echo "[F] plan018 commit history OK"

echo "=== 정적 검증 전부 통과 ==="
```

### 3. index.json status=completed

```bash
cd /home/bifos/ai-nodes
python3 - <<'PY'
import json
from pathlib import Path
p = Path("career-os/tasks/plan018-docs-check-and-adr-health/index.json")
data = json.loads(p.read_text(encoding="utf-8"))
data["status"] = "completed"
data["current_phase"] = 4
for phase in data["phases"]:
    phase["status"] = "completed"
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("[index.json] completed")
PY
```

### 4. 최종 commit + push

```bash
cd /home/bifos/ai-nodes
HEAD_BEFORE=$(git rev-parse HEAD)

git add AGENTS.md \
        career-os/tasks/plan018-docs-check-and-adr-health/index.json

git commit -m "$(cat <<'COMMIT_EOF'
docs(ai-nodes): docs-check skill 안내 AGENTS.md 추가 + plan018 완료 마킹 (phase-04)

ADR-003 적용 마무리. plan018 phase-01~03 완료:
- phase-01: SKILL.md draft 작성
- phase-02: 28 ADR 전수 audit + Quick Index + 5 drift Status 갱신
- phase-03: ~/ai-nodes/skills/docs-check/ 신규

본 commit:
- ai-nodes/AGENTS.md: 모노레포 공용 skills 안내에 docs-check 추가
- career-os/tasks/plan018/index.json: status=completed

정적 검증 6개 항목 통과:
- 5축 + Quick Index 키워드
- adr.md Quick Index ↔ 본문 양방향 sync (career-os + ai-nodes)
- 5 drift Status 갱신 유지
- AGENTS.md docs-check 안내
- 6-7 잔재 0
- plan018 phase commit history ≥3
COMMIT_EOF
)" || { echo "PHASE_FAILED: commit"; exit 1; }

HEAD_AFTER=$(git rev-parse HEAD)
COMMITS=$(git rev-list "$HEAD_BEFORE..$HEAD_AFTER" --count)
[ "$COMMITS" = "1" ] \
  || { echo "PHASE_FAILED: 본 phase commit 수 $COMMITS (expected 1)"; exit 1; }

git push origin main || { echo "PHASE_FAILED: push"; exit 1; }
echo "[4] commit + push OK"
```

### 5. trailing cleanup

```bash
cd /home/bifos/ai-nodes
if [ -n "$(git status --porcelain career-os/tasks/plan018-docs-check-and-adr-health/index.json)" ]; then
  git add career-os/tasks/plan018-docs-check-and-adr-health/index.json
  git commit -m "task(career-os): plan018 index.json commitSha 후기록"
  git push origin main
fi

DIRTY=$(git status --porcelain career-os/tasks/plan018-docs-check-and-adr-health/ | wc -l)
[ "$DIRTY" = "0" ] || { echo "PHASE_FAILED: trailing 후 dirty"; exit 1; }
echo "trailing cleanup OK"
```

## Critical Files

| 파일 | 변경 |
|---|---|
| `ai-nodes/AGENTS.md` | docs-check skill 안내 추가 |
| `career-os/tasks/plan018-docs-check-and-adr-health/index.json` | status=completed |

## 사용자 직접 처리 안내 (phase 외)

phase 종료 후 사용자가 환경에서 수행:

```bash
# 첫 docs-check 실행
claude -p "/docs-check career-os"        # career-os 워크스페이스 감사
claude -p "/docs-check all"              # 모든 워크스페이스 감사

# 발견 사항을 Critical/Warning/Safe로 분류 보고 → 사용자 승인 후 수정 진행
```

## Blocked 조건

- phase-03 commit 없음 → `PHASE_BLOCKED` + `exit 2`
- branch != main → `PHASE_BLOCKED` + `exit 2`
- skill 위치 부재 → `PHASE_BLOCKED` + `exit 2`
- 정적 검증 A~F 실패 → `PHASE_FAILED: <항목>` + `exit 1`
- commit 수 ≠ 1 → `PHASE_FAILED: commit 위장 의심` + `exit 1`
- push 실패 → `PHASE_FAILED` + `exit 1`
- trailing 후 dirty → `PHASE_FAILED` + `exit 1`

## 의도 메모

- 정적 검증 6개 항목 — skill + Quick Index sync + drift Status + AGENTS + 6-7 + commit history.
- 사용자 docs-check smoke는 *읽기만* 안전 (수정은 승인 후) — fos-study 등 외부 영향 없음.
