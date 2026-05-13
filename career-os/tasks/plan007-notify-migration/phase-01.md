# Phase 01 — _shared/lib/notify_discord.ts 재구현 + types 갱신 + unit smoke

**Model**: sonnet
**Status**: pending

---

## 목표

ADR-021에 따라 `_shared/lib/notify_discord.ts`를 옛 `notify_discord.sh`의 실제 동작인 `openclaw message send` subprocess 호출 방식으로 재구현. `--media <path>` 옵션을 추가해 옛 `notify_discord_media.sh` 동등 동작도 흡수. `_shared/types/index.ts`의 `NotificationPayload`는 webhook payload 형태였으므로 openclaw 사용에 맞게 갱신 또는 제거. 본 phase는 라이브러리 코드만 만진다 — caller 갱신은 phase-02 책임.

**범위 외**: career-os caller 갱신 (phase-02), run-phases.py 갱신 (phase-03), apartment caller 갱신 (별도 plan).

## 관련 docs (실행 전 필수 읽기)

- `career-os/docs/adr.md` ADR-021 — 본 phase의 결정 출처. openclaw 명령 시그니처, `--media` 옵션, `DISCORD_CHANNEL_ID` env 필수 처리 모두 여기 명시.
- `_shared/lib/notify_discord.ts` 기존 (webhook fetch 구현) — 재구현 대상.
- `_shared/types/index.ts::NotificationPayload` — 인터페이스 갱신 대상.

## 옛 동작 (재구현 기준)

git history의 옛 `career-os/skills/cj-oliveyoung-java-backend-prep/scripts/notify_discord.sh` 본문 (commit `0d96c74^`에서 확인 가능):

```bash
CHANNEL_ID="${DISCORD_CHANNEL_ID:-1492521172099666021}"   # hardcoded fallback은 ADR-021로 제거
openclaw message send --channel discord --target "channel:${CHANNEL_ID}" --message "$MESSAGE" --json >/dev/null
```

옛 `apartment/skills/apartment-daily-report/scripts/notify_discord_media.sh` 본문 (현재도 존재):

```bash
openclaw message send --channel discord --target "channel:${CHANNEL_ID}" --media "$MEDIA" --json
# (선택) --message "$MESSAGE"
```

본 phase의 .ts는 위 두 동작을 단일 진입점으로 합친다.

## 작업 항목

### 1. `_shared/lib/notify_discord.ts` 전체 재작성

기존 webhook 구현 전체 덮어쓰기. Write 도구 사용 (Edit으로 부분 수정 금지 — destructive 재구현).

```typescript
#!/usr/bin/env bun
// _shared/lib/notify_discord.ts
// Discord 알림 — openclaw CLI subprocess 경유. ADR-021.
//
// Usage:
//   bun --env-file=<ws>/.env _shared/lib/notify_discord.ts [--media <path>] "<message>"
//   또는 import { notifyDiscord } from "@shared/lib/notify_discord.ts"
//
// 환경 변수:
//   DISCORD_CHANNEL_ID (필수) — 누락 시 exit 1.

const OPENCLAW_TIMEOUT_MS = 10_000;

export interface NotifyOptions {
  media?: string;
}

export async function notifyDiscord(message: string, opts?: NotifyOptions): Promise<void> {
  const channelId = process.env.DISCORD_CHANNEL_ID;
  if (!channelId) {
    console.error("[notify_discord] DISCORD_CHANNEL_ID env 누락 — 알림 발송 불가 (ADR-021)");
    process.exit(1);
  }

  const args = [
    "message", "send",
    "--channel", "discord",
    "--target", `channel:${channelId}`,
    "--message", message,
    "--json",
  ];
  if (opts?.media) {
    args.splice(args.indexOf("--message"), 0, "--media", opts.media);
  }

  const proc = Bun.spawn(["openclaw", ...args], {
    stdout: "pipe",
    stderr: "pipe",
  });

  const timeoutId = setTimeout(() => {
    proc.kill();
    console.error(`[notify_discord] openclaw timeout after ${OPENCLAW_TIMEOUT_MS}ms`);
  }, OPENCLAW_TIMEOUT_MS);

  const exitCode = await proc.exited;
  clearTimeout(timeoutId);

  if (exitCode !== 0) {
    const stderr = await new Response(proc.stderr).text();
    console.error(`[notify_discord] openclaw exit ${exitCode}: ${stderr.trim()}`);
    process.exit(1);
  }
}

// CLI 진입점
if (import.meta.main) {
  const argv = process.argv.slice(2);
  let media: string | undefined;
  const positional: string[] = [];

  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--media") {
      media = argv[++i];
    } else {
      positional.push(argv[i]);
    }
  }

  const message = positional[0];
  if (!message) {
    console.error("usage: notify_discord.ts [--media <path>] <message>");
    process.exit(1);
  }

  await notifyDiscord(message, media ? { media } : undefined);
}
```

