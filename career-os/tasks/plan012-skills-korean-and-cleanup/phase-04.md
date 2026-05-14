# Phase 4 — 통합 smoke + 잔재 grep + push + trailing cleanup

## 목표

phase-01~03 통과 후 fos-study-pack 잔재 0 + 11→10 skill 구조 확인 + dispatcher 동작 보존 + trailing 변경 정리 후 push.

## 의존성 / 가정

- phase-01~03 모두 `completed`.
- working tree clean.

## 작업

### 1. fos-study-pack 코드 잔재 통합 grep

```bash
HITS=$(grep -rln 'fos-study-pack' career-os/ _shared/ \
  --include='*.sh' --include='*.ts' --include='*.py' --include='*.json' --include='*.md' 2>/dev/null \
  | grep -v 'tasks/' | grep -v 'docs/' | grep -v 'AGENTS.md' | grep -v 'sources/fos-study')
if [ -n "$HITS" ]; then
  echo "PHASE_FAILED: fos-study-pack 잔재"
  echo "$HITS"
  exit 1
fi
```

### 2. skill 수 확인 (11 → 10)

```bash
SKILL_COUNT=$(find career-os/skills -maxdepth 1 -mindepth 1 -type d | wc -l)
[ "$SKILL_COUNT" = "10" ] || { echo "PHASE_FAILED: skill 수 $SKILL_COUNT (expected 10)"; exit 1; }
```

### 3. 한글화 + docs-audit 안내 통합 확인

```bash
# 6 SKILL.md 모두 한글 비율 ≥30% 재확인
for skill in study-pack-writer study-pack-maintainer experience-question-bank-writer \
             interview-master-writer position-recommender cj-foodville-coffeechat-prep; do
  f="career-os/skills/$skill/SKILL.md"
  ko=$(awk 'BEGIN{c=0} {n=gsub(/[가-힣]/,"",$0); c+=n} END{print c}' "$f")
  total=$(wc -m < "$f")
  pct=$((ko * 100 / (total + 1)))
  [ "$pct" -ge 30 ] || { echo "PHASE_FAILED: $skill 한글 $pct% < 30%"; exit 1; }
done

# maintainer에 docs-audit 안내
grep -q 'docs-audit' career-os/skills/study-pack-maintainer/SKILL.md
```

### 4. dispatcher smoke (옛 fos-study-pack case 영향 점검)

fos-study-pack은 dispatcher 미연결이었으므로 14 case 그대로. smoke 1회 실행으로 dispatcher 자체 동작 확인:

```bash
career-os/bin/run-now smoke
```

(plan011 후 환경 가정 — bin/run-now 존재.)

### 5. push + trailing cleanup

```bash
git add career-os/ _shared/
git commit -m "chore(career-os): plan012 통합 smoke 통과 + fos-study-pack 잔재 정리"
git push origin main

if [ -n "$(git status --porcelain career-os/tasks/plan012-skills-korean-and-cleanup/index.json)" ]; then
  git add career-os/tasks/plan012-skills-korean-and-cleanup/index.json
  git commit -m "chore(career-os): plan012 index.json commitSha 후기록"
  git push origin main
fi
```

## 검증 명령 (요약)

```bash
[ "$(find career-os/skills -maxdepth 1 -mindepth 1 -type d | wc -l)" = "10" ]
[ -z "$(grep -rln 'fos-study-pack' career-os/ _shared/ --include='*.sh' --include='*.ts' --include='*.py' 2>/dev/null | grep -v 'tasks/' | grep -v 'docs/')" ]
career-os/bin/run-now smoke
git log -1 --pretty=%s | grep -q 'plan012.*통합 smoke\|plan012 index.json commitSha'
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

phase-04은 두 커밋(2번째 옵션):
1. `chore(career-os): plan012 통합 smoke 통과 + fos-study-pack 잔재 정리`
2. `chore(career-os): plan012 index.json commitSha 후기록`

## 범위 외

- maintainer가 docs-audit subprocess 자동 호출(ADR-025에서 명시적 제외).
- 나머지 5 skill(이미 한글 비율 ≥25%) 추가 한글화 — 별도 plan.
- skill 폴더명 변경(cj-foodville-coffeechat-prep 등) — 별도 plan, 면접 활성 자산 보호.
