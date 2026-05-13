#!/usr/bin/env bun
// _shared/lib/format_cost_summary.ts
// logs/task-runs.jsonl 최신 entry → 한 줄 cost 요약. ADR-019.
// Usage:
//   bun run _shared/lib/format_cost_summary.ts <workspace-root> <task-name>

import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { TaskRunEntry } from "../types/index.ts";

function shortModel(model: string | null): string {
  if (!model) return "";
  // "claude-opus-4-7[1m]" → "opus-4-7[1m]"
  return model.replace(/^claude-/, "");
}

function shortDuration(sec: number | null): string {
  if (!sec || sec <= 0) return "";
  if (sec < 60) return `${sec}s`;
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return s ? `${m}m${s}s` : `${m}m`;
}

function shortCost(usd: number | null): string {
  if (usd === null || usd === undefined || usd <= 0) return "";
  return `\$${usd.toFixed(4)}`;
}

function shortTokens(input: number | null, output: number | null): string {
  if (input == null && output == null) return "";
  const fmt = (n: number | null) => {
    if (n == null) return "?";
    if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
    return String(n);
  };
  const ti = fmt(input);
  const to = fmt(output);
  if (ti === "0" && to === "0") return "";
  return `${ti}→${to} 토큰`;
}

function shortCache(cached: number | null): string {
  if (cached == null || cached <= 0) return "";
  if (cached >= 1000) return `cache ${(cached / 1000).toFixed(1)}k`;
  return `cache ${cached}`;
}

export function formatCostSummary(workspaceRoot: string, taskName: string): string {
  const logPath = join(workspaceRoot, "logs", "task-runs.jsonl");
  let lines: string[];
  try {
    lines = readFileSync(logPath, "utf-8").trimEnd().split("\n");
  } catch {
    return "";
  }

  // task-name 일치하는 최신 entry 부터 역순 탐색.
  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i].trim();
    if (!line) continue;
    let entry: TaskRunEntry;
    try {
      entry = JSON.parse(line) as TaskRunEntry;
    } catch {
      continue;
    }
    if (entry.task_name !== taskName) continue;

    const parts = [
      shortCost(entry.cost_usd),
      shortModel(entry.model),
      shortTokens(entry.tokens_in_delta, entry.tokens_out_delta),
      shortCache(entry.cache_read_input_tokens as number | null),
      shortDuration(entry.duration_sec),
    ].filter(Boolean);

    if (parts.length === 0) return "";
    return " · " + parts.join(" · ");
  }

  return "";
}

// CLI 진입점
if (import.meta.main) {
  const workspaceRoot = process.argv[2];
  const taskName = process.argv[3];
  if (!workspaceRoot || !taskName) {
    console.error("usage: format_cost_summary.ts <workspace-root> <task-name>");
    process.exit(1);
  }
  const out = formatCostSummary(workspaceRoot, taskName);
  if (out) process.stdout.write(out);
}
