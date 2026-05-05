# AGENTS.md - stock-investment task workspace

This directory is an independent task workspace under `~/ai-nodes`.

## Purpose

Daily stock/crypto investment monitoring and morning briefing automation.

Initial focus:
- Circle Internet Group (`CRCL`)
- Bitcoin (`BTC-USD`)

Planned expansion:
- Nasdaq / QQQ / Nasdaq 100
- Google / Alphabet (`GOOGL`, `GOOG`)
- Other crypto-adjacent equities when explicitly added

## Structure

- `skills/` reusable task skills
- `config/` watchlists, source config, briefing profiles
- `data/YYYY-MM-DD/` daily outputs
- `logs/` execution logs
- `docs/decisions/` ADRs and workflow decisions

## Rules

- Keep this task reusable and isolated from other tasks.
- Prefer storing durable assets here, not in `~/.openclaw/workspace`.
- Be explicit about uncertainty; this is not financial advice.
- Separate verified facts/data from interpretation.
- Morning Discord messages should be concise; detailed artifacts live under `data/YYYY-MM-DD/`.
