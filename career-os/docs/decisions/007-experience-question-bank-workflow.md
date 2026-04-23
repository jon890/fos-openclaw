# ADR-007: Dedicated workflow for experience-based interview question banks

- Status: Accepted
- Date: 2026-04-16

## Context

The existing `study-pack-writer` workflow was designed for technical article-style outputs.
It works well for topic-centric documents such as EXPLAIN, InnoDB MVCC, JPA N+1, Kafka design, and live-coding packs.

Experience-based interview preparation is a different output type:

- input is resume + selected task history + target JD
- output is a question-bank and answer-prep sheet, not a technical article
- validation needs to check question structure rather than article sections
- feeding too many task files at once makes generation unstable

Repeated attempts showed that the shared study-pack path was a poor fit for question-bank outputs.

## Decision

Create a dedicated workflow for experience-based interview question banks.

Key design choices:

1. Separate skill and prompt from `study-pack-writer`
2. Use selected input files only, not the full task tree
3. Maintain separate topic config in `config/experience-question-bank-topics.json`
4. Use dedicated output structure under `interview/experience-based/`
5. Validate for question-bank structure:
   - five main questions
   - five follow-up questions per main question
   - answer points
   - one-minute answer structure
   - pressure-question defense points
6. Start with two tracks:
   - AI service team
   - slot team

## Consequences

### Positive
- Better alignment between prompt, input, validation, and output type
- Lower generation instability from oversized input scopes
- More directly usable interview-prep documents
- Easier to tune tracks independently by career area

### Negative
- Additional workflow surface to maintain
- Some duplication with the study-pack infrastructure

## Notes

Morning Discord recommendations for experience-based prep should remain short summary messages.
Full markdown generation should happen on demand or via the dedicated workflow.
