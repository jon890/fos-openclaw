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
   - Naver Land (static collector)
   - optional Naver browser fallback
   - Hogangnono
   - KB Land
4. normalize into `summary.json`
5. synthesize `report.md` with Claude CLI JSON output
6. write artifacts under `data/YYYY-MM-DD/`
7. append run metadata under `logs/`

## Known behavior

- Naver Land API collection uses cookie/Bearer authentication and should paginate article lists until `isMoreData` is false (bounded by the collector's page cap), not just page 1.
- Hogangnono and KB Land are useful cross-check sources, especially for complex metadata and non-Naver listing context.
- Focus-unit matching is handled in the normalizer and should stay conservative.
- Whole-complex values must not be presented as focus-unit-confirmed unless exact match logic supports it.

## Guri buy-search preferences

Current buyer-priority scoring for the recurring Guri search:
- Put location/입지 first: daily infrastructure, transit/bus access, commercial/medical/school convenience, and easy walking routes should outweigh simple price sorting.
- Penalize steep hill / daily access friction. 수택주공 was visited and felt too uphill, so its price/area appeal should be discounted.
- Include good-location smaller units instead of filtering them out: keep LG원앙/엘지원앙 전용49/52 and 대림한숲 전용51 candidates visible when they fit the budget.
- Include 구리럭키 / 럭키아파트 (Naver complexNo `24858`) with direct Naver article links: `https://new.land.naver.com/complexes/24858?articleNo=<articleNo>`.
- Include 인창동 주공 by explicit Naver complex numbers instead of relying on Naver search endpoint discovery: 인창1단지주공 `1659`, 인창2단지주공 `1660`, 인창4단지주공 `1661`, 인창6단지주공 `1662`.
- Keep durable candidate complex metadata in `config/guri-buy-complexes.json`; use it as the source of truth for known complex numbers in broad Guri buy-search runs.
- For 구리럭키 and 인창동 주공, separate 실거주+주담대-friendly listings from 세안고/갭투 listings. Treat 세안고, 전세안고, 갭투자, 갱신권, or late-2027/2028 occupancy as high risk for this buyer unless a bank and realtor confirm financing/possession feasibility.
- Prefer 주인거주, 즉시입주, 공실 인도 가능, or near-term 입주협의 listings even if the sticker price is slightly higher.

## Guardrails

- Prefer exact or clearly-labeled provisional matches.
- Do not invent prices, listing counts, or transaction evidence.
- If a source fails, preserve the failure in raw/summary outputs.
- Keep outputs reproducible and idempotent per report date when practical.

## Improvement priorities

1. Naver 수집은 ADR-001(쿠키+Bearer 기반 API 통합)로 정착했다. 후속: NID_SES 만료 감지/알림, JWT 자동 추출 PoC, 추가 교차검증 소스(국토부 실거래가 등) 검토.
2. Move target/source config from env defaults into explicit config files where useful.
3. Expand the smoke-test entrypoint into a routine health check for collector/normalizer changes.
4. Clarify notification policy vs pure batch mode.
5. Keep OpenClaw wrapper glue-only.

## Smoke test

Quick collector/normalizer health check:
- `skills/apartment-daily-report/scripts/run_smoke_test.sh`

Optional browser mode example:
- `NAVER_BROWSER_ENABLED=1 NAVER_BROWSER_CLAUDE_COMMAND='...' skills/apartment-daily-report/scripts/run_smoke_test.sh`

Current expectation:
- Naver collector should at least return a non-error status plus limited static signals.
- Hogangnono and KB Land should produce structured data.
- `summary.json` should be generated successfully.
