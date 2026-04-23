# fos-openclaw / ai-nodes mono-repo

This repository is the source-of-truth mono-repo for reusable OpenClaw-oriented task workspaces.

## Structure

- `apartment/` — apartment market tracking and reporting workflows
- `career-os/` — study/interview preparation workflows
- `_shared/` — shared helper scripts used across task workspaces

Each task workspace owns its own:
- `AGENTS.md`
- `TOOLS.md`
- `skills/`
- `config/`
- generated `data/` and `logs/` (ignored in git)

## Architecture

- Durable workflow logic lives in this repo under `~/ai-nodes`.
- `~/.openclaw/workspace` is the orchestrator/runtime layer.
- OpenClaw workspace skills should stay thin and delegate into this repo.
- If a task workflow changes, update this repo first.

## Git policy

Ignored by default:
- `.omc/`, `.claude/`
- `**/data/`, `**/logs/`, `**/tmp/`
- transient result files such as `*.result.json`

Nested repo note:
- `career-os/sources/fos-study/` is managed separately and ignored from the mono-repo.

## Apartment workflow quick start

Canonical runner:
- `apartment/skills/apartment-daily-report/scripts/run_report.sh`

Thin OpenClaw wrapper:
- `~/.openclaw/workspace/skills/apartment-daily-report/scripts/run_report.sh`

The wrapper must remain glue-only.
