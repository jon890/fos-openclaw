# AGENTS.md - career-os task workspace

This directory is an independent task workspace under `~/ai-nodes`.

## Purpose

This workspace is dedicated to career growth, company-fit analysis, and interview preparation automation.

Current MVP target:
- Company: CJ OliveYoung
- Domain: Wellness Platform
- Role: Java backend
- Interview date: 2026-04-21

## Structure

- `skills/` — reusable task skills
- `sources/` — local synced source repositories
- `config/` — candidate profile, baseline core file list, topic-file-map.json
- `data/reports/` — **auto-generated** baseline and daily reports (written by scripts)
- `data/study-progress.json` — learning progress tracker (topic + file history, auto-updated by run_daily.sh)
- `data/normalized/` — structured intermediate data
- `data/source/` — collected external notes when needed
- `docs/decisions/` — Architecture Decision Records (ADRs) for workflow design choices
- `logs/` — execution logs

## Workflow Entry Points

```
run_now.sh baseline                    # Baseline gap analysis (curated 10-file core set, ADR-003)
run_now.sh daily                       # Daily report — auto-selects most overdue weak spot
run_now.sh daily <topic>               # Daily report — forced topic (see config/topic-file-map.json)
run_now.sh study-pack <topic>          # Generate full-article study pack, commit/push to fos-study
run_now.sh question-bank <topic>       # Generate experience-based interview Q&A, commit/push
run_now.sh master [topic]              # Generate senior-backend master playbook, commit/push
run_now.sh smoke                       # Smoke test
```

Sub-skills invoked via the dispatcher:
- `skills/study-pack-writer/` — topic resolver + extractor/validator + runner
- `skills/experience-question-bank-writer/` — topic resolver + JSON-schema-validated renderer + runner
- `skills/interview-master-writer/` — topic resolver + runner (reuses study-pack extractor for validation)

**External dependencies** (all under `~/ai-nodes/_shared/bin/`):
- `track_task.sh` — every mode exec's through this tracker; missing ⇒ every run fails.
- `extract_claude_result.py` — Claude CLI JSON → `report.md` (baseline/daily/smoke/apartment).
- `update_artifacts.py` — upsert `data/generated-artifacts.json` after study-pack/question-bank/master publish.

## Architecture Decisions

Design rationale is in `docs/decisions/`. Key ADRs:

| ADR | 주제 |
|-----|------|
| [001](docs/decisions/001-daily-file-selection-strategy.md) | Daily 파일 선택 전략 |
| [002](docs/decisions/002-study-progress-tracking.md) | 학습 진도 추적 |
| [003](docs/decisions/003-baseline-chunking-removal.md) | Baseline 청킹 제거 |
| [004](docs/decisions/004-reports-directory-convention.md) | reports/ 디렉터리 컨벤션 (폐기) |

## Rules

- Keep this task reusable and isolated from other tasks.
- Prefer local source sync for repositories, then Claude for analysis.
- Keep workflows background-rerunnable and simple before adding extra normalization layers.
- Store durable assets here, not in `~/.openclaw/workspace`.
- If version control is added later, manage it from this task directory.
