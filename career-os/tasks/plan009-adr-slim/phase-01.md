# Phase 1 — 비대 ADR 4개 슬림 + 중간 위험 3개 점검·슬림

## 목표

`career-os/docs/adr.md`에서 5문서 공통 작성 원칙(코드 명세 X · 파일 전수 목록 X · 변경 이력 X · 미래 enhancement X)을 위반해 비대해진 ADR들을 의사결정의 *왜·무엇·결과*만 남도록 압축. 결정 자체나 cross-reference는 보존(자기-완결).

### 슬림 대상 (확정 4개)

- ADR-015 (47줄, 19 불릿) — docs/ 피드백 루프 + data/ 위치 정책
- ADR-017 (49줄, 21 불릿) — cj-oliveyoung 거대 skill 분해
- ADR-019 (49줄, 18 불릿) — career-os: skill 폴더와 실행 스크립트 디렉터리 분리
- ADR-021 (38줄, 22 불릿) — Discord 알림 openclaw 경유 + .env 격리

### 점검 후 슬림(필요 시) 3개

- ADR-016 (27줄, 13 불릿) — config 디렉터리 통합
- ADR-018 (31줄, 17 불릿) — docs/ 운영 정책: 휘발성 vs 영속
- ADR-020 (27줄, 13 불릿) — 공용 헬퍼 TS(Bun) 마이그레이션

