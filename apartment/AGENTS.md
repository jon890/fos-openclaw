# AGENTS.md - apartment task workspace

This directory is an independent task workspace under `~/ai-nodes`.

## Purpose

This workspace is dedicated to apartment market reporting and automation.

Current target:
- 엘지원앙아파트 (LG원앙)
- 경기 구리시 수택동 854-2 / 체육관로 54

## Structure

- `skills/` reusable task skills
- `data/YYYY-MM-DD/` daily outputs
- `logs/` execution logs
- `config/` task-specific configuration

## Rules

- Keep this task reusable and isolated from other tasks.
- Prefer storing durable assets here, not in `~/.openclaw/workspace`.
- The OpenClaw workspace is the orchestrator layer, not the long-term home for this task.
- This task now lives inside the `~/ai-nodes` mono-repo. Make durable workflow changes here first.
- OpenClaw workspace skills should remain thin wrappers, not parallel implementations.
- See `WORKFLOW.md` for the current apartment pipeline contract.
- 아키텍처 결정 사항은 `docs/decisions/`에 ADR로 기록 — 현재 [ADR-001](docs/decisions/001-naver-api-integration.md): 네이버 부동산을 쿠키+Bearer 기반 API로 통합.
