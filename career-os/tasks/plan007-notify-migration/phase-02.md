# Phase 02 — career-os caller 갱신 + career-os/.env.example 신설

**Model**: sonnet
**Status**: pending

---

## 목표

ADR-021의 caller 호출 패턴을 career-os 안 모든 notify_discord.ts caller에 일괄 적용 (`bun run` → `bun --env-file=<ws>/.env run`). 동시에 `career-os/.env.example`을 신설해 secret 키 템플릿을 git 추적 자산으로 등록. 본 phase는 career-os 워크스페이스 한정 — apartment caller는 손대지 않는다 (워크스페이스 격리).

**범위 외**: `_shared/lib/notify_discord.ts` 본체 (phase-01에서 처리), run-phases.py (phase-03), apartment caller (별도 plan).

## 관련 docs (실행 전 필수 읽기)

- `career-os/docs/adr.md` ADR-021 — caller 호출 패턴 결정.
- `career-os/docs/data-schema.md` `.env / Secrets` 섹션 — `.env` / `.env.example` 위치와 스키마.
- `_shared/lib/notify_discord.ts` (phase-01 산출물) — 본 phase가 호출할 대상.

## 작업 항목

### 1. caller 식별 — grep 실측

plan006 완료 후 career-os caller는 `career-os/scripts/<skill>/` 디렉터리에 분포. 정확한 호출 위치 grep:

```bash
cd /home/bifos/ai-nodes
echo "=== notify_discord.ts 호출 위치 ==="
grep -rln "notify_discord\.ts" career-os/ 2>/dev/null | grep -v sources/fos-study | tee /tmp/plan007-phase02-callers.txt
count=$(wc -l < /tmp/plan007-phase02-callers.txt)
[ "$count" -ge 1 ] || { echo "PHASE_FAILED: caller 0건 — plan004 phase-05 caller 갱신 결과가 사라졌거나 grep 패턴 오류"; exit 1; }
echo "caller $count건"
```

각 파일에서 현재 호출 패턴 sample 확인:

```bash
for f in $(cat /tmp/plan007-phase02-callers.txt); do
  echo "--- $f ---"
  grep -nF "notify_discord.ts" "$f" | head -3
done
```

### 2. 호출 패턴 갱신

plan004 phase-05가 박은 기존 패턴 (예시):
```bash
bun run "$HOME/ai-nodes/_shared/lib/notify_discord.ts" "<message>"
```

ADR-021의 새 패턴:
```bash
bun --env-file="$AI_NODES_ROOT/career-os/.env" run "$AI_NODES_ROOT/_shared/lib/notify_discord.ts" "<message>"
```

또는 변수화:
```bash
WS_ROOT="$AI_NODES_ROOT/career-os"   # 또는 dispatcher 진입점에서 export
SHARED_LIB="$AI_NODES_ROOT/_shared/lib/notify_discord.ts"
NOTIFY="bun --env-file=$WS_ROOT/.env run $SHARED_LIB"
$NOTIFY "<message>"
```

phase 실행 Claude는 각 caller 파일에서 다음을 처리:

- 단순 호출인 곳: `bun run "<path>/notify_discord.ts"` → `bun --env-file="$WS_ROOT/.env" run "<path>/notify_discord.ts"` 형태로 갱신. `$WS_ROOT`가 정의되지 않은 caller는 `"$HOME/ai-nodes/career-os/.env"` 절대경로 사용 (caller가 자기 워크스페이스 root를 알고 있다는 가정 — career-os 한정 안전).
- `$NOTIFY_SCRIPT` / `NOTIFY=` 변수 정의가 있는 곳: 변수 정의 자체를 갱신.
- `--media`가 필요한 호출(현재 없을 가능성 큼)이 발견되면 `bun --env-file=... run <ts> --media <path> "<msg>"` 패턴 사용.

### 3. dispatcher (`run_now.sh`)의 `run_tracked()` 헬퍼

plan006 후 위치: `career-os/scripts/command-router/run_now.sh`. `run_tracked()` 안에 notify 호출이 있을 가능성. 동일 패턴으로 갱신.

```bash
cd /home/bifos/ai-nodes
grep -n "notify\|NOTIFY" career-os/scripts/command-router/run_now.sh 2>/dev/null | head -10
```

찾은 호출을 ADR-021 패턴으로 갱신.

### 4. `career-os/.env.example` 신설

```bash
cd /home/bifos/ai-nodes
cat > career-os/.env.example <<'EOF'
# Discord 채널 ID (필수 — notify_discord.ts가 ADR-021 정책으로 이 값을 요구)
DISCORD_CHANNEL_ID=

# fos-study publish용 GitHub API (study-pack / question-bank / master 실행 시 필요)
GITHUB_TOKEN=
GITHUB_REPO_OWNER=jon890
GITHUB_REPO_NAME=fos-study
GITHUB_REPO_BRANCH=main
EOF
```

`.env.example`은 git 추적 (ai-nodes 루트 `.gitignore`의 `!.env.example` 예외).

### 5. 옛 `career-os/config/.env.example` 정리 (있으면)

```bash
cd /home/bifos/ai-nodes
if [ -f career-os/config/.env.example ]; then
  git rm career-os/config/.env.example
  echo "옛 config/.env.example 제거"
fi
```

`career-os/config/.env` 자체는 git에 없으므로 git rm 대상 아님. 사용자가 자기 환경에서 `mv career-os/config/.env career-os/.env` 수동 처리.

## Critical Files

