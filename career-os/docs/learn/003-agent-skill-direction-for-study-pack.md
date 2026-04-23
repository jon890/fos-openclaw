# Agent Skill Direction for Study Pack

## Decision

Study-pack generation should move toward a user-owned Agent Skill interface instead of exposing internal runner modes (`study-pack`, `maintain-study-pack`, etc.) to the user.

## Intended UX

Users should be able to say things like:

- `/study-pack JVM GC 튜닝 가이드`
- `Redis cache-aside 스터디팩 만들어줘`
- `기존 문서 확인하고 InnoDB gap lock 쪽 업데이트해줘`

without needing to know whether the system will:
- create a new file,
- update an existing file,
- use maintainer-backed overlap inspection,
- or route through a curated topic config.

## Architecture direction

- User-facing Agent Skill: `fos-study-pack`
- Internal orchestrator: `career-os` `run_now.sh study-pack <topic>`
- Overlap-sensitive routing: integrated maintainer logic inside `study-pack`
- Final writing and update-vs-new judgment: Claude-driven when needed
- Commit/push + artifact tracking: runner responsibility

## Why

This hides operational complexity from the user while keeping the internal pipeline reusable and robust.
