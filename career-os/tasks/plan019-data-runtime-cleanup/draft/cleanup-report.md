# data/runtime + config Cleanup Audit Report (plan019)

본 plan019 실행 결과 history. data/runtime은 gitignore라 폐기 자체는 commit에 안 잡힘 — 본 보고서가 *기록*.

## 요약

- 총 audit 대상: data/runtime 32 파일 + config 8 파일
- **Category A (활성, 유지)**: 8 파일 (data/runtime 안)
- **Category B (stale, 폐기)**: 22 파일 (data/runtime 안)
- **Category C (위치 위반, 폐기)**: 1 파일 (augment_positions.py)
- 적용 결과: **23 파일 폐기**, 활성 8 파일 보존

## Category A — 유지 (활성, 매주 갱신되는 산출물)

| 파일 | 최근 수정 | 사용 위치 |
|---|---|---|
| `data/runtime/position-recommendation.md` | 2026-05-15 | recommend-positions 출력 |
| `data/runtime/wanted-server-postings.md` | 2026-05-15 | recommend-positions 입력 |
| `data/runtime/augmented-position-postings.md` | 2026-05-15 | position-recommender 변형 (현재 활성 형식) |
| `data/runtime/position-postings-augmented.md` | 2026-05-14 | position-recommender |
| `data/runtime/topic-inventory.json` | 2026-05-15 | study-topic-recommender 출력 (plan016 ts 진행) |
| `data/runtime/topic-inventory-history.jsonl` | 2026-05-15 | study-topic-recommender 이력 |
| `data/runtime/morning-topic-recommendation.md` | 2026-05-15 | study-topic-recommender 출력 |
| `data/runtime/cj-foodville-coffeechat-prep.md` | 2026-05-13 | cj-foodville-coffeechat-prep 출력 |

## Category B — 폐기 완료 (stale, 22 파일)

| 파일 | 최근 수정 | 폐기 근거 |
|---|---|---|
| `freeform-study-pack-topic.json` | 2026-04-24 | 한 달+ 미사용, 폐기 runner 잔재 |
| `live-coding-generated-topic.json` | 2026-05-04 | plan016 study-topic-recommender 흡수로 의미 변경 |
| `bootcamp-summary.md` | 2026-05-14 | plan014 bootcamp-batch 폐기 잔재 |
| `cj-foodville-bootcamp-summary.md` | 2026-05-13 | plan014 동일 |
| `topic-replenishment.json` | 2026-05-13 | plan015 topic-pool-replenisher 폐기 잔재 |
| `topic-replenishment.md` | 2026-05-13 | 동일 |
| `broad-plus-kakaopay-position-snapshot.md` | 2026-05-11 | 1회성 position snapshot |
| `kakaopay-focused-position-snapshot.md` | 2026-05-11 | 1회성 |
| `wanted-server-postings-300.md` | 2026-05-09 | 변형 stale |
| `wanted-server-postings-augmented.md` | 2026-05-08 | 변형 stale |
| `wanted-server-postings-compact.md` | 2026-05-08 | 변형 stale |
| `wanted-server-postings-1000-active.md` | 2026-05-13 | 변형 stale (`wanted-server-postings.md`가 활성) |
| `toss-server-postings.md` | 2026-05-09 | 변형 stale |
| `live-position-postings.md` | 2026-05-07 | 변형 stale |
| `live-position-postings-all.md` | 2026-05-11 | 변형 stale |
| `augmented-server-postings-no-toss.md` | 2026-05-11 | 변형 stale (`augmented-position-postings.md`가 활성) |
| `augmented-server-postings.md` | 2026-05-13 | 변형 stale |
| `verified-company-postings-raw.md` | 2026-05-13 | 1회성 분석 결과 |
| `verified-company-postings-with-links.md` | 2026-05-13 | 1회성 |
| `2026-05-13-position-review.md` | 2026-05-13 | 1회성 날짜 분석 |
| `2026-05-13-verified-company-position-scan.md` | 2026-05-13 | 1회성 |
| `2026-05-13-deep-active-posting-scan.md` | 2026-05-13 | 1회성 |

## Category C — 폐기 완료 (위치 위반, 1 파일)

| 파일 | 위반 사유 | 권장 처리 | 적용 결과 |
|---|---|---|---|
| `data/runtime/augment_positions.py` | data/에 Python script (ADR-015 위반) | 사용 위치 grep 결과 0건 → 폐기 | rm 완료 |

## config 자산 audit 결과

`career-os/config/` 8 파일 — *모두 활성* (Category A). 폐기 없음.

- `mvp-target.json` — 단일 출처
- `candidate-profile.md` — 사용자 hand-crafted
- `baseline-core-files.json` — interview-prep-analyzer (plan017) baseline 모드 입력
- `topic-file-map.json` — interview-prep-analyzer daily 모드 입력
- `topic-profiles.json` — study-pack-writer 입력
- `topics.json` — study-pack-writer + study-topic-recommender + interview-asset-writer (plan017에서 3 json 분리 예정)
- `live-coding-seed-pool.json` + `live-coding-seed-candidates.json` — study-topic-recommender (plan016 흡수)

## 후속

- plan020 (candidate-baseline-suggester skill — config 자산 갱신 제안): 별도 `/planning` 세션에서 계획.
- data/runtime은 gitignore라 본 폐기는 commit 영향 없음. 본 보고서가 history 단일 출처.
