---
name: docs-audit
description: Audit documentation structure and quality to find overlap, stale docs, weak linking, role confusion, low-value notes, and cleanup opportunities. Use when the user asks to review docs, reduce duplication, improve hub/deep-dive structure, retire outdated learnings, identify archive/delete candidates, or check whether recent document changes actually improved the docs.
---

# docs-audit

Audit documentation quality, structure, and long-term maintainability after many workflow changes.

## Purpose

As automation evolves, docs accumulate quickly.
This skill helps answer both kinds of questions:
- **structure questions**: what should stay, merge, archive, refresh, or be deleted?
- **quality questions**: is this document actually good, useful, well-linked, non-duplicative, and in the right role?

## What this skill should do

1. Read the current documentation set.
2. Identify documents that are:
   - still active and useful,
   - partially duplicated,
   - obsolete,
   - too narrow to justify keeping,
   - better merged into another document,
   - archive/delete candidates,
   - weakly linked,
   - unclear about whether they are a hub, deep-dive, reference, or case-study.
3. Evaluate quality as well as structure.
4. Produce an audit report with concrete reasoning.
5. Prefer recommendations and targeted cleanup plans before destructive edits.
6. When asked to validate a recent cleanup or restructuring, inspect the resulting diff and judge whether it actually improved the documentation.

## Expected classification

Each reviewed document should usually end up in one of these buckets:
- `keep`
- `refresh-needed`
- `merge`
- `archive`
- `delete-candidate`

## Quality dimensions to evaluate

For each document or small doc set, consider:
- clarity
- overlap
- role fit (hub / deep-dive / reference / case-study)
- link quality
- practical value
- interview value (when applicable)
- maintenance cost

## Primary scope

Default audit scope:
- `career-os/docs/learn/`
- `career-os/docs/decisions/`
- selected content trees such as `sources/fos-study/database/mysql/`
- related skill references when they duplicate docs

## Output

Write an audit report under:
- `career-os/docs/audit/`

The report should explain:
- what was reviewed,
- what still matters,
- what became stale,
- what overlaps,
- what should be merged or retired,
- which docs are weakly linked,
- whether recent changes actually improved the docs.

## Diff-based validation mode

If the user asks whether a cleanup/refactor actually helped:
1. read the affected docs,
2. inspect the diff,
3. judge whether overlap decreased,
4. judge whether links improved,
5. judge whether document roles became clearer,
6. report the result plainly.

## Guardrails

- Do not delete docs automatically.
- Prefer recommendations and small cleanup plans first.
- Treat recent docs cautiously unless the user explicitly asks for aggressive cleanup.
- Do not confuse “different depth” with duplication; a hub and a deep-dive may coexist if the relationship is clear.
