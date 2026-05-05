# ADR-001: stock-investment workspace and morning brief pipeline

- Status: Accepted
- Date: 2026-05-05

## Context

User wants a reusable morning briefing workflow for stock/crypto investing, starting with Circle Internet Group and Bitcoin, then expanding to Nasdaq and Google.

## Decision

Create `~/ai-nodes/stock-investment` as the canonical task workspace.

The first skill is `stock-investing-morning-brief`:

1. collect price data and lightweight public news snippets
2. save raw artifacts under `data/YYYY-MM-DD/`
3. use Claude CLI for concise Korean synthesis
4. send a short Discord briefing to `#주식토크`
5. keep the watchlist profile-based so CRCL/BTC can later expand to Nasdaq/Google

## Guardrails

- Morning output must distinguish data from interpretation.
- Do not provide personalized buy/sell orders.
- Note blocked/inaccessible sources explicitly.
- Keep scripts idempotent and file-backed.
