# Phase 03 — 통합 정적 검증 + status=completed + push

**Model**: haiku
**Status**: pending

---

## 목표

plan003 전체 산출물 통합 정적 검증 + `index.json status="completed"` + `git push origin main`.

**범위 외**: 본문 작성 / 갱신 (phase-01/02 완료).

---

## 본 phase 강제 주의문

- Bash 검증 명령은 *실제 실행*. prose 응답만으로는 PHASE_FAILED (common-pitfalls 6-4).
- 검증 결과를 stdout raw value echo로 명시 — 추정 보고 금지.
- section sigil (U+00A7) 사용 금지.

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

# 1-A. ts file 4개 존재
for f in apartment/scripts/apartment-daily-report/naver_api_schemas.ts \
         apartment/scripts/apartment-daily-report/collect_naver_api.ts \
         apartment/scripts/apartment-daily-report/collect_sources.ts; do
  test -f "$f" || { echo "PHASE_FAILED: $f missing"; exit 1; }
done
echo "[1-A ts file] OK"

# 1-B. type/syntax
for f in apartment/scripts/apartment-daily-report/naver_api_schemas.ts \
         apartment/scripts/apartment-daily-report/collect_naver_api.ts \
         apartment/scripts/apartment-daily-report/collect_sources.ts; do
  bun build --no-bundle "$f" > /dev/null 2>&1 || { echo "PHASE_FAILED: $f type"; exit 1; }
done
echo "[1-B type] OK"

# 1-C. shell syntax
bash -n apartment/scripts/apartment-daily-report/run_report.sh || { echo "PHASE_FAILED: run_report syntax"; exit 1; }
echo "[1-C shell] OK"

# 1-D. 옛 Python file 부재 (git tracked + filesystem)
for f in apartment/scripts/apartment-daily-report/collect_sources.py \
         apartment/scripts/apartment-daily-report/collect_naver_api.py; do
  test ! -e "$f" || { echo "PHASE_FAILED: $f 잔존"; exit 1; }
done
LEFT_TRACKED=$(git ls-files apartment/scripts/apartment-daily-report/collect_sources.py apartment/scripts/apartment-daily-report/collect_naver_api.py | wc -l)
[ "$LEFT_TRACKED" -eq 0 ] || { echo "PHASE_FAILED: git tracked 잔존 $LEFT_TRACKED"; exit 1; }
echo "[1-D 옛 Python 폐기] OK"

# 1-E. ADR-005/006/007 패턴 적용 (grep)
grep -q "Bun.fetch" apartment/scripts/apartment-daily-report/collect_naver_api.ts || { echo "PHASE_FAILED: ADR-005 미적용"; exit 1; }
grep -q "from \"./collect_naver_api\"\|from './collect_naver_api'" apartment/scripts/apartment-daily-report/collect_sources.ts || { echo "PHASE_FAILED: ADR-006 미적용"; exit 1; }
grep -q "from \"zod\"\|from 'zod'" apartment/scripts/apartment-daily-report/naver_api_schemas.ts || { echo "PHASE_FAILED: ADR-007 미적용"; exit 1; }
echo "[1-E ADR-005/006/007] OK"

# 1-F. run_report.sh bun 호출
grep -q "bun run.*collect_sources" apartment/scripts/apartment-daily-report/run_report.sh || { echo "PHASE_FAILED: run_report bun 호출 누락"; exit 1; }
echo "[1-F run_report bun] OK"

# 1-G. section sigil 전수
for f in apartment/scripts/apartment-daily-report/naver_api_schemas.ts \
         apartment/scripts/apartment-daily-report/collect_naver_api.ts \
         apartment/scripts/apartment-daily-report/collect_sources.ts \
         apartment/scripts/apartment-daily-report/run_report.sh; do
  COUNT=$(grep -c "$SIGIL_CHAR" "$f" 2>/dev/null || echo 0)
  [ "$COUNT" -eq 0 ] || { echo "PHASE_FAILED: $f sigil $COUNT"; exit 1; }
done
echo "[1-G sigil] 0건"

echo "=== 통합 정적 검증 통과 ==="
```

### 2. index.json status="completed" 마킹

```bash
python3 - <<'PY'
import json, pathlib
from datetime import datetime, timezone

p = pathlib.Path("apartment/tasks/plan003-collectors-ts-migration/index.json")
data = json.loads(p.read_text())
data["status"] = "completed"
data["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
print(f"[index.json] status={data['status']}")
PY

STATUS=$(python3 -c "import json; print(json.load(open('apartment/tasks/plan003-collectors-ts-migration/index.json'))['status'])")
[ "$STATUS" = "completed" ] || { echo "PHASE_FAILED: status != completed"; exit 1; }
```

### 3. status commit + push

```bash
git add apartment/tasks/plan003-collectors-ts-migration/index.json
git commit -m "$(cat <<'EOF'
task(apartment): plan003 index.json status=completed (phase-03)

plan003 3 phase 모두 통과:
- phase-01: naver_api_schemas.ts + collect_naver_api.ts (Bun.fetch + zod + agent-browser Bun.spawn)
- phase-02: collect_sources.ts (import 통합) + run_report.sh bun 호출 + 옛 Python 2개 git rm
- phase-03: 통합 정적 검증 + status=completed

ADR-005 (Bun.fetch) + ADR-006 (import 통합) + ADR-007 (zod) 적용 완료.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"

git push origin main
```

---

## 검증 (phase 종료 직전)

```bash
STATUS=$(python3 -c "import json; print(json.load(open('apartment/tasks/plan003-collectors-ts-migration/index.json'))['status'])")
[ "$STATUS" = "completed" ] || { echo "PHASE_FAILED"; exit 1; }

UNPUSHED=$(git log origin/main..HEAD --oneline | wc -l)
[ "$UNPUSHED" -eq 0 ] || { echo "PHASE_FAILED: unpushed $UNPUSHED"; exit 1; }

echo "✓ Phase 03 통과"
echo "✓ plan003 전체 완료"
```

---

## 의도 메모

- haiku 모델 — 기계적 검증 + JSON 마킹 + push.
- ADR-005/006/007 모두 grep으로 *코드 적용 검증* 포함.
- push는 마지막 phase에서만 (plan-and-build 표준).
