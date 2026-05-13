# Phase 04 — 통합 smoke + 잔재 grep + push + trailing cleanup

**Model**: sonnet
**Status**: pending

---

## 목표

phase-01/02/03 산출물을 통합 검증. 옛 webhook / `.sh` 잔재 0건 확인. `index.json` status=completed 마킹. 모든 커밋을 origin/main에 push. run-phases.py 후처리로 워킹 트리에 남는 trailing 변경 정리.

**범위 외**: apartment 마이그레이션 (별도 plan), 사용자 채널에 실제 알림이 도달했는지 (사용자 수동 확인).

## 관련 docs

- `career-os/docs/adr.md` ADR-021 — 본 plan 전체 결정.
- `career-os/tasks/plan007-notify-migration/index.json` — status 마킹 대상.

## 작업 항목

### 1. 통합 smoke — 잔재 0건 검증

```bash
cd /home/bifos/ai-nodes

# 1-1. webhook 잔재 0건 (DISCORD_WEBHOOK_URL은 plan007 이후 절대 안 나와야)
hits=$(grep -rln "DISCORD_WEBHOOK_URL" _shared/ career-os/ skills/plan-and-build/ 2>/dev/null | grep -v node_modules | wc -l)
[ "$hits" -eq 0 ] || { echo "PHASE_FAILED: DISCORD_WEBHOOK_URL 잔존 $hits건"; grep -rln "DISCORD_WEBHOOK_URL" _shared/ career-os/ skills/plan-and-build/ | grep -v node_modules; exit 1; }

# 1-2. notify_discord.sh 코드 참조 잔존 0건 (career-os + _shared + plan-and-build 영역)
# apartment의 옛 .sh는 아직 살아있으므로 apartment/ 안 잔재는 의도된 보존 — 본 검사에서 제외
hits=$(grep -rln "notify_discord\.sh" _shared/ career-os/scripts/ skills/plan-and-build/ 2>/dev/null | wc -l)
[ "$hits" -eq 0 ] || { echo "PHASE_FAILED: notify_discord.sh 참조 잔존 $hits건 (career-os/_shared/plan-and-build 한정)"; grep -rln "notify_discord\.sh" _shared/ career-os/scripts/ skills/plan-and-build/; exit 1; }

# 1-3. _shared/lib/notify_discord.ts에 openclaw 호출 + DISCORD_CHANNEL_ID 처리
grep -qF 'Bun.spawn(["openclaw"' _shared/lib/notify_discord.ts || { echo "PHASE_FAILED: notify_discord.ts openclaw subprocess 누락"; exit 1; }
grep -qF "DISCORD_CHANNEL_ID" _shared/lib/notify_discord.ts || { echo "PHASE_FAILED: notify_discord.ts DISCORD_CHANNEL_ID 처리 누락"; exit 1; }

# 1-4. career-os caller가 --env-file 모두 사용
for f in $(grep -rln "notify_discord\.ts" career-os/ 2>/dev/null | grep -v sources/fos-study); do
  if grep -F "notify_discord.ts" "$f" | grep -vF "env-file" >/dev/null; then
    echo "PHASE_FAILED: $f 에 --env-file 없는 호출 잔존"
    grep -nF "notify_discord.ts" "$f"
    exit 1
  fi
done

# 1-5. run-phases.py의 .sh glob / find_notify_script 잔존 0건
hits=$(grep -nE "find_notify_script|notify_discord\.sh" skills/plan-and-build/scripts/run-phases.py 2>/dev/null | wc -l)
[ "$hits" -eq 0 ] || { echo "PHASE_FAILED: run-phases.py 잔재 $hits건"; grep -nE "find_notify_script|notify_discord\.sh" skills/plan-and-build/scripts/run-phases.py; exit 1; }

# 1-6. career-os/.env.example 존재 + 옛 위치 잔존 0건
[ -f career-os/.env.example ] || { echo "PHASE_FAILED: career-os/.env.example 누락"; exit 1; }
[ ! -f career-os/config/.env.example ] || { echo "PHASE_FAILED: 옛 career-os/config/.env.example 잔존"; exit 1; }

echo "잔재 검증 6개 모두 통과"
```

### 2. 문법 검증

```bash
cd /home/bifos/ai-nodes

# 2-1. tsc
bunx tsc --noEmit
[ $? -eq 0 ] || { echo "PHASE_FAILED: tsc"; exit 1; }

# 2-2. python (run-phases.py)
python3 -m py_compile skills/plan-and-build/scripts/run-phases.py || { echo "PHASE_FAILED: run-phases.py py_compile"; exit 1; }

# 2-3. career-os caller bash 문법 일괄 (notify_discord.ts 호출 파일만)
for f in $(grep -rln "notify_discord\.ts" career-os/ 2>/dev/null | grep -v sources/fos-study | grep '\.sh$'); do
  bash -n "$f" || { echo "PHASE_FAILED: $f bash syntax"; exit 1; }
done

echo "문법 검증 통과"
```

