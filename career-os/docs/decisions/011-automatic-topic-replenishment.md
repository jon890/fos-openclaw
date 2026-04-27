# ADR-011: Study topic replenishment should be automatic and file-backed

- Status: Accepted
- Date: 2026-04-27

## Context

ADR-009/010으로 추천 reservoir 구조는 생겼지만, 실제 study topic 재고 보충은 여전히 수동이었다.

그 결과:

1. primary curated topic의 미생성 재고가 0이 되면 사용자가 추천을 고른 뒤 실행할 때 사람이 promotion을 한 번 더 해줘야 했다.
2. candidate reservoir도 시간이 지나면 다시 고갈되므로 아침 추천 품질이 서서히 떨어진다.
3. prompt를 조금 바꾸는 것만으로는 재고 부족 문제가 해결되지 않는다.

## Decision

study topic replenishment를 daily cron으로 자동화한다.

파이프라인은 다음 순서를 따른다.

1. `config/study-topic-candidates.json` 기존 항목을 정리한다.
   - primary key/outputPath와 충돌하는 후보 제거
   - 최근 생성 주제와 과하게 유사한 후보 제거
2. candidate reservoir가 목표치보다 적으면 Claude가 새 후보를 JSON으로 생성한다.
3. 로컬 validator가 key/domain/tag/outputPath/prompt 품질을 검증한다.
4. 검증 통과한 후보만 candidate reservoir에 append한다.
5. primary curated 미생성 재고가 목표치보다 적으면 candidate 중 일부를 자동 promotion한다.
6. `refresh_topic_inventory.py`를 다시 실행해 runtime inventory를 갱신한다.

## Why this boundary

- **Claude는 제안만 한다.**
- **실제 반영은 로컬 규칙 검증 후에만 일어난다.**

즉 완전 자유 생성이 아니라, file-backed reservoir + deterministic validator + controlled promotion 구조다.

## Consequences

### Positive

- 아침 추천 전 재고가 자동으로 채워진다.
- 사용자가 추천 후보를 골랐을 때 study-pack 생성까지 이어지는 마찰이 줄어든다.
- weak area / domain balance / duplicate 방지 규칙을 코드로 유지할 수 있다.

### Negative

- Claude 출력 형식이 흔들리면 보충이 실패할 수 있다.
- 유사도 규칙은 완벽하지 않아서 가끔 보수적으로 후보를 버릴 수 있다.
- reservoir 품질을 위해서도 가끔 사람이 결과를 훑어보는 편이 좋다.

## Follow-up

- cron은 아침 추천보다 먼저 돈다.
- study-pack 실행 경로는 primary에 topic이 없을 경우 candidate auto-promotion을 한 번 시도한다.
- 품질 이슈가 생기면 prompt 튜닝보다 validator/threshold를 먼저 조정한다.
