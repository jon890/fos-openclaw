# ADR-010: Recommendation scoring and mix targets

- Status: Accepted
- Date: 2026-04-25

## Context

ADR-009로 morning topic recommendation을 prompt 기반에서 reservoir 기반으로 전환했지만, 첫 구현(`refresh_topic_inventory.py`의 `pick_recommendations`)은 다음 한계를 보였다.

1. 5개 추천이 모두 [new] 태그로 수렴 — ADR-009의 mix 목표(new/deepen/review/live-coding)가 코드 레벨에서 강제되지 않음
2. live-coding 슬롯 미보장 — `target_order` 리스트에 `'live-coding'`이 없어 1차 패스에서 절대 선택되지 않음
3. weak area(`career-os/CLAUDE.md`의 "Self-assessed weak area: DB") 가중치 없음 — DB 쪽 후보를 의식적으로 띄울 신호가 없음
4. 같은 항목이 매일 반복 추천돼도 다양성 페널티 없음

## Decision

`pick_recommendations`를 점수 기반(score-based)으로 리팩토링하고, 다음 정책을 도입한다.

### Mix target

5개 추천에 다음 비율을 강제한다.

- `new` 2개
- `deepen` 1개
- `review` 1개
- `live-coding` 1개

mix target을 모두 채우면 그 시점에 5개가 채워진다. 채울 후보가 부족한 태그가 있으면 남은 슬롯은 점수 순으로 다른 태그가 차지한다(=mix 위반은 reservoir 부족의 신호로 본다).

### Score formula

```
score = -RECENT_PENALTY_PER * recent10_domain_count(domain)
      + (WEAK_AREA_BONUS if domain in WEAK_AREAS else 0)
      + TAG_PRIORITY[tag]
      - (CARRYOVER_PENALTY if key in yesterday_keys else 0)
```

기본값:

- `RECENT_PENALTY_PER = 2` — 최근 10개 study-pack에 같은 도메인이 N건 있으면 `-2N`
- `WEAK_AREAS = {"mysql", "redis"}`, `WEAK_AREA_BONUS = 3` — `career-os/CLAUDE.md`의 weak area 명시
- `TAG_PRIORITY = {"new": 0, "deepen": -1, "review": -2, "live-coding": 0}` — mix target이 우선이지만 같은 태그 내부에서 정렬을 안정화하는 용도
- `CARRYOVER_PENALTY = 1` — 어제 추천에 있고 사용자가 아직 만들지 않은 항목은 다양성 위해 약하게 페널티

### Carry-over 추적

`data/runtime/topic-inventory-history.jsonl`에 매 실행 시 추천된 key set을 한 줄씩 append한다. 다음 실행은 직전 라인의 key set을 `yesterday_keys`로 사용한다. 첫 실행은 빈 set이라 페널티 없음.

## Consequences

### Positive

- 추천이 한 도메인/한 태그로 수렴하지 않는다. 첫 반영 결과(2026-04-25): mix [new 2 / deepen 1 / review 1 / live-coding 1] 정확 충족, 도메인도 database / architecture / mysql / live-coding로 분산.
- weak area(DB) 후보가 자동으로 가중치를 받아 deepen 슬롯에 자연스럽게 등장한다.
- 어제 추천 항목이 만들어지지 않으면 자연스럽게 다른 후보가 떠오를 가능성이 커진다.
- live-coding이 매번 1개 이상 추천된다.

### Negative

- 점수 계산이 명시적인 만큼 향후 수치 튜닝 부담이 있다. 가중치를 바꾸려면 이 ADR을 갱신하거나 후속 ADR로 대체한다.
- mix target이 강제이므로 한 태그의 후보가 계속 부족하면 fallback이 자주 일어난다. 본질적으로 reservoir 품질이 중요해진다(ADR-009의 follow-up guidance와 일치).

## Follow-up

- 추천 품질이 떨어지면 (1) 후보 reservoir 보강 → (2) 점수 가중치 조정 순으로 대응한다. prompt 튜닝은 그 다음.
- 면접 일정/단계가 크게 바뀌면 mix target을 새 ADR로 갱신한다. 예: 면접 직전엔 review 비중을 더 키우고, 다음 직장 탐색 단계에선 new 비중을 키우는 식.
- carry-over history가 너무 길어지면 별도 정책으로 잘라낸다(현재는 무한 append).
