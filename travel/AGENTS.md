# AGENTS.md - travel workspace

이 작업공간은 여러 여행 계획과 의사결정을 여행별 폴더로 분리해 관리한다.

## 구조
- `trips/<trip-id>/docs/` : 일정, 결정 로그, 개요
- `trips/<trip-id>/memory/` : 여행별 대화/변경 기록
- `trips/<trip-id>/data/` : 예약 관련 산출물이나 보조 데이터

## 운영 원칙
- 여행마다 별도 폴더를 만든다.
- 공통 인덱스는 루트에 두고, 실제 내용은 각 여행 폴더에 쌓는다.
- 결정이 필요한 내용은 각 여행의 `docs/decision-log.md`에 남긴다.
- 날짜별 일정은 각 여행의 `docs/itinerary.md`에서 관리한다.
- 예약/고정 정보는 각 여행의 `docs/trip-overview.md`에 정리한다.
