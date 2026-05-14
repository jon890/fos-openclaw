# Phase 1 — docs-first: ADR-025 + 5문서 갱신

## 목표

본 plan012의 결정(fos-study-pack 흡수 + 한글화 정책 + docs-audit 수동 연계)을 ADR-025로 기록. AGENTS.md ADR 카운트 + code-architecture.md 트리 + prd.md 갱신.

본 phase는 planning 세션에서 미룬 docs-first 작업(plan010 phase-03이 adr.md를 동시에 만질 가능성 회피).

## 의존성 / 가정

- plan010 + plan011 모두 `completed`.
- working tree clean.
- adr.md에 ADR-024(공용 헬퍼 위치 분리)까지 정렬됨. 다음 가용 ADR-025.

## 작업

### 1. adr.md에 ADR-025 추가

5섹션·코드 명세 없이 의사결정만:

- **헤더**: `## ADR-025 — Skills 정리 + 한글화 정책` + Status: Accepted + Date: 2026-05-14.
- **맥락**: career-os skills 11개가 plan005·plan010·plan011을 거치며 도메인·언어 자산이 안정됐으나 (1) fos-study-pack은 dispatcher 미연결 + run_from_request deferred 상태로 1개월+ 방치(사용 가치 없음), (2) 7 SKILL.md가 영문 위주(한글 ≤15%)라 다른 skill·docs와 톤 비대칭, (3) maintainer가 update-vs-new 판단 시 fos-study 전체 상태 점검이 필요하지만 docs-audit과 명시적 링크 없음.
- **결정**: fos-study-pack 폴더 제거 + 자연어 라우팅 의도는 study-pack-writer로 흡수(Claude Code skill description의 trigger pattern 활용). 한글화 정책 = description + prose는 한글, 코드 식별자(skill명·command명·파일경로·함수명)는 영어 유지. maintainer와 docs-audit은 SKILL.md 안내 한 줄로 수동 링크 — 자동 호출 X(cross-skill 의존 회피).
- **거절한 대안**: fos-study-pack을 dispatcher에 wire-up(미사용 자산을 살려둘 정당화 없음) / 한글 비율 100%(코드 식별자까지 한글로 가면 trigger pattern matching·grep 영향) / maintainer에서 docs-audit subprocess 자동 호출(cross-skill 결합도 상승).
- **결과**: skill 수 11 → 10. SKILL.md 톤 일관성. 한글화로 사용자(한국어 native) 가독성·유지보수성 ↑. 코드 식별자 영어 유지로 Claude Code skill trigger 매칭 보존. 단점: 한글화 후 영문 검색 grep 시 일부 안내 누락 가능 — 코드 식별자는 영어라 핵심 검색은 영향 없음.
- **적용**: phase 명세는 `tasks/plan012-skills-korean-and-cleanup/`. depends_on: plan010(skills 추상화 완료) + plan011(runner TS 마이그).

### 2. AGENTS.md ADR 카운트 갱신

`career-os/AGENTS.md`의 `ADR-001~024` → `ADR-001~025`.

루트 `AGENTS.md`(career-os 외부)는 카운트 표기 없음 — 변경 없음.

### 3. code-architecture.md skill 트리 갱신

`career-os/skills/` 트리에서 `fos-study-pack/` 항목 제거. `study-pack-writer/` 항목 안에 "자연어 요청 라우팅 (옛 fos-study-pack 흡수, plan012)" 1줄 코멘트 추가.

### 4. prd.md 변경 최소

prd.md에서 fos-study-pack 언급 영역(미연결/보류 항목)에서 제거. dispatch 명령 표는 영향 없음 — fos-study-pack은 dispatcher에 wire-up 안 됐었음.

## 검증 명령

```bash
# 1. ADR-025 추가 + 위치 맨 뒤
grep -q '^## ADR-025 —' career-os/docs/adr.md
LAST=$(grep '^## ADR-' career-os/docs/adr.md | tail -1)
echo "$LAST" | grep -q 'ADR-025' || { echo "PHASE_FAILED: ADR-025 위치"; exit 1; }

# 2. AGENTS.md ADR 카운트
grep -q 'ADR-001~025' career-os/AGENTS.md

# 3. ADR-025 본문 ≤35 lines + 코드 블록 0
LINES=$(awk '/^## ADR-025 —/,EOF' career-os/docs/adr.md | wc -l)
[ "$LINES" -le 35 ] || { echo "PHASE_FAILED: ADR-025 비대 $LINES > 35"; exit 1; }
[ "$(awk '/^## ADR-025 —/,EOF' career-os/docs/adr.md | grep -c '```')" = "0" ]

# 4. code-architecture.md에 fos-study-pack 트리 항목 제거됨 (단 history 보존용 ADR 인용은 OK)
[ "$(grep -c 'fos-study-pack/' career-os/docs/code-architecture.md)" -le 1 ]

# 5. prd.md 미연결 항목에서 fos-study-pack 제거
[ "$(grep -c 'fos-study-pack' career-os/docs/prd.md)" -le 1 ]
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

```
docs(career-os): plan012 ADR-025 + 5문서 갱신 (skills 정리 + 한글화 결정)

- ADR-025 본문 (5섹션, 코드 명세 없이)
- AGENTS.md ADR 카운트 ADR-001~024 → ADR-001~025
- code-architecture.md skill 트리에서 fos-study-pack 제거 + writer 흡수 코멘트
- prd.md 미연결/보류 항목에서 fos-study-pack 제거
```

## 범위 외

- 실제 fos-study-pack 폴더 제거 + 자연어 라우팅 흡수(phase-02).
- 6 SKILL.md 한글화(phase-03).
