---
adr: "006"
title: study-pack 엔트리포인트와 topic 라우팅 전략
status: 결정됨
date: 2026-04-14
---

# ADR-006: study-pack 엔트리포인트와 topic 라우팅 전략

## 배경

study pack 생성은 daily report와 목적이 다르다.

- daily report: 오늘 무엇을 공부할지 요약하고 학습 포인트를 제안
- study pack: 특정 주제에 대한 블로그형 완성 문서를 생성하고 fos-study에 바로 발행

이 둘을 같은 엔트리포인트에 섞으면 사용자 의도가 흐려진다. 또한 topic 수가 늘어나면 domain, 출력 경로, 주제별 프롬프트 강조점을 반복해서 수동 입력해야 한다.

## 결정

다음 구조를 사용한다.

1. 별도 엔트리포인트를 추가한다.
   - `run_now.sh study-pack <topic>`
2. study-pack topic 메타데이터는 `config/study-pack-topics.json`에 둔다.
3. topic key에서 다음 정보를 해석한다.
   - domain
   - fos-study 출력 경로
   - topic-specific prompt append
4. topic이 명확하면 바로 실행한다.
5. topic이 애매하면 실행 전에 사용자 확인을 받는다.
6. 현 단계에서는 복잡한 별도 라우터 서비스 대신, 얇은 resolver 스크립트로 충분하다고 본다.

## 결과

- 사용자는 `study-pack`과 `daily`를 구분해서 요청할 수 있다.
- 주제별 경로 규칙과 프롬프트 강조점이 구조화된다.
- 향후 topic 확장 시 config만 늘리면 된다.
- 애매한 주제에 대해서만 추가 질의를 하므로 흐름이 가볍다.
