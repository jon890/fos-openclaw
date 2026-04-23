# Docs Audit Report

## 감사 범위
- reviewed paths:
  - `sources/fos-study/database/mysql/`
  - `sources/fos-study/java/spring/`
  - `sources/fos-study/rabbitmq/`
- reviewed count:
  - mysql: sampled core hub/deep-dive docs
  - spring: sampled recent cross-cutting docs
  - rabbitmq: full current set
- audit mode: structure + quality + partial diff-validation

## 요약
- keep: 6
- refresh-needed: 3
- merge: 0
- archive: 0
- delete-candidate: 0

## 전체 판단
- strongest docs:
  - `database/mysql/b-tree-index.md`
  - `java/spring/filter-interceptor-aop.md`
  - `rabbitmq/rabbitmq-vs-kafka.md`
- weakest docs:
  - `database/mysql/innodb-storage-architecture.md`
- biggest overlap areas:
  - mysql 내부에서 `innodb-storage-architecture.md`와 다른 mysql 문서들의 설명 깊이/톤 불균형
  - spring 내부에서 향후 AOP 심화 문서와 `filter-interceptor-aop.md` 사이의 링크 설계는 더 좋아질 수 있음
- link structure quality:
  - mysql는 최근 개선으로 확실히 좋아졌음
  - spring은 중간 수준, 앞으로 허브성 문서 정리가 더 있으면 좋음
  - rabbitmq는 문서 수가 적어 단순하지만 아직 허브 문서가 없음
- role clarity quality:
  - mysql는 `b-tree-index.md` 허브화로 명확해졌음
  - spring은 개별 문서 품질은 좋지만 폴더 차원의 허브 구조는 더 만들 수 있음
  - rabbitmq는 현재 문서 수가 적어 문제는 작지만, 이후 문서가 늘면 README/허브가 필요함

## 문서별 판정

### `database/mysql/b-tree-index.md`
- status: keep
- role: hub
- clarity: strong
- overlap: low after recent cleanup
- link-quality: strong
- practical-value: high
- interview-value: high
- reason:
  - 예전보다 허브 역할이 분명해졌고, 반복 설명을 줄인 대신 `composite-index.md`, `explain-plan.md`, `innodb-storage-architecture.md`로 잘 내려보낸다.
  - '인덱스를 안 타는 경우'도 한 번 훑고 상세는 링크로 넘기는 구조가 잘 잡혀 있다.
- action suggestion:
  - 현재 구조 유지
  - mysql README에서도 이 문서를 인덱스 허브로 명시하면 더 좋음

### `database/mysql/innodb-storage-architecture.md`
- status: refresh-needed
- role: engine-architecture deep-dive / possible hub
- clarity: medium
- overlap: medium
- link-quality: weak
- practical-value: medium
- interview-value: medium
- reason:
  - 내용 자체는 유용하지만 문체가 오래된 노트 느낌이고, `공부 중..` 표기가 남아 있어 현재 품질 기준과 어긋난다.
  - 최근 mysql 허브 구조가 좋아진 반면, 이 문서는 다른 관련 문서로의 링크와 역할 설명이 부족하다.
  - InnoDB 엔진 내부 허브로 쓰기엔 정리도가 부족하고, deep-dive로 보기엔 안내 문장이 약하다.
- action suggestion:
  - Claude maintainer로 재정리 추천
  - 문서 첫머리에 역할 정의 추가
  - 관련 문서(`b-tree-index`, `redo-log`, `transaction-lock`, `innodb-mvcc`) 링크 추가
  - 오래된 학습노트 톤을 현재 study-pack 수준으로 정리

### `database/mysql/composite-index.md`
- status: keep
- role: deep-dive
- clarity: strong
- overlap: acceptable
- link-quality: medium
- practical-value: high
- interview-value: high
- reason:
  - 허브에서 내려오는 심화 문서 역할이 분명하다.
  - 예시, 실수 패턴, EXPLAIN 연결까지 좋아서 학습용 가치가 높다.
- action suggestion:
  - 상단 또는 하단에 허브 복귀 링크(`b-tree-index.md`)를 한 줄 추가하면 더 좋음

### `database/mysql/explain-plan.md`
- status: keep
- role: practical diagnostic guide
- clarity: strong
- overlap: acceptable
- link-quality: medium
- practical-value: very high
- interview-value: very high
- reason:
  - 실행 계획 읽기라는 실전 축이 분명하다.
  - 인덱스 일반론과 일부 겹치지만, 현재는 허브/실전 역할이 구분되는 편이다.
- action suggestion:
  - 허브 복귀 링크를 조금 더 눈에 띄게 둘 수 있음

### `java/spring/filter-interceptor-aop.md`
- status: keep
- role: comparative deep-dive / decision guide
- clarity: strong
- overlap: low
- link-quality: medium
- practical-value: high
- interview-value: high
- reason:
  - 요청 처리 파이프라인 기준으로 Filter, Interceptor, AOP를 연결해 설명하는 점이 좋다.
  - 단순 비교가 아니라 '어디에 둬야 하는가'라는 선택 기준이 살아 있다.
- action suggestion:
  - `spring-aop-proxies-deep-dive.md`로 가는 링크를 더 명시하면 좋음
  - 나중에 spring 허브 문서에서 이 문서를 cross-cutting concern 축으로 연결 추천

### `rabbitmq/rabbitmq-basics.md`
- status: keep
- role: fundamentals
- clarity: strong
- overlap: low
- link-quality: medium
- practical-value: high
- interview-value: high
- reason:
  - RabbitMQ 입문/기본기로는 충분히 탄탄하다.
  - 실수 패턴, 설정 포인트, Spring 예시가 있어 공부 가치가 높다.
- action suggestion:
  - `rabbitmq-vs-kafka.md`로 자연스럽게 연결하는 링크를 명시하면 좋음
  - rabbitmq 문서가 늘기 전에 README/허브를 하나 두는 것이 바람직

### `rabbitmq/rabbitmq-vs-kafka.md`
- status: keep
- role: comparative decision guide
- clarity: strong
- overlap: low
- link-quality: medium
- practical-value: high
- interview-value: high
- reason:
  - 둘을 대체재로만 보지 않고 문제 유형별 선택 기준으로 정리한 점이 좋다.
  - 실전 운영과 면접 답변 프레임이 잘 들어가 있다.
- action suggestion:
  - `rabbitmq-basics.md`와 상호 링크 추가 추천

## diff validation (optional)
- changed files:
  - `database/mysql/b-tree-index.md` (commit `4757782`)
- did overlap decrease?: yes
- did links improve?: yes
- did role clarity improve?: yes
- overall result:
  - MySQL 인덱스 문서군은 최근 정리로 실제 품질이 개선됐다. 특히 허브/심화 역할 구분이 생긴 것이 가장 큰 개선점이다.

## 우선 실행 추천
1. `innodb-storage-architecture.md`를 다음 maintainer 대상으로 잡아 현재 품질 기준에 맞게 재정리
2. mysql / rabbitmq / spring 각각에 짧은 README 또는 허브 링크 구조를 더 강화
3. `docs-audit`를 실제 호출 가능한 skill로 노출/강화하고, 최근 변경 문서에 대해 주기적으로 diff-validation 수행

## 보류할 것
- 최근 생성된 rabbitmq 문서들은 지금 바로 큰 정리보다, 2~3개 문서가 더 쌓인 뒤 허브 문서를 만드는 편이 효율적
- spring 폴더 전체 구조 개편은 개별 문서가 조금 더 쌓인 뒤 진행해도 됨
