---
name: fos-study-pack
description: Create or update fos-study technical study-pack markdown documents from natural-language topic requests. Use when the user asks for a study pack, says things like '/study-pack ...', wants an interview-oriented backend study document, or wants existing fos-study documents checked first to avoid duplicates before writing. This skill routes freeform topic requests into the career-os study-pack pipeline, lets Claude decide update-vs-new when overlap exists, and publishes the result to fos-study with commit/push.
---

# fos-study-pack

Handle natural-language study-pack requests for `fos-study`.

## Purpose

Hide internal routing complexity from the user.
The user should be able to ask for a study pack in plain language, and this skill should map that request into the correct `career-os` generation flow.

Before acting, read `references/request-patterns.md`.

## Core behavior

When triggered:

1. Interpret the requested topic from natural language, including slash-style prompts like `/study-pack ...`.
2. Check whether it already maps cleanly to an existing maintained topic.
3. If overlap or ambiguity exists, prefer the maintainer-backed `study-pack` flow so Claude can inspect existing related docs and decide update-vs-new.
4. If it is a straightforward new curated topic already present in config, the normal `study-pack` flow is acceptable.
5. Publish only to `sources/fos-study/...`.
6. Commit and push document changes.

## Invocation target

Primary runtime entrypoint:

```bash
/home/bifos/ai-nodes/career-os/skills/cj-oliveyoung-java-backend-prep/scripts/run_now.sh study-pack <topic>
```

This entrypoint already supports maintainer-backed routing internally for registered maintainer topics.

## Natural-language request handling

Typical user prompts that should trigger this skill:
- `/study-pack JVM GC 튜닝 가이드`
- `study pack으로 Redis cache-aside 정리해줘`
- `InnoDB gap lock 공부하고 싶은데 기존 문서 보고 업데이트해줘`
- `면접용으로 Kafka DLQ / retry / idempotency 스터디팩 만들어줘`

## Important policy

- Prefer a single user-facing interface.
- Do not force the user to choose between create/update modes.
- When overlap matters, let Claude inspect candidate docs and decide.
- Keep operational commentary short; the main value is execution.
