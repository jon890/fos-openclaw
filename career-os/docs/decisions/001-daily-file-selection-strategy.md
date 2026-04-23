---
adr: "001"
title: Daily 파일 선택 전략
status: 결정됨
date: 2026-04-13
---

# ADR-001: Daily 파일 선택 전략

## 배경

`run_daily.sh`의 원래 의도는 매일 3-5개의 고가치 파일만 분석하는 것이었다.
그러나 `build_target_file_list.py`는 `database/`, `architecture/`, `java/`, `interview/`
전체를 긁어 실제로는 70개 이상의 파일을 생성하고 있었다.
설계 의도와 구현이 완전히 어긋난 상태였다.

## 결정

- `config/topic-file-map.json`에 토픽 → 파일 목록 매핑을 관리한다.
- `run_daily.sh`는 `DAILY_TOPIC` 환경 변수 또는 `run_now.sh`의 두 번째 인자로 토픽을 받는다.
- 토픽이 지정되지 않으면 `data/study-progress.json`에서 `last_studied`가 가장 오래된
  (또는 null인) 약점 토픽을 자동 선택한다.
- `build_target_file_list.py`는 `--topic` / `--topic-map` 인자를 받아 정확한 파일 목록을 반환한다.
- 토픽 매핑이 없는 fallback 상황에서는 기존 INCLUDE_DIRS 방식으로 후퇴한다.

## 거절한 대안

| 대안 | 거절 이유 |
|------|-----------|
| INCLUDE_DIRS 전체 유지 | 의도(3-5개)와 구현(70개+) 간 괴리 해소 불가 |
| 고정 파일 5개 하드코딩 | 매일 같은 파일, 학습 진도 반영 불가 |
| 토픽을 항상 필수 인자로 강제 | 자동화 워크플로에서 매번 수동 지정 필요 |

## 결과

- daily 분석 범위가 실제로 3-5개로 줄어 토큰 비용 절감
- 새 토픽 추가 시 `config/topic-file-map.json`만 수정하면 됨 (스크립트 불필요)
- 자동 토픽 선택으로 중복 학습 방지 가능 (`study-progress.json` 연동 필요 → ADR-002)
