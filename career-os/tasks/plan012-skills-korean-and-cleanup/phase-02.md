# Phase 2 — fos-study-pack → study-pack-writer 자연어 라우팅 흡수 + 폴더 제거

## 목표

`career-os/skills/fos-study-pack/`와 `career-os/scripts/fos-study-pack/`를 git rm. 자연어 라우팅 기능(주제 자연어 입력 → topic 매핑 → study-pack 흐름)은 `study-pack-writer`로 흡수: writer SKILL.md의 description에 trigger pattern 추가 + run_study_pack runner에 자연어 입력 처리 분기.

## 의존성 / 가정

- phase-01 완료. ADR-025 + docs 반영.
- plan010 / plan011 완료. study-pack-writer는 TS 환경(`scripts/study-pack-writer/run_study_pack.ts`).
- working tree clean.

## 작업

### 1. study-pack-writer SKILL.md에 자연어 라우팅 trigger 추가

`career-os/skills/study-pack-writer/SKILL.md`의 frontmatter description에 자연어 입력 트리거 패턴 추가:

- 기존: "Generate and publish reusable study-pack markdown documents..."
- 추가: "주제를 자연어로 표현한 요청(예: '/study-pack ...', '~에 대한 스터디팩 만들어줘')도 처리한다. 자연어 요청은 내부에서 topic key로 변환 후 동일 흐름. (옛 fos-study-pack skill 흡수, ADR-025)"

description은 Claude Code skill trigger pattern으로 사용되므로 자연어 표현·키워드 노출이 중요.

### 2. run_study_pack.ts에 자연어 입력 분기 추가

기존 인자: `<topic-key>`(config/topics.json의 study-pack namespace에서 매핑).

추가 분기:
- 인자가 *topic key 형식이 아니면*(예: `freeform:...` prefix 또는 공백 포함 문자열) 자연어 입력으로 간주.
- `_shared/lib/invoke_claude_skills.ts` 또는 directly Claude 호출로 자연어 → topic key 변환(또는 임시 topic 생성).
- 옛 `scripts/fos-study-pack/run_from_request.ts`(plan011 결과)의 로직을 가져와 통합.

phase 본문은 흡수 의도만 명시 — 구체 구현은 phase 실행 Claude가 옛 fos-study-pack 코드를 읽고 1:1 포팅.

### 3. fos-study-pack 폴더 git rm

```bash
git rm -r career-os/skills/fos-study-pack/
git rm -r career-os/scripts/fos-study-pack/
```

옛 자산: `references/request-patterns.md` 등 SKILL.md 외 references가 있다면 study-pack-writer/references/로 이동 또는 제거.

### 4. 외부 caller 점검

`fos-study-pack`을 직접 호출하는 외부 caller가 있는지 grep:

```bash
grep -rln 'fos-study-pack' career-os/ _shared/ \
  --include='*.sh' --include='*.ts' --include='*.py' --include='*.md' --include='*.json' \
  | grep -v 'tasks/' | grep -v 'docs/' | grep -v 'AGENTS.md'
```

검색 결과는 모두 갱신 또는 제거. docs / tasks / AGENTS.md의 history 참조는 보존(ADR-025 컨텍스트 인용).

## 검증 명령

```bash
# 1. fos-study-pack 폴더 git에서 제거됨
[ -z "$(git ls-files career-os/skills/fos-study-pack/)" ]
[ -z "$(git ls-files career-os/scripts/fos-study-pack/)" ]

# 2. study-pack-writer SKILL.md에 자연어 트리거 명시
grep -qE '자연어|natural language|freeform|/study-pack' career-os/skills/study-pack-writer/SKILL.md

# 3. study-pack-writer runner가 자연어 분기 처리
grep -qE 'freeform|자연어|natural' career-os/scripts/study-pack-writer/run_study_pack.ts

# 4. 외부 코드 잔재 0 (docs/tasks 제외)
HITS=$(grep -rln 'fos-study-pack' career-os/ _shared/ \
  --include='*.sh' --include='*.ts' --include='*.py' --include='*.json' 2>/dev/null \
  | grep -v 'tasks/' | grep -v 'docs/' | grep -v 'AGENTS.md' | grep -v 'sources/fos-study')
[ -z "$HITS" ] || { echo "PHASE_FAILED: fos-study-pack 코드 잔재"; echo "$HITS"; exit 1; }

# 5. run_study_pack.ts syntax 보존
bun --no-install build --target=bun career-os/scripts/study-pack-writer/run_study_pack.ts --outdir=/tmp/plan012 >/dev/null 2>&1
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

```
refactor(career-os): fos-study-pack 폴더 제거 + 자연어 라우팅 study-pack-writer로 흡수

- skills/fos-study-pack/ + scripts/fos-study-pack/ git rm
- study-pack-writer SKILL.md description에 자연어 trigger 추가
- run_study_pack.ts에 자연어 입력 분기 (옛 run_from_request 로직 흡수)
- 외부 caller 점검 → 잔재 0
```

## 범위 외

- SKILL.md 한글화(phase-03).
- maintainer + docs-audit 안내(phase-03).
