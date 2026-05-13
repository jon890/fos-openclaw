# knowledge-gap-analyzer

name: knowledge-gap-analyzer
description: 후보자의 코드/문서 갭을 분석. baseline(전체 큐레이션 set, ADR-003)·daily(토픽 집중, ADR-001)·smoke(최소 점검) 세 가지 모드. dispatcher의 `baseline` / `daily` / `smoke` 명령이 이 skill의 runner를 호출.

## 모드

| 모드 | 설명 | 진입 스크립트 |
|---|---|---|
| baseline | 큐레이션된 core 파일 전체 분석 (ADR-003) | `scripts/run_baseline.sh` |
| daily | 오늘의 토픽 집중 분석 (ADR-001) | `scripts/run_daily.sh` |
| smoke | 최소 파일 세트로 파이프라인 점검 | `scripts/run_smoke_test.sh` |

## 산출물

- `data/reports/baseline/YYYY-MM-DD/report.md`
- `data/reports/daily/YYYY-MM-DD/report.md`
- `data/study-progress.json` (daily 실행 시 자동 갱신)

## helper 스크립트

- `scripts/build_target_file_list.py` — 토픽 기반 대상 파일 목록 생성
- `scripts/select_topic.py` — study-progress.json 기반 토픽 자동 선택
- `scripts/update_study_progress.py` — daily 완료 후 study-progress.json 갱신

## 관련 ADR

- ADR-001: daily 실행 토픽 선택 전략
- ADR-002: 파일 선택 전략
- ADR-003: baseline chunking 제거 (단일 호출)
- ADR-014: 스터디 진행 추적
- ADR-017: skill 폴더 분해 계획
