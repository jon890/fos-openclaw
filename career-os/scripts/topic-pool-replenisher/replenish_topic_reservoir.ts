#!/usr/bin/env bun
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, join } from "node:path";
import { spawnSync } from "node:child_process";
import { persistUsage } from "../../../_shared/lib/invoke_claude_skills.ts";

const HOME = process.env.HOME ?? "/root";
const TASK_ROOT = join(HOME, "ai-nodes", "career-os");
const CONFIG = join(TASK_ROOT, "config");
const RUNTIME = join(TASK_ROOT, "data", "runtime");
mkdirSync(RUNTIME, { recursive: true });

const PRIMARY_TARGET = 8;
const CANDIDATE_TARGET = 18;
const LIVE_PRIMARY_TARGET = 3;
const MAX_GENERATION_BATCH = 12;
const RECENT_ARTIFACT_LIMIT = 24;
const MODEL = "claude-sonnet-4-5";

const ALLOWED_CANDIDATE_DOMAINS = new Set([
  "mysql", "redis", "architecture", "spring", "java",
  "message-queue", "search", "interview", "observability",
  "security", "testing",
]);
const ALLOWED_PROMOTION_DOMAINS = new Set([
  "mysql", "redis", "architecture", "spring", "java", "kafka",
  "rabbitmq", "message-queue", "opensearch", "interview", "observability",
  "security", "testing",
]);
const ALLOWED_TAGS = new Set(["new", "deepen", "review"]);
const ALLOWED_DIFFICULTIES = new Set(["중", "중상", "상"]);
const WEAK_AREAS = new Set(["mysql", "redis"]);
const PROMOTION_TAG_PRIORITY: Record<string, number> = { new: 0, deepen: -1, review: -3 };

// ─── Types ────────────────────────────────────────────────────────────────────

interface PromotionTarget {
  domain?: string;
  outputPath?: string;
  commitTopic?: string;
  appendPrompt?: string;
  [key: string]: unknown;
}

interface CandidateTopic {
  key?: string;
  title?: string;
  domain?: string;
  tag?: string;
  difficulty?: string;
  estMinutes?: unknown;
  whyNow?: unknown;
  promotionTarget?: PromotionTarget;
  [key: string]: unknown;
}

interface CandidatesDoc {
  topics?: CandidateTopic[];
  [key: string]: unknown;
}

interface PrimaryTopicValue {
  domain?: string;
  outputPath?: string;
  [key: string]: unknown;
}

interface PrimaryConfig {
  [key: string]: PrimaryTopicValue;
}

interface TopicsData {
  "study-pack": PrimaryConfig;
  "study-pack-candidates": CandidatesDoc;
  [key: string]: unknown;
}

interface Artifact {
  kind?: string;
  outputPath?: string;
  topic?: string;
  updatedAt?: string;
  createdAt?: string;
  [key: string]: unknown;
}

interface LiveSeed {
  slug?: string;
  outputPath?: string;
  [key: string]: unknown;
}

interface LiveDoc {
  seeds?: LiveSeed[];
  [key: string]: unknown;
}

interface Context {
  recent_domains: Record<string, number>;
  primary_keys: string[];
  candidate_titles: string[];
  recent_lines: string[];
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function readJson(path: string): unknown {
  return JSON.parse(readFileSync(path, "utf-8"));
}

function writeJson(path: string, data: unknown): void {
  writeFileSync(path, JSON.stringify(data, null, 2) + "\n", "utf-8");
}

function utcNow(): string {
  return new Date().toISOString();
}

function normalizeText(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9가-힣]+/g, " ").trim();
}

function tokenSet(text: string): Set<string> {
  return new Set(normalizeText(text).split(" ").filter(Boolean));
}

function basenameTokens(filePath: string): Set<string> {
  const b = basename(filePath);
  const dot = b.lastIndexOf(".");
  const stem = dot > 0 ? b.slice(0, dot) : b;
  return tokenSet(stem);
}

function similarTokens(a: Set<string>, b: Set<string>): number {
  if (a.size === 0 || b.size === 0) return 0.0;
  let intersectionSize = 0;
  for (const x of a) {
    if (b.has(x)) intersectionSize++;
  }
  const unionSize = a.size + b.size - intersectionSize;
  return intersectionSize / unionSize;
}

