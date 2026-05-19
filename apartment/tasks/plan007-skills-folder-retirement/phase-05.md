# Phase 05 — 잔여 참조 grep + 정적 검증 + status=completed + push

**Model**: haiku
**Status**: pending

---

## 목표

plan007 전체 산출물 통합 정적 검증 + 잔여 참조 grep + `index.json status="completed"` 마킹 + `git push origin main`. 5 phase cross-validation.

**범위 외**: 본문 작성 / 갱신 (phase-01~04 완료).

---

## 본 phase 강제 주의문

- Bash 검증 명령은 *실제 실행*해야 한다. prose 응답만으로는 PHASE_FAILED (common-pitfalls 6-4).
- 통합 검증 결과를 stdout에 raw value echo로 명시 — 추정 보고 금지.
- section sigil (section mark, U+00A7) 사용 금지.

---

## 사전 cwd 설정 (run-phases.py hotfix)

```bash
cd "$(git rev-parse --show-toplevel)"
pwd  # 기대: /home/bifos/ai-nodes
```

---

## 작업 항목

### 1. 통합 정적 검증

```bash
SIGIL_CHAR=$(printf '\xc2\xa7')

# 1-A. 새 위치 자산 (apartment/scripts/<name>/ + apartment/.claude/skills/<name>/)
for skill in apartment-daily-report apartment-interior-reference-digest; do
  test -d apartment/scripts/$skill || { echo "PHASE_FAILED: apartment/scripts/$skill missing"; exit 1; }
  test -f apartment/.claude/skills/$skill/SKILL.md || { echo "PHASE_FAILED: $skill SKILL.md missing"; exit 1; }
  test -d apartment/.claude/skills/$skill/references || { echo "PHASE_FAILED: $skill references/ missing"; exit 1; }
done
echo "[1-A 분리 구조] OK"

# 1-B. apartment/skills/ 디렉터리 자체 폐기
test ! -e apartment/skills || { echo "PHASE_FAILED: apartment/skills/ 잔존"; exit 1; }
echo "[1-B apartment/skills/ 폐기] OK"

# 1-C. native skill 2개 모두 등록
test -f apartment/.claude/skills/apartment-daily-report/SKILL.md || { echo "PHASE_FAILED"; exit 1; }
test -f apartment/.claude/skills/apartment-interior-reference-digest/SKILL.md || { echo "PHASE_FAILED"; exit 1; }
echo "[1-C native skill 2개] OK"

# 1-D. shell syntax (모든 *.sh)
for f in apartment/scripts/apartment-daily-report/*.sh apartment/scripts/apartment-interior-reference-digest/*.sh; do
  bash -n "$f" || { echo "PHASE_FAILED: $f syntax 오류"; exit 1; }
done
echo "[1-D shell syntax] OK"

# 1-E. 옛 path 인용 잔재 전수 (apartment 영역)
LEFT=$(grep -rln "apartment/skills/apartment" \
  apartment/scripts/ apartment/.claude/ apartment/docs/ apartment/AGENTS.md \
  2>/dev/null | wc -l)
echo "[1-E 옛 apartment/skills 인용 잔재] $LEFT"
[ "$LEFT" -eq 0 ] || { echo "PHASE_FAILED: 잔재 $LEFT 건"; grep -rln "apartment/skills/apartment" apartment/scripts/ apartment/.claude/ apartment/docs/ apartment/AGENTS.md 2>/dev/null; exit 1; }

# 1-F. ai-nodes 메타 갱신 검증
grep -q "ADR-006" docs/workspace-structure.md || { echo "PHASE_FAILED: workspace-structure.md ADR-006 인용 누락"; exit 1; }
grep -q "ADR-006" AGENTS.md || { echo "PHASE_FAILED: ai-nodes AGENTS.md ADR-006 인용 누락"; exit 1; }
echo "[1-F ai-nodes 메타] OK"

# 1-G. section sigil 전수
for f in apartment/AGENTS.md \
         apartment/docs/prd.md apartment/docs/data-schema.md apartment/docs/flow.md apartment/docs/code-architecture.md apartment/docs/adr.md \
         apartment/.claude/skills/apartment-daily-report/SKILL.md apartment/.claude/skills/apartment-interior-reference-digest/SKILL.md \
         docs/workspace-structure.md docs/adr.md AGENTS.md; do
  COUNT=$(grep -c "$SIGIL_CHAR" "$f" 2>/dev/null || echo 0)
  [ "$COUNT" -eq 0 ] || { echo "PHASE_FAILED: $f sigil 잔재 $COUNT"; exit 1; }
done
echo "[1-G sigil 전수] 0건"

echo "=== 통합 정적 검증 통과 ==="
```

### 2. index.json status="completed" 마킹

```bash
python3 - <<'PY'
import json, pathlib
from datetime import datetime, timezone

p = pathlib.Path("apartment/tasks/plan007-skills-folder-retirement/index.json")
data = json.loads(p.read_text())
data["status"] = "completed"
data["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
print(f"[index.json] status={data['status']} updated_at={data['updated_at']}")
PY
```

검증:

```bash
STATUS=$(python3 -c "import json; print(json.load(open('apartment/tasks/plan007-skills-folder-retirement/index.json'))['status'])")
echo "[plan007 status] $STATUS"
[ "$STATUS" = "completed" ] || { echo "PHASE_FAILED: status != completed"; exit 1; }
```

### 3. status commit + push

```bash
git add apartment/tasks/plan007-skills-folder-retirement/index.json
git commit -m "$(cat <<'EOF'
task(apartment): plan007 index.json status=completed (phase-05)

plan007 5 phase 모두 통과:
- phase-01: apartment-daily-report 마이그 (scripts 이동 + SKILL/references 이동 + SKILL_ROOT 정정 + symlink 폐기)
- phase-02: apartment-interior-reference-digest 마이그 + native 등록 + apartment/skills/ 디렉터리 폐기
- phase-03: apartment 5문서 + AGENTS.md 진입점 path 갱신
- phase-04: ai-nodes 메타 (workspace-structure + AGENTS 1-1 비대칭 표 제거, ADR-006 적용)
- phase-05: 통합 정적 검증 + status=completed

ADR-004 + ai-nodes ADR-006 적용 완료. 모든 apartment skill 분리 패턴.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"

git push origin main
```

---

## 검증 (phase 종료 직전)

```bash
# 1. index.json status=completed
STATUS=$(python3 -c "import json; print(json.load(open('apartment/tasks/plan007-skills-folder-retirement/index.json'))['status'])")
echo "[plan007 status] $STATUS"
[ "$STATUS" = "completed" ] || { echo "PHASE_FAILED: status != completed"; exit 1; }

# 2. push 성공 확인 (HEAD == origin/main)
UNPUSHED=$(git log origin/main..HEAD --oneline | wc -l)
echo "[unpushed commits] $UNPUSHED"
[ "$UNPUSHED" -eq 0 ] || { echo "PHASE_FAILED: $UNPUSHED unpushed commits"; exit 1; }

echo "✓ Phase 05 검증 통과"
echo "✓ plan007 전체 완료 — apartment skills/ 폐기 + .claude/skills/ 본체화 + ai-nodes 분리 표준 격상"
```

---

## 의도 메모

- haiku 모델 — 기계적 검증 + JSON 마킹 + push.
- 통합 검증: phase별 자체 검증 + cross-phase 정합.
- push는 마지막 phase에서만 (plan-and-build 표준).
- 본 phase 후 apartment 워크스페이스 = 완전 분리 패턴. career-os와 같은 표준. ai-nodes ADR-006 적용 사례 완성.
