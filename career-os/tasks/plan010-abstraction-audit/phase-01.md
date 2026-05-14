# Phase 1 — 회사·직무 하드코딩 제거 + config 의존 전환

## 목표

코드·references에 박힌 회사명·직무·옛 MVP 타깃 잔재를 제거. `config/mvp-target.json`을 단일 출처로 활용. 필요 시 새 config(`config/target-context.json` 등) 신설해 회사·역할·우선 도메인 같은 컨텍스트를 외부 주입 받도록.

## 의존성 / 가정

- plan007 + plan008 모두 `completed`.
- working tree clean.
- audit으로 다음 영역에서 회사·직무 잔재 확인됨(실제 위치는 phase 실행 시 grep 재확인):
  - `scripts/cj-foodville-coffeechat-prep/run_foodville_coffeechat_prep.sh` — 회사명 9 mentions.
  - `scripts/knowledge-gap-analyzer/run_{baseline,daily,smoke_test}.sh` — kakao 잔재 (옛 MVP).
  - `skills/position-recommender/references/*` — kakao 회사 정보 박힘 (5 files).
  - `skills/knowledge-gap-analyzer/references/{baseline,daily}-prompt.md` — kakao 컨텍스트.
  - `scripts/experience-question-bank-writer/render_question_bank.ts` — plan008이 새로 만든 TS에 kakao 박힘.
  - `scripts/command-router/run_now.sh` — usage 메시지 등 회사명 잔재.

## 작업

### 1. 새 config (선택)

`mvp-target.json`이 회사명·팀명·면접일만 담는 단일 출처. 그 외 부수 컨텍스트(직무 역할, 우선 도메인, 후보자 강점·약점, 부트캠프 토픽 우선순위 등)가 코드·references에 분산된 경우, 새 `config/target-context.json`을 신설해 다음 키를 담는다:

- `role` — 예: "java-backend".
- `priorityDomains` — 예: `["db", "spring", "jpa"]`.
- `weakAreas` — 예: `["jpa-n+1", "redis-caching"]`.
- `industryContext` — primary 회사가 속한 산업 컨텍스트 (예: "F&B 도메인 e-commerce"). 회사명 자체는 mvp-target.json에서 join.

스키마는 `docs/data-schema.md`에 추가. `mvp-target.json`의 primary 엔트리에 직접 임베드해도 OK — 본 phase에서 결정.

### 2. cj-foodville-coffeechat-prep skill 일반화

- 폴더 이름은 본 phase에서 변경하지 않는다 (cross-ref 큼, plan-and-build 컨벤션상 별도 plan에서 처리). 대신 *내용*에서 회사명 제거.
- `run_foodville_coffeechat_prep.sh` 안의 heredoc·문자열 라인에서 `CJ푸드빌` / `푸드빌` / `foodville` 표기를 `mvp-target.json`의 `primary.company` 또는 `primary.industryContext` 변수에서 읽도록 변경 (실제 변수 주입은 phase-02에서 일괄).
- 산출물 경로 `data/.../cj-foodville-coffeechat/`는 phase-01에서는 그대로 두고, phase-02에서 mvp-target 기반 동적 경로로.

### 3. knowledge-gap-analyzer kakao 잔재 정리

- `run_baseline.sh` / `run_daily.sh` / `run_smoke_test.sh`의 inline 회사명·역할 표기를 mvp-target 의존으로.
- `references/baseline-prompt.md` / `daily-prompt.md`의 옛 kakao 타깃 컨텍스트를 일반 표현으로 갱신. 회사 컨텍스트는 phase-02에서 프롬프트 템플릿화 시 동적 주입.

### 4. position-recommender references kakao 잔재

- `verified-company-research-targets.json`, `position-context-index.md`, `company-upside-reference.md`, `position-decision-criteria.md`, `verified-company-discovery.md` — kakao 등 회사 정보 박힘.
- 활성 자산이면 그대로 두고, 옛 자산이면 git rm. 활성/옛 판별: `mvp-target.json`의 `primary`와 `history`를 기준으로. primary 회사 관련만 보존, 옛 history에 속하면 정리.
- 결정 모호하면 references 안에 별도 `archive/` 폴더로 이전 (삭제는 별도 plan).

### 5. render_question_bank.ts 회사명 정리

plan008 phase-01이 작성한 `scripts/experience-question-bank-writer/render_question_bank.ts`에 kakao 박혀있다면 동적 변수로 전환. Python 원본 마이그 시 회사명까지 옮긴 흔적.

## 검증 명령

```bash
# 1. kakao 회사명 잔재가 활성 자산에 0 (references/archive/ 제외)
HITS=$(grep -rln 'kakao\|카카오' career-os/scripts career-os/skills 2>/dev/null \
  | grep -v __pycache__ | grep -v 'archive/' | grep -v 'docs-audit')
[ -z "$HITS" ] || { echo "PHASE_FAILED: kakao 잔재"; echo "$HITS"; exit 1; }

# 2. cj-foodville-coffeechat-prep runner 안 회사명 0 (skill 이름은 phase 외, 별도 plan)
[ "$(grep -cE 'CJ푸드빌|푸드빌|foodville' career-os/scripts/cj-foodville-coffeechat-prep/run_foodville_coffeechat_prep.sh)" = "0" ]

# 3. mvp-target.json 의존 진입 — coffeechat / baseline / daily / smoke runner가 mvp-target 또는 새 config 참조
for runner in career-os/scripts/cj-foodville-coffeechat-prep/run_foodville_coffeechat_prep.sh \
              career-os/scripts/knowledge-gap-analyzer/run_baseline.sh \
              career-os/scripts/knowledge-gap-analyzer/run_daily.sh \
              career-os/scripts/knowledge-gap-analyzer/run_smoke_test.sh; do
  grep -qE 'mvp-target|target-context' "$runner" \
    || { echo "PHASE_FAILED: $runner 가 mvp-target 의존하지 않음"; exit 1; }
done

# 4. runner / TS 자산 syntax 보존
bash -n career-os/scripts/cj-foodville-coffeechat-prep/run_foodville_coffeechat_prep.sh
bash -n career-os/scripts/knowledge-gap-analyzer/run_baseline.sh
bash -n career-os/scripts/knowledge-gap-analyzer/run_daily.sh
bash -n career-os/scripts/knowledge-gap-analyzer/run_smoke_test.sh
bun --no-install build --target=bun career-os/scripts/experience-question-bank-writer/render_question_bank.ts --outdir=/tmp/plan010 >/dev/null 2>&1 \
  || { echo "PHASE_FAILED: render_question_bank.ts syntax"; exit 1; }
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

```
refactor(career-os): 회사·직무 하드코딩 제거 + mvp-target.json 의존 전환

- coffeechat runner 안 푸드빌/foodville 문자열을 mvp-target 변수 참조로
- knowledge-gap-analyzer 3 runner의 kakao 옛 컨텍스트 정리
- position-recommender references 활성/옛 분류 + 옛 자산 archive 이동
- render_question_bank.ts 회사명 동적 변수화
- (선택) config/target-context.json 신설 + data-schema.md 갱신
```

## 범위 외

- 회사명 폴더(cj-foodville-coffeechat-prep) 이름 변경 (별도 plan).
- 프롬프트(heredoc) 안의 회사명 → config 주입 패턴 일괄 적용 (phase-02).
- study-pack 공통 코어 추출 (phase-03).
- SKILL.md 안의 bifos 절대 경로 (phase-05).