function domainFromOutputPath(p: string): string {
  if (p.startsWith("database/mysql/")) return "mysql";
  if (p.startsWith("database/redis/")) return "redis";
  if (p.startsWith("java/spring/")) return "spring";
  if (p.startsWith("java/")) return "java";
  if (p.startsWith("architecture/")) return "architecture";
  if (p.startsWith("search/")) return "search";
  if (p.startsWith("kafka/") || p.startsWith("rabbitmq/")) return "message-queue";
  if (p.startsWith("interview/")) return "interview";
  if (p.startsWith("observability/")) return "observability";
  if (p.startsWith("security/")) return "security";
  if (p.startsWith("testing/")) return "testing";
  return "other";
}

// ─── Core logic ───────────────────────────────────────────────────────────────

function buildContext(primaryCfg: PrimaryConfig, candidatesDoc: CandidatesDoc, artifacts: Artifact[]): Context {
  let recentStudy = artifacts.filter(a => a.kind === "study-pack");
  recentStudy.sort((a, b) => {
    const aDate = a.updatedAt ?? a.createdAt ?? "";
    const bDate = b.updatedAt ?? b.createdAt ?? "";
    return bDate.localeCompare(aDate);
  });
  recentStudy = recentStudy.slice(0, RECENT_ARTIFACT_LIMIT);

  const recentDomains: Record<string, number> = {};
  for (const a of recentStudy) {
    const d = domainFromOutputPath(a.outputPath ?? "");
    recentDomains[d] = (recentDomains[d] ?? 0) + 1;
  }

  return {
    recent_domains: recentDomains,
    primary_keys: Object.keys(primaryCfg),
    candidate_titles: (candidatesDoc.topics ?? []).map(t => t.title ?? ""),
    recent_lines: recentStudy.map(a => `- ${a.topic} -> ${a.outputPath}`),
  };
}

function buildPrompt(requestCount: number, context: Context): string {
  const templatePath = `${TASK_ROOT}/skills/topic-pool-replenisher/references/topic-replenishment-prompt.md`;
  const template = readFileSync(templatePath, "utf-8");
  return [
    template,
    `이번에 생성할 후보 topic 개수: ${requestCount}`,
    "최근 study-pack 도메인 분포:",
    JSON.stringify(context.recent_domains, null, 2),
    "이미 primary config에 있는 topic key들:",
    JSON.stringify(context.primary_keys, null, 2),
    "이미 candidate reservoir에 있는 title들:",
    JSON.stringify(context.candidate_titles, null, 2),
    "최근 생성된 study-pack 목록:",
    context.recent_lines.join("\n"),
    "추가 지시:",
    "- 최근 생성된 주제와 겹치지 않는 후보만 만든다.",
    "- MySQL/Redis 약점 영역 보강을 우선하되 한 도메인에 몰아넣지 않는다.",
    "- review는 최대 2개, deepen은 최대 3개, 나머지는 new로 구성한다.",
    "- outputPath는 이미 존재하는 파일과 겹치지 않게 새 경로를 잡는다.",
  ].join("\n\n");
}

function callClaude(prompt: string): { topics: CandidateTopic[] } {
  const result = spawnSync(
    "timeout",
    [
      "900s", "claude",
      "--model", MODEL,
      "--permission-mode", "bypassPermissions",
      "--print",
      "--output-format", "json",
      "--no-session-persistence",
      prompt,
    ],
    { encoding: "utf-8", maxBuffer: 50 * 1024 * 1024 },
  );

  if (result.error) {
    throw new Error(`claude failed to start: ${result.error.message}`);
  }
  if (result.status !== 0) {
    const errMsg = ((result.stderr as string) ?? "").trim() || ((result.stdout as string) ?? "").trim();
    throw new Error(`claude failed (${result.status ?? "signal"}): ${errMsg}`);
  }

  const stdout = result.stdout as string;
  const tmpFile = join(tmpdir(), `replenish-usage-${Date.now()}.json`);
  writeFileSync(tmpFile, stdout, "utf-8");
  persistUsage(tmpFile);

  const outer = JSON.parse(stdout) as { result?: string };
  let raw = (outer.result ?? "").trim();
  raw = raw.replace(/^```(?:json)?\s*/s, "").replace(/\s*```\s*$/s, "").trim();

  const parsed = JSON.parse(raw) as { topics?: unknown };
  if (typeof parsed !== "object" || !Array.isArray(parsed?.topics)) {
    throw new Error("Claude output did not contain {topics:[...]} JSON");
  }
  return parsed as { topics: CandidateTopic[] };
}

