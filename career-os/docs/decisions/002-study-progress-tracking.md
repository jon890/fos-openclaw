---
adr: "002"
title: 학습 진도 추적
status: 결정됨
date: 2026-04-13
---

# ADR-002: 학습 진도 추적

## 배경

daily 리포트가 매번 동일한 파일을 분석해 동일한 약점을 반복 제안하는 문제가 있었다.
어제 무엇을 공부했는지 기록이 없어 D-8처럼 촉박한 일정에서 중복 학습이 발생할 수 있었다.

## 결정

- `data/study-progress.json`에 세션 기록과 약점 토픽별 진도를 함께 저장한다.
- **하이브리드 포맷**: 세션별 토픽(의미 단위) + 파일 경로(참조 추적) 둘 다 기록한다.
- `run_daily.sh`가 리포트 생성 성공 후 자동으로 해당 파일을 업데이트한다.
- `weak_spots` 섹션의 `last_studied`와 `study_count`를 기반으로 ADR-001의 자동 토픽 선택이 동작한다.

```json
{
  "sessions": [
    {
      "date": "2026-04-13",
      "topics": ["redis-cache-aside"],
      "files": ["database/redis/basic.md", "architecture/cache-strategies.md"],
      "source": "daily-run"
    }
  ],
  "weak_spots": {
    "jpa-n+1": { "last_studied": null, "study_count": 0 },
    "redis-cache-aside": { "last_studied": "2026-04-13", "study_count": 1 }
  }
}
```

## 거절한 대안

| 대안 | 거절 이유 |
|------|-----------|
| 파일 단위만 기록 | 어떤 토픽을 다뤘는지 사람이 읽기 어려움 |
| 토픽 단위만 기록 | 어떤 파일을 실제로 분석했는지 재현 불가 |
| 대화 기반 수동 업데이트 | 자동화 워크플로에서 누락 위험 |

## 결과

- daily 리포트 실행만 해도 진도가 자동 기록됨
- 자동 토픽 선택 시 중복 학습 방지
- 세션 히스토리로 공부 패턴 파악 가능
