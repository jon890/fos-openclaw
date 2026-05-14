# Phase 5 — SKILL.md 일관성 표준 + 절대 경로 정리

## 목표

11 SKILL.md(symlink docs-audit 제외)의 길이·내용 표준화 + `bifos` 등 사용자별 절대 경로 잔재 제거. SKILL.md가 Claude 컨텍스트 자산이므로 일관된 가이드라인으로 토큰 효율 + drift 회피.

## 의존성 / 가정

- phase-01~04 완료. 코드 영역은 안정.
- audit 결과 (SKILL.md 길이 29~101 lines, bifos 잔재 3 files: position-recommender / fos-study-pack / cj-foodville-coffeechat-prep).

## 작업

### 1. SKILL.md 공통 스켈레톤

각 SKILL.md를 다음 섹션 5개로 정렬:

1. **헤더** — `# <skill-name>` + 1줄 의도.
2. **호출 방법** — `scripts/command-router/run_now.sh <command> [args]` (workspace-relative). 절대 경로 ❌.
3. **입력** — config / references / 환경 변수 목록 (한 줄씩, 패턴으로).
4. **산출물** — 경로 + git push 여부.
5. **관련 ADR** — 결정 cross-ref만 한 줄.

목표 길이: 30~60 lines. 너무 짧은 (topic-pool-replenisher 29) 또는 너무 김 (study-pack-writer 101 / experience-question-bank-writer 84)을 균형. 단 docs-audit는 fos-study 측 심링크라 손대지 않음.

### 2. bifos 절대 경로 제거

3 SKILL.md(`position-recommender` / `fos-study-pack` / `cj-foodville-coffeechat-prep`)의 `/home/bifos/ai-nodes/...` 형태를 `<workspace-root>/...` 또는 그냥 `career-os/...`로.

### 3. SKILL.md 안의 path 갱신 검증

plan006 이후 `scripts/<skill>/` 컨벤션이라 SKILL.md 안의 호출 예시도 그 형식.

## 검증 명령

```bash
# 1. bifos 절대 경로 잔재 0
[ "$(grep -rln '/home/bifos\|/Users/' career-os/skills/ --include='SKILL.md' | wc -l)" = "0" ]

# 2. SKILL.md 길이 범위 확인 (symlink docs-audit 제외)
for f in career-os/skills/*/SKILL.md; do
  [ -L "$f" ] && continue
  L=$(wc -l < "$f")
  [ "$L" -ge 20 ] && [ "$L" -le 80 ] \
    || { echo "PHASE_FAILED: $f $L lines 범위 외 (20-80)"; exit 1; }
done

# 3. 모든 SKILL.md에 5개 섹션 헤더 패턴 존재
for f in career-os/skills/*/SKILL.md; do
  [ -L "$f" ] && continue
  for section in '호출\|진입\|invoke' '입력\|input\|config' '산출\|output' 'ADR'; do
    grep -qiE "$section" "$f" \
      || { echo "PHASE_FAILED: $f 섹션 ($section) 누락"; exit 1; }
  done
done

# 4. 호출 예시가 workspace-relative (scripts/<skill>/ 또는 scripts/command-router/)
[ "$(grep -lE 'skills/[a-z-]+/scripts/' career-os/skills/*/SKILL.md | grep -v docs-audit | wc -l)" = "0" ]
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

```
docs(career-os): SKILL.md 일관성 표준 + 절대 경로 정리

- 11 SKILL.md를 5섹션 스켈레톤으로 정렬 (목표 30-60 lines)
- bifos / Users 절대 경로 제거 → workspace-relative
- 호출 예시를 scripts/command-router/ 또는 scripts/<skill>/ 형식으로
```

## 범위 외

- 코드 영역 변경 (phase-01~04).
- docs-audit SKILL.md (fos-study 측 심링크).