function validateTopic(
  item: CandidateTopic,
  existingKeys: Set<string>,
  existingOutputPaths: Set<string>,
  existingTitles: Set<string>,
  existingReferenceTokens: Set<string>[],
): [string[], Set<string>, string] {
  const errors: string[] = [];

  const key = item.key ?? "";
  if (!/^[a-z0-9-]{8,120}$/.test(key)) errors.push("invalid key");
  if (existingKeys.has(key)) errors.push("duplicate key");

  const title = item.title ?? "";
  if (typeof title !== "string" || title.trim().length < 8) {
    errors.push("invalid title");
  } else if (existingTitles.has(normalizeText(title))) {
    errors.push("duplicate title");
  }

  if (!ALLOWED_CANDIDATE_DOMAINS.has(item.domain ?? "")) errors.push("invalid candidate domain");
  if (!ALLOWED_TAGS.has(item.tag ?? "")) errors.push("invalid tag");
  if (!ALLOWED_DIFFICULTIES.has((item.difficulty ?? "") as string)) errors.push("invalid difficulty");

  const minutes = item.estMinutes;
  if (typeof minutes !== "number" || minutes < 20 || minutes > 70) errors.push("invalid estMinutes");

  const whyNow = item.whyNow;
  if (
    !Array.isArray(whyNow) ||
    whyNow.length !== 2 ||
    !whyNow.every((x: unknown) => typeof x === "string" && (x as string).trim())
  ) {
    errors.push("invalid whyNow");
  }

  const promotion = (item.promotionTarget ?? {}) as PromotionTarget;
  const promoDomain = promotion.domain ?? "";
  const outputPath = promotion.outputPath ?? "";
  const commitTopic = promotion.commitTopic ?? "";
  const appendPrompt = promotion.appendPrompt ?? "";

  if (!ALLOWED_PROMOTION_DOMAINS.has(promoDomain)) errors.push("invalid promotion domain");
  if (!outputPath.endsWith(".md") || existingOutputPaths.has(outputPath)) errors.push("duplicate/invalid outputPath");
  if (!/^[a-z0-9-]{8,120}$/.test(commitTopic)) errors.push("invalid commitTopic");
  if (!appendPrompt.includes("[초안]") || appendPrompt.trim().length < 60) errors.push("weak appendPrompt");

  const refTokens = new Set([...tokenSet(key), ...tokenSet(title), ...basenameTokens(outputPath)]);
  if (existingReferenceTokens.some(tokens => similarTokens(refTokens, tokens) >= 0.72)) {
    errors.push("too similar to existing topic");
  }

  return [errors, refTokens, normalizeText(title)];
}

