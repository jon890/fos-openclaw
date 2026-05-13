---
name: command-router
description: career-os의 14개 dispatch 명령 단일 진입점. `_shared/bin/track_task.sh`로 모든 runner 래핑, 자동 Discord 알림 + cost summary 부착. 직접 호출하지 말 것 — 일상 운영은 `run_now.sh <command>` 경유.
---

# command-router

career-os 워크스페이스의 단일 dispatch 진입점.

## 역할

- 모든 14개 명령(`baseline`, `daily`, `study-pack`, `question-bank`, `master`, `recommend-topics`, `recommend-positions`, `replenish-topics`, `maintain-study-pack`, `foodville-coffeechat`, `smoke`, `bootcamp-batch`, `live-coding-dispatch`, `auto-question-bank`)을 하나의 진입점으로 라우팅.
- 각 runner를 `_shared/bin/track_task.sh`로 래핑하여 실행 메트릭을 `logs/task-runs.jsonl` + `logs/token-usage.jsonl`에 기록.
- `run_tracked()` 헬퍼가 완료·실패 시 `_shared/lib/notify_discord.ts`를 통해 Discord 알림에 `_shared/lib/format_cost_summary.ts` 비용 요약을 자동 부착.

## 파일 구성

- `scripts/run_now.sh` — dispatcher 본체. 모든 명령 case를 포함.
- `scripts/setup_env.sh` — `config/.env` 초기화 헬퍼. dispatcher와 함께 두는 이유: 워크스페이스 진입 시 dispatcher보다 먼저 실행해야 하는 setup 자산이라 응집도가 높음.

`notify_discord.sh`는 plan004에서 `_shared/lib/notify_discord.ts`로 마이그레이션 완료. 이 폴더에는 존재하지 않음.

## 관련 ADR

- ADR-008: Discord 알림 설계
- ADR-014: usage 전파 및 비용 측정
- ADR-017: command-router skill 분리 (본 폴더 신설 근거)

## 호출 방법

```bash
career-os/skills/command-router/scripts/run_now.sh <command> [args...]
```

plan006(ADR-019) 이후에는 `career-os/scripts/command-router/run_now.sh`로 재배치 예정.
