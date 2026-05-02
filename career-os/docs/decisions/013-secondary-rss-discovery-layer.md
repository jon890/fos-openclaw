# ADR-013: tech-blog / AI / geek 추천에 RSS·Atom discovery 레이어 부착

- Status: Accepted
- Date: 2026-05-02

## Context

ADR-012로 morning 추천이 backend 3 / tech-blog 3 / AI 3 / geek 1 구조가 됐지만, 보조 카테고리(tech-blog / AI / geek)는 여전히 reservoir 항목의 "원본 카드"만 보여줬다. 그 결과 매일 같은 출력이 반복됐다.

관찰된 문제:

1. "당근 tech blog — 백엔드/event-driven 글 1편" 같이 source 단위 카드만 나와 실제로 어떤 글을 읽어야 할지 사람이 다시 검색해야 했다.
2. 링크 필드가 블로그 홈/소스 인덱스라 클릭해도 추가 탐색이 필요했다.
3. ADR-012 future enhancement에 적어 둔 "기술 블로그 RSS / Atom 자동 수집"을 더 미루면 reservoir staleness가 누적된다.

## Decision

morning 추천 파이프라인에 RSS/Atom discovery 레이어를 붙여, **feedUrl이 있는 reservoir 항목은 매일 최신 글 1편의 title + URL을 자동 부착한다**. discovery가 실패하거나 feedUrl이 없는 항목은 기존 reservoir 카드를 그대로 fallback으로 사용한다.

### 구성

- 새 모듈: `skills/cj-oliveyoung-java-backend-prep/scripts/feed_discovery.py`
  - Python stdlib(`urllib.request`, `xml.etree.ElementTree`)만 사용. 신규 의존성 금지.
  - RSS 2.0 + Atom 1.0 파서를 직접 구현.
  - 디스크 캐시: `data/runtime/feed-cache/<sha1>.json`, TTL 6시간.
  - 타임아웃 8초. 실패 시 stale cache로 fallback, 그것도 없으면 빈 리스트 반환.
  - 절대 hard fail하지 않는다 — morning 추천 파이프라인 전체를 깨면 안 된다.

- `refresh_topic_inventory.py` 변경
  - 보조 카테고리 추천이 정해진 직후 각 항목에 대해 `discover_for_item(item)` 호출.
  - 성공 시 `item['discoveredArticle'] = {title, url, published}` 부착.
  - 같은 morning 안에서 동일 URL 중복 추천 금지.
  - 최근 `RECENT_ARTICLE_URL_LOOKBACK = 7` 개 history entry의 article URL은 회피 (cooldown).
  - markdown 렌더링이 article이 있으면 article title을 1순위로 표시하고, 없으면 기존 reservoir 카드 그대로 표시.

- config 스키마 확장 (`tech-blog-sources.json`, `ai-topic-sources.json`, `geek-news-sources.json`)
  - `feedUrl` (optional): RSS/Atom 피드 URL. 있으면 discovery 시도.
  - `filterKeywords` (optional): 글 제목에 포함되면 우선하는 키워드 배열 (case-insensitive). 매칭이 없으면 전체 entries에서 fallback.
  - 기존 필드(`title`, `source`, `url`, `tags`, `whyNow`, `estMinutes`)는 그대로 유지. discovery 실패 시 fallback 카드로 사용.

- history 스키마 확장 (`data/runtime/topic-inventory-history.jsonl`)
  - 신규 필드 `articleUrls: [...]` — 그날 부착된 article URL 목록.
  - ADR-010 / ADR-012의 기존 필드(`keys`, `techBlogKeys`, `aiKeys`, `geekKeys`, `todayPickKeys`)는 변경 없음.

### Discovery 알고리즘

```
1. item.feedUrl이 없으면 skip → reservoir 카드 fallback.
2. fetch_feed_cached(feedUrl):
   - 캐시 fresh(6h 이내)면 캐시 반환.
   - 아니면 HTTP GET → parse → 디스크에 캐시 저장.
   - 네트워크/파싱 실패 시 stale cache → 그래도 없으면 [].
3. select_article(entries, filter_keywords, exclude_urls):
   - filter_keywords가 있으면 title 부분 일치(any-match)를 요구한다.
   - exclude_urls(=최근 7일 + 같은 morning에 이미 뽑힌 URL)에 들어 있는 글은 회피.
   - 키워드 매칭 글이 없으면 discovery를 포기하고 reservoir 카드로 fallback한다. broad company feed에서 관련 없는 최신 글을 붙이지 않기 위해서다.
   - filter_keywords가 없는 broad/news source는 첫 비-제외 글을 선택한다.
4. 성공 시 item.discoveredArticle 부착.
```

