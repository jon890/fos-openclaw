# study-topic-recommender

## 메타데이터

- `name: study-topic-recommender`
- `workspace: career-os`

## 설명

morning 학습 토픽 추천 파이프라인. inventory 갱신 + 점수(ADR-010) + mix target(ADR-012) + RSS/Atom feed discovery(ADR-013). live-coding seed pool에서 1개를 골라 study-pack-writer로 dispatch하는 wrapper도 포함. dispatcher의 `recommend-topics` / `live-coding-dispatch` 명령이 이 skill의 runner를 호출.

## 진입점

| 스크립트 | 설명 |
|---|---|
| `scripts/run_topic_recommendation.sh` | inventory 갱신 후 추천 markdown 출력 (`recommend-topics` 명령) |
| `scripts/run_live_coding_dispatch.sh` | live-coding seed pool에서 1개 선택 → `study-pack` 위임 (`live-coding-dispatch` 명령) |

## 산출물

- `data/runtime/topic-inventory.json` — 전체 토픽 풀 재고 + 추천 결과
- `data/runtime/topic-inventory-history.jsonl` — 추천 이력 (cooldown 계산용)
- `data/runtime/morning-topic-recommendation.md` — 10픽 + 오늘의 3선 markdown
- `data/runtime/live-coding-generated-topic.json` (임시) — live-coding 선택 결과 → study-pack 흐름으로 위임

## 핵심 스크립트

| 파일 | 역할 |
|---|---|
| `scripts/refresh_topic_inventory.py` | 재고 계산 + 점수 기반 추천 + feed discovery + markdown 렌더링 |
| `scripts/feed_discovery.py` | RSS/Atom fetch·파싱·캐싱 모듈 (ADR-013) |

## 관련 ADR

ADR-009 (reservoir), ADR-010 (점수 기반 선택), ADR-012 (10픽 mix target), ADR-013 (feed discovery), ADR-017 (skill 분해).

## 관련 config

- `config/topics.json` — study-pack 토픽 정의
- `config/live-coding-seed-pool.json` / `live-coding-seed-candidates.json` — live-coding seed
- `config/sources.json` — tech-blog / AI / geek reservoir