| 파일 | 변경 |
|---|---|
| `career-os/scripts/<skill>/*.sh` (캘러 다수) | notify_discord.ts 호출 패턴 갱신 (`bun run` → `bun --env-file=<ws>/.env run`) |
| `career-os/.env.example` | 신규 |
| `career-os/config/.env.example` | git rm (존재 시) |

다른 파일 (`_shared/lib/`, `_shared/types/`, run-phases.py)은 손대지 않는다. apartment 워크스페이스 절대 안 만진다.

## 검증

```bash
cd /home/bifos/ai-nodes

# 1. .env.example 신설 확인
[ -f career-os/.env.example ] || { echo "PHASE_FAILED: .env.example 누락"; exit 1; }
grep -q "^DISCORD_CHANNEL_ID=" career-os/.env.example || { echo "PHASE_FAILED: .env.example DISCORD_CHANNEL_ID 누락"; exit 1; }

# 2. 옛 위치 잔재 없음
[ ! -f career-os/config/.env.example ] || { echo "PHASE_FAILED: 옛 config/.env.example 잔존"; exit 1; }

# 3. 모든 notify_discord.ts 호출이 --env-file 패턴 사용
echo "=== --env-file 없는 호출 (잔존하면 안 됨) ==="
bad=$(grep -rln "notify_discord\.ts" career-os/ 2>/dev/null | grep -v sources/fos-study | \
  xargs -I{} bash -c 'grep -L -- "--env-file" "{}" && grep -qF "notify_discord.ts" "{}" && echo "{}"' 2>/dev/null | sort -u | wc -l)
# 위 명령은 false positive 가능 — 더 정확한 체크는 grep 패턴 직접:
for f in $(grep -rln "notify_discord\.ts" career-os/ 2>/dev/null | grep -v sources/fos-study); do
  if grep -F "notify_discord.ts" "$f" | grep -vF "env-file" >/dev/null; then
    echo "PHASE_FAILED: $f 에 --env-file 없는 notify_discord.ts 호출 잔존"
    grep -nF "notify_discord.ts" "$f"
    exit 1
  fi
done

# 4. caller bash 문법
for f in $(grep -rln "notify_discord\.ts" career-os/ 2>/dev/null | grep -v sources/fos-study | grep '\.sh$'); do
  bash -n "$f" || { echo "PHASE_FAILED: $f bash syntax"; exit 1; }
done

echo "phase-02 검증 통과"
```

## 커밋

```bash
cd /home/bifos/ai-nodes
git add career-os/scripts/ career-os/.env.example
git add -A career-os/config/.env.example 2>/dev/null  # 제거 반영 (존재 시)
git commit -m "refactor(career-os): notify caller 일괄 --env-file 패턴 + .env.example 신설 (plan007 phase-02)

ADR-021. career-os 안 모든 notify_discord.ts caller 호출을
'bun run' → 'bun --env-file=<ws>/.env run' 패턴으로 갱신.

- career-os/.env.example 신설 (DISCORD_CHANNEL_ID + GitHub 키)
- 옛 career-os/config/.env.example 제거 (있던 경우)
- dispatcher run_tracked() + 각 skill runner notify 호출 일괄 갱신

본 phase는 career-os 한정. apartment caller 갱신은 별도 plan.

사용자 직접 처리 안내: mv career-os/config/.env career-os/.env 후 DISCORD_CHANNEL_ID 값 입력."
```

push는 phase-04.

## 사용자 직접 처리 안내

phase 종료 후 사용자가 환경에서 수행 (phase 외, git 외):

```bash
# 1. 옛 위치에서 .env 이동
mv ~/ai-nodes/career-os/config/.env ~/ai-nodes/career-os/.env  # 없으면 직접 생성

# 2. DISCORD_CHANNEL_ID 값 입력 (편집기로 .env 열어서)

# 3. 옛 위치 디렉터리 정리 (선택)
rmdir ~/ai-nodes/career-os/config 2>/dev/null   # 비어 있으면 정리, 다른 파일 있으면 보존
```

phase-03 run-phases.py 갱신 후, phase-04 통합 smoke에서 실제 알림 발송 여부는 사용자 환경에서 확인.

## Blocked 조건

**중요 — exit code 명시**: 아래 어느 마커든 출력만 하지 말고 반드시 `sys.exit(1)` (FAILED) 또는 `sys.exit(2)` (BLOCKED) — shell에서는 `exit 1` / `exit 2` — 비-0 exit code로 종료한다. 본문의 모든 검증 bash 블록은 반드시 Bash 도구로 직접 실행한다 (prose로 마커만 출력하면 run-phases.py가 success로 잘못 처리 — plan001/plan004 사례).

- caller 0건 → `PHASE_FAILED: caller 0건` + `exit 1` (plan004 phase-05 caller 갱신 결과가 사라진 상태)
- `.env.example` 작성 실패 → `PHASE_FAILED: .env.example 작성` + `exit 1`
- `--env-file` 없는 잔존 호출 → `PHASE_FAILED: 잔존 caller` + `exit 1`
- caller bash syntax 실패 → `PHASE_FAILED: syntax (<file>)` + `exit 1`

## 의도 메모

- destructive 검증 (`grep -vF "env-file"` 사용) — 잔존 호출 0건 강제 (common-pitfalls 6-5).
- 워크스페이스 격리 강제 — `career-os/`와 `career-os/.env.example`만 변경. apartment 접근 금지.
- 사용자가 `.env` 직접 처리는 phase 책임 외. 안내만.
