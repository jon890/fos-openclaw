# CLAUDE.md - career-os working context

## Current MVP Goal

Prepare for the **CJ OliveYoung Wellness Platform Java backend interview** scheduled for **2026-04-21**.

## Candidate Focus

- Primary track: **Java backend**
- Exclude Kotlin for the current MVP
- Self-assessed weak area: **DB**
- Goal: practical, interview-focused daily study guidance

## Source of Truth

- Local synced repo: `~/ai-nodes/career-os/sources/fos-study`
- Analyze markdown files only
- Ignore `.claude/**`
- Candidate profile: `~/ai-nodes/career-os/config/candidate-profile.md` — evidence-tagged 11-section profile (커리어 타임라인, 보유 기술 스택, 주요 프로젝트, 강점/약점, 의사결정 패턴, 협업 스타일, 면접 준비 우선순위 등). 모든 claim은 `task/**` 또는 `resume/**` 경로가 태깅되어 있음. 프로필 수정은 여기 단일 파일에 집중.

## Current Workflow

Single dispatcher: `skills/cj-oliveyoung-java-backend-prep/scripts/run_now.sh`. Supported sub-commands:

```
run_now.sh baseline                     # curated 10-file baseline gap analysis (ADR-003)
run_now.sh daily [topic]                # daily focus report; auto-picks most overdue topic if omitted
run_now.sh study-pack <topic>           # generate one topic study pack, commit/push to fos-study
run_now.sh question-bank <topic>        # generate experience-based interview Q&A, commit/push
run_now.sh master [topic]               # generate senior-backend master playbook, commit/push
run_now.sh smoke                        # minimal smoke check
```

All sub-commands are exec-wrapped by `_shared/bin/track_task.sh`, which appends per-run metrics to `logs/task-runs.jsonl` and `logs/token-usage.jsonl`.

Sub-skills:
- `skills/study-pack-writer/` — topic → full markdown study pack
- `skills/experience-question-bank-writer/` — resume/task → strict-schema JSON → rendered interview Q&A
- `skills/interview-master-writer/` — resume/task → senior-backend master playbook

Shared helpers under `_shared/bin/`:
- `extract_claude_result.py` (Claude CLI JSON → `report.md`, feeds usage metrics to the tracker)
- `update_artifacts.py` (upsert `data/generated-artifacts.json` after a successful push)

## Baseline Strategy

Do **not** analyze the full repo by default.
Use the curated core set in:
- `config/baseline-core-files.txt`

Current baseline core set centers on:
- `interview/cj-oliveyoung-wellness-backend.md`
- DB fundamentals and MySQL internals
- Spring JPA transactions
- distributed transactions
- cache basics
- Redis basics

## Daily Strategy

Daily reports should be smaller than the baseline.
Prefer 3-5 high-value documents tied to the current study topic.

## Known Findings So Far

Smoke test succeeded and identified these likely weak spots:
- JPA N+1 handling
- reading `EXPLAIN` plans
- composite / covering index design
- Redis caching patterns
- Kafka practical design

Likely strong areas based on notes already found:
- B+Tree / index structure
- InnoDB MVCC and locking
- Spring transaction pitfalls
- distributed transaction concepts

## Token / Cost Discipline

Be conservative with model usage.
- Avoid broad full-repo analysis.
- Keep baseline bounded to the curated core set.
- Keep daily runs even smaller.
- If Claude usage is exhausted, plan a fallback path later instead of repeatedly retrying large prompts.

## Working Principle

Prefer simple, rerunnable local workflows over complex collection pipelines.
Git sync + local file reading is the current preferred pattern.

## Architecture Decisions

Key design decisions are recorded as ADRs in `docs/decisions/`.
Consult them before modifying workflow scripts or changing file selection strategy.

| ADR | 주제 |
|-----|------|
| [001](docs/decisions/001-daily-file-selection-strategy.md) | Daily 파일 선택 전략 (토픽 기반 3-5개) |
| [002](docs/decisions/002-study-progress-tracking.md) | 학습 진도 추적 (data/study-progress.json) |
| [003](docs/decisions/003-baseline-chunking-removal.md) | Baseline 청킹 제거 (단일 호출) |
| [004](docs/decisions/004-reports-directory-convention.md) | reports/ 디렉터리 컨벤션 (폐기) |
| [005](docs/decisions/005-study-pack-publishing-policy.md) | study-pack 퍼블리싱 정책 |
| [006](docs/decisions/006-study-pack-entrypoint-and-routing.md) | study-pack 엔트리포인트 및 라우팅 |
| [007](docs/decisions/007-study-pack-stdout-capture.md) | study-pack 생성: 파일 쓰기 → stdout 캡처 |
