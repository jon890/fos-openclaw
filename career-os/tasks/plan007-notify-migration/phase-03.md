# Phase 03 — skills/plan-and-build/scripts/run-phases.py 갱신

**Model**: sonnet
**Status**: pending

---

## 목표

`run-phases.py`의 notify 통합을 ADR-021에 맞춰 갱신. `find_notify_script`가 `skills/*/scripts/notify_discord.sh` glob을 폐기하고 항상 `_shared/lib/notify_discord.ts`를 호출. subprocess 호출 시 `bun --env-file=<workspace>/.env` 옵션 전달.

**범위 외**: `_shared/lib/notify_discord.ts` 본체 (phase-01), career-os caller (phase-02), apartment 마이그레이션 (별도 plan).

## 관련 docs (실행 전 필수 읽기)

- `career-os/docs/adr.md` ADR-021 — 본 phase의 결정 출처. caller 호출 패턴 명시.
- `_shared/lib/notify_discord.ts` (phase-01 산출물) — run-phases.py가 호출할 대상.

## 현재 상태 파악

```bash
cd /home/bifos/ai-nodes
sed -n '55,85p' skills/plan-and-build/scripts/run-phases.py
```

기대 결과 (현재):
```python
def find_notify_script(workspace: Path) -> Path | None:
    candidates = list(workspace.glob("skills/*/scripts/notify_discord.sh"))
    return candidates[0] if candidates else None

def notify(message: str, notify_script: Path | None) -> None:
    if notify_script is None:
        return
    try:
        subprocess.run(
            [str(notify_script), message],
            timeout=10,
            check=False,
            capture_output=True,
        )
    except Exception as e:
        ...
```

`workspace.glob` 패턴이 `.sh`만 찾으므로 plan004 phase-05 이후 항상 None 반환 → 알림 자체가 발송 안 됨.

## 작업 항목

### 1. `find_notify_script` 폐기 + 단일 경로 상수 도입

`run-phases.py` 상단에 ai-nodes 루트 경로 + notify.ts 절대경로 상수 추가:

```python
AI_NODES_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # skills/plan-and-build/scripts/ → ai-nodes
NOTIFY_TS = AI_NODES_ROOT / "_shared" / "lib" / "notify_discord.ts"
```

(정확한 상위 디렉터리 수는 실제 경로 보고 phase Claude가 조정 — `skills/plan-and-build/scripts/run-phases.py`라면 `.parent` 3번이면 ai-nodes 루트.)

검증 명령:

```bash
cd /home/bifos/ai-nodes
python3 -c "
from pathlib import Path
script = Path('skills/plan-and-build/scripts/run-phases.py').resolve()
ai_nodes = script.parent.parent.parent.parent
assert (ai_nodes / '_shared' / 'lib' / 'notify_discord.ts').exists(), f'경로 검증 실패: {ai_nodes}'
print('AI_NODES_ROOT =', ai_nodes)
"
```

### 2. `notify` 함수 갱신

호출 형태:

```python
def notify(message: str, workspace: Path) -> None:
    """ADR-021. _shared/lib/notify_discord.ts를 bun --env-file=<ws>/.env로 호출.
    
    .env 파일이 없거나 DISCORD_CHANNEL_ID env가 누락이면 ts가 exit 1.
    notify 자체는 phase 진행을 막지 않음 — exit code 무시.
    """
    env_file = workspace / ".env"
    if not env_file.exists():
        # .env 없으면 알림 발송 불가 — silent skip (caller 깨뜨리지 않음).
        return
    try:
        subprocess.run(
            ["bun", f"--env-file={env_file}", "run", str(NOTIFY_TS), message],
            timeout=15,
            check=False,
            capture_output=True,
        )
    except Exception as e:
        print(f"[warn] 알림 실패: {e}", flush=True)
```

`notify_script` 파라미터 제거. `workspace`만 받음. 모든 caller 호출도 시그니처 갱신:

```python
# 기존:
notify(f"[진행] ...", notify_script)
# 갱신:
notify(f"[진행] ...", workspace)
```

`find_notify_script` 호출 1곳 (`notify_script = find_notify_script(workspace)`) 제거. 함수 정의 자체도 제거.

### 3. 갱신 자동 검증

