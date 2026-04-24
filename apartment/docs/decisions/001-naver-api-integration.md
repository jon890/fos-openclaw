# ADR-001: 네이버 부동산을 쿠키+Bearer 기반 API로 통합

## 상태

Accepted

## 날짜

2026-04-24

## 배경

apartment 일일 리포트는 Naver Land 데이터를 주요 축 중 하나로 삼아 왔으나, 2026-04 기준 다음 경로는 모두 차단됐다:

- `new.land.naver.com/complexes/{id}?*` SSR 페이지: `/404` 리다이렉트
- `fin.land.naver.com/complexes/{id}`: 지도 레이어로 갔다가 약 5초 후 `financial.pstatic.net/404.html`로 강제 이탈
- SPA UI / 검색 textbox 제출 / 지도 상호작용: 모두 `/404`
- DevTools 오픈 감지까지 걸려 있어 수동 디버깅도 제약

그러나 추가 probe로 **API 채널은 조건부로 열려 있음**을 확인했다:

| 엔드포인트 | 인증 | 결과 |
|---|---|---|
| `/api/complexes/overview/{id}` | 쿠키만 | HTTP 200 (개요) |
| `/api/complexes/{id}/prices?tradeType=A1\|B1&year=5&type=summary` | 쿠키 + Bearer | HTTP 200 (한국부동산원 공식 시세) |
| `/api/articles/complex/{id}?tradeType=A1\|B1` | 쿠키 + Bearer | HTTP 200 (매물 호가 전체 리스트) |
| `/api/search?keyword=...` | (미확인) | HTTP 429 지속 |

인증 구조:

- **쿠키**: `NID_AUT`, `NID_SES` 등 로그인 세션. 수주~수개월 유효. 사용자가 브라우저 로그아웃 안 하면 유지됨.
- **Bearer**: SPA가 페이지 로드 시 내부 발급하는 JWT. payload `{"id":"REALESTATE","iat":...,"exp":...}` 기준 `exp-iat=3h`. 매 수집 실행마다 자동 재발급이 가능함.

## 결정

1. **Naver SPA 우회(헤드리스 렌더링)는 완전히 포기**한다. 단지 직링크, 검색 submit, 지도 인터랙션은 시도하지 않는다.
2. **API 3개(`overview`, `prices`, `articles`)만 정식 수집 대상**으로 삼는다. 나머지 엔드포인트(search, map, SSR 페이지)는 건드리지 않는다.
3. **쿠키는 사용자 수동 갱신**한다. 대화를 통해 Claude에 전달되면 `apartment/config/.env`의 `NAVER_COOKIE=...`로 동기화한다. 갱신 빈도는 NID_SES 만료 시(실측 약 수주~수개월).
4. **Bearer JWT는 agent-browser로 자동 추출**한다. 매 수집 실행마다 쿠키 주입된 agent-browser 세션에서 `new.land.naver.com/`을 로드해 SPA가 발급하는 토큰을 가로챈다. 실패 시 환경변수 `NAVER_BEARER`로 수동 주입 옵션을 제공한다.
5. 호출 정책: 요청 간 **2초 sleep**, 429 시 지수 백오프(2→4→8s, 3회), 실패 지속 시 마지막 성공 스냅샷으로 폴백하고 Discord 알림을 전송한다.
6. 기존 `collect_naver.py` / `collect_naver_browser.py`는 legacy로 남기되 실제 호출 경로에서는 제외한다. 완전 삭제 여부는 다음 정리 ADR에서 별도 결정한다.

## 결과

- 리포트가 공식 시세(한국부동산원) + 매물 호가 전체 + 단지 개요 3축으로 확장된다. 기존에 Hogangnono/KB로만 추정하던 59A 타입 매칭을 `pyeongs` 프로필로 정확히 할 수 있다.
- 사용자 개입 비용: 쿠키 갱신만 주 1회 이내, 기술적 지식 불요(복사/붙여넣기).
- `.env`에 `NAVER_COOKIE`가 없으면 Naver 수집은 비활성화된다. Hogangnono/KB만으로 리포트가 완성되는 기존 경로는 그대로 유지된다.
- 리스크: 네이버가 API 엔드포인트/인증 구조를 변경할 경우 수집기 수정이 필요하다. `new.land.naver.com/api/*`는 비공식 API이므로 SLA가 없다.

## 참고

- 진단 세션 기록(2026-04-24): agent-browser 다경로 probe, `curl` 쿠키+Bearer 조합 검증, JWT payload 분석(`id=REALESTATE`, `exp-iat=3h`)
- 실제 확인된 샘플 응답: overview 2.4KB(단지 기본 + `pyeongs` 프로필 + 최근 `realPrice`), prices 0.6KB(상/평균/하 + 전세가율), articles 27~29KB(매물 객체 상세)
- API 응답 스키마는 수집기 구현 시점에 JSON Schema 문서로 별도 관리 예정
