# 다음 단계 — fos-openclaw 소스 오브 트루스화

## 현재 상태
- career-os 쪽 생성/유지보수 스킬은 실전 검증이 어느 정도 끝났다.
- fos-study의 `CLAUDE.md` 규칙 일부를 reference로 흡수하기 시작했다.
- user-facing skill `fos-study-pack`도 OpenClaw workspace skill로 등록되었다.

## 다음 큰 단계
`fos-openclaw`를 오케스트레이션/자동화 소스 오브 트루스로 삼으려면 다음이 필요하다.

### 1. 관리 대상 명확화
fos-openclaw에 넣을 우선 대상:
- study-pack-writer
- study-pack-maintainer
- experience-question-bank-writer
- interview-master-writer
- fos-study-pack bridge skill
- 관련 config / scripts / docs/learn

### 2. 얇은 브리지 유지
OpenClaw workspace 쪽 skill은 최소한의 user-facing bridge만 유지한다.
실행 본체는 fos-openclaw(or career-os) 쪽 스크립트를 호출한다.

### 3. 점진 이전
한 번에 전부 옮기지 말고,
- reference 규칙 흡수
- skill 소스 정리
- repo 생성/연결
- sync 방식 정리
순서로 진행한다.

## 추천 첫 실무 단계
- fos-openclaw repo 로컬 클론/초기 구조 확인
- career-os 내 핵심 skill 디렉터리들을 어떤 트리로 옮길지 설계
- OpenClaw workspace skill과의 관계(복사/심볼릭/동기화 스크립트) 결정
