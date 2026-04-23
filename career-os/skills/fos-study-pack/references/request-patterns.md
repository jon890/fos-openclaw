# Request Patterns for fos-study-pack

Use this skill when the user expresses any of these intents in natural language:

## Direct slash-style triggers
- `/study-pack JVM GC 튜닝 가이드`
- `/study-pack Redis cache-aside`
- `/study-pack InnoDB gap lock`

## Natural Korean requests
- `스터디팩 만들어줘`
- `study pack으로 정리해줘`
- `면접용 학습 문서 만들어줘`
- `기존 문서 확인하고 업데이트해줘`
- `이 주제 fos-study에 정리해줘`

## Decision cues

### Prefer normal study-pack flow when:
- the request clearly matches an existing curated topic key
- the request is already a known maintained path

### Prefer maintainer-backed study-pack flow when:
- user explicitly mentions overlap, duplication, update, merge, or existing docs
- user asks to check existing files first
- the topic is a refinement of an existing document rather than an obvious fresh topic
- the natural-language topic is not yet normalized into a curated topic key
