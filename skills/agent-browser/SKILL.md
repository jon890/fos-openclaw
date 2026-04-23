---
name: agent-browser
description: Browser automation via the local agent-browser CLI. Use when Claude should directly control a browser to navigate pages, click, type, wait for dynamic content, extract visible text/data, take screenshots, or automate web UI workflows. Prefer this over static web fetching for hydration-heavy sites like Naver Land, and use it as the primary browser skill for apartment collection, exploratory QA, and visible-page evidence gathering.
---

# agent-browser

Use the locally installed `agent-browser` CLI as the primary browser automation layer.

## Install status

Installed locally via:
- `npm i -g agent-browser`
- `agent-browser install`

If Chrome launch fails on Linux due to missing shared libraries, run:
- `agent-browser install --with-deps`

## Start here

Before using commands, load the live CLI guidance so instructions match the installed version:

```bash
agent-browser skills get core
agent-browser skills get core --full
```

List specialized skills when needed:

```bash
agent-browser skills list
```

Current notable specializations:
- `electron`
- `slack`
- `dogfood`
- `vercel-sandbox`
- `agentcore`

## Core workflow

Use the snapshot/ref loop:

```bash
agent-browser open <url>
agent-browser snapshot -i
agent-browser click @eN
agent-browser snapshot -i
```

Rules:
- Re-snapshot after any page-changing action.
- Prefer `snapshot -i` over raw HTML scraping.
- Prefer visible-page evidence over guessed DOM assumptions.
- Use `wait --load networkidle`, `wait --text`, or `wait --url` instead of blind sleeps.

## For apartment / Naver Land

Use `agent-browser` as the primary dynamic collection path when Naver Land requires hydration.

Preferred extraction order:
1. Open target URL
2. Snapshot interactive elements
3. Navigate to visible listing/complex views
4. Extract only clearly visible evidence:
   - complex name
   - focus unit labels (59A / 전용 59㎡)
   - listing counts
   - visible price text
   - short visible snippets
5. Return structured JSON for downstream normalizers

Do not invent values hidden behind incomplete page state.

## Architecture role

In `~/ai-nodes`, this skill is a reusable browser capability layer.
Task-specific workflows like `apartment/` should call into it or mirror its command contract, while staying thin on orchestration.
