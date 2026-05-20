# flow — travel

travel 워크스페이스의 **데이터 흐름 단일 출처**.
자동화가 없으므로 *사용자 대화 흐름* 중심으로 기술한다.

다른 워크스페이스(apartment / career-os / stock-investment / health-care)는 cron / runner / Claude CLI 호출 흐름이 핵심이다.
travel은 그와 달리 *사용자가 직접 대화하며 문서를 만드는* 흐름만 존재한다.
cron 없음. runner 없음. 자동 트리거 없음.

## 1. trip 생성 흐름

```
사용자 대화
  → trip 목적지·기간 결정
  → trip-id 결정 (<도시-slug>-<YYYY-MM>)
  → trips/<trip-id>/ 디렉터리 생성
    → docs/ + data/ + memory/ + output/ 초기화
  → docs/index.md에 trip 추가
```

초기화 시 생성하는 파일:
- `docs/trip-overview.md` (빈 템플릿)
- `docs/itinerary.md` (빈 템플릿)
- `docs/decision-log.md` (빈 파일)

## 2. 예약·고정 정보 수집 흐름

```
사용자 입력 (항공 / 숙소 / 교통 / 보험 정보)
  → Claude 보조 정리
  → trips/<trip-id>/docs/trip-overview.md 갱신
  → 예약 파일 → trips/<trip-id>/data/ 저장
```

trip-overview.md 내용 예시:
- 항공편 편명·시각·좌석
- 숙소 이름·주소·체크인/아웃 시각
- 교통 패스 종류·유효기간
- 여행자 보험 증권번호·긴급연락처

## 3. 일정 작성 흐름

```
사용자 입력 (방문지 / 식당 / 활동 계획)
  + 웹 검색 또는 사용자 조사 결과 참고
  → Claude 보조 Day별 정리
  → trips/<trip-id>/docs/itinerary.md 갱신
```

itinerary.md 구조 예시:
- Day 1 — 도착·체크인·저녁
- Day 2 — 주요 관광지·식사
- Day N — 체크아웃·귀국

이동 시간·예약 필요 여부·대기 시간 등을 함께 기록한다.

## 4. 결정 기록 흐름

```
결정 발생 시점
  → 결정 내용 한 줄 또는 단락
  → trips/<trip-id>/docs/decision-log.md append
```

decision-log.md는 누적 전용.
삭제·수정보다 *새 라인 append* 원칙.

기록 예시:
- `2026-05-01 — 숙소 A 최종 확정 (가격·위치 우선)`
- `2026-05-03 — Day 2 일정에 B 식당 추가 (예약 완료)`

## 5. trip별 특화 문서 흐름

```
trip 특성에 따라 추가 문서 필요 발생
  → 사용자·Claude 논의
  → trips/<trip-id>/docs/<특화문서>.md 신설
```

예시:
- 음식·쇼핑 목록 → `food-shopping-prep.md`
- 짐 목록 → `packing-list.md`
- 예산 계획 → `budget.md`

특화 문서는 trip 개성에 맞게 자유롭게 추가.
워크스페이스 레벨 스키마 변경 없음.

## 6. 출발 전 정리 흐름

```
출발 D-N일
  → itinerary.md + trip-overview.md 검토
  → Claude 보조 — Day별 체크리스트 생성
  → trips/<trip-id>/output/체크리스트.md 저장
```

출발 전 산출물 예시:
- Day별 이동 요약 (출발지·도착지·교통수단·시각)
- 예약 확인 체크리스트
- 필수 지참 목록

## 7. trip 종료 흐름

```
귀국 후
  → docs/index.md 상태 → 완료로 갱신
  → (선택) 기억·감상 → trips/<trip-id>/memory/에 기록
```

trip-instance 내부 파일은 삭제하지 않는다.
아카이브 목적으로 영구 보존.

## 8. 흐름 요약

| 단계 | 입력 | Claude 역할 | 산출물 |
|---|---|---|---|
| trip 생성 | 목적지·기간 | 디렉터리 생성 보조 | `trips/<trip-id>/` 구조 |
| 정보 수집 | 예약·고정 정보 | 정리·포맷 | `trip-overview.md` |
| 일정 작성 | 방문지·활동 계획 | Day별 정리 | `itinerary.md` |
| 결정 기록 | 결정 내용 | append 보조 | `decision-log.md` |
| 출발 전 | itinerary 검토 | 체크리스트 생성 | `output/` |
| trip 종료 | 귀국 확인 | 인덱스 갱신 보조 | `docs/index.md` |

모든 단계에서 사용자가 주도하고 Claude는 보조 역할만 한다.
