# Phase 2 — Claude 호출 프롬프트 템플릿화 + config 주입

## 목표

5+ runner의 `cat <<EOF` heredoc 안에 박힌 회사명·역할·우선 도메인·후보자 컨텍스트를 config(`mvp-target.json` + `target-context.json` + `candidate-profile.md`)에서 동적 주입받도록 템플릿화. 새 컨벤션을 `_shared/lib/build_prompt.ts`(또는 envsubst 패턴)로 표준화.

## 의존성 / 가정

- phase-01 완료 — 회사명 하드코딩은 변수 참조로 전환된 상태.
- working tree clean.

## 작업

### 1. 템플릿 패턴 선택

두 옵션:

- **(a) `_shared/lib/build_prompt.ts`**: TS 모듈. `buildPrompt(templatePath, context)` 형태. 템플릿은 `skills/<skill>/references/*.md`에 두고 `{{primary.company}}` / `{{role}}` placeholder. 본 phase에서 선택.
- **(b) shell envsubst**: bash 기본 도구. 가볍지만 dependency 추적 어려움.

(a) 권장 — plan004/008의 TS 일관성. context는 `mvp-target.json` + `target-context.json` + `candidate-profile.md` 머지 결과.

### 2. `_shared/lib/build_prompt.ts` 신설

- 입력: 템플릿 파일 경로 + (선택) 컨텍스트 override.
- 컨텍스트 로드 순서: `<workspace>/config/mvp-target.json` → `<workspace>/config/target-context.json`(있으면) → `<workspace>/config/candidate-profile.md`(머리말 metadata).
- 출력: stdout으로 완성된 프롬프트 마크다운.
- shebang `#!/usr/bin/env bun`. 단독 실행 가능 + import 가능.
- 누락된 placeholder는 비-0 exit + stderr 에러(엄격 모드 기본).

### 3. 영향 runner 5개 + 1개 dispatcher heredoc 갱신

| runner | 현재 heredoc 내용 | 마이그레이션 |
|---|---|---|
| `scripts/cj-foodville-coffeechat-prep/run_foodville_coffeechat_prep.sh` | 9개 회사·역할 mention | 템플릿 파일 분리 → `skills/cj-foodville-coffeechat-prep/references/coffeechat-prompt.md` |
| `scripts/knowledge-gap-analyzer/run_baseline.sh` | 회사 컨텍스트 2 mention | `skills/knowledge-gap-analyzer/references/baseline-prompt.md` 이미 있음 — 안의 회사 표기를 placeholder로 |
| `scripts/knowledge-gap-analyzer/run_daily.sh` | 회사 컨텍스트 | `daily-prompt.md` 동일 처리 |
| `scripts/knowledge-gap-analyzer/run_smoke_test.sh` | 회사 컨텍스트 3 mention | `smoke-prompt.md` 신설 또는 baseline-prompt 재사용 + placeholder |
| `scripts/command-router/run_now.sh` | usage 메시지 안 회사명 4 mention | mvp-target 참조 또는 회사-중립 표기 |

각 runner는 `bun "$TASK_ROOT/_shared/lib/build_prompt.ts" "$TEMPLATE_PATH" > "$INPUT_NOTE"` 형태로 프롬프트 빌드 호출.

### 4. 템플릿 placeholder 규약

- `{{primary.company}}` — 현재 active 회사명.
- `{{primary.team}}` — 팀명.
- `{{primary.interviewDate}}` — 면접일.
- `{{primary.industryContext}}` — 산업 컨텍스트.
- `{{role}}` — target-context.json의 role.
- `{{priorityDomains}}` — 우선 도메인 배열을 ", " join.
- `{{weakAreas}}` — 약점 영역.
- `{{candidateProfile}}` — `candidate-profile.md` 전체 본문.

새 placeholder 추가 시 `_shared/lib/build_prompt.ts`의 strict mode가 누락 placeholder를 검출하도록.

## 검증 명령

```bash
# 1. _shared/lib/build_prompt.ts 신설
test -f _shared/lib/build_prompt.ts
test -x _shared/lib/build_prompt.ts
head -1 _shared/lib/build_prompt.ts | grep -q '#!/usr/bin/env bun'
bun --no-install build --target=bun _shared/lib/build_prompt.ts --outdir=/tmp/plan010 >/dev/null 2>&1

# 2. 영향 runner들이 build_prompt.ts 호출
for runner in career-os/scripts/cj-foodville-coffeechat-prep/run_foodville_coffeechat_prep.sh \
              career-os/scripts/knowledge-gap-analyzer/run_baseline.sh \
              career-os/scripts/knowledge-gap-analyzer/run_daily.sh \
              career-os/scripts/knowledge-gap-analyzer/run_smoke_test.sh; do
  grep -q 'build_prompt' "$runner" \
    || { echo "PHASE_FAILED: $runner build_prompt.ts 미호출"; exit 1; }
done

# 3. 영향 runner heredoc 안 회사명 0 (템플릿으로 이동됨)
for runner in career-os/scripts/cj-foodville-coffeechat-prep/run_foodville_coffeechat_prep.sh \
              career-os/scripts/knowledge-gap-analyzer/run_baseline.sh \
              career-os/scripts/knowledge-gap-analyzer/run_daily.sh \
              career-os/scripts/knowledge-gap-analyzer/run_smoke_test.sh; do
  [ "$(grep -cE 'CJ푸드빌|푸드빌|foodville|kakao|카카오' "$runner")" = "0" ] \
    || { echo "PHASE_FAILED: $runner heredoc 회사명 잔재"; exit 1; }
done

# 4. 템플릿 파일에 placeholder 존재 (회사명이 정적 텍스트가 아닌 변수로)
grep -q '{{primary\.\|{{role}}' career-os/skills/cj-foodville-coffeechat-prep/references/coffeechat-prompt.md
grep -q '{{primary\.\|{{role}}' career-os/skills/knowledge-gap-analyzer/references/baseline-prompt.md
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

```
feat(_shared, career-os): Claude 프롬프트 템플릿화 + config 주입 (_shared/lib/build_prompt.ts)

- _shared/lib/build_prompt.ts 신설: 템플릿 + mvp-target/target-context/candidate-profile 머지
- {{primary.company}} / {{role}} / {{weakAreas}} placeholder 규약
- 5 runner heredoc → references/*-prompt.md 분리 + build_prompt.ts 호출
- 회사명·역할이 정적 텍스트에서 사라짐
```

## 범위 외

- study-pack 생성 공통 코어 추출 (phase-03).
- fos-study git ops 추상화 (phase-04).
- 회사명 폴더 이름 변경 (별도 plan).