`shebang #!/usr/bin/env bun` + `chmod +x`.

### 2. `_shared/types/index.ts` 갱신

기존 `NotificationPayload` 인터페이스는 Discord webhook payload 형태(`content`/`username`/`avatar_url`)였다. ADR-021로 openclaw subprocess 사용이라 webhook payload 형태가 더 이상 필요 없음. 다음 둘 중 선택:

(a) `NotificationPayload` 제거 — caller가 import 하는 곳이 없으면 안전.
(b) `NotifyOptions { media?: string }` 형태로 재정의 — 본 phase의 export와 일치.

phase 실행 Claude는 다음 명령으로 import 사용처 확인 후 결정:

```bash
cd /home/bifos/ai-nodes
grep -rln "NotificationPayload" --include='*.ts' . 2>/dev/null | grep -v node_modules
```

- 결과 0건이면 (a) — `NotificationPayload` export 제거.
- 결과 있으면 (b) — 새 형태로 갱신하고 caller도 같이 import 갱신.

### 3. 실행 권한 + shebang 검증

```bash
cd /home/bifos/ai-nodes
chmod +x _shared/lib/notify_discord.ts
head -1 _shared/lib/notify_discord.ts | grep -qF "#!/usr/bin/env bun" || { echo "PHASE_FAILED: shebang 누락"; exit 1; }
```

### 4. tsc 컴파일 검증

```bash
cd /home/bifos/ai-nodes
bunx tsc --noEmit 2>&1 | tee /tmp/plan007-phase01-tsc.log
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "PHASE_FAILED: tsc 에러"; cat /tmp/plan007-phase01-tsc.log; exit 1; }
```

### 5. Unit smoke — negative path 위주 (positive path는 실제 Discord 발송이라 phase에서 회피)

```bash
cd /home/bifos/ai-nodes

# 5-1. usage 메시지 (인자 누락)
out=$(bun run _shared/lib/notify_discord.ts 2>&1)
echo "$out" | grep -qF "usage:" || { echo "PHASE_FAILED: usage 메시지 없음"; echo "$out"; exit 1; }

# 5-2. DISCORD_CHANNEL_ID 누락 → exit 1
DISCORD_CHANNEL_ID="" bun run _shared/lib/notify_discord.ts "test message" 2>&1 >/tmp/plan007-phase01-noenv.log
code=$?
[ "$code" -eq 1 ] || { echo "PHASE_FAILED: env 누락 시 exit code $code expected 1"; cat /tmp/plan007-phase01-noenv.log; exit 1; }
grep -qF "DISCORD_CHANNEL_ID env 누락" /tmp/plan007-phase01-noenv.log || { echo "PHASE_FAILED: 누락 메시지 mismatch"; exit 1; }

# 5-3. openclaw 명령 부재 시뮬레이션 — PATH 비우고 호출
DISCORD_CHANNEL_ID="0000000000000000" PATH="/tmp" bun run _shared/lib/notify_discord.ts "test" 2>&1 >/tmp/plan007-phase01-noclaw.log
code=$?
[ "$code" -eq 1 ] || { echo "PHASE_FAILED: openclaw 누락 시 exit code $code expected 1"; cat /tmp/plan007-phase01-noclaw.log; exit 1; }

echo "phase-01 unit smoke 통과"
```

