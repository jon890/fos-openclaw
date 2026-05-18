export interface DuplicateCandidateInput {
  key: string;
  candidatePath: string;
}

export interface PathMatch {
  key: string;
  candidatePath: string;
  matchedPath: string;
}

export interface PossibleDuplicate extends PathMatch {
  reason: string;
}

export interface DeterministicDedupeResult {
  exactPathMatches: PathMatch[];
  normalizedPathMatches: PathMatch[];
  possibleDuplicates: PossibleDuplicate[];
}

export function normalizePath(p: string): string {
  return p.toLowerCase().replace(/\\/g, "/").replace(/\.md$/, "");
}

function slugTokens(p: string): string[] {
  const basename = p.split("/").pop() ?? p;
  return basename.replace(/\.md$/, "").split("-").filter(Boolean);
}

export function deterministicDedupe(
  candidates: DuplicateCandidateInput[],
  existingPaths: string[],
  options?: { possibleDuplicateLimit?: number }
): DeterministicDedupeResult {
  const limit = options?.possibleDuplicateLimit ?? 20;
  const exactSet = new Set(existingPaths);
  const normalizedExisting = existingPaths.map((p) => ({ original: p, normalized: normalizePath(p) }));

  const exactPathMatches: PathMatch[] = [];
  const normalizedPathMatches: PathMatch[] = [];
  const possibleDuplicates: PossibleDuplicate[] = [];

  const exactKeys = new Set<string>();
  const normalizedKeys = new Set<string>();

  for (const candidate of candidates) {
    if (exactSet.has(candidate.candidatePath)) {
      exactPathMatches.push({
        key: candidate.key,
        candidatePath: candidate.candidatePath,
        matchedPath: candidate.candidatePath,
      });
      exactKeys.add(candidate.key);
      continue;
    }

    const normalizedCandidate = normalizePath(candidate.candidatePath);
    const normMatch = normalizedExisting.find((e) => e.normalized === normalizedCandidate);
    if (normMatch) {
      normalizedPathMatches.push({
        key: candidate.key,
        candidatePath: candidate.candidatePath,
        matchedPath: normMatch.original,
      });
      normalizedKeys.add(candidate.key);
      continue;
    }
  }

  const candidateTokensMap = new Map(
    candidates.map((c) => [c.key, slugTokens(c.candidatePath)])
  );

  for (const candidate of candidates) {
    if (exactKeys.has(candidate.key) || normalizedKeys.has(candidate.key)) continue;
    if (possibleDuplicates.length >= limit) break;

    const cTokens = candidateTokensMap.get(candidate.key) ?? [];
    if (cTokens.length === 0) continue;

    for (const existing of existingPaths) {
      const eTokens = slugTokens(existing);
      const overlap = cTokens.filter((t) => eTokens.includes(t));
      if (overlap.length >= 2) {
        possibleDuplicates.push({
          key: candidate.key,
          candidatePath: candidate.candidatePath,
          matchedPath: existing,
          reason: `slug overlap: ${overlap.join(", ")}`,
        });
        break;
      }
    }
  }

  return { exactPathMatches, normalizedPathMatches, possibleDuplicates };
}
