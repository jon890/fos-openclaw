---
adr: "005"
title: study pack 출력 및 발행 정책
status: 결정됨
date: 2026-04-14
---

# ADR-005: study pack 출력 및 발행 정책

## 배경

career-os는 면접 준비 자동화를 위한 작업 공간이지만, 생성되는 문서들은 단순 내부 산출물이 아니라 외부 블로그와 동기화되는 `fos-study` 저장소 문서이기도 하다.

초안 생성 이후 별도 수동 반영 단계를 두면 흐름이 느려지고, 작업 누락 가능성도 생긴다. 반면 곧바로 공개 저장소 성격의 문서 트리에 반영할 경우, 문서 상태를 명확히 표시하고 변경 이력을 추적할 규칙이 필요하다.

## 결정

다음 정책을 채택한다.

1. study pack 출력 대상은 항상 `sources/fos-study`로 한다.
2. 생성 문서는 즉시 대상 경로에 기록한다.
3. 생성 문서 제목에는 `[초안]` 표시를 붙인다.
4. 문서 생성 또는 갱신 직후, 변경 내역은 개별 commit 및 push 한다.
5. commit message는 문서 도메인과 변경 성격이 드러나도록 규칙화한다.
6. career-os 내부 `data/reports/`는 실행 로그/중간 산출물 용도로 유지하고, 최종 학습 문서는 fos-study를 기준으로 삼는다.

## commit message 규칙

기본 형식:

- `docs(<domain>): add draft <topic> study pack`
- `docs(<domain>): update draft <topic> study pack`

예시:

- `docs(mysql): add draft explain-plan study pack`
- `docs(redis): update draft cache-aside study pack`
- `docs(kafka): add draft consumer-group study pack`

## 문서 경로 규칙

주제 도메인에 따라 다음 경로 규칙을 우선 적용한다.

- MySQL / DB 성능 / 실행계획: `database/mysql/<topic>.md`
- Redis: `database/redis/<topic>.md`
- Kafka: `kafka/<topic>.md`
- Spring / JPA: `java/spring/<topic>.md`
- 일반 DB 개념: `database/<topic>.md`

필요 시 topic profile에서 명시 경로를 우선 사용한다.

## 결과

- 생성 결과가 블로그 동기화 경로와 바로 일치한다.
- 문서 발행 흐름이 단순해진다.
- 초안 상태가 제목에 명확히 드러난다.
- 문서 변경 이력이 topic 단위 commit으로 추적 가능해진다.
