# Phase 01 — ADR 본문 슬림화

**Model**: sonnet
**Status**: pending

---

## 목표

`career-os/docs/adr.md`에 누적된 15개 ADR(001~015)의 본문을 ADR 작성 원칙에 맞춰 슬림화한다. 의사결정과 맥락은 보존하되, AI 에이전트가 *왜*만 이해하면 충분한 내용을 위해 코드 구현 상세·전수 목록·변경 이력 등은 제거한다.

**범위 외**: 새 ADR 추가, ADR 번호 리넘버링(007a/007b 충돌 해소), 코드 변경. 이 phase는 `adr.md` 한 파일만 in-place 수정한다.

---

## 관련 docs

실행 전 반드시 읽기:

- `skills/planning/SKILL.md` — "ADR 작성 원칙 (토큰 효율 + drift 회피)" 섹션. 본 phase의 슬림화 기준은 여기서 가져온다.
- `career-os/docs/adr.md` — 슬림화 대상 자체.

## ADR 작성 원칙 (요약)

각 ADR은 5개 섹션만 가진다:

1. **헤더** — `## ADR-N — 제목` + Status / Date 라인.
2. **맥락** — 왜 이 결정이 필요했는지. AI 에이전트가 *왜*를 추론하기에 충분한 만큼만.
3. **결정** — 무엇을 결정했는지. 핵심 trade-off + 거절한 대안 한 줄씩.
4. **결과** — 결정의 의도된 효과 + 알려진 단점.
5. **(선택) 적용** — 가이드라인이 박혀 있는 *포인터*만. 코드 블록 ❌, 파일 전수 목록 ❌.

다음은 ADR에 넣지 않는다:

- 코드 블록 (before/after 비교, 함수 구현, 셸 명령 시퀀스).
- 적용 대상 파일의 전수 목록 (디렉터리 한 줄 또는 패턴으로 표현).
- 변경 이력 (git history가 단일 출처 — `## 변경 이력` 섹션 통째로 제거).
- 검증 결과의 구체 수치 (별도 회고로).
- 미래 enhancement / TODO (`## Future enhancements`, `## Follow-up` 류 섹션 통째로 제거 — 별도 plan이나 task로).

코드를 알아야 결정 자체를 이해할 수 없는 경우만 짧은 인용 1-2줄 허용.

---

## 작업 항목

### 1. ADR-014 슬림화 (가장 큰 작업)

ADR-014는 현재 가장 길고 본 원칙에 가장 어긋난다. 다음을 제거:

- "## 적용" 섹션의 코드 블록 (before/after `bash` 예시) → 한 줄 인용으로 축약. 어디에 패턴이 박혀 있는지 *포인터*만 남긴다 (`_shared/bin/claude_lib.sh`의 `claude_persist_usage`).
- "## 적용 대상" 섹션의 runner / extractor / Python 인라인 전수 목록 → "career-os의 모든 Claude 호출 runner + Python 직접 호출 1건" 같이 한 줄로 축약.
- "## 변경 이력" 섹션 통째로 제거.

### 2. ADR-013, ADR-012, ADR-011, ADR-010, ADR-009 정리

이 ADR들은 코드 블록이나 algorithm pseudocode가 본문에 들어가 있다. 결정의 *왜*를 이해하기에 코드가 필수가 아닌 경우 제거. 필수면 짧은 인용으로 축약.

- "Future enhancements (not in this ADR)" 섹션 통째로 제거 (있는 경우).
- "Follow-up" 또는 "Future enhancements" 류 섹션 통째로 제거.
- "Source separation" 같은 표가 결정 자체를 설명하지 않고 적용 매트릭스인 경우 → 핵심만 결정 섹션에 흡수 후 표 제거.

### 3. ADR-007a, ADR-007b 정리

- ADR-007a "Decision" 섹션에 1~6번 번호 매긴 디자인 결정 항목이 있는데, 그중 코드·디렉터리 명시는 *포인터*만 남기고 구체 경로/스키마는 제거 또는 1줄로 축약.
- ADR-007b의 코드 블록 (before/after `bash`) 제거. 결정이 *왜* 필요했는지(prompt 충돌) 맥락만 보존.

### 4. ADR-002, ADR-005 정리

