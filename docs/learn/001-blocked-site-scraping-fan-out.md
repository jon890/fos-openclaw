# LEARN-001: 차단된 사이트 진단 시 우회 옵션 fan-out

## 날짜

2026-04-25

## 상황

2026-04-24~25 `apartment` 워크스페이스에서 Naver Land 부동산 데이터 수집을 강화하려고 시도했다. 출발점에서 Naver SPA 페이지 직접 접근(`new.land.naver.com/complexes/1649?...`)부터 `/404` 리다이렉트로 차단되었고, DevTools 오픈 감지까지 걸려 있어 일반 디버깅도 제약된 상태였다. 1.5시간 이상을 다양한 헤드리스 브라우저 우회 시도(agent-browser snapshot, autocomplete, --headed 등)에 투자했지만, 결국 사용자가 본인 브라우저의 Network 탭을 직접 열어 `/api/complexes/...` 호출 + `Authorization: Bearer ...` 헤더 + 쿠키 조합을 보여준 뒤에야 정답에 도달했다.

## 무엇을 잘못했는가 (시간 손실 지점)

- 첫 두 번째 `/404` 신호에서 **SPA 헤드리스 우회를 단일 가설로 깊게 팠다.** UA 변경, sandbox 비활성, autocomplete 시도 등에 시간을 흘렸지만 본질은 SPA 라우팅이 아니라 인증 헤더의 부재였다.
- `m.land.naver.com`, `fin.land.naver.com`, `/api/*` 같은 **우회 후보 도메인/엔드포인트를 한 번에 fan-out 점검하지 않았다.** 순차적으로 하나씩 검증하느라 누적 시간이 컸다.
- "naver land scraping", "네이버 부동산 API", "naver real estate reverse engineering" 같은 **알려진 사례 웹검색을 시작 시점에 한 번도 돌리지 않았다.** 외부에 공개된 우회 패턴이 있을 가능성을 처음부터 무시했다.
- 결국 정답("쿠키+Bearer로 `/api/complexes/...` 직접 호출")은 사용자 개입 후에 발견되었다. 같은 결론에 더 빨리 도달할 수 있었다.

## 학습 / 패턴

외부 사이트의 첫 차단 신호(`/404` 리다이렉트, HTTP 429, DevTools 감지, JS challenge, Cloudflare interstitial 등)를 마주하면, 단일 가설을 깊게 파기 전에 다음을 먼저 한다.

1. **도메인/엔드포인트 fan-out**: (a) 모바일 도메인(`m.*`), (b) 레거시/리뉴얼 도메인(`fin.*` / `old.*` / `legacy.*`), (c) 공식·비공식 API 추정 경로(`/api/...`, `/v1/...`, `/internal/...`), (d) JSON-LD / og:meta / RSS 같은 부수 채널, (e) 통합검색 결과 카드의 외부 링크를 동시에 probe한다. 한 메시지에서 여러 `curl` 또는 `agent-browser open`을 병렬로 던진다.
2. **알려진 사례 검색**: `<service> 크롤링`, `<service> scraping`, `<service> mobile app api`, `<service> reverse engineering` 같은 키워드로 web-search 또는 GitHub 검색을 5분 이내에 한 번 실행해, 공개된 우회 패턴(쿠키 헤더 조합, Bearer 토큰 발급 경로, 비공식 SDK)을 먼저 확인한다.
3. **가설 트리 명시화**: 현재 차단 신호별로 가능 원인(JS challenge / IP rate limit / cookie auth / referer 검사 / 헤더 시그니처 / 캡차 / fingerprinting)을 짧게 트리로 적고, 가장 저비용 가설부터 차례로 검증한다.
4. **30분 룰**: 단일 가설을 30분 이상 파기 전에 사용자에게 후보 리스트를 보고하고 우선순위를 받는다. 사용자가 직접 네트워크 탭을 보거나 도메인 지식을 줄 수 있다.

## 향후 적용

- **트리거**: 외부 사이트의 첫 차단 신호(`/404` 리다이렉트, HTTP 429, DevTools 감지, JS challenge, anti-fingerprint, CAPTCHA 등).
- **행동 순서**:
  1. fan-out probe(병렬 `curl` 또는 `agent-browser open`)를 즉시 실행
  2. 5분 web-search로 알려진 사례 1회 확인
  3. 후보 리스트 + 가설 트리 정리 → 사용자에게 우선순위 제안
  4. 사용자 결정 이후에 깊은 파기를 시작한다

## 후속 검증 (이번 세션 내, 2026-04-25)

이 회고를 정리한 직후 별도로 진행한 PoC에서, **agent-browser의 HAR 캡처(`network har start/stop`)로 Naver SPA가 자동 발급받는 Bearer JWT 토큰을 자동 추출 가능**함을 확인했다.

- 페이지가 `/404`로 redirect돼도 SPA 백그라운드 JS는 그대로 동작하며, 첫 `/api/...` 호출에 `Authorization: Bearer eyJ...`를 자동 inject한다.
- HAR(HTTP Archive) 파일에 모든 요청 헤더가 그대로 캡처되어 표준 JSON 파싱으로 토큰을 뽑을 수 있다.
- JWT payload 패턴 `{"id":"REALESTATE","iat":...,"exp":iat+10800}` 검증 — 3시간 수명이지만 매 수집 실행마다 신규 발급 가능하므로 사용자가 토큰을 수동으로 줄 필요가 없다.

이를 활용하면 ADR-001의 후속 항목인 "JWT 자동 추출"을 `collect_naver_api.py`에 통합할 수 있다(별도 구현 커밋 예정).

## 참고

- ADR-001: `apartment/docs/decisions/001-naver-api-integration.md`
- 관련 커밋(시간순): `2806b30` ADR-001, `edb5a05` .env 인프라, `02e5f74` 수집기 코드 보완, `16c5641` WORKFLOW priorities 갱신
- 메모리: `~/.claude/projects/-home-bifos-ai-nodes/memory/feedback_diagnosing_blocked_site_scraping.md` (Claude Code 세션 시작 시 자동 recall)
