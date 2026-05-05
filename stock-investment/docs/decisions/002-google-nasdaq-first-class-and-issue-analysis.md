# ADR-002: Google/Nasdaq first-class monitoring and issue analysis

- Status: Accepted
- Date: 2026-05-05

## Context

The user clarified that Google/Alphabet and Nasdaq should not be treated as secondary expansion context inside the CRCL/BTC report. They should be analyzed like independent watch targets, especially because Google I/O is approaching and can become an event-driven catalyst.

## Decision

1. Promote `GOOGL`/`GOOG` and `QQQ`/`^NDX` into first-class report sections in the morning brief.
2. Add technical overheating context to each target using RSI14, distance from 20-day SMA, 52-week high distance, and volume vs 20-day average.
3. Add Google/Alphabet and Nasdaq-specific sources and focus areas:
   - Google I/O
   - Gemini / AI product updates
   - Google Cloud / TPU / AI infrastructure
   - Search/ads transition risk
   - antitrust/regulation and CapEx burden
   - QQQ/Nasdaq growth-tech risk tone
4. Add a one-off issue-analysis topic for `google-io-alphabet-ai` so Google I/O and Alphabet AI momentum can be analyzed more deeply than the morning brief.

## Guardrails

- Do not treat RSI or moving-average distance as a buy/sell signal by itself.
- Explain that strong trends can stay overbought.
- Separate event expectation from already-priced-in momentum.
- Treat Google I/O as a catalyst with both upside surprise and sell-the-news risk.
