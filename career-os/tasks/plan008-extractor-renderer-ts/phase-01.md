# Phase 1 — Extractor/Renderer 3개 + _shared/lib/extract_claude_result.ts 신설 + caller 갱신

## 목표

Claude JSON → validated markdown으로 변환하는 도메인 자산 3개와 `_shared/bin/extract_claude_result.py`(plan004 사각지대) 1개를 TS(Bun)로 마이그레이션. 자기 caller(각 skill의 runner) path를 새 TS로 갱신하고, 옛 Python을 git rm.

마이그레이션 대상:

- `scripts/study-pack-writer/extract_and_validate_study_pack.py` → `scripts/study-pack-writer/extract_and_validate_study_pack.ts`
- `scripts/experience-question-bank-writer/render_question_bank.py` → `scripts/experience-question-bank-writer/render_question_bank.ts`
- `scripts/position-recommender/extract_position_report.py` → `scripts/position-recommender/extract_position_report.ts`
- `_shared/bin/extract_claude_result.py` → `_shared/lib/extract_claude_result.ts`(신설)

## 의존성 / 가정

- plan004 + plan006 + plan007 모두 `status: completed`.
- working tree clean(main).
- Bun 설치 확인(plan004 phase-02에서 확보). 없으면 `command -v bun >/dev/null || { echo 'PHASE_BLOCKED: Bun 미설치'; exit 2; }`.

## 작업

### 1. _shared/lib/extract_claude_result.ts 신설

`_shared/bin/extract_claude_result.py`의 동작을 TS로 1:1 포팅:
- Claude `--output-format json` 출력을 stdin 또는 파일 인자로 읽음.
- `.result` 필드를 추출해 마크다운으로 저장.
- usage 인자(파일 경로 또는 env)가 있으면 raw envelope을 그 위치로 cp.

shebang `#!/usr/bin/env bun`. 호출 인터페이스(인자 순서·env 변수)는 Python 버전과 동일 유지 — caller 변경 최소화.

타입은 `_shared/types/index.ts`의 `ClaudeUsage` 등 기존 정의 재사용.

### 2. 3개 skill extractor/renderer TS 신설

각각 기존 Python의 검증 규칙·출력 포맷을 보존:

- **`extract_and_validate_study_pack.ts`**: `'#'`로 시작 / ≥80줄 / 금지 prefix / 코드 펜스 언어 명시 4가지 검증. 실패 시 비-0 exit. 검증 통과한 마크다운만 stdout으로 출력.
- **`render_question_bank.ts`**: Claude `--json-schema` 출력을 받아 5 main Q + 5 follow-up + answer points + 1분 답변 + 압박 방어 섹션을 마크다운으로 렌더.
- **`extract_position_report.ts`**: Claude JSON에서 position recommendation 본문을 추출, 후처리 후 마크다운으로.

모두 shebang `#!/usr/bin/env bun`. stdin/stdout/exit code 인터페이스는 Python 버전과 동일.

### 3. caller 갱신 (5개 runner)

dispatcher가 호출하는 runner들 안에서 `python3 .../*.py` → 새 TS path 직접 실행:

영향 받는 runner(grep으로 정확 확정 후 갱신):
- `scripts/study-pack-writer/run_study_pack.sh`
- `scripts/experience-question-bank-writer/run_question_bank.sh`
- `scripts/position-recommender/run_position_recommendation.sh`
- `scripts/interview-master-writer/run_master.sh`
- `scripts/study-pack-maintainer/run_maintainer.sh`
- `scripts/command-router/run_now.sh`(`extract_claude_result.py` 직접 호출이 있을 경우)

치환 패턴:
- `python3 "$TASK_ROOT/_shared/bin/extract_claude_result.py" ...` → `"$TASK_ROOT/_shared/lib/extract_claude_result.ts" ...`(실행 권한 + shebang)
- `python3 "$TASK_ROOT/career-os/scripts/<skill>/<name>.py" ...` → `"$TASK_ROOT/career-os/scripts/<skill>/<name>.ts" ...`

### 4. 새 TS 파일 실행 권한 부여

