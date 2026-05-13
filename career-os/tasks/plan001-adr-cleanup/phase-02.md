# Phase 02 — 통합 검증 + status=completed + push

**Model**: haiku
**Status**: pending

---

## 목표

Phase 01의 ADR 슬림화 산출물을 통합 검증하고, `index.json`의 `status`를 `completed`로 마킹한 뒤 push까지 완료한다.

**범위 외**: 새 코드 변경, 새 ADR 추가, 다른 파일 수정. 이 phase는 검증 + 메타데이터 마킹 + push만.

---

## 관련 docs

- `career-os/docs/adr.md` — Phase 01에서 슬림화된 결과.
- `career-os/tasks/plan001-adr-cleanup/index.json` — status 마킹 대상.

---

## 작업 항목

### 1. 검증 명령 실행

Phase 01의 검증 섹션과 동일하지만, **자체적으로 한 번 더** 돌려서 일관성 확인.

```bash
cd /home/bifos/ai-nodes

# 1. adr.md 줄 수
echo "[adr.md lines]"; wc -l career-os/docs/adr.md

# 2. 코드 펜스 카운트
echo "[fence count]"; grep -c '^```' career-os/docs/adr.md

# 3. 금지 섹션 카운트 (0이어야 함)
echo "[forbidden sections]"; grep -c "^## 변경 이력\|^## Follow-up\|^## Future enhancements\|^## 적용 대상" career-os/docs/adr.md

# 4. ADR 헤더 수 (15여야 함)
echo "[ADR headers]"; grep -c "^## ADR-" career-os/docs/adr.md
```

기대:
- adr.md 줄 수: 250 이하 (현재 ~400대에서 줄었어야)
- 코드 펜스: 0 또는 1-2 (의도된 짧은 인용만)
- 금지 섹션: 0
- ADR 헤더: 15

위 4개 중 하나라도 어긋나면 `PHASE_FAILED: 검증 항목 N 미충족 (실제값=X)` 출력 후 종료.

### 2. index.json의 status 마킹

```bash
python3 - <<'PY'
import json
from pathlib import Path
p = Path("career-os/tasks/plan001-adr-cleanup/index.json")
data = json.loads(p.read_text(encoding="utf-8"))
data["status"] = "completed"
data["current_phase"] = 2
for phase in data["phases"]:
    phase["status"] = "completed"
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("[index.json] marked completed")
PY
```

`run-phases.py`도 자동으로 한 번 더 마킹하지만 phase 본문에서 명시적으로 한 번 — `common-pitfalls.md`의 표준 패턴.

### 3. 커밋 + push

```bash
git add career-os/tasks/plan001-adr-cleanup/index.json
git commit -m "task(career-os): plan001-adr-cleanup 완료 마킹"
git push origin main
```

push 실패 시 `PHASE_FAILED: push 실패 (<git stderr>)` 출력 후 종료.

---

## Critical Files

| 파일 | 변경 |
|---|---|
| `career-os/tasks/plan001-adr-cleanup/index.json` | status 마킹 (in-place) |

다른 파일은 손대지 않는다.

---

## 검증

위 작업 1번이 검증 자체. 추가 smoke:

```bash
# index.json이 valid JSON인지
python3 -c "import json; json.load(open('career-os/tasks/plan001-adr-cleanup/index.json'))" && echo "JSON ok"

# 모든 phase status가 completed
python3 - <<'PY'
import json
data = json.load(open("career-os/tasks/plan001-adr-cleanup/index.json"))
assert data["status"] == "completed", f"task status={data['status']}"
for p in data["phases"]:
    assert p["status"] == "completed", f"phase {p['number']} status={p['status']}"
print("all phases completed")
PY
```

---

## 의도 메모 (왜)

- 검증을 phase로 분리해서 슬림화 작업 자체의 실수가 통합 검증 단계에서 잡히게.
- index.json의 status 마킹은 run-phases.py가 자동 처리하지만 명시적으로 한 번 더 — 표준 패턴 + run-phases.py 외 경로(예: 수동 실행)에서도 일관성.

## Blocked 조건

- adr.md 검증 실패 시 `PHASE_FAILED`. 사람이 phase-01의 산출물을 손봐야 함.
- push 권한 없으면 `PHASE_BLOCKED: push 권한 없음`. 사람이 직접 push.
