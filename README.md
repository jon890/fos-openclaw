# fos-openclaw / ai-nodes 모노레포

이 저장소는 재사용 가능한 OpenClaw 지향 작업 워크스페이스들의 단일 출처(source-of-truth) 모노레포입니다.

## 구조

- `apartment/` — 아파트 시세 추적 및 리포트 워크플로
- `career-os/` — 학습/면접 준비 워크플로
- `_shared/` — 작업 워크스페이스 전반에서 쓰이는 공용 헬퍼 스크립트

각 작업 워크스페이스는 다음을 자체 소유합니다:
- `AGENTS.md`
- `TOOLS.md`
- `skills/`
- `config/`
- 생성되는 `data/`, `logs/` (git 무시 대상)

## 아키텍처

- 영속적인 워크플로 로직은 이 저장소(`~/ai-nodes`)에 존재합니다.
- `~/.openclaw/workspace`는 오케스트레이터/런타임 레이어입니다.
- OpenClaw 워크스페이스 스킬은 얇게 유지하고, 이 저장소로 위임해야 합니다.
- 작업 워크플로가 바뀌면 이 저장소를 **먼저** 업데이트하세요.

## Git 정책

기본 무시 대상:
- `.omc/`, `.claude/`
- `**/data/`, `**/logs/`, `**/tmp/`
- `*.result.json` 같은 일시적 결과 파일

중첩 저장소 주의:
- `career-os/sources/fos-study/`는 별도 관리되며 이 모노레포에서 무시됩니다.

## Apartment 워크플로 빠른 시작

표준 러너:
- `apartment/skills/apartment-daily-report/scripts/run_report.sh`

얇은 OpenClaw 래퍼:
- `~/.openclaw/workspace/skills/apartment-daily-report/scripts/run_report.sh`

래퍼는 반드시 글루(glue) 역할만 수행해야 합니다.
