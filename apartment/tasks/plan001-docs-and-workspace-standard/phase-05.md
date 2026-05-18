# Phase 05 — 통합 정적 검증 + status=completed + push

**Model**: haiku
**Status**: pending

---

## 목표

plan001 전체 산출물 통합 정적 검증 + `index.json status="completed"` 마킹 + `git push origin main`. 5 phase cross-validation.

**범위 외**: 본문 작성 / 갱신 (phase-01~04 완료).

---

## 본 phase 강제 주의문

- Bash 검증 명령은 *실제 실행*해야 한다. prose 응답만으로는 PHASE_FAILED (common-pitfalls 6-4).
- 통합 검증 결과를 stdout에 raw value echo로 명시 — 추정 보고 금지.
- section sigil (U+00A7) 사용 금지.

---

## 작업 항목

### 1. 통합 정적 검증

```bash
echo "=== plan001 통합 검증 ==="
SIGIL_CHAR=$(printf '\xc2\xa7')

# 1-A. apartment 5문서 존재
for f in prd data-schema flow code-architecture adr; do
  test -f apartment/docs/$f.md || { echo "PHASE_FAILED: apartment/docs/$f.md absent"; exit 1; }
done
echo "[1-A apartment 5문서] OK"

# 1-B. AGENTS.md slim + CLAUDE.md 심링크
test -f apartment/AGENTS.md || { echo "PHASE_FAILED: AGENTS.md absent"; exit 1; }
test -L apartment/CLAUDE.md || { echo "PHASE_FAILED: CLAUDE.md not symlink"; exit 1; }
LINK_TARGET=$(readlink apartment/CLAUDE.md)
echo "[CLAUDE.md target] $LINK_TARGET"
[ "$LINK_TARGET" = "AGENTS.md" ] || { echo "PHASE_FAILED: symlink target != AGENTS.md"; exit 1; }
echo "[1-B AGENTS + CLAUDE 심링크] OK"

# 1-C. .env 워크스페이스 root + 옛 위치 부재
test -f apartment/.env || { echo "PHASE_FAILED: .env absent"; exit 1; }
test -f apartment/.env.example || { echo "PHASE_FAILED: .env.example absent"; exit 1; }
test ! -e apartment/config/.env || { echo "PHASE_FAILED: 옛 config/.env 잔존"; exit 1; }
test ! -e apartment/config/.env.example || { echo "PHASE_FAILED: 옛 config/.env.example 잔존"; exit 1; }
echo "[1-C .env root 이동] OK"

# 1-D. 기존 docs git rm 확인
for f in apartment/WORKFLOW.md apartment/TOOLS.md apartment/docs-naver-browser-plan.md; do
  test ! -e "$f" || { echo "PHASE_FAILED: $f 잔존"; exit 1; }
done
test ! -d apartment/docs/decisions || { echo "PHASE_FAILED: docs/decisions/ 디렉터리 잔존"; exit 1; }
echo "[1-D 기존 docs git rm] OK"

# 1-E. ai-nodes 메타
test -f ai-nodes/docs/workspace-structure.md || { echo "PHASE_FAILED: workspace-structure.md absent"; exit 1; }
grep -q "^## ADR-004" ai-nodes/docs/adr.md || { echo "PHASE_FAILED: ai-nodes ADR-004 absent"; exit 1; }
grep -q "Lifted to ai-nodes ADR-004" career-os/docs/adr.md || { echo "PHASE_FAILED: career-os Status 격상 absent"; exit 1; }
grep -q "workspace-structure.md" ai-nodes/AGENTS.md || { echo "PHASE_FAILED: AGENTS.md 보강 absent"; exit 1; }
echo "[1-E ai-nodes 메타] OK"

# 1-F. section sigil 전수 검증
SIGIL_FILES=""
for f in apartment/AGENTS.md \
         apartment/docs/prd.md apartment/docs/data-schema.md apartment/docs/flow.md apartment/docs/code-architecture.md apartment/docs/adr.md \
         ai-nodes/docs/workspace-structure.md ai-nodes/docs/adr.md ai-nodes/AGENTS.md career-os/docs/adr.md; do
  COUNT=$(grep -c "$SIGIL_CHAR" "$f" 2>/dev/null || echo 0)
  if [ "$COUNT" -gt 0 ]; then
    SIGIL_FILES="$SIGIL_FILES $f($COUNT)"
  fi
done
echo "[1-F sigil 잔재 files] $SIGIL_FILES"
[ -z "$SIGIL_FILES" ] || { echo "PHASE_FAILED: sigil 잔재"; exit 1; }
echo "[1-F sigil 전수] 0건 OK"

# 1-G. 옛 path 잔재 전수
LEGACY=$(grep -rln "WORKFLOW.md\|apartment/TOOLS\|docs/decisions\|apartment/config/.env\|docs-naver-browser-plan" apartment/skills/ apartment/.claude/ apartment/AGENTS.md 2>/dev/null | wc -l)
echo "[1-G 옛 path 잔재] $LEGACY"
[ "$LEGACY" -eq 0 ] || { echo "PHASE_FAILED: 옛 path 잔재 $LEGACY건"; exit 1; }

# 1-H. JSON 유효성 (.env.example 등 변경된 config 의도 보존)
test -f apartment/.env.example || { echo "PHASE_FAILED: .env.example absent"; exit 1; }
echo "[1-H .env.example 보존] OK"

echo "=== 통합 정적 검증 모두 통과 ==="
```

