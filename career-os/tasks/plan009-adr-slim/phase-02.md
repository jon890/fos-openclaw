# Phase 2 — ADR-007a→ADR-007 / 007b→ADR-023 리넘버링 + cross-ref 갱신 + push

## 목표

ADR-007 번호 충돌(007a + 007b 두 ADR 공존)을 해소. ADR-007a를 단일 ADR-007로, ADR-007b는 ADR-022 다음 ADR-023으로 옮김. adr.md 내부 self-reference + 외부 cross-ref(flow.md / common-pitfalls.md / AGENTS.md)를 일괄 갱신.

## 의존성 / 가정

- phase-01 완료 (ADR 본문 슬림).
- working tree clean.
- plan008과 충돌 없음(plan008은 코드 영역, 본 phase는 docs).

## 작업

### 1. adr.md 내부 변경

- `## ADR-007a — Experience-based interview question bank workflow` → `## ADR-007 — Experience-based interview question bank workflow`.
- `## ADR-007b — Study-pack 생성: 파일 쓰기 → stdout 캡처` 본문 전체(헤더부터 다음 `## ADR-008` 직전까지)를 잘라 파일 끝(ADR-022 본문 다음)으로 이동. 옮긴 뒤 헤더를 `## ADR-023 — Study-pack 생성: 파일 쓰기 → stdout 캡처`로 변경.
- ADR-007a / 007b 본문 끝의 "비고 — 번호 충돌" 라인 제거(충돌 해소됨).
- ADR-007b 본문 안에 ADR-007a를 가리키는 self-reference가 있다면 `ADR-007`로 갱신. 역방향도 동일.

### 2. adr.md self-reference 점검

```bash
grep -n 'ADR-007a\|ADR-007b' career-os/docs/adr.md
```

남은 모든 라인의 `ADR-007a` → `ADR-007`, `ADR-007b` → `ADR-023`로 치환.

### 3. 외부 cross-ref 갱신

대상 파일:
- `career-os/docs/flow.md` — `question-bank` 흐름에 ADR-007a 언급.
- `skills/plan-and-build/references/common-pitfalls.md` — plan001 회고 언급.

각각 `ADR-007a` → `ADR-007`, `ADR-007b` → `ADR-023`로 치환.

`career-os/tasks/plan001-adr-cleanup/` · `plan003-docs-legacy-cleanup/` 안의 ADR-007a/b 참조는 *history 보존*이므로 손대지 않는다(완료된 plan의 phase 파일).

### 4. AGENTS.md ADR 카운트 라인 갱신

```
| [`docs/adr.md`](docs/adr.md) | 모든 아키텍처 결정 누적 기록 (현재 ADR-001~022) ...
```

→ `ADR-001~023`(ADR-023이 새 번호로 추가됨).

### 5. 검증 + 푸시

검증 후 두 커밋:
1. `docs(career-os): ADR-007a/007b 단일화 + 리넘버링 (007a → 007, 007b → 023)`
2. (run-phases.py 후기록 trailing 변경이 있으면) `chore(career-os): plan009 index.json commitSha 후기록`

`git push origin main`.

## 검증 명령

```bash
# 1. adr.md에 ADR-007a / 007b 잔재 0
[ "$(grep -c 'ADR-007a\|ADR-007b' career-os/docs/adr.md)" = "0" ]

# 2. ADR-007 / ADR-023 헤더 존재 (정확히 1개씩)
[ "$(grep -c '^## ADR-007 —' career-os/docs/adr.md)" = "1" ]
[ "$(grep -c '^## ADR-023 —' career-os/docs/adr.md)" = "1" ]

# 3. ADR-023이 ADR-022 뒤에 오는지 (위치 순서)
ADR022_LINE=$(grep -n '^## ADR-022 —' career-os/docs/adr.md | cut -d: -f1)
ADR023_LINE=$(grep -n '^## ADR-023 —' career-os/docs/adr.md | cut -d: -f1)
[ "$ADR023_LINE" -gt "$ADR022_LINE" ] || { echo "PHASE_FAILED: ADR-023 위치"; exit 1; }

# 4. 외부 cross-ref 갱신 — flow.md / common-pitfalls.md에 ADR-007a/007b 잔재 0
[ "$(grep -c 'ADR-007a\|ADR-007b' career-os/docs/flow.md skills/plan-and-build/references/common-pitfalls.md 2>/dev/null | grep -v ':0$' | wc -l)" = "0" ]

# 5. AGENTS.md ADR 카운트 갱신
grep -q 'ADR-001~023' career-os/AGENTS.md

# 6. 워크스페이스 코드(sh / ts / py)에 ADR-007a/007b 참조 없음 — 본문 외 인용
HITS=$(grep -rln 'ADR-007a\|ADR-007b' career-os/ _shared/ skills/ 2>/dev/null \
  --include='*.sh' --include='*.ts' --include='*.py' \
  | grep -v 'tasks/')
[ -z "$HITS" ] || { echo "PHASE_FAILED: ADR-007a/b 코드 참조 잔재"; echo "$HITS"; exit 1; }

# 7. push 완료
git log -1 --pretty=%s | grep -q 'ADR-007.*단일화\|plan009 index.json commitSha'
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

```
docs(career-os): ADR-007a/007b 단일화 + 리넘버링 (007a → 007, 007b → 023)

- ADR-007a 헤더의 "a" 접미사 제거 → 단일 ADR-007
- ADR-007b 본문을 ADR-022 다음 ADR-023으로 이동
- "번호 충돌" 비고 라인 제거
- adr.md 내부 self-ref + flow.md + common-pitfalls.md cross-ref 갱신
- AGENTS.md ADR 카운트 ADR-001~022 → ADR-001~023
- history plan(plan001, plan003) phase 파일은 보존
```

## 범위 외

- 다른 ADR 본문 슬림(phase-01).
- 새 ADR 추가.
- 다른 워크스페이스(apartment) cross-ref(워크스페이스 격리).
