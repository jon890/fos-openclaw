# Phase 4 — 통합 smoke + Python 잔재 grep + push + trailing cleanup

## 목표

phase-01~03 통과 후 9개 도메인 헬퍼 + 1개 _shared 자산이 TS로 모두 이전됐는지 확인. 워크스페이스 전역에 본 plan 범위 Python 호출 잔재 0. dispatcher smoke 1회 실행으로 실제 동작 검증. trailing working tree 변경 정리 후 push.

## 의존성 / 가정

- phase-01~03 모두 `status: completed`.
- working tree clean(이전 phase 후기록 cleanup 완료).
- Bun 설치 확인됨.

## 작업

### 1. 본 plan 범위 Python 잔재 0 확인

```bash
# 9개 옛 Python 파일이 모두 git에서 제거됐는지
for f in \
  _shared/bin/extract_claude_result.py \
  career-os/scripts/study-pack-writer/extract_and_validate_study_pack.py \
  career-os/scripts/experience-question-bank-writer/render_question_bank.py \
  career-os/scripts/position-recommender/extract_position_report.py \
  career-os/scripts/study-pack-writer/resolve_study_pack_topic.py \
  career-os/scripts/experience-question-bank-writer/resolve_question_bank_topic.py \
  career-os/scripts/interview-master-writer/resolve_master_topic.py \
  career-os/scripts/study-pack-maintainer/resolve_maintainer_topic.py \
  career-os/scripts/fos-study-pack/resolve_freeform_study_pack.py \
  career-os/scripts/topic-pool-replenisher/replenish_topic_reservoir.py; do
  if [ -n "$(git ls-files "$f")" ]; then
    echo "PHASE_FAILED: $f git에 잔재"; exit 1
  fi
done

# 코드(sh / ts)에 옛 .py 호출 잔재 0
HITS=$(grep -rln 'extract_claude_result\.py\|extract_and_validate_study_pack\.py\|render_question_bank\.py\|extract_position_report\.py\|resolve_study_pack_topic\.py\|resolve_question_bank_topic\.py\|resolve_master_topic\.py\|resolve_maintainer_topic\.py\|resolve_freeform_study_pack\.py\|replenish_topic_reservoir\.py' career-os/ _shared/ \
  --include='*.sh' --include='*.ts' --include='*.py' \
  | grep -v 'tasks/' | grep -v 'docs/')
if [ -n "$HITS" ]; then
  echo "PHASE_FAILED: 본 plan 범위 Python 호출 잔재"
  echo "$HITS"
  exit 1
fi
```

### 2. 새 TS 자산 통합 syntax 통과

```bash
# 9개 + 1개 새 TS 모두 syntax check
for f in \
  _shared/lib/extract_claude_result.ts \
  career-os/scripts/study-pack-writer/extract_and_validate_study_pack.ts \
  career-os/scripts/experience-question-bank-writer/render_question_bank.ts \
  career-os/scripts/position-recommender/extract_position_report.ts \
  career-os/scripts/study-pack-writer/resolve_study_pack_topic.ts \
  career-os/scripts/experience-question-bank-writer/resolve_question_bank_topic.ts \
  career-os/scripts/interview-master-writer/resolve_master_topic.ts \
  career-os/scripts/study-pack-maintainer/resolve_maintainer_topic.ts \
  career-os/scripts/fos-study-pack/resolve_freeform_study_pack.ts \
  career-os/scripts/topic-pool-replenisher/replenish_topic_reservoir.ts; do
  test -f "$f" || { echo "PHASE_FAILED: $f 없음"; exit 1; }
  test -x "$f" || { echo "PHASE_FAILED: $f 실행 권한"; exit 1; }
  head -1 "$f" | grep -q '#!/usr/bin/env bun' || { echo "PHASE_FAILED: $f shebang"; exit 1; }
  bun --no-install build --target=bun "$f" --outdir=/tmp/plan008-check >/dev/null 2>&1 \
    || { echo "PHASE_FAILED: $f bun syntax"; exit 1; }
done
```

### 3. dispatcher 14 case 모두 syntax + path 일관성

```bash
bash -n career-os/scripts/command-router/run_now.sh

# dispatcher에 본 plan 범위 옛 Python 호출 없음
[ "$(grep -cE 'extract_claude_result\.py|extract_and_validate_study_pack\.py|render_question_bank\.py|extract_position_report\.py|resolve_.*_topic\.py|resolve_freeform_study_pack\.py|replenish_topic_reservoir\.py' career-os/scripts/command-router/run_now.sh)" = "0" ]
```

### 4. dispatcher smoke 1회 실행

```bash
bash career-os/scripts/command-router/run_now.sh smoke
```

`smoke` case는 knowledge-gap-analyzer를 호출하며 본 plan 범위 자산을 직접 안 건드리지만, dispatcher path 일관성·shebang 동작이 깨지지 않았는지 확인.

### 5. push + trailing cleanup

```bash
git add career-os/ _shared/
git commit -m "chore(career-os, _shared): ADR-022 통합 smoke + Python 9개 정리 완료"
git push origin main

# run-phases.py가 phase-04 SHA를 index.json에 후기록한 뒤
if [ -n "$(git status --porcelain career-os/tasks/plan008-extractor-renderer-ts/index.json)" ]; then
  git add career-os/tasks/plan008-extractor-renderer-ts/index.json
  git commit -m "chore(career-os): plan008 index.json commitSha 후기록"
  git push origin main
fi
```

## 검증 명령 (요약)

```bash
# 9개 옛 Python 모두 git에서 제거
test -z "$(git ls-files _shared/bin/extract_claude_result.py career-os/scripts/*/extract_*.py career-os/scripts/*/render_*.py career-os/scripts/*/resolve_*.py career-os/scripts/*/replenish_*.py 2>/dev/null)"
# 새 TS 자산 모두 존재 + shebang
[ "$(find _shared/lib career-os/scripts -maxdepth 3 -name 'extract_*.ts' -o -name 'render_*.ts' -o -name 'resolve_*.ts' -o -name 'replenish_*.ts' 2>/dev/null | wc -l)" -ge 10 ]
bash -n career-os/scripts/command-router/run_now.sh
git log -1 --pretty=%s | grep -q 'ADR-022 통합 smoke\|plan008 index.json commitSha'
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

phase-04 자체는 두 커밋(2번째는 옵션):
1. `chore(career-os, _shared): ADR-022 통합 smoke + Python 9개 정리 완료`
2. `chore(career-os): plan008 index.json commitSha 후기록`(run-phases.py 후기록 trailing 변경 시).

## 범위 외

- 본 plan에서 다루지 않은 8개 Python(`collect_*.py`, `build_target_file_list.py`, `select_topic.py`, `update_study_progress.py`, `feed_discovery.py`, `refresh_topic_inventory.py`, `promote_candidate_topics.py`) — 별도 plan.
- `_shared/bin/update_artifacts.py` — 별도 plan(Python 잔재 정리 시 검토).