function cleanExistingCandidates(
  primaryCfg: PrimaryConfig,
  candidatesDoc: CandidatesDoc,
  artifacts: Artifact[],
): [{ key: string; reason: string }[], Set<string>, Set<string>, Set<string>, Set<string>[]] {
  const existingOutputPaths = new Set<string>([
    ...Object.values(primaryCfg).map(v => v.outputPath ?? ""),
    ...artifacts.filter(a => a.outputPath).map(a => a.outputPath!),
  ]);
  const existingKeys = new Set<string>(Object.keys(primaryCfg));
  const existingTitles = new Set<string>();
  const existingReferenceTokens: Set<string>[] = [];

  for (const [key, value] of Object.entries(primaryCfg)) {
    existingReferenceTokens.push(new Set([...tokenSet(key), ...basenameTokens(value.outputPath ?? "")]));
  }
  for (const artifact of artifacts) {
    existingReferenceTokens.push(new Set([...tokenSet(artifact.topic ?? ""), ...basenameTokens(artifact.outputPath ?? "")]));
  }

  const kept: CandidateTopic[] = [];
  const removed: { key: string; reason: string }[] = [];
  const seenKeys = new Set<string>();
  const seenOutputPaths = new Set<string>();
  const seenTitles = new Set<string>();

  for (const item of (candidatesDoc.topics ?? [])) {
    const promotion = (item.promotionTarget ?? {}) as PromotionTarget;
    const key = item.key ?? "";
    const outputPath = promotion.outputPath ?? "";
    const normTitle = normalizeText(item.title ?? "");
    const refTokens = new Set([...tokenSet(key), ...tokenSet(item.title ?? ""), ...basenameTokens(outputPath)]);

    let reason: string | null = null;
    if (existingKeys.has(key) || seenKeys.has(key)) {
      reason = "duplicate key";
    } else if (existingOutputPaths.has(outputPath) || seenOutputPaths.has(outputPath)) {
      reason = "duplicate outputPath";
    } else if (normTitle && (seenTitles.has(normTitle) || existingTitles.has(normTitle))) {
      reason = "duplicate title";
    } else if (existingReferenceTokens.some(tokens => similarTokens(refTokens, tokens) >= 0.72)) {
      reason = "too similar to existing topic";
    }

    if (reason) {
      removed.push({ key, reason });
      continue;
    }

    kept.push(item);
    seenKeys.add(key);
    seenOutputPaths.add(outputPath);
    seenTitles.add(normTitle);
    existingTitles.add(normTitle);
    existingReferenceTokens.push(refTokens);
  }

  candidatesDoc.topics = kept;
  return [
    removed,
    new Set([...existingKeys, ...seenKeys]),
    new Set([...existingOutputPaths, ...seenOutputPaths]),
    existingTitles,
    existingReferenceTokens,
  ];
}

function mergeGeneratedTopics(
  primaryCfg: PrimaryConfig,
  candidatesDoc: CandidatesDoc,
  artifacts: Artifact[],
  generatedTopics: CandidateTopic[],
): [CandidateTopic[], { key?: string; errors: string[] }[], { key: string; reason: string }[]] {
  const [removed, existingKeys, existingOutputPaths, existingTitles, existingReferenceTokens] =
    cleanExistingCandidates(primaryCfg, candidatesDoc, artifacts);

  const accepted: CandidateTopic[] = [];
  const rejected: { key?: string; errors: string[] }[] = [];

  for (const item of generatedTopics) {
    const [errors, refTokens, normTitle] = validateTopic(
      item, existingKeys, existingOutputPaths, existingTitles, existingReferenceTokens,
    );
    if (errors.length > 0) {
      rejected.push({ key: item.key, errors });
      continue;
    }
    if (!candidatesDoc.topics) candidatesDoc.topics = [];
    candidatesDoc.topics.push(item);
    accepted.push(item);
    existingKeys.add(item.key!);
    existingOutputPaths.add((item.promotionTarget as PromotionTarget).outputPath!);
    existingTitles.add(normTitle);
    existingReferenceTokens.push(refTokens);
  }

  return [accepted, rejected, removed];
}

function scoreForPromotion(item: CandidateTopic, recentDomainCounts: Map<string, number>): number {
  const domain = (item.promotionTarget as PromotionTarget)?.domain ?? item.domain ?? "other";
  let score = -2 * (recentDomainCounts.get(domain) ?? 0);
  if (WEAK_AREAS.has(domain)) score += 3;
  score += PROMOTION_TAG_PRIORITY[item.tag ?? "new"] ?? -4;
  return score;
}

function promoteCandidates(
  primaryCfg: PrimaryConfig,
  candidatesDoc: CandidatesDoc,
  artifacts: Artifact[],
): string[] {
  const studyPaths = new Set(artifacts.filter(a => a.kind === "study-pack").map(a => a.outputPath));
  const uncovered = Object.entries(primaryCfg).filter(([, v]) => !studyPaths.has(v.outputPath));
  const need = Math.max(0, PRIMARY_TARGET - uncovered.length);
  if (need <= 0) return [];

  const recentDomains = new Map<string, number>();
  for (const a of artifacts.filter(a => a.kind === "study-pack")) {
    const d = domainFromOutputPath(a.outputPath ?? "");
    recentDomains.set(d, (recentDomains.get(d) ?? 0) + 1);
  }

  const topics = candidatesDoc.topics ?? [];
  const ranked = topics
    .map((item, idx) => ({ idx, item }))
    .sort((a, b) => scoreForPromotion(b.item, recentDomains) - scoreForPromotion(a.item, recentDomains));
  const chosenIndices = new Set(ranked.slice(0, need).map(x => x.idx));

  const promoted: string[] = [];
  const remaining: CandidateTopic[] = [];

  topics.forEach((item, idx) => {
    if (!chosenIndices.has(idx)) {
      remaining.push(item);
      return;
    }
    const promotion = item.promotionTarget as PromotionTarget;
    if (!promotion || primaryCfg[item.key!]) {
      remaining.push(item);
      return;
    }
    primaryCfg[item.key!] = promotion;
    promoted.push(item.key!);
  });

  candidatesDoc.topics = remaining;
  return promoted;
}

