# Phase 2 — Resolver 5개 TS 신설 + dispatcher case 갱신

## 목표

config(`topics.json`) → env exports(`export KEY=value\nexport KEY2=value2\n`)를 출력하는 resolver 5개를 TS(Bun)로 마이그레이션. dispatcher가 `eval $(python3 .../resolve_*.py ...)`로 받는 인터페이스 보존.

마이그레이션 대상:
- `scripts/study-pack-writer/resolve_study_pack_topic.py` → `.ts`
- `scripts/experience-question-bank-writer/resolve_question_bank_topic.py` → `.ts`
- `scripts/interview-master-writer/resolve_master_topic.py` → `.ts`
- `scripts/study-pack-maintainer/resolve_maintainer_topic.py` → `.ts`
- `scripts/fos-study-pack/resolve_freeform_study_pack.py` → `.ts`

## 의존성 / 가정

- phase-01 완료. extractor/renderer 3 + extract_claude_result.ts 마이그 완료.
- working tree clean.

## 작업

### 1. Resolver 5개 TS 신설

각 resolver는 동일 패턴:
- 인자: `<topic-config.json>` + `<topic-key>` (현재 인터페이스 보존).
- config에서 해당 namespace의 topic 엔트리 조회.
- 필요한 키들을 `export KEY=value` 라인으로 stdout 출력.
- topic 미존재 시 비-0 exit + stderr 에러 메시지.

shebang `#!/usr/bin/env bun`. 값에 쉘 메타문자가 들어갈 수 있으면 적절히 quote(`export KEY="value"` 형식).

각 resolver의 namespace + 출력 키:
- `resolve_study_pack_topic.ts` — `study-pack` namespace, 옛 Python의 출력 변수 그대로.
- `resolve_question_bank_topic.ts` — `question-bank` namespace.
- `resolve_master_topic.ts` — `master` namespace.
- `resolve_maintainer_topic.ts` — `study-pack-maintainer` namespace.
- `resolve_freeform_study_pack.ts` — `data/runtime/freeform-study-pack-topic.json` 임시 config 처리.

정확한 출력 키는 기존 Python 본문에서 확인 후 1:1 포팅.

### 2. 실행 권한 + git rm

```bash
chmod +x career-os/scripts/study-pack-writer/resolve_study_pack_topic.ts
chmod +x career-os/scripts/experience-question-bank-writer/resolve_question_bank_topic.ts
chmod +x career-os/scripts/interview-master-writer/resolve_master_topic.ts
chmod +x career-os/scripts/study-pack-maintainer/resolve_maintainer_topic.ts
chmod +x career-os/scripts/fos-study-pack/resolve_freeform_study_pack.ts

git rm career-os/scripts/study-pack-writer/resolve_study_pack_topic.py
git rm career-os/scripts/experience-question-bank-writer/resolve_question_bank_topic.py
git rm career-os/scripts/interview-master-writer/resolve_master_topic.py
git rm career-os/scripts/study-pack-maintainer/resolve_maintainer_topic.py
git rm career-os/scripts/fos-study-pack/resolve_freeform_study_pack.py
```

### 3. dispatcher case 갱신

`scripts/command-router/run_now.sh` 안의 5개 case 갱신:

- `study-pack)` 안의 `RESOLVER="..."resolve_study_pack_topic.py"` + `eval "$(python3 "$RESOLVER" ...)"` → `RESOLVER="..."resolve_study_pack_topic.ts"` + `eval "$("$RESOLVER" ...)"`.
- `question-bank)`, `master)`, `maintain-study-pack)`, freeform 경로 동일.

또 `study-pack)` case 안의 maintainer 분기도 동일 갱신.

## 검증 명령

```bash
# 1. 새 TS 파일 존재
test -f career-os/scripts/study-pack-writer/resolve_study_pack_topic.ts
test -f career-os/scripts/experience-question-bank-writer/resolve_question_bank_topic.ts
test -f career-os/scripts/interview-master-writer/resolve_master_topic.ts
test -f career-os/scripts/study-pack-maintainer/resolve_maintainer_topic.ts
test -f career-os/scripts/fos-study-pack/resolve_freeform_study_pack.ts

# 2. shebang + 실행 권한
for f in career-os/scripts/study-pack-writer/resolve_study_pack_topic.ts \
         career-os/scripts/experience-question-bank-writer/resolve_question_bank_topic.ts \
         career-os/scripts/interview-master-writer/resolve_master_topic.ts \
         career-os/scripts/study-pack-maintainer/resolve_maintainer_topic.ts \
         career-os/scripts/fos-study-pack/resolve_freeform_study_pack.ts; do
  head -1 "$f" | grep -q '#!/usr/bin/env bun' || { echo "PHASE_FAILED: shebang $f"; exit 1; }
  test -x "$f" || { echo "PHASE_FAILED: 실행 권한 $f"; exit 1; }
done

# 3. 옛 Python git에서 제거
for skill in study-pack-writer experience-question-bank-writer interview-master-writer study-pack-maintainer fos-study-pack; do
  [ -z "$(git ls-files career-os/scripts/$skill/resolve_*.py)" ] || { echo "PHASE_FAILED: $skill 옛 resolver 잔재"; exit 1; }
done

# 4. dispatcher 갱신
[ "$(grep -c 'resolve_.*\.py' career-os/scripts/command-router/run_now.sh)" = "0" ]
grep -q 'resolve_study_pack_topic.ts' career-os/scripts/command-router/run_now.sh
grep -q 'resolve_question_bank_topic.ts' career-os/scripts/command-router/run_now.sh
grep -q 'resolve_master_topic.ts' career-os/scripts/command-router/run_now.sh
grep -q 'resolve_maintainer_topic.ts' career-os/scripts/command-router/run_now.sh
bash -n career-os/scripts/command-router/run_now.sh

# 5. 1개 resolver의 stdout 형식 검증 (sample topic으로)
SAMPLE=$(career-os/scripts/study-pack-writer/resolve_study_pack_topic.ts career-os/config/topics.json $(python3 -c 'import json; cfg=json.load(open("career-os/config/topics.json")); print(list(cfg.get("study-pack",{}).keys())[0])') 2>/dev/null)
echo "$SAMPLE" | grep -q '^export ' || { echo "PHASE_FAILED: resolver stdout 형식"; exit 1; }
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

```
feat(career-os): resolver 5개 TS 마이그레이션 + dispatcher case 갱신

- 5 skill의 resolve_*_topic.py → .ts (shebang, 실행 권한)
- dispatcher case 안 eval(python3 ...) → eval(.ts 직접 실행)
- 출력 인터페이스(export KEY=value) 보존
```

## 범위 외

- replenish_topic_reservoir(phase-03).
- 실제 dispatch 호출 검증(phase-04).
