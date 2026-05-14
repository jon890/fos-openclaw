# Phase 3 — replenish_topic_reservoir TS + invoke_claude_skills.ts 활용

## 목표

`scripts/topic-pool-replenisher/replenish_topic_reservoir.py`를 TS로 마이그레이션. 본 스크립트는 Claude subprocess로 후보 topic을 직접 호출하므로 `_shared/lib/invoke_claude_skills.ts`를 활용해 호출 통합. 로컬 validator(key/domain/tag/outputPath/prompt 검증) + candidate append + promotion 로직 보존.

## 의존성 / 가정

- phase-01 + phase-02 완료. extractor/renderer/resolver 모두 TS.
- working tree clean.

## 작업

### 1. replenish_topic_reservoir.ts 신설

기존 Python의 본문 로직 1:1 포팅 + Claude 호출만 invoke_claude_skills.ts로 위임:

- 입력: `config/topics.json` 현재 상태 읽기.
- `study-pack-candidates` namespace 정리(중복·최근 생성 충돌 제거).
- candidate 부족 시 Claude subprocess 호출 — `invoke_claude_skills.ts`의 export된 함수 또는 CLI 인터페이스 사용.
- Claude JSON 출력 받아 로컬 validator(key·domain·tag·outputPath·prompt 5개 키 + 형식)로 게이트.
- 통과 후보만 `config/topics.json`에 append.
- primary 재고 부족하면 일부 candidate 자동 promotion.
- `data/runtime/topic-replenishment.json`에 실행 요약 저장.
- usage 전파는 `invoke_claude_skills.ts` 내부에서 자동 처리(TRACK_TASK_CLAUDE_USAGE_FILE env).

shebang `#!/usr/bin/env bun`. Python 버전의 인자·env 변수 인터페이스 보존.

### 2. self-path 참조 갱신

기존 Python은 형제 스크립트 `refresh_topic_inventory.py`를 호출. 본 phase에서는 그대로 Python 형제 호출 유지(refresh_topic_inventory는 본 plan 범위 외).

`replenish_topic_reservoir.ts`가 `refresh_topic_inventory.py`를 부르는 라인:
- `python3 "$TASK_ROOT/career-os/scripts/study-topic-recommender/refresh_topic_inventory.py"` 형태로 유지(별도 plan에서 TS 마이그).

또 references 경로: `career-os/skills/topic-pool-replenisher/references/topic-replenishment-prompt.md` 그대로(plan006 컨벤션).

### 3. caller 갱신

`scripts/topic-pool-replenisher/run_topic_replenishment.sh` 안:
- `SCRIPT="$TASK_ROOT/career-os/scripts/topic-pool-replenisher/replenish_topic_reservoir.py"` → `replenish_topic_reservoir.ts`.
- 호출 라인 `python3 "$SCRIPT" ...` → `"$SCRIPT" ...`(shebang 직접 실행).

### 4. 실행 권한 + git rm

```bash
chmod +x career-os/scripts/topic-pool-replenisher/replenish_topic_reservoir.ts
git rm career-os/scripts/topic-pool-replenisher/replenish_topic_reservoir.py
```

## 검증 명령

```bash
# 1. 새 TS 파일 존재
test -f career-os/scripts/topic-pool-replenisher/replenish_topic_reservoir.ts
head -1 career-os/scripts/topic-pool-replenisher/replenish_topic_reservoir.ts | grep -q '#!/usr/bin/env bun'
test -x career-os/scripts/topic-pool-replenisher/replenish_topic_reservoir.ts

# 2. 옛 Python git에서 제거
[ -z "$(git ls-files career-os/scripts/topic-pool-replenisher/replenish_topic_reservoir.py)" ]

# 3. invoke_claude_skills.ts 활용 흔적
grep -q 'invoke_claude_skills' career-os/scripts/topic-pool-replenisher/replenish_topic_reservoir.ts \
  || { echo "PHASE_FAILED: invoke_claude_skills 활용 누락"; exit 1; }

# 4. caller 갱신
grep -q 'replenish_topic_reservoir\.ts' career-os/scripts/topic-pool-replenisher/run_topic_replenishment.sh
[ "$(grep -c 'replenish_topic_reservoir\.py' career-os/scripts/topic-pool-replenisher/run_topic_replenishment.sh)" = "0" ]
bash -n career-os/scripts/topic-pool-replenisher/run_topic_replenishment.sh

# 5. 본 TS syntax
bun --no-install build --target=bun career-os/scripts/topic-pool-replenisher/replenish_topic_reservoir.ts --outdir=/tmp/plan008-check >/dev/null 2>&1 \
  || { echo "PHASE_FAILED: replenish_topic_reservoir.ts syntax"; exit 1; }

# 6. references 위치 보존 (plan006 컨벤션)
grep -q 'skills/topic-pool-replenisher/references/topic-replenishment-prompt.md' career-os/scripts/topic-pool-replenisher/replenish_topic_reservoir.ts
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

```
feat(career-os): replenish_topic_reservoir TS 마이그레이션 + invoke_claude_skills.ts 활용

- replenish_topic_reservoir.py → .ts (shebang)
- Claude subprocess 호출을 _shared/lib/invoke_claude_skills.ts에 위임
- 로컬 validator(key/domain/tag/outputPath/prompt) 로직 보존
- caller(run_topic_replenishment.sh) 호출 라인 갱신
```

## 범위 외

- `refresh_topic_inventory.py` TS 마이그(별도 plan).
- 통합 smoke 실행(phase-04).