- ADR-002의 JSON 스키마 블록은 `docs/data-schema.md`로 옮길 정보. ADR에서는 "study-progress.json에 세션 + 약점 토픽별 진도를 하이브리드 포맷으로 기록"이라는 결정 자체만 남긴다. JSON 예시는 제거.
- ADR-005의 commit message 규칙 예시(`docs(mysql): add draft ...`)는 결정 자체이므로 유지 가능. 단 "문서 경로 규칙" 표가 너무 자세하면 `docs/code-architecture.md` 또는 `docs/data-schema.md`로 위임 가능.

### 5. 짧은 ADR (001, 003, 004, 006, 008, 015)은 검토만

이미 5섹션 안에 있고 코드 블록도 없는 ADR은 변경하지 않는다.

### 6. ADR-016 추가 금지

본 cleanup의 근거 원칙은 이미 `skills/planning/SKILL.md`에 있으므로 ADR로 또 만들지 않는다. (애초에 만들었다가 사용자 결정으로 제거된 이력이 있음 — 같은 원칙을 두 곳에 쓰지 않는다.)

---

## Critical Files

| 파일 | 변경 |
|---|---|
| `career-os/docs/adr.md` | 수정 (in-place 슬림화) |

다른 파일은 손대지 않는다. `docs/data-schema.md` / `docs/code-architecture.md`로 정보 *이동*이 필요하면 별도 plan으로 분리한다 — 이 phase에선 *제거*만.

## 검증

phase 끝에 다음을 실행해 슬림화 성공 확인:

```bash
cd /home/bifos/ai-nodes

# 1. adr.md 줄 수가 줄었는지 (현재 ~400줄대 → 슬림화 후 ~250줄 이하 기대)
wc -l career-os/docs/adr.md

# 2. 코드 펜스가 거의 사라졌는지 (단순 inline `command` 외의 ```블록은 거의 0이어야)
grep -c '^```' career-os/docs/adr.md
# 기대값: 매우 적음 (0 또는 1-2). 많이 남으면 PHASE_FAILED.

# 3. "변경 이력" / "Follow-up" / "Future enhancements" 섹션이 모두 제거됐는지
grep -c "^## 변경 이력\|^## Follow-up\|^## Future enhancements\|^## 적용 대상" career-os/docs/adr.md
# 기대값: 0

# 4. ADR 헤더 15개 모두 그대로 (001~015)
grep -c "^## ADR-" career-os/docs/adr.md
# 기대값: 15

# 5. 마크다운 구조 깨지지 않았는지 - 헤더가 정상 순서
grep "^## " career-os/docs/adr.md | head -16
```

위 5개 모두 통과하면 success. 한 가지라도 실패하면 `PHASE_FAILED: <검증 실패 항목>` 출력 후 종료.

## 커밋

phase 끝에 다음 커밋:

```
docs(career-os): ADR 본문 슬림화 (작성 원칙 적용)

각 ADR을 5섹션(헤더/맥락/결정/결과/적용 포인터)으로 정렬. 코드 블록·전수 목록·변경 이력·미래 enhancements 섹션 제거. 결정 자체를 이해하는 데 필요한 짧은 인용은 유지.

ADR-014가 가장 많이 줄었다. ADR-007a/b의 디렉터리/스키마 명세는 포인터만. ADR-002의 JSON 예시는 제거 (필요 시 docs/data-schema.md 참조).
```

push는 phase-02에서. 이 phase는 commit까지만.

## 의도 메모 (왜)

- ADR의 *왜* 가치는 시간이 갈수록 커지지만, 코드 구현 상세는 거짓이 되기 쉽다. 슬림화로 drift 위험 축소.
- 토큰 효율 — AI 에이전트가 docs/adr.md를 읽을 때 의사결정 맥락에만 집중하도록.

## Blocked 조건

- 슬림화 도중 의미 보존이 어렵다고 판단되는 ADR이 있으면 그 ADR만 건너뛰고 진행. 종료 시 stdout에 `[skipped] ADR-N: <reason>` 한 줄 보고. 모든 ADR이 skip되면 `PHASE_BLOCKED: 슬림화 가능한 ADR 없음`.
- `career-os/docs/adr.md` 파일 자체가 존재하지 않으면 `PHASE_BLOCKED: adr.md 없음`.
