# ADR-009: Morning topic recommendation should manage its own reservoir

- Status: Accepted
- Date: 2026-04-25

## Context

The earlier morning recommendation flow depended too heavily on a small fixed set of curated study topics and a small fixed live-coding seed pool.

That caused two recurring problems:

1. recommendation breadth narrowed over time because the curated pool was almost fully consumed
2. live-coding generation stopped entirely when the main seed pool was exhausted

The old flow also made the recommendation agent conservative by construction:

- it strongly preferred already-registered curated topics
- it had very little structured candidate inventory to choose from
- it had no explicit reservoir-health check

## Decision

Morning recommendation should become a small pipeline, not just a prompt.

The pipeline now has these layers:

1. **primary curated topics**
   - `config/study-pack-topics.json`
   - `config/live-coding-seed-pool.json`
2. **candidate reservoir**
   - `config/study-topic-candidates.json`
   - `config/live-coding-seed-candidates.json`
3. **runtime inventory + recommendation summary**
   - `data/runtime/topic-inventory.json`
   - `data/runtime/morning-topic-recommendation.md`

## Live-coding policy

Live-coding generation should first consume the main seed pool.
If that pool is empty, it should automatically fall back to the live-coding candidate reservoir before failing.

This means the morning live-coding workflow can keep creating new material without requiring immediate manual seed-pool edits every time the primary list runs dry.

## Recommendation policy

Morning study recommendation should not act as if only curated topics exist.
It should select from a broader reservoir with explicit mix targets:

- new topics
- deepen topics
- review topics
- live-coding topics

The default recommendation set should remain five items, but the underlying pool should be diversified enough that the output does not collapse into one narrow domain.

## Safety boundary

Candidate topics are kept separate from the main curated configs.
That separation is intentional.

Reason:

- main configs are the stable execution contract
- candidate configs are a reviewable backlog / reservoir

This allows agents to propose and consume fallback topics without silently mutating the canonical config every day.

## Consequences

### Positive

- broader morning recommendations
- less repeated MySQL/Spring concentration by accident
- live-coding can keep moving after the main seed pool is exhausted
- easier handoff to other agents because the reservoir is explicit and file-backed

### Negative

- more moving parts than a single prompt
- candidate reservoirs still need occasional curation
- recommendation quality now depends partly on candidate inventory quality

## Follow-up guidance

When reservoir health gets low again, prefer these actions in order:

1. refresh candidate files
2. promote good candidates into primary curated configs when they become stable
3. only then tune prompt wording

Prompt tuning alone is not enough if the underlying reservoir is empty.
