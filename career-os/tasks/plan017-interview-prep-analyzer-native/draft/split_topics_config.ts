#!/usr/bin/env bun
// topics.json (62KB / 3 namespace) → 3 json 분리 마이그
//
// usage: bun split_topics_config.ts [--dry-run]
//
// Input:  career-os/config/topics.json
// Output:
//   career-os/config/study-pack-topics.json     (study-pack namespace, 55 keys)
//   career-os/config/study-pack-candidates.json (study-pack-candidates namespace)
//   career-os/config/question-bank-topics.json  (question-bank namespace, 2 keys)
//
// _meta는 각 출력 파일에 source + namespace 정보 포함하여 재구성.
// dry-run: 출력 path별 키 수만 표시, 파일 쓰기 없음.

import { readFileSync, writeFileSync } from "fs";
import { join, resolve } from "path";

// draft/ → plan017/ → tasks/ → career-os/
const CAREER_OS_ROOT = resolve(import.meta.dir, "../../..");
const CONFIG_DIR = join(CAREER_OS_ROOT, "config");

const INPUT_FILE = join(CONFIG_DIR, "topics.json");

const OUTPUT_FILES = {
  "study-pack": join(CONFIG_DIR, "study-pack-topics.json"),
  "study-pack-candidates": join(CONFIG_DIR, "study-pack-candidates.json"),
  "question-bank": join(CONFIG_DIR, "question-bank-topics.json"),
} as const;

type Namespace = keyof typeof OUTPUT_FILES;

const NAMESPACES: Namespace[] = ["study-pack", "study-pack-candidates", "question-bank"];

interface OriginalMeta {
  purpose?: string;
  schema_version?: string;
  namespaces?: string[];
  [key: string]: unknown;
}

interface TopicsJson {
  _meta: OriginalMeta;
  "study-pack": Record<string, unknown>;
  "study-pack-candidates": Record<string, unknown>;
  "question-bank": Record<string, unknown>;
  [key: string]: unknown;
}

function buildMeta(namespace: Namespace, sourcePath: string): Record<string, unknown> {
  return {
    purpose: `career-os ${namespace} 토픽 메타데이터 단일 출처 (ADR-027 분리)`,
    schema_version: "2",
    namespace,
    source: sourcePath,
    migrated_from: "topics.json",
    migrated_at: new Date().toISOString().slice(0, 10),
  };
}

function main(): void {
  const isDryRun = process.argv.includes("--dry-run");

  if (isDryRun) {
    console.log("[dry-run] 파일을 쓰지 않고 키 수만 표시합니다.\n");
  }

  const raw = readFileSync(INPUT_FILE, "utf-8");
  const data = JSON.parse(raw) as TopicsJson;

  let allOk = true;

  for (const ns of NAMESPACES) {
    const nsData = data[ns];
    if (nsData === undefined) {
      console.error(`ERROR: namespace '${ns}' not found in topics.json`);
      allOk = false;
      continue;
    }

    const keyCount = Object.keys(nsData).length;
    const outputPath = OUTPUT_FILES[ns];

    if (isDryRun) {
      console.log(`[dry-run] ${ns}`);
      console.log(`  → ${outputPath}`);
      console.log(`  keys: ${keyCount}\n`);
      continue;
    }

    const output = {
      _meta: buildMeta(ns, INPUT_FILE),
      ...nsData,
    };

    writeFileSync(outputPath, JSON.stringify(output, null, 2) + "\n", "utf-8");
    console.log(`Written: ${outputPath} (${keyCount} keys)`);
  }

  if (!allOk) {
    process.exit(1);
  }

  if (!isDryRun) {
    console.log(
      "\n마이그 완료. 다음 단계 (phase-02):\n" +
        "1. 각 skill SKILL.md의 Read 경로를 새 json 파일로 갱신\n" +
        "2. topics.json 제거 (분리 완료 후)"
    );
  }
}

main();
