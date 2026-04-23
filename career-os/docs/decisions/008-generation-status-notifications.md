# ADR-008: Generation status notifications for career-os document workflows

- Status: Accepted
- Date: 2026-04-17

## Context

Career-os now generates several classes of interview-prep artifacts:

- technical study packs
- live-coding packs
- experience question banks
- company/domain analysis documents

The user wants lightweight operational visibility in Discord when a document workflow runs.
A missing notification makes it hard to tell whether a task started, failed, or completed.

## Decision

Document-generation workflows should emit concise Discord-visible status updates for three stages:

1. start
2. failure
3. completion

These notifications should be short and operational, not verbose.

## Notification shape

### Start
- what started
- optional target topic

Example:
- `문서 생성 시작: Redis Cache-Aside study-pack`

### Failure
- what failed
- one-line reason/blocker

Example:
- `문서 생성 실패: Redis Cache-Aside study-pack (원인: markdown heading validation 실패)`

### Completion
- what completed
- output path
- optional short learning point

Example:
- `문서 생성 완료: Redis Cache-Aside study-pack`
- `경로: database/redis/cache-aside.md`

## Consequences

### Positive
- Better operator visibility in Discord
- Easier debugging when cron runs silently fail
- Lower confusion about whether a document was actually created

### Negative
- Slightly more workflow complexity
- More channel noise if too verbose

## Guidance

Keep notifications short.
Prefer one message per meaningful state transition.
Include the error reason only at a high level unless detailed debugging is explicitly requested.
