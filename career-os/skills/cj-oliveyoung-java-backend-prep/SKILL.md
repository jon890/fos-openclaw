---
name: cj-oliveyoung-java-backend-prep
description: Collect markdown study notes from the jon890/fos-study repository, combine them with CJ OliveYoung target-role context and candidate profile data, then generate Java backend interview preparation reports. Use for baseline gap analysis and daily study reports before the 2026-04-21 interview.
---

# CJ OliveYoung Java Backend Prep

This skill supports a focused interview-prep workflow for the CJ OliveYoung Wellness Platform Java backend role.

## Scope

- Repository: `https://github.com/jon890/fos-study`
- Branch: `main`
- Include: markdown files only (`**/*.md`)
- Exclude: `.claude/**`
- Focus: Java backend
- De-emphasize/exclude: Kotlin for current MVP
- Candidate weak area hint: DB

## Workflow

1. Sync the local source repository under `sources/fos-study` using git clone/pull.
2. For the baseline report, use the curated core file set in `config/baseline-core-files.txt`.
3. For daily reports, use the target list builder to expand scope selectively.
4. Read `config/candidate-profile.md`.
5. Use Claude CLI in print mode to generate:
   - baseline gap report
   - daily study report
6. Save outputs under `data/reports/`.
7. Keep the workflow runnable by direct script execution so Claude can invoke it immediately in the local task workspace.

## Output goals

Reports should emphasize:
- backend interview readiness
- database weaknesses and missing depth
- Spring / transaction / JPA / performance / architecture gaps
- likely high-value study topics before 2026-04-21
- concrete daily study actions and likely interview questions

## Files

Dispatcher:
- `scripts/run_now.sh` — single entry point for `baseline | daily | study-pack | question-bank | master | smoke`; wraps every sub-runner through `_shared/bin/track_task.sh`.

Baseline / daily runners:
- `scripts/run_baseline.sh` — baseline gap analysis (ADR-003, single call)
- `scripts/run_daily.sh` — daily report, auto-selects most overdue topic unless `DAILY_TOPIC` is set
- `scripts/run_smoke_test.sh` — minimal end-to-end check
- `scripts/build_target_file_list.py` — expand topic → 3–5 markdown paths for daily runs
- `scripts/select_topic.py` — pick the most overdue weak-spot topic
- `scripts/update_study_progress.py` — append session + bump weak-spot counter after a daily run

Morning automations:
- `scripts/run_morning_live_coding.sh` — pick next uncovered live-coding topic, dispatch study-pack, notify Discord
- `scripts/run_morning_question_bank.sh` — regenerate the default experience question bank, notify Discord
- `scripts/notify_discord.sh` — thin Discord webhook poster

Utilities:
- `scripts/collect_fos_study.py` — GitHub Contents API fetcher for ad-hoc collection
- `scripts/setup_env.sh` — dev-time env bootstrap

Prompts:
- `references/baseline-prompt.md`
- `references/daily-prompt.md`

## External dependencies

- `_shared/bin/track_task.sh` — all runners exec through this tracker; missing ⇒ every run fails.
- `_shared/bin/extract_claude_result.py` — used by baseline/daily/smoke to pull `result` out of Claude CLI JSON and to feed usage metrics into the tracker.
- `claude` CLI on PATH (uses `--permission-mode bypassPermissions --print --output-format json`).
- Sub-skills invoked via dispatcher: `study-pack-writer`, `experience-question-bank-writer`, `interview-master-writer`.