### 출력 형식

discovery 성공 시:
```
1. **{글 제목}**
   - 출처: {source}
   - 링크: {article URL}
   - 게시: {published timestamp}
   - 태그: ...
   - 왜 지금 보면 좋은지: ...
```

discovery 실패 시 (기존 동작):
```
1. **{reservoir title}**
   - 출처: {source}
   - 링크: {reservoir URL}
   - (피드 fetch 실패 또는 매칭 글 없음 — reservoir 카드로 표시)
   ...
```

## Why this boundary

- AI 카테고리는 대부분 doc-site/콘셉트 학습 위주라 의미있는 RSS 피드가 적다 → 일부 항목만 feedUrl을 붙이고 나머지는 reservoir 그대로 둔다.
- 한국 기업 블로그는 feed 노출이 제각각이라(예: 우아한형제들 Cloudflare 차단, Shopify/blog.atom 404) **discovery는 best-effort로 설계**한다. 한 source가 안 되어도 다른 source는 정상 작동해야 한다.
- live web fetch를 하지만 cron 5~30분 주기 재실행에서도 안전하도록 6시간 캐시를 둔다.

## Source separation

| 카테고리 | discovery 적용 가능? | feedUrl 부착 정책 |
|----------|---------------------|------------------|
| 백엔드 (study-pack) | X — 자체 score/promotion 로직 | 적용 안 함 |
| 기술 블로그 | O — 대부분 RSS 노출 | 가능한 항목 모두 |
| AI | △ — doc-site 위주, 일부만 가능 | OpenAI news 등 일부만 |
| Geek/뉴스 | O — GeekNews/HN/Postgres 등 RSS 풍부 | 가능한 항목 모두 |

## Consequences

### Positive

- "당근 tech blog — 글 1편" 같은 source-level 추천이 실제 글 title + URL이 붙은 형태로 진화한다.
- 사람이 "오늘 어떤 글 읽지" 결정에 쓰는 시간이 줄어든다.
- 같은 글이 며칠 연속으로 추천되는 일을 history-기반 cooldown으로 차단한다.
- reservoir에 feedUrl만 추가하면 점진적으로 자동화 비율을 늘릴 수 있다.

### Negative

- 첫 morning 실행이나 cache 만료 직후엔 외부 HTTP 호출이 발생한다(최대 N개 source × 8초 타임아웃). cron 폭주를 막기 위해 6시간 TTL을 둔다.
- 일부 source(예: 우아한형제들 Cloudflare 차단)는 인디케이션 없이 fallback으로 떨어질 수 있다 → discovery_log를 inventory JSON에 남겨 사람이 진단 가능하게 한다.
- malformed feed(Coupang Medium 일부)는 파싱 단계에서 실패해 fallback. 강건한 partial 파서를 도입하지 않는다(복잡도 증가 대비 효과 낮음).

## Future enhancements (not in this ADR)

- HTML scraping fallback (RSS가 없는 source용). 현재는 fallback = reservoir 카드.
- recency 점수화 — 최근 글일수록 우선하는 가중치. 지금은 feed 순서(=대부분 신선도순)에 의존.
- discovery 결과를 candidate study pack 후보로 자동 promote하는 흐름. 현재 ADR-012에서 의도적으로 분리한 정책이라 제외.
- 우아한형제들 같은 차단 source에 대해 별도 user agent / 헤더 전략. 현재는 표준 UA만 사용.

## Follow-up

- discovery_log에 `no-match`가 반복되는 source는 (1) filterKeywords 완화, (2) feedUrl 자체 점검, (3) reservoir 카드만 유지로 정리.
- feed-cache가 disk 부담이 되면 entries 본문을 자르거나 정기 cleanup 추가.