### 3. index.json status=completed 마킹

```bash
cd /home/bifos/ai-nodes
python3 - <<'PY'
import json
from pathlib import Path
p = Path("career-os/tasks/plan007-notify-migration/index.json")
data = json.loads(p.read_text(encoding="utf-8"))
data["status"] = "completed"
data["current_phase"] = 4
for phase in data["phases"]:
    phase["status"] = "completed"
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("[index.json] marked completed")
PY
```

### 4. 최종 commit + push

phase-01/02/03이 각자 commit했으므로 본 phase는 index.json만:

```bash
cd /home/bifos/ai-nodes
git add career-os/tasks/plan007-notify-migration/index.json
git commit -m "task(career-os): plan007-notify-migration 완료 마킹"
git push origin main
```

push 실패 시 `PHASE_FAILED: push (<stderr>)` 출력 + exit 1.

### 5. trailing cleanup — run-phases.py 후처리 변경 처리

run-phases.py가 phase-04 commit 직후 index.json에 commitSha + updated_at 후기록 → 워킹 트리 dirty. 추가 cleanup commit:

```bash
cd /home/bifos/ai-nodes

# 트레일링 변경 감지
if [ -n "$(git status --porcelain career-os/tasks/plan007-notify-migration/index.json)" ]; then
  python3 -c "
from pathlib import Path
p = Path('career-os/tasks/plan007-notify-migration/index.json')
text = p.read_text(encoding='utf-8')
if not text.endswith('\n'):
    p.write_text(text + '\n', encoding='utf-8')
"
  git add career-os/tasks/plan007-notify-migration/index.json
  git commit -m "task(career-os): plan007 index.json에 phase-04 commitSha 후기록 + EOL 보정"
  git push origin main
fi

# 최종 cleanliness 검증
[ -z "$(git status --porcelain career-os/tasks/plan007-notify-migration/)" ] || { echo "PHASE_FAILED: trailing cleanup 후에도 잔재"; git status --porcelain; exit 1; }
```

(working tree에 사용자 작업이나 다른 plan trailing이 있을 수 있으므로 `git status --porcelain`은 plan007 task 경로 한정.)

### 6. 사용자 수동 확인 안내 (phase 외)

phase 종료 후 stdout에 다음 안내 출력:

```
plan007-notify-migration 완료. 사용자가 환경에서 수행 필요:
1. mv career-os/config/.env career-os/.env  (없으면 career-os/.env.example 보고 직접 생성)
2. DISCORD_CHANNEL_ID 값 입력
3. 다음 plan 또는 임의 dispatcher 실행으로 알림이 실제 Discord 채널에 도달하는지 확인
4. apartment 마이그레이션은 별도 plan으로 후속 진행
```

## Critical Files

| 파일 | 변경 |
|---|---|
| `career-os/tasks/plan007-notify-migration/index.json` | status 마킹 (in-place) |

`index.json` 외 다른 파일은 phase-01/02/03이 이미 commit. trailing cleanup 단계에서만 index.json 한 번 더.

## Blocked 조건

**중요 — exit code 명시**: 아래 어느 마커든 출력만 하지 말고 반드시 `sys.exit(1)` (FAILED) 또는 `sys.exit(2)` (BLOCKED) — shell에서는 `exit 1` / `exit 2` — 비-0 exit code로 종료한다. 본문의 모든 검증 bash 블록은 반드시 Bash 도구로 직접 실행한다 (prose로 마커만 출력하면 run-phases.py가 success로 잘못 처리 — plan001/plan004 사례).

- 잔재 검증 1-1~1-6 중 하나 실패 → `PHASE_FAILED: 잔재 <항목>` + `exit 1`
- 문법 검증 실패 → `PHASE_FAILED: <tsc/py/bash>` + `exit 1`
- push 실패 → `PHASE_FAILED: push (<stderr>)` + `exit 1`
- trailing cleanup 후에도 plan007 경로에 dirty 잔존 → `PHASE_FAILED: trailing cleanup 미완` + `exit 1`
- phase-01/02/03 commit이 없음 → `PHASE_BLOCKED: 선행 phase 미완` + `exit 2`

## 의도 메모

- 잔재 검증은 destructive 검증 (`grep -vF`, 횟수 비교) — additive 갱신만으로 통과 못 함 (common-pitfalls 6-5).
- 실제 알림 발송 smoke는 phase에서 안 함 — 사용자 채널 영향. 사용자 수동 확인 안내만.
- apartment 잔재는 본 phase 검사에서 제외 — 워크스페이스 격리 (ADR-021).
- trailing cleanup은 plan001~005에서 매번 발생한 패턴 (common-pitfalls 6-2). 본 phase가 자체 처리.
