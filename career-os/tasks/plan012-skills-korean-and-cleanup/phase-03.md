# Phase 3 — 6 SKILL.md 한글화 + maintainer에 docs-audit 활용 권장 명시

## 목표

영문 위주 SKILL.md 6개(study-pack-writer / study-pack-maintainer / experience-question-bank-writer / interview-master-writer / position-recommender / cj-foodville-coffeechat-prep)를 description + prose 한글로 갱신. 코드 식별자(skill명·command명·파일경로·함수명·trigger pattern)는 영어 유지. maintainer SKILL.md에는 docs-audit 활용 권장 한 줄 추가.

## 의존성 / 가정

- phase-01 + phase-02 완료. fos-study-pack 폴더 제거됨.
- working tree clean.

## 작업

### 1. 한글화 대상 6 SKILL.md + 패턴

각 SKILL.md를 다음 원칙으로 갱신:

- **frontmatter description**: 영어 → 한글. 단 trigger pattern용 키워드(예: '/study-pack', '/question-bank')는 영어 유지 — Claude Code skill 자동 매칭 영향.
- **# Heading**: 한글 또는 영어 skill명 유지(코드 식별자).
- **## 섹션 헤더**: 한글(예: "## Purpose" → "## 목적", "## Output policy" → "## 산출 정책").
- **본문 prose**: 영어 → 한글. 명령·파일경로·함수명은 그대로(예: `run_now.sh study-pack <topic>`).
- **코드 블록 안 텍스트**: 그대로 영어(코드는 보존).

목표 한글 비율: 40~60%. 너무 100%로 가면 코드 식별자까지 한글화돼 검색 어려움 — 균형 유지.

### 2. study-pack-writer 한글화 + 자연어 트리거 보존

phase-02에서 추가한 자연어 라우팅 안내는 그대로. 한글화 시 description에 영어 trigger keyword(`/study-pack`, `study pack`) 보존.

### 3. study-pack-maintainer에 docs-audit 활용 권장 추가

`career-os/skills/study-pack-maintainer/SKILL.md`에 새 섹션 또는 추가 줄:

```
## fos-study 전체 점검 시

fos-study 저장소 전체 상태(broken link / orphan doc / cross-link 누락 등)를 미리 파악하고 싶다면 `docs-audit` skill을 먼저 실행한다. maintainer는 docs-audit 결과를 자동으로 호출하지 않으므로, 대규모 업데이트 전에 사용자가 수동으로 실행 권장.

docs-audit은 fos-study 측 진실 출처(`sources/fos-study/.claude/skills/docs-audit/SKILL.md`)의 심볼릭 링크다.
```

한글로 작성(maintainer SKILL.md 자체가 한글화 대상이라 일관).

### 4. cj-foodville-coffeechat-prep 한글화 + plan010 결과 보존

plan010 phase-01에서 회사명을 mvp-target.json 의존으로 전환했음. 본 phase는 SKILL.md *텍스트만* 한글화 — 코드 변경 X. 회사명이 SKILL.md prose에 직접 박혀있다면 동적 표현(예: "현 active 타깃은 `mvp-target.json` 참조")으로.

## 검증 명령

```bash
# 1. 6 SKILL.md 한글 비율 ≥ 30%
for skill in study-pack-writer study-pack-maintainer experience-question-bank-writer \
             interview-master-writer position-recommender cj-foodville-coffeechat-prep; do
  f="career-os/skills/$skill/SKILL.md"
  ko=$(awk 'BEGIN{c=0} {n=gsub(/[가-힣]/,"",$0); c+=n} END{print c}' "$f")
  total=$(wc -m < "$f")
  pct=$((ko * 100 / (total + 1)))
  [ "$pct" -ge 30 ] || { echo "PHASE_FAILED: $skill 한글 비율 $pct% < 30%"; exit 1; }
done

# 2. study-pack-maintainer에 docs-audit 안내 존재
grep -q 'docs-audit' career-os/skills/study-pack-maintainer/SKILL.md

# 3. 코드 식별자 보존 — skill명·command명이 SKILL.md 안에 영어로 그대로
grep -q 'run_now\|study-pack\|question-bank' career-os/skills/study-pack-writer/SKILL.md

# 4. trigger keyword 영어 보존 (description 안)
grep -q '/study-pack\|study pack\|study-pack' career-os/skills/study-pack-writer/SKILL.md

# 5. § 기호 0 (사용자 글로벌 directive)
for skill in study-pack-writer study-pack-maintainer experience-question-bank-writer \
             interview-master-writer position-recommender cj-foodville-coffeechat-prep; do
  [ "$(grep -c '§' "career-os/skills/$skill/SKILL.md")" = "0" ] \
    || { echo "PHASE_FAILED: $skill § 기호 잔재"; exit 1; }
done
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

```
docs(career-os): 6 SKILL.md 한글화 + maintainer에 docs-audit 활용 권장 추가

- study-pack-writer / maintainer / experience-question-bank-writer / interview-master-writer / position-recommender / cj-foodville-coffeechat-prep
- description + prose 한글 (목표 40-60%)
- 코드 식별자(skill명·command명·trigger pattern)는 영어 유지
- maintainer SKILL.md에 docs-audit 수동 활용 권장 한 줄
```

## 범위 외

- 다른 5 skill(이미 한글 비율 ≥25%) 추가 한글화 — 본 plan 범위 외.
- docs-audit skill 자체 변경 — fos-study 측 진실 출처.
- 통합 smoke(phase-04).
