# Phase 6 — 통합 smoke + 잔재 grep + push + trailing cleanup

## 목표

phase-01~05 모두 통과 후 추상화·config 의존 강화의 통합 검증. 회사·직무 잔재 0 + 새 _shared/lib/ 자산 동작 + dispatcher smoke. trailing 변경 정리 후 push.

## 의존성 / 가정

- phase-01~05 모두 `completed`.
- working tree clean.

## 작업

### 1. 회사·직무 하드코딩 통합 grep

```bash
HITS=$(grep -rln 'CJ푸드빌\|푸드빌\|foodville\|kakao\|카카오\|oliveyoung' career-os/scripts career-os/skills _shared 2>/dev/null \
  | grep -v __pycache__ | grep -v 'docs-audit' | grep -v 'archive/' \
  | grep -v 'cj-foodville-coffeechat-prep/$')  # skill 폴더명 자체는 별도 plan
if [ -n "$HITS" ]; then
  echo "PHASE_FAILED: 회사·직무 잔재"
  echo "$HITS"
  exit 1
fi
```

### 2. 새 _shared/lib/ 자산 syntax 통합 통과

```bash
for f in _shared/lib/build_prompt.ts _shared/lib/study_pack_publish.ts _shared/lib/fos_study_git.ts; do
  test -f "$f" || { echo "PHASE_FAILED: $f 없음"; exit 1; }
  test -x "$f" || { echo "PHASE_FAILED: $f 실행 권한"; exit 1; }
  head -1 "$f" | grep -q '#!/usr/bin/env bun' || { echo "PHASE_FAILED: $f shebang"; exit 1; }
  bun --no-install build --target=bun "$f" --outdir=/tmp/plan010 >/dev/null 2>&1 \
    || { echo "PHASE_FAILED: $f bun syntax"; exit 1; }
done
```

### 3. dispatcher smoke

```bash
bash career-os/scripts/command-router/run_now.sh smoke
```

smoke case는 knowledge-gap-analyzer를 호출. 본 plan에서 변경된 path·프롬프트 동작 점검.

### 4. push + trailing cleanup

```bash
git add career-os/ _shared/
git commit -m "chore(career-os, _shared): plan010 통합 smoke 통과 + 회사·직무 잔재 정리"
git push origin main

if [ -n "$(git status --porcelain career-os/tasks/plan010-abstraction-audit/index.json)" ]; then
  git add career-os/tasks/plan010-abstraction-audit/index.json
  git commit -m "chore(career-os): plan010 index.json commitSha 후기록"
  git push origin main
fi
```

## 검증 명령 (요약)

```bash
[ -z "$(grep -rln 'CJ푸드빌\|푸드빌\|foodville\|kakao\|카카오' career-os/scripts career-os/skills _shared --include='*.sh' --include='*.ts' --include='*.py' --include='*.md' 2>/dev/null | grep -v 'docs-audit\|archive/' )" ]
test -f _shared/lib/build_prompt.ts
test -f _shared/lib/study_pack_publish.ts
test -f _shared/lib/fos_study_git.ts
bash -n career-os/scripts/command-router/run_now.sh
git log -1 --pretty=%s | grep -q 'plan010.*통합 smoke\|plan010 index.json commitSha'
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

phase-06은 두 커밋(2번째 옵션):
1. `chore(career-os, _shared): plan010 통합 smoke 통과 + 회사·직무 잔재 정리`
2. `chore(career-os): plan010 index.json commitSha 후기록`

## 범위 외

- `cj-foodville-coffeechat-prep` skill 폴더 이름 변경 (별도 plan — 면접 종료 후 안전).
- question-bank / position 흐름의 study_pack_publish 통합 (별도 plan).
