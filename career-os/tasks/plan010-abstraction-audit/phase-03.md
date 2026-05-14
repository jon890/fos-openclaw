# Phase 3 — study-pack 생성 공통 코어 → _shared/lib/study_pack_publish.ts

## 목표

study-pack-writer · study-pack-maintainer · study-pack-batch · live-coding-dispatch · fos-study-pack/run_from_request 5곳이 반복하는 공통 흐름(Claude 호출 + extractor + validator + fos-study commit/push + artifacts upsert)을 `_shared/lib/study_pack_publish.ts`로 추출. 5 runner는 thin wrapper로 축소.

## 의존성 / 가정

- phase-01 + phase-02 완료. 회사명·프롬프트 모두 config 주입.
- plan008 완료 — `_shared/lib/extract_claude_result.ts` 존재.
- working tree clean.

## 작업

### 1. `_shared/lib/study_pack_publish.ts` 신설

함수 인터페이스 (단독 실행 + 모듈 import 두 모드):

- 입력 옵션(env 또는 인자):
  - `TOPIC_KEY` — topic 식별자.
  - `OUTPUT_PATH` — fos-study 내 상대 경로.
  - `PROMPT_TEMPLATE` — `build_prompt.ts` 결과 또는 inline.
  - `VALIDATOR_KIND` — `study_pack` | `question_bank` | `master` | `none`.
  - `COMMIT_PREFIX` — ADR-005 메시지 prefix.
- 흐름:
  1. fos-study git pull (또는 clone).
  2. `invoke_claude_skills.ts` 위임 → Claude 호출.
  3. `extract_claude_result.ts` 결과 + validator 분기 (kind에 따라 `extract_and_validate_study_pack.ts` 등 호출).
  4. fos-study `<OUTPUT_PATH>` 쓰기 → commit + push.
  5. `update_artifacts.py` 호출 또는 그 동작을 TS로 내장 (data/generated-artifacts.json upsert).
- 출력: 성공 시 exit 0 + summary stdout. 실패 시 비-0 + stderr.

shebang `#!/usr/bin/env bun`. 단독 실행 + `import { studyPackPublish } from '...'` 두 모드.

### 2. 5개 runner를 thin wrapper로 축소

각 runner는 자기 도메인 특성만 남기고 공통 흐름은 `study_pack_publish.ts`에 위임:

- `study-pack-writer/run_study_pack.sh` — `VALIDATOR_KIND=study_pack` + study-pack-prompt.md.
- `study-pack-maintainer/run_maintainer.sh` — update-vs-new 판단(기존 fos-study 문서 읽기) 후 prompt에 추가 컨텍스트 주입.
- `study-pack-batch/run_bootcamp_batch.sh` — 큐에서 topic 추출 후 각 topic마다 study_pack_publish 위임.
- `study-topic-recommender/run_live_coding_dispatch.sh` — seed 선택 후 TOPIC_CONFIG_OVERRIDE 환경에서 study_pack_publish 호출.
- `fos-study-pack/run_from_request.sh` — freeform request → topic 변환 + study_pack_publish.

각 runner 목표 줄 수 ≤ 60 (현재 60-217). 도메인 특성만 명시.

### 3. 검증 분기

`study_pack_publish.ts`가 4종 validator를 동적 import:
- `extract_and_validate_study_pack.ts` (kind=study_pack)
- `render_question_bank.ts` (kind=question_bank) — question-bank는 별도 흐름이지만 fos-study commit/push는 같음, 검토 후 통합 여부 결정
- `extract_position_report.ts` (kind=position) — 별도 흐름, 본 plan에서 통합하지 않을 수 있음

question-bank / position을 본 phase에서 포함할지 결정: 본 phase는 *study-pack 계열* 5개만 우선. question-bank / position은 별도 plan으로 (작업량 통제).

## 검증 명령

```bash
# 1. _shared/lib/study_pack_publish.ts 신설
test -f _shared/lib/study_pack_publish.ts
test -x _shared/lib/study_pack_publish.ts
bun --no-install build --target=bun _shared/lib/study_pack_publish.ts --outdir=/tmp/plan010 >/dev/null 2>&1

# 2. 5 runner가 study_pack_publish.ts 호출
for runner in career-os/scripts/study-pack-writer/run_study_pack.sh \
              career-os/scripts/study-pack-maintainer/run_maintainer.sh \
              career-os/scripts/study-pack-batch/run_bootcamp_batch.sh \
              career-os/scripts/study-topic-recommender/run_live_coding_dispatch.sh \
              career-os/scripts/fos-study-pack/run_from_request.sh; do
  grep -q 'study_pack_publish' "$runner" \
    || { echo "PHASE_FAILED: $runner study_pack_publish 미호출"; exit 1; }
done

# 3. 5 runner 줄 수 ≤ 60 (thin wrapper 검증)
for runner in career-os/scripts/study-pack-writer/run_study_pack.sh \
              career-os/scripts/study-pack-maintainer/run_maintainer.sh \
              career-os/scripts/study-pack-batch/run_bootcamp_batch.sh \
              career-os/scripts/study-topic-recommender/run_live_coding_dispatch.sh \
              career-os/scripts/fos-study-pack/run_from_request.sh; do
  L=$(wc -l < "$runner")
  [ "$L" -le 60 ] || { echo "PHASE_FAILED: $runner $L lines > 60 (thin wrapper 위반)"; exit 1; }
done

# 4. syntax
for runner in career-os/scripts/study-pack-writer/run_study_pack.sh \
              career-os/scripts/study-pack-maintainer/run_maintainer.sh \
              career-os/scripts/study-pack-batch/run_bootcamp_batch.sh \
              career-os/scripts/study-topic-recommender/run_live_coding_dispatch.sh \
              career-os/scripts/fos-study-pack/run_from_request.sh; do
  bash -n "$runner"
done
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

```
feat(_shared, career-os): study-pack 생성 공통 코어 추출 → _shared/lib/study_pack_publish.ts

- 5 runner의 fos-study commit/push 흐름 단일화
- 각 runner는 thin wrapper로 축소 (목표 ≤60 lines)
- VALIDATOR_KIND 분기로 study_pack / question_bank / master 다형성
- artifacts upsert 흐름 통합
```

## 범위 외

- question-bank / position 흐름 통합 (별도 plan).
- fos-study git ops 자체 추상화 (phase-04, study_pack_publish 안에서 호출).
- runner 안 dispatcher case 변경 (run_now.sh는 phase-01에서 이미 처리).
