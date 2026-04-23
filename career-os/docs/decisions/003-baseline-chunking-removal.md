---
adr: "003"
title: Baseline 청킹 제거
status: 결정됨
date: 2026-04-13
---

# ADR-003: Baseline 청킹 제거

## 배경

`run_baseline.sh`는 10개 파일을 5개씩 2청크로 나눠 Claude를 3번 호출했다
(chunk1 분석 → chunk2 분석 → merge). 10개 파일은 컨텍스트 윈도우에 충분히 들어가는
크기임에도 불필요한 복잡도와 비용이 발생하고 있었다.

- 3회 API 호출 = 3배 비용 + 3배 레이턴시
- merge 단계에서 두 청크의 내용이 희석될 위험
- chunk 파일들(`analysis-input.chunk1.md`, `claude.chunk1.json` 등)이 결과 디렉터리를 어지럽힘

## 결정

baseline은 단일 Claude 호출로 처리한다.
10개 파일 기준으로 충분히 한 번에 처리 가능하다.
baseline core set이 25개 이상으로 늘어나는 시점에서 청킹 재도입을 고려한다.

## 거절한 대안

| 대안 | 거절 이유 |
|------|-----------|
| 청킹 유지 | 10개 파일에 불필요, 비용 3배, 복잡도 높음 |
| 청크 수 줄이기 (2→1) | 청킹 자체가 불필요한 상황 |

## 결과

- baseline 실행 비용 약 60% 절감 (3 API 호출 → 1 API 호출)
- 결과 디렉터리에 `target-files.txt`, `analysis-input.md`, `claude.result.json`, `report.md`만 남아 깔끔
- 재도입 기준: `config/baseline-core-files.txt`가 25개 초과 시 검토
