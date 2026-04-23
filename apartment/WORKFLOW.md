# Apartment Workflow

## Goal

Produce a repeatable daily apartment market report for the target complex while keeping workflow logic durable in `~/ai-nodes/apartment`.

Current default target:
- 엘지원앙아파트 (LG원앙)
- 경기 구리시 수택동 854-2 / 체육관로 54
- focus unit: 59A / 전용 59㎡

## Source of truth

All business logic for the apartment workflow should live here:
- collectors
- normalizer
- Claude prompt
- task-specific config

OpenClaw workspace files should only provide thin delegation or scheduling glue.

## Current execution path

1. `skills/apartment-daily-report/scripts/run_report.sh`
2. self-wrap through `_shared/bin/track_task.sh`
3. collect source data from:
   - Naver Land
   - Hogangnono
   - KB Land
4. normalize into `summary.json`
5. synthesize `report.md` with Claude CLI JSON output
6. write artifacts under `data/YYYY-MM-DD/`
7. append run metadata under `logs/`

## Known behavior

- Naver Land currently resolves to a usable entry path, but extraction is still partial (`legacy-map-redirect`).
- Hogangnono and KB Land are currently the strongest structured signals.
- Focus-unit matching is handled in the normalizer and should stay conservative.
- Whole-complex values must not be presented as 59A-confirmed unless exact match logic supports it.

## Guardrails

- Prefer exact or clearly-labeled provisional matches.
- Do not invent prices, listing counts, or transaction evidence.
- If a source fails, preserve the failure in raw/summary outputs.
- Keep outputs reproducible and idempotent per report date when practical.

## Improvement priorities

1. Deepen Naver extraction beyond redirect/static shell signals.
2. Move target/source config from env defaults into explicit config files where useful.
3. Expand the smoke-test entrypoint into a routine health check for collector/normalizer changes.
4. Clarify notification policy vs pure batch mode.
5. Keep OpenClaw wrapper glue-only.

## Smoke test

Quick collector/normalizer health check:
- `skills/apartment-daily-report/scripts/run_smoke_test.sh`

Current expectation:
- Naver collector should at least return a non-error status plus limited static signals.
- Hogangnono and KB Land should produce structured data.
- `summary.json` should be generated successfully.