function promoteLiveCodingCandidates(
  livePrimaryDoc: LiveDoc,
  liveCandidateDoc: LiveDoc,
  artifacts: Artifact[],
): string[] {
  const covered = new Set(artifacts.filter(a => a.kind === "live-coding").map(a => a.outputPath));
  const remainingPrimary = (livePrimaryDoc.seeds ?? []).filter(s => !covered.has(s.outputPath));
  const need = Math.max(0, LIVE_PRIMARY_TARGET - remainingPrimary.length);
  if (need <= 0) return [];

  const promoted: string[] = [];
  const keptCandidates: LiveSeed[] = [];

  for (const seed of (liveCandidateDoc.seeds ?? [])) {
    if (promoted.length < need && !covered.has(seed.outputPath)) {
      if (!livePrimaryDoc.seeds) livePrimaryDoc.seeds = [];
      livePrimaryDoc.seeds.push(seed);
      promoted.push(seed.slug ?? "");
    } else {
      keptCandidates.push(seed);
    }
  }

  liveCandidateDoc.seeds = keptCandidates;
  return promoted;
}

function refreshInventory(): void {
  const script = join(TASK_ROOT, "scripts", "study-topic-recommender", "refresh_topic_inventory.py");
  const result = spawnSync("python3", [script], { cwd: TASK_ROOT, stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`refresh_topic_inventory.py failed with status ${result.status}`);
  }
}

// ─── Entry point ──────────────────────────────────────────────────────────────