positive path (실제 메시지 발송)는 phase-02 caller 갱신 후 사용자 환경에서 수동 확인.

## Critical Files

| 파일 | 변경 |
|---|---|
| `_shared/lib/notify_discord.ts` | Write 전체 덮어쓰기 (webhook → openclaw) |
| `_shared/types/index.ts` | `NotificationPayload` 제거 또는 `NotifyOptions`로 갱신 |

다른 파일은 손대지 않는다. caller 갱신은 phase-02.

## 검증

위 작업 3·4·5의 검증식이 검증 자체. 추가 smoke:

```bash
cd /home/bifos/ai-nodes

# 1. notifyDiscord export 확인
grep -qE "^export (async )?function notifyDiscord" _shared/lib/notify_discord.ts || { echo "PHASE_FAILED: notifyDiscord export 누락"; exit 1; }

# 2. openclaw subprocess 호출 확인 (재구현 본질)
grep -qF 'Bun.spawn(["openclaw"' _shared/lib/notify_discord.ts || { echo "PHASE_FAILED: openclaw subprocess 호출 없음 — 옛 webhook fetch 잔존 가능"; exit 1; }

# 3. webhook fetch 잔존 확인 (역방향)
grep -qF "DISCORD_WEBHOOK_URL" _shared/lib/notify_discord.ts && { echo "PHASE_FAILED: DISCORD_WEBHOOK_URL 잔존 — webhook 구현 안 지워짐"; exit 1; }

echo "phase-01 검증 통과"
```

## 커밋

```bash
git add _shared/lib/notify_discord.ts _shared/types/index.ts
git commit -m "feat(_shared/lib): notify_discord.ts openclaw subprocess 재구현 (plan007 phase-01)

ADR-021. plan004 phase-03이 옛 .sh 동작을 webhook으로 추정 재구현했던 것을
실제 동작인 openclaw message send subprocess로 재구현.

- DISCORD_CHANNEL_ID env 필수, 누락 시 exit 1 (caller fail-fast)
- --media <path> 옵션 지원 (옛 notify_discord_media.sh 동등 동작 흡수)
- timeout 10초
- _shared/types/index.ts: NotificationPayload 제거 또는 NotifyOptions로 갱신

caller 갱신은 phase-02. positive path는 사용자 수동 확인."
```

push는 phase-04.

## Blocked 조건

**중요 — exit code 명시**: 아래 어느 마커든 출력만 하지 말고 반드시 `sys.exit(1)` (FAILED) 또는 `sys.exit(2)` (BLOCKED) — shell에서는 `exit 1` / `exit 2` — 비-0 exit code로 종료한다. 본문의 모든 검증 bash 블록은 반드시 Bash 도구로 직접 실행한다 (prose로 마커만 출력하면 run-phases.py가 success로 잘못 처리 — plan001/plan004 사례).

- `_shared/lib/notify_discord.ts` 부재 시 `PHASE_BLOCKED: 옛 .ts 파일 누락` + `exit 2`.
- tsc 에러 시 `PHASE_FAILED: tsc` + `exit 1`.
- unit smoke 실패 시 `PHASE_FAILED: smoke <항목>` + `exit 1`.

## 의도 메모

- Write로 전체 덮어쓰기 — Edit으로 webhook 코드 일부만 바꾸면 잔존 위험 (common-pitfalls 6-5).
- positive path는 phase에서 안 함 — 실제 Discord 채널에 테스트 메시지가 가는 부작용. 사용자 수동 확인.
- openclaw subprocess 검증을 `grep -qF "Bun.spawn"` + `grep -qF "DISCORD_WEBHOOK_URL"` 부정으로 — 재구현 본질이 옛 webhook을 *대체*했음을 강제.