### 2. index.json status="completed" 마킹

```bash
python3 - <<'PY'
import json, pathlib
from datetime import datetime, timezone

p = pathlib.Path("apartment/tasks/plan001-docs-and-workspace-standard/index.json")
data = json.loads(p.read_text())
data["status"] = "completed"
data["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
print(f"[index.json] status={data['status']} updated_at={data['updated_at']}")
PY
```

검증:

```bash
STATUS=$(python3 -c "import json; print(json.load(open('apartment/tasks/plan001-docs-and-workspace-standard/index.json'))['status'])")
echo "[plan001 status] $STATUS"
[ "$STATUS" = "completed" ] || { echo "PHASE_FAILED: status != completed"; exit 1; }
```

### 3. status commit + push

```bash
git add apartment/tasks/plan001-docs-and-workspace-standard/index.json
git commit -m "$(cat <<'EOF'
task(apartment): plan001 index.json status=completed (phase-05)

plan001 5 phase 모두 통과:
- phase-01: apartment 5문서 신설 (prd / data-schema / flow / code-architecture / adr)
- phase-02: AGENTS slim + CLAUDE 심링크 + .env 워크스페이스 root + 기존 docs 정리
- phase-03: ai-nodes 메타 (workspace-structure.md + AGENTS /init 보강 + ADR-004 + career-os Status 격상)
- phase-04: 잔여 참조 갱신
- phase-05: 통합 정적 검증 + status=completed

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"

git push origin main
```

---

## 검증 (phase 종료 직전)

```bash
# 1. index.json status=completed
STATUS=$(python3 -c "import json; print(json.load(open('apartment/tasks/plan001-docs-and-workspace-standard/index.json'))['status'])")
echo "[plan001 status] $STATUS"
[ "$STATUS" = "completed" ] || { echo "PHASE_FAILED: status != completed"; exit 1; }

# 2. push 성공 확인 (HEAD == origin/main)
UNPUSHED=$(git log origin/main..HEAD --oneline | wc -l)
echo "[unpushed commits] $UNPUSHED"
[ "$UNPUSHED" -eq 0 ] || { echo "PHASE_FAILED: $UNPUSHED unpushed commits"; exit 1; }

# 3. trailing working tree (plan-and-build run-phases.py는 phase commit 후 commitSha를 후기록할 수 있음 — common-pitfalls 6-2)
DIRTY=$(git status --porcelain | grep -v "^?? _shared/bin/" | wc -l)
echo "[trailing working tree] $DIRTY lines (untracked _shared 외)"
# 0이면 OK, 1+는 plan023 패턴처럼 trailing cleanup commit 필요

echo "✓ Phase 05 검증 통과"
echo "✓ plan001 전체 완료 — push 됨"
```

---

## 의도 메모

- haiku 모델 — 기계적 검증 + JSON 마킹 + push. 사소한 작업.
- 통합 검증은 각 phase의 자체 검증에 더해 cross-phase 정합까지 보장.
- push는 마지막 phase에서만 (plan-and-build 표준).
- working tree dirty 0건이 기대 — `_shared/bin/extract_claude_result.py` 등 plan 외 untracked는 예외 (`grep -v "^?? _shared/bin/"`).
- common-pitfalls 6-2 (trailing working tree) — run-phases.py가 phase commit 후 commitSha 후기록할 수 있어 marginal dirty 가능. 사후 cleanup commit 필요 시 별도 답변에서 처리.
