# Naver browser-assisted collection plan

## Why this is needed

Current static collection reaches:
- fin.land redirect confirmation
- map route + layer token
- Next-flight shell blobs

But it does not reliably expose:
- article list payloads
- listing prices
- complex detail data bound after hydration

So a browser-assisted collector is justified as a secondary path.

## Recommended approach

1. Keep the current static collector as the default cheap path.
2. Add a browser-assisted collector as an optional fallback for Naver only.
3. Extract only conservative fields:
   - current URL / route
   - visible listing counts if shown
   - visible trade tabs and selected tab
   - visible text snippets for complex title / address / counts
4. Record uncertainty explicitly.

## Integration idea

- new script: `skills/apartment-daily-report/scripts/collect_naver_browser.py`
- use it only when:
  - static collector returns `legacy-map-redirect` with weak signals, or
  - user explicitly requests browser mode
- merge browser result into `sources[].numericSignals` / `note`

## Guardrails

- Browser mode is slower and more brittle.
- Do not make browser mode the only path.
- Prefer visible text extraction over DOM assumptions when possible.
- Keep fallback behavior clear in report output.