점검 기준(어느 하나라도 해당 시 슬림):
- 코드 블록 (` ``` `) 1개 이상 등장.
- 적용 대상 파일/스크립트 5개 이상의 전수 목록 등장.
- "before/after" 비교 또는 마이그레이션 step-by-step 등장.
- 미래 enhancement / TODO 라인 등장.

## 의존성 / 가정

- working tree clean(main).
- plan008이 외부 세션에서 실행 중일 수 있음 — 본 phase는 `career-os/docs/adr.md`만 만지므로 plan008(코드 영역)과 충돌 없음. 단 ADR-022 본문은 plan008이 이미 적정 크기로 작성된 상태 — 손대지 않음.

## 작업

### 1. 각 ADR 슬림 패턴 (4 + 점검 대상 3)

5섹션 구조 유지: 헤더 · 맥락 · 결정 · 결과 · (선택)적용.

각 섹션 압축 기준:
- **맥락**: 결정의 *왜*를 추론하기에 충분한 만큼만(2-5줄). 기존 상태 + 발견된 문제. 구체 수치·파일명·과거 의사결정 이력 제거.
- **결정**: 무엇을·핵심 trade-off·거절 대안 한 줄씩. 적용 대상 파일 전수 목록을 패턴 한 줄로 압축(예: "11개 skill의 `scripts/<name>/`로 이동" → 그대로 유지 OK이나 "skill A·B·C·D·E·F·G·H·I·J·K"라면 압축).
- **결과**: 의도된 효과 + 단점. 정량 수치 제거(`19+ → 9` → "디렉터리 수 통제"). 미래 TODO 제거.
- **적용**: 포인터만(예: "`tasks/planNNN-<slug>/` 참조"). 코드 블록·파일 목록 ❌.

### 2. 보존해야 할 것

- 결정의 *의도*와 *trade-off*.
- 다른 ADR 번호 참조(cross-reference).
- 폐기·supersede 상태 마킹(예: ADR-004의 `[폐기]`).
- 날짜 라인(history 추적).

### 3. 본 phase에서 안 한다

- ADR-007a → 007 / 007b → ADR-023 리넘버링(phase-02).
- 새 ADR 추가 또는 ADR-022 슬림(이미 적정).
- adr.md 외 문서(flow.md / AGENTS.md 등) 변경.

## 검증 명령

```bash
# 1. 슬림 대상 4개 줄 수가 임계 이하
python3 - <<'PY'
import re
from pathlib import Path
text = Path('career-os/docs/adr.md').read_text(encoding='utf-8')
adrs = {}
cur_id, cur_lines = None, []
for line in text.split('\n'):
    m = re.match(r'^## (ADR-\S+)\s', line)
    if m:
        if cur_id:
            adrs[cur_id] = cur_lines
        cur_id, cur_lines = m.group(1), [line]
    elif cur_id:
        cur_lines.append(line)
if cur_id:
    adrs[cur_id] = cur_lines

fail = False
for adr in ('ADR-015', 'ADR-017', 'ADR-019', 'ADR-021'):
    lines = adrs.get(adr, [])
    if len(lines) > 30:
        print(f'PHASE_FAILED: {adr} 줄 수 {len(lines)} > 30')
        fail = True
    if sum(1 for l in lines if l.startswith('- ')) > 12:
        print(f'PHASE_FAILED: {adr} 불릿 > 12')
        fail = True
    if '```' in '\n'.join(lines):
        print(f'PHASE_FAILED: {adr} 코드 블록 잔재')
        fail = True

import sys
sys.exit(1 if fail else 0)
PY

# 2. 점검 대상 3개: 코드 블록 0 + 미래 enhancement 키워드 ('TODO', '향후', '추후') 0
python3 - <<'PY'
import re, sys
from pathlib import Path
text = Path('career-os/docs/adr.md').read_text(encoding='utf-8')
adrs = {}
cur_id, cur_lines = None, []
for line in text.split('\n'):
    m = re.match(r'^## (ADR-\S+)\s', line)
    if m:
        if cur_id:
            adrs[cur_id] = cur_lines
        cur_id, cur_lines = m.group(1), [line]
    elif cur_id:
        cur_lines.append(line)
if cur_id:
    adrs[cur_id] = cur_lines

fail = False
for adr in ('ADR-016', 'ADR-018', 'ADR-020'):
    body = '\n'.join(adrs.get(adr, []))
    if '```' in body:
        print(f'PHASE_FAILED: {adr} 코드 블록 잔재'); fail = True
    for kw in ('TODO', '향후 ', '추후 '):
        if kw in body:
            print(f'PHASE_FAILED: {adr} 미래 키워드 {kw!r} 잔재'); fail = True
sys.exit(1 if fail else 0)
PY

# 3. 슬림이 결정 자체를 깎지 않았는지 — 헤더·Status·Date 라인 모두 보존
for adr in ADR-015 ADR-017 ADR-019 ADR-021 ADR-016 ADR-018 ADR-020; do
  grep -q "^## ${adr} —" career-os/docs/adr.md || { echo "PHASE_FAILED: ${adr} 헤더 손실"; exit 1; }
  awk "/^## ${adr} —/,/^## ADR-/" career-os/docs/adr.md | grep -q '^- Status:' || { echo "PHASE_FAILED: ${adr} Status 라인 손실"; exit 1; }
  awk "/^## ${adr} —/,/^## ADR-/" career-os/docs/adr.md | grep -q '^- Date:' || { echo "PHASE_FAILED: ${adr} Date 라인 손실"; exit 1; }
done

# 4. adr.md 전체 줄 수 감소 확인 (대략 50줄 이상 줄어듦)
LINES_AFTER=$(wc -l < career-os/docs/adr.md)
echo "adr.md after slim: $LINES_AFTER lines"
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

```
docs(career-os): ADR 본문 슬림 (비대 4 + 중간 3 점검) — 토큰 효율·drift 회피

- ADR-015/017/019/021 본문을 5섹션 원칙대로 압축
- ADR-016/018/020은 위반 점검 후 위반 시 슬림
- 결정·trade-off·cross-reference·날짜는 보존
- ADR-007 단일화 + ADR-023 리넘버링은 phase-02
```

## 범위 외

- ADR-007a → 007 / 007b → 023 리넘버링(phase-02).
- AGENTS.md ADR 카운트 라인 갱신(phase-02).
- flow.md / common-pitfalls.md cross-ref 갱신(phase-02).
- 새 ADR 추가(본 plan 의도에 없음).