```bash
cd /home/bifos/ai-nodes

# 1. find_notify_script 잔존 0건
grep -nE "find_notify_script|notify_discord\.sh" skills/plan-and-build/scripts/run-phases.py 2>&1 | tee /tmp/plan007-phase03-residual.log
[ -s /tmp/plan007-phase03-residual.log ] && { echo "PHASE_FAILED: find_notify_script 또는 .sh 잔존"; cat /tmp/plan007-phase03-residual.log; exit 1; }

# 2. bun + --env-file 호출 패턴 등장
grep -qF "bun" skills/plan-and-build/scripts/run-phases.py || { echo "PHASE_FAILED: bun 호출 없음"; exit 1; }
grep -qF "--env-file" skills/plan-and-build/scripts/run-phases.py || { echo "PHASE_FAILED: --env-file 옵션 없음"; exit 1; }
grep -qF "_shared/lib/notify_discord.ts" skills/plan-and-build/scripts/run-phases.py || { echo "PHASE_FAILED: notify_discord.ts 참조 없음"; exit 1; }

# 3. python syntax
python3 -m py_compile skills/plan-and-build/scripts/run-phases.py || { echo "PHASE_FAILED: py_compile"; exit 1; }

# 4. run-phases.py --help 또는 인자 없이 호출 (smoke)
python3 skills/plan-and-build/scripts/run-phases.py 2>&1 | grep -qE "usage|task-dir" || { echo "PHASE_FAILED: run-phases.py usage 메시지 깨짐"; exit 1; }

echo "phase-03 검증 통과"
```

### 4. 실제 동작 smoke — career-os/.env가 있을 때만

```bash
cd /home/bifos/ai-nodes
if [ -f career-os/.env ] && grep -q "^DISCORD_CHANNEL_ID=." career-os/.env; then
  # Bash 도구로 직접 실행 — 실제 알림이 사용자 Discord 채널에 발송됨
  echo "[smoke] 실제 알림 발송 시도 (사용자 채널에 메시지 도달 예상)"
  python3 -c "
import sys
sys.path.insert(0, 'skills/plan-and-build/scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('run_phases', 'skills/plan-and-build/scripts/run-phases.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
from pathlib import Path
mod.notify('[plan007 phase-03 smoke] notify pipeline 복구 테스트', Path('career-os'))
print('smoke: notify 함수 호출 완료 (실제 발송 여부는 Discord 채널 확인)')
"
else
  echo "[smoke] career-os/.env 또는 DISCORD_CHANNEL_ID 미설정 — 실제 발송 smoke 스킵 (사용자가 phase-04 끝나고 수동 확인)"
fi
```

`career-os/.env`가 없거나 값이 비어 있으면 smoke 스킵 — `PHASE_BLOCKED`가 아닌 정상 skip (사용자가 .env 직접 처리 안 한 경우 정상).

## Critical Files

| 파일 | 변경 |
|---|---|
| `skills/plan-and-build/scripts/run-phases.py` | `find_notify_script` 제거 + `notify` 함수 갱신 + caller 호출 시그니처 일괄 갱신 |

다른 파일은 손대지 않는다.

## 커밋

```bash
cd /home/bifos/ai-nodes
git add skills/plan-and-build/scripts/run-phases.py
git commit -m "refactor(plan-and-build): run-phases.py notify 통합을 _shared/lib/notify_discord.ts로 (plan007 phase-03)

ADR-021. plan004 phase-05 이후 find_notify_script가 .sh glob만 찾아
항상 None 반환 → 알림 자체가 발송 안 됨. _shared/lib/notify_discord.ts
직접 호출 패턴으로 통합.

- find_notify_script 함수 제거
- notify(message, workspace) 시그니처 갱신 — workspace의 .env를
  --env-file로 전달
- 모든 caller 호출 시그니처 갱신

.env 부재 시 silent skip — caller 깨뜨리지 않음."
```

push는 phase-04.

## Blocked 조건

**중요 — exit code 명시**: 아래 어느 마커든 출력만 하지 말고 반드시 `sys.exit(1)` (FAILED) 또는 `sys.exit(2)` (BLOCKED) — shell에서는 `exit 1` / `exit 2` — 비-0 exit code로 종료한다. 본문의 모든 검증 bash 블록은 반드시 Bash 도구로 직접 실행한다 (prose로 마커만 출력하면 run-phases.py가 success로 잘못 처리 — plan001/plan004 사례).

- `_shared/lib/notify_discord.ts` 부재 시 `PHASE_BLOCKED: phase-01 미완` + `exit 2`
- `find_notify_script` 잔존 → `PHASE_FAILED: 잔존 함수` + `exit 1`
- `.sh` 참조 잔존 → `PHASE_FAILED: 옛 .sh 참조` + `exit 1`
- py_compile 실패 → `PHASE_FAILED: syntax` + `exit 1`

## 의도 메모

- `find_notify_script`를 *함수째* 제거 — additive 갱신 회피 (common-pitfalls 6-5). 단일 경로 상수로 단순화.
- `.env` 부재 시 silent skip은 ts의 `DISCORD_CHANNEL_ID` 누락 exit 1과 다른 layer — run-phases.py는 caller 안전성 우선. .env 없는 환경에서도 phase 진행은 막지 않음.
- 실제 발송 smoke는 사용자 채널에 메시지 도달 — phase가 한 번 시도하고 결과는 사용자 수동 확인.
