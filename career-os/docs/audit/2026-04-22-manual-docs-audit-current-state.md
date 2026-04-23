# Docs Audit Report

## 감사 범위
- reviewed paths:
  - `sources/fos-study/database/mysql/`
  - `sources/fos-study/database/redis/`
  - `sources/fos-study/java/spring/`
  - `sources/fos-study/rabbitmq/`
- reviewed count:
  - representative hub and recently changed docs
- audit mode: structure + quality

## 요약
- keep: 8
- refresh-needed: 2
- merge: 0
- archive: 0
- delete-candidate: 0

## 전체 판단
- strongest areas:
  - mysql hub/deep-dive split
  - redis advanced pattern linking
  - spring cross-cutting concern docs
- weakest areas:
  - 일부 오래된 fundamentals 문서의 역할 선명도
- link structure quality:
  - 전반적으로 개선 중이며 폴더 허브가 생기면서 탐색성이 좋아짐
- role clarity quality:
  - 최근 문서들은 허브/심화 역할이 예전보다 분명함

## 문서별 샘플 판정

### `database/mysql/b-tree-index.md`
- status: keep
- role: hub
- reason:
  - 허브 역할이 잘 잡혀 있고 상세 문서 연결이 자연스럽다.

### `database/redis/redis-advanced-patterns.md`
- status: keep
- role: bridge / advanced hub
- reason:
  - 기존 Redis 문서군과 연결되는 구조가 생겼고, 실전 패턴 묶음 문서로 의미가 있다.

### `database/redis/basic.md`
- status: refresh-needed
- role: fundamentals
- reason:
  - 내용은 유효하지만 입문 허브인지 자료구조 기초 심화인지 역할이 조금 애매하다.

### `java/spring/filter-interceptor-aop.md`
- status: keep
- role: comparative deep-dive
- reason:
  - 요청 처리 흐름과 선택 기준을 잘 연결해준다.

### `rabbitmq/rabbitmq-basics.md`
- status: keep
- role: fundamentals
- reason:
  - 기본기 문서로 충분히 탄탄하고 실무 포인트가 있다.

## 우선 실행 추천
1. fundamentals 계열 오래된 문서는 허브형인지 심화형인지 역할을 더 선명하게 다듬기
2. 새 문서 추가 시 항상 허브 링크를 먼저 점검하기
3. 큰 정리 뒤에는 diff-validation 방식의 docs-audit를 다시 실행하기

## 보류할 것
- 최근 정리된 Redis 문서군은 지금 바로 추가 정리보다 한 템포 두고 보는 편이 좋다