```bash
chmod +x _shared/lib/extract_claude_result.ts
chmod +x career-os/scripts/study-pack-writer/extract_and_validate_study_pack.ts
chmod +x career-os/scripts/experience-question-bank-writer/render_question_bank.ts
chmod +x career-os/scripts/position-recommender/extract_position_report.ts
```

### 5. 옛 Python git rm

```bash
git rm _shared/bin/extract_claude_result.py
git rm career-os/scripts/study-pack-writer/extract_and_validate_study_pack.py
git rm career-os/scripts/experience-question-bank-writer/render_question_bank.py
git rm career-os/scripts/position-recommender/extract_position_report.py
```

## 검증 명령

```bash
# 1. 새 TS 파일 존재
test -f _shared/lib/extract_claude_result.ts
test -f career-os/scripts/study-pack-writer/extract_and_validate_study_pack.ts
test -f career-os/scripts/experience-question-bank-writer/render_question_bank.ts
test -f career-os/scripts/position-recommender/extract_position_report.ts

# 2. shebang 검증
for f in _shared/lib/extract_claude_result.ts \
         career-os/scripts/study-pack-writer/extract_and_validate_study_pack.ts \
         career-os/scripts/experience-question-bank-writer/render_question_bank.ts \
         career-os/scripts/position-recommender/extract_position_report.ts; do
  head -1 "$f" | grep -q '#!/usr/bin/env bun' || { echo "PHASE_FAILED: shebang $f"; exit 1; }
  test -x "$f" || { echo "PHASE_FAILED: 실행 권한 $f"; exit 1; }
done

# 3. 옛 Python git에서 제거
[ -z "$(git ls-files _shared/bin/extract_claude_result.py)" ]
[ -z "$(git ls-files career-os/scripts/study-pack-writer/extract_and_validate_study_pack.py)" ]
[ -z "$(git ls-files career-os/scripts/experience-question-bank-writer/render_question_bank.py)" ]
[ -z "$(git ls-files career-os/scripts/position-recommender/extract_position_report.py)" ]

# 4. TS 타입 체크 (Bun)
bun tsc --noEmit _shared/lib/extract_claude_result.ts 2>&1 | grep -v 'Cannot find module' || true
# bun 자체 syntax 체크
bun --no-install build --target=bun _shared/lib/extract_claude_result.ts --outdir=/tmp/plan008-check >/dev/null 2>&1 \
  || { echo "PHASE_FAILED: extract_claude_result.ts syntax"; exit 1; }

# 5. caller 잔재 0 — Python extractor/renderer 호출 라인 없음
HITS=$(grep -rln 'extract_claude_result\.py\|extract_and_validate_study_pack\.py\|render_question_bank\.py\|extract_position_report\.py' career-os/ _shared/ \
  --include='*.sh' --include='*.ts' \
  | grep -v 'tasks/' | grep -v 'docs/')
[ -z "$HITS" ] || { echo "PHASE_FAILED: 옛 Python 호출 잔재"; echo "$HITS"; exit 1; }

# 6. caller syntax 보존
bash -n career-os/scripts/study-pack-writer/run_study_pack.sh
bash -n career-os/scripts/experience-question-bank-writer/run_question_bank.sh
bash -n career-os/scripts/position-recommender/run_position_recommendation.sh
bash -n career-os/scripts/command-router/run_now.sh
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

```
feat(career-os, _shared): extractor/renderer 3 + _shared/lib/extract_claude_result.ts TS 마이그레이션

- _shared/lib/extract_claude_result.ts 신설 (Python 잔재 정리, ADR-022)
- 3개 skill extractor/renderer를 scripts/<skill>/<name>.ts로
- shebang `#!/usr/bin/env bun` + 실행 권한
- caller 5+ runner의 python3 호출을 직접 실행으로 갱신
- 옛 Python 4개 git rm
```

## 범위 외

- Resolver 5개 마이그레이션(phase-02).
- replenish_topic_reservoir(phase-03).
- 통합 smoke / 데이터 검증(phase-04).
- code-architecture.md 디렉터리 트리 갱신은 docs commit에서 처리.
