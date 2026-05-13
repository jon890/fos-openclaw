#!/usr/bin/env bun
// _shared/lib/notify_discord.ts
// Discord webhook 알림. ADR-019.
// Usage:
//   bun run _shared/lib/notify_discord.ts "메시지"
//   또는 from-import: await notifyDiscord("메시지")

import type { NotificationPayload } from "../types/index.ts";

const DEFAULT_USERNAME = "ai-nodes";
const TIMEOUT_MS = 10_000;

export async function notifyDiscord(content: string, opts?: { username?: string }): Promise<void> {
  const url = process.env.DISCORD_WEBHOOK_URL;
  if (!url) {
    // webhook 없음 — silent. 워크스페이스 격리 원칙.
    return;
  }

  const payload: NotificationPayload = {
    content,
    username: opts?.username ?? DEFAULT_USERNAME,
  };

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    if (!res.ok) {
      // 비치명적 — phase 진행 막지 X.
      console.error(`[notify_discord] webhook returned ${res.status}`);
    }
  } catch (err) {
    console.error(`[notify_discord] failed: ${err instanceof Error ? err.message : String(err)}`);
  } finally {
    clearTimeout(timeout);
  }
}

// CLI 진입점 — bash 에서 직접 호출용.
if (import.meta.main) {
  const message = process.argv[2];
  if (!message) {
    console.error("usage: notify_discord.ts <message>");
    process.exit(1);
  }
  await notifyDiscord(message);
}