function main(): void {
  const topicsPath = join(CONFIG, "topics.json");
  const livePrimaryPath = join(CONFIG, "live-coding-seed-pool.json");
  const liveCandidatePath = join(CONFIG, "live-coding-seed-candidates.json");
  const artifactsPath = join(TASK_ROOT, "data", "generated-artifacts.json");
  const reportJsonPath = join(RUNTIME, "topic-replenishment.json");
  const reportMdPath = join(RUNTIME, "topic-replenishment.md");

  const topicsData = readJson(topicsPath) as TopicsData;
  const primaryCfg = topicsData["study-pack"];
  const candidatesDoc = topicsData["study-pack-candidates"];
  const livePrimaryDoc = readJson(livePrimaryPath) as LiveDoc;
  const liveCandidateDoc = readJson(liveCandidatePath) as LiveDoc;
  const artifacts = ((readJson(artifactsPath) as { artifacts?: Artifact[] }).artifacts) ?? [];

  const studyPaths = new Set(artifacts.filter(a => a.kind === "study-pack").map(a => a.outputPath));
  const livePaths = new Set(artifacts.filter(a => a.kind === "live-coding").map(a => a.outputPath));

  const beforeCandidateCount = (candidatesDoc.topics ?? []).length;
  const beforePrimaryUncovered = Object.values(primaryCfg).filter(v => !studyPaths.has(v.outputPath)).length;
  const beforeLivePrimaryRemaining = (livePrimaryDoc.seeds ?? []).filter(s => !livePaths.has(s.outputPath)).length;
  const beforeLiveCandidateRemaining = (liveCandidateDoc.seeds ?? []).filter(s => !livePaths.has(s.outputPath)).length;

  const [cleaned] = cleanExistingCandidates(primaryCfg, candidatesDoc, artifacts);
  const context = buildContext(primaryCfg, candidatesDoc, artifacts);
  const currentCandidates = (candidatesDoc.topics ?? []).length;
  const currentUncovered = Object.values(primaryCfg).filter(v => !studyPaths.has(v.outputPath)).length;
  const promoteNeed = Math.max(0, PRIMARY_TARGET - currentUncovered);
  const requestCount = Math.min(MAX_GENERATION_BATCH, Math.max(0, CANDIDATE_TARGET + promoteNeed - currentCandidates));

  let claudeInvoked = false;
  let accepted: CandidateTopic[] = [];
  let rejected: { key?: string; errors: string[] }[] = [];

  if (requestCount > 0) {
    claudeInvoked = true;
    const generated = callClaude(buildPrompt(requestCount, context)).topics;
    const [acc, rej, cleanedAgain] = mergeGeneratedTopics(primaryCfg, candidatesDoc, artifacts, generated);
    accepted = acc;
    rejected = rej;
    cleaned.push(...cleanedAgain);
  }

  const promoted = promoteCandidates(primaryCfg, candidatesDoc, artifacts);
  const promotedLiveCoding = promoteLiveCodingCandidates(livePrimaryDoc, liveCandidateDoc, artifacts);

  writeJson(topicsPath, topicsData);
  writeJson(livePrimaryPath, livePrimaryDoc);
  writeJson(liveCandidatePath, liveCandidateDoc);
  refreshInventory();

  const afterCandidateCount = (candidatesDoc.topics ?? []).length;
  const afterPrimaryUncovered = Object.values(primaryCfg).filter(v => !studyPaths.has(v.outputPath)).length;
  const afterLivePrimaryRemaining = (livePrimaryDoc.seeds ?? []).filter(s => !livePaths.has(s.outputPath)).length;
  const afterLiveCandidateRemaining = (liveCandidateDoc.seeds ?? []).filter(s => !livePaths.has(s.outputPath)).length;

  const report = {
    generatedAt: utcNow(),
    claudeInvoked,
    requestedGenerationCount: requestCount,
    requestedPromotionGap: promoteNeed,
    before: {
      candidateCount: beforeCandidateCount,
      primaryUncovered: beforePrimaryUncovered,
      livePrimaryRemaining: beforeLivePrimaryRemaining,
      liveCandidateRemaining: beforeLiveCandidateRemaining,
    },
    after: {
      candidateCount: afterCandidateCount,
      primaryUncovered: afterPrimaryUncovered,
      livePrimaryRemaining: afterLivePrimaryRemaining,
      liveCandidateRemaining: afterLiveCandidateRemaining,
    },
    accepted: accepted.map(item => item.key!),
    rejected,
    cleaned,
    promoted,
    promotedLiveCoding,
  };
  writeJson(reportJsonPath, report);

  const lines = [
    "# topic replenishment",
    "",
    `- generatedAt: ${report.generatedAt}`,
    `- claudeInvoked: ${claudeInvoked}`,
    `- requestedGenerationCount: ${requestCount}`,
    `- requestedPromotionGap: ${promoteNeed}`,
    `- candidateCount: ${beforeCandidateCount} -> ${afterCandidateCount}`,
    `- primaryUncovered: ${beforePrimaryUncovered} -> ${afterPrimaryUncovered}`,
    `- livePrimaryRemaining: ${beforeLivePrimaryRemaining} -> ${afterLivePrimaryRemaining}`,
    `- liveCandidateRemaining: ${beforeLiveCandidateRemaining} -> ${afterLiveCandidateRemaining}`,
    `- accepted: ${report.accepted.length ? report.accepted.join(", ") : "-"}`,
    `- promoted: ${promoted.length ? promoted.join(", ") : "-"}`,
    `- promotedLiveCoding: ${promotedLiveCoding.length ? promotedLiveCoding.join(", ") : "-"}`,
    "",
    "## cleaned",
  ];

  if (cleaned.length > 0) {
    lines.push(...cleaned.map(item => `- ${item.key}: ${item.reason}`));
  } else {
    lines.push("- none");
  }
  lines.push("", "## rejected");
  if (rejected.length > 0) {
    lines.push(...rejected.map(item => `- ${item.key ?? "?"}: ${item.errors.join(", ")}`));
  } else {
    lines.push("- none");
  }

  writeFileSync(reportMdPath, lines.join("\n") + "\n", "utf-8");
  console.log(JSON.stringify(report));
}

main();
