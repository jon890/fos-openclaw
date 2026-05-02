# ADR-012: Morning 추천을 10픽 + 오늘의 3선 큐레이션으로 확장

- Status: Accepted
- Date: 2026-05-02

## Context

ADR-009/010/011로 morning 추천 reservoir와 점수 기반 mix가 자리 잡았지만, 결과는 여전히 백엔드 / live-coding / DB 한 축에 갇혀 있었다.

관찰된 문제:

1. 매일 추천 5개가 거의 백엔드 study-pack/live-coding으로만 구성되어 reading 자료, 회사 사례, AI 흐름이 빠져 있었다.
2. 면접 준비라는 1차 목적은 유지하되, 답변 폭(다른 회사 사례, AI 시그널, 산업 동향)을 늘릴 외부 input이 부족했다.
3. AI 흐름이 빠르게 변하는 중인데 career-os가 이를 매일 갱신하지 않으면 본인이 운영하는 도구·기술 스택과 인지 사이의 격차가 벌어졌다.
4. 5개 항목 모두에 동등한 무게를 두면 사용자가 결국 "오늘 뭐부터 보지?"를 다시 결정해야 했다.

## Decision

morning 추천 결과를 다음 10픽 + 오늘의 3선 구조로 확장한다.

| 카테고리 | 슬롯 |
|----------|------|
| 백엔드 스터디 주제 | 3 |
| 회사·엔지니어링 기술 블로그 | 3 |
| AI 관련 | 3 |
| Geek/뉴스/산업 흐름 | 1 |
| **합계** | **10** |

추가로 "오늘의 3선" 섹션을 표시한다.

- 백엔드 1
- 기술 블로그 1
- AI 1

규칙은 단순히 "각 카테고리 추천 리스트의 맨 위 항목"이다. (백엔드 1순위는 ADR-010 점수 1위, 기타 카테고리는 reservoir 우선도 1위.)

### 백엔드 mix target 변경

ADR-010의 5-item mix(`new 2 / deepen 1 / review 1 / live-coding 1`)에서 3-item mix(`new 1 / deepen 1 / live-coding 1`)로 축소.
- review 슬롯은 mix 강제에서 제외하고, 점수 기반 2차 패스에서 fallback으로만 들어오게 한다.
- 면접 일자가 가까워질 때 review 비중을 다시 강제하고 싶으면 후속 ADR로 다시 키운다.

기존 ADR-010의 점수식, weak area bonus, recent-domain penalty, carry-over penalty는 모두 유지한다.

### 신규 reservoir 파일

```
config/tech-blog-sources.json   # 회사·엔지니어링 블로그 큐레이션
config/ai-topic-sources.json    # AI 주제 큐레이션
config/geek-news-sources.json   # 산업/OSS/언어 흐름 큐레이션
```

각 파일은 `_meta`(목적·정책·schema)와 `items[]`만 가진다. 별도 promotion 단계는 없다(외부 reading 추천은 study-pack처럼 생성 산출물이 따라 붙지 않기 때문).

### 보조 카테고리 선택 알고리즘

```
1. 최근 N개(=3) history entry에 등장한 key는 cooldown으로 회피
2. cooldown 통과 항목을 reservoir 순서대로 limit개까지 채움
3. 부족하면 cooldown 위반 허용해 reservoir 순서로 채움
```

reservoir 순서는 사람이 큐레이션한 우선도이므로 추가 정렬·점수 계산을 일부러 하지 않는다(백엔드 쪽과 다르게 단순한 rotation으로 의도).

### History schema 확장

`data/runtime/topic-inventory-history.jsonl`에 다음 필드를 추가한다.

```json
{
  "generatedAt": "...",
  "keys": [...],            // backend (ADR-010 호환)
  "techBlogKeys": [...],
  "aiKeys": [...],
  "geekKeys": [...],
  "todayPickKeys": { "backend": "...", "techBlog": "...", "ai": "..." }
}
```

`keys` 필드는 ADR-010 carry-over 로직과의 호환을 위해 그대로 백엔드 키로 둔다.

## Why this boundary

- 백엔드 추천은 명시적 점수/페널티가 의미 있다 → 기존 score 기반 유지.
- 기술 블로그/AI/geek은 본인이 직접 큐레이션한 reservoir 자체가 우선도 신호 → 단순 rotation으로 충분.
- 외부 reading은 자동 publishing 대상이 아니므로 promotion 흐름이 없어도 된다.

## Source separation

| 카테고리 | 자동 publish 대상? | promotion 흐름? |
|----------|-------------------|----------------|
| 백엔드 (study-pack) | O | candidate → primary auto-promote (ADR-011) |
| 기술 블로그 / AI / geek | X | 없음. reservoir 직접 편집 |

이 경계는 의도적이다. 외부 reading 추천이 사일런트로 study-pack 산출물을 만드는 일은 없게 한다.

## Consequences

### Positive

- 매일 학습 input의 폭이 백엔드 한 축에서 4축으로 늘어난다.
- "오늘의 3선"이 따로 있어 사용자 결정 비용이 낮아진다(3개만 보면 됨).
- 기술 블로그/AI/geek은 reservoir 파일만 편집하면 즉시 다음 morning 추천에 반영된다.
- 백엔드 추천도 5→3으로 줄여 핵심 항목에 집중하기 쉬워진다.

### Negative

- reservoir 파일이 stale해지지 않도록 사람이 분기마다 한 번은 살펴봐야 한다.
- live web fetch가 없어 "최신 글"은 사람이 수동으로 reservoir에 반영해야 한다(future enhancement).
- 백엔드 review 슬롯이 mix 강제에서 빠졌으므로 review 항목이 한동안 적게 노출될 수 있다.

## Future enhancements (not in this ADR)

- 기술 블로그 RSS / Atom 자동 수집 → reservoir 보충 후보 생성.
- Hacker News / GeekNews 일일 top 자동 수집.
- 기술 블로그/AI/geek에 백엔드 같은 점수 기반 가중치 도입(현재는 단순 rotation).
- 면접 D-N 시점에 따라 카테고리 슬롯 비율 자동 변경(예: D-7부터 review 강제).

## Follow-up

- reservoir 품질이 떨어지면 (1) reservoir 보강 → (2) cooldown 길이 조정 → (3) 점수화 도입 순으로 대응한다.
- ADR-010과 본 ADR이 점수/mix를 분리해서 명시하므로, 향후 mix만 갱신할 때는 본 ADR의 후속 ADR로 처리하고 ADR-010 점수식 자체는 가능하면 보존한다.
