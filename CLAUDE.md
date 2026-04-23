# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository shape

`~/ai-nodes` is a multi-workspace container, not a single project. Each top-level directory is an **independent task workspace** with its own skills, data, logs, and config. Workspaces should remain isolated — do not cross-reference assets between them.

Current workspaces:

- `apartment/` — daily apartment market report pipeline (target: 엘지원앙아파트 / LG원앙, 59A unit). See `apartment/AGENTS.md` and `apartment/TOOLS.md`.
- `career-os/` — CJ OliveYoung Wellness Platform Java backend interview prep (interview date 2026-04-21). Has its own `career-os/CLAUDE.md` that overrides this one when working in that subtree.
- `_shared/` — the **only** cross-workspace code. Contents: `track_task.sh` (run tracker), `extract_claude_result.py` (Claude CLI JSON → markdown report), `update_artifacts.py` (`data/generated-artifacts.json` upsert).

Each workspace follows the same layout: `skills/`, `data/`, `logs/`, `config/`, and (for career-os) `docs/decisions/` for ADRs.

## Execution model

All workspace runs are wrapped by `_shared/bin/track_task.sh`, which:

- writes per-run logs to `<workspace>/logs/task-runs.jsonl` and `token-usage.jsonl`
- captures `openclaw status` before/after to diff model/token/cache deltas
- snapshots file metrics (`report.md`, `analysis-input.md`, `target-files.txt`) before and after
- ingests Claude CLI usage JSON via `TRACK_TASK_CLAUDE_USAGE_FILE` when a runner writes it

Workspace runners must be invokable via the tracker; never bypass it when producing durable artifacts. All `run_now.sh`-style entry points in `career-os` already `exec` through the tracker, and `apartment/skills/apartment-daily-report/scripts/run_report.sh` self-wraps via `TRACK_TASK_WRAPPED`.

**External dependency**: if `_shared/bin/track_task.sh` is missing, all workspace runners fail. Treat this script as load-bearing.

## Workspace entry points

### apartment

```bash
apartment/skills/apartment-daily-report/scripts/run_report.sh
```

Outputs land under `apartment/data/YYYY-MM-DD/` as `report.md`, `raw-search.json`, `summary.json`, `claude.result.json`. Uses `claude --permission-mode bypassPermissions --print --output-format json` for synthesis, with a fallback markdown if Claude times out (90s).

### career-os

```bash
career-os/skills/cj-oliveyoung-java-backend-prep/scripts/run_now.sh baseline
career-os/skills/cj-oliveyoung-java-backend-prep/scripts/run_now.sh daily [topic]
career-os/skills/cj-oliveyoung-java-backend-prep/scripts/run_now.sh study-pack <topic>
career-os/skills/cj-oliveyoung-java-backend-prep/scripts/run_now.sh question-bank <topic>
career-os/skills/cj-oliveyoung-java-backend-prep/scripts/run_now.sh master [topic]
career-os/skills/cj-oliveyoung-java-backend-prep/scripts/run_now.sh smoke
```

`run_now.sh` is the single dispatch point — it resolves topic config from `career-os/config/*.json`, uses a topic-specific resolver (`resolve_study_pack_topic.py`, `resolve_question_bank_topic.py`, `resolve_master_topic.py`) that emits `export KEY=value` lines consumed via `eval`, then `exec`s the matching skill runner through `track_task.sh`. Topic keys live in `career-os/config/{topic-file-map,study-pack-topics,experience-question-bank-topics,interview-master-topics}.json`.

`study-pack`, `question-bank`, and `master` runs commit and push the generated markdown into `career-os/sources/fos-study` and upsert `data/generated-artifacts.json` via `_shared/bin/update_artifacts.py` — any failure to push must surface, not silently stop.

Sub-skills live under `career-os/skills/`: `cj-oliveyoung-java-backend-prep` (dispatcher + baseline/daily/smoke/morning-*), `study-pack-writer` (topic-driven markdown), `experience-question-bank-writer` (JSON-schema-validated interview Q&A), `interview-master-writer` (cross-team senior-backend playbook).

## Working conventions

- `career-os/sources/fos-study` is a synced external repo (`github.com/jon890/fos-study`, branch `main`). Analyze markdown only; ignore `.claude/**`. Do not treat it as editable project code unless a study-pack/question-bank run is actively publishing into it.
- Auto-generated reports go to `<workspace>/data/reports/`. There is no separate curation sink — see ADR-004 (폐기).
- Architecture decisions for `career-os` are ADRs in `career-os/docs/decisions/`. Consult them before changing workflow scripts, file-selection strategy, or publishing policy.
- Keep workflows rerunnable and idempotent per date. Prefer local git-sync + file reading over live collection pipelines.
- Be explicit about uncertainty in reports (listing counts, transaction matches). Don't fill gaps with guesses — record the gap.
- Secrets live in `<workspace>/config/.env` (e.g. `GITHUB_TOKEN`), not in the repo root.
- Cost discipline for career-os: avoid broad full-repo analysis; baseline uses the curated core set in `career-os/config/baseline-core-files.txt`, daily runs stay smaller.
