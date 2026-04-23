# fos-openclaw 대상 트리 초안

## 목표
`fos-openclaw`를 오케스트레이션/자동화 소스 오브 트루스로 만들기 위한 1차 대상 트리를 정리한다.

## 우선 이관 대상

### user-facing skill
- `skills/fos-study-pack/`

### orchestration skills
- `career-os/skills/study-pack-writer/`
- `career-os/skills/study-pack-maintainer/`
- `career-os/skills/experience-question-bank-writer/`
- `career-os/skills/interview-master-writer/`
- `career-os/skills/cj-oliveyoung-java-backend-prep/`

### config / state-like templates
- `career-os/config/study-pack-topics.json`
- `career-os/config/study-pack-maintainer-topics.json`
- `career-os/config/experience-question-bank-topics.json`
- `career-os/config/interview-master-topics.json`
- `career-os/config/live-coding-seed-pool.json`

### docs
- `career-os/docs/learn/`
- 필요시 `career-os/docs/decisions/` 중 오케스트레이션 관련 문서

## 추천 배치

```text
fos-openclaw/
├── skills/
│   └── fos-study-pack/
├── career-os/
│   ├── skills/
│   │   ├── study-pack-writer/
│   │   ├── study-pack-maintainer/
│   │   ├── experience-question-bank-writer/
│   │   ├── interview-master-writer/
│   │   └── cj-oliveyoung-java-backend-prep/
│   ├── config/
│   └── docs/
│       └── learn/
```

## 유지 원칙
- `sources/fos-study` 자체는 이 repo의 관리 대상이 아니다.
- 게시물 markdown은 계속 fos-study repo가 소스 오브 트루스다.
- fos-openclaw는 생성 로직 / 실행 규칙 / skill 인터페이스만 관리한다.
- OpenClaw workspace 쪽 skill은 얇은 bridge로 두고, 실제 본체는 fos-openclaw를 바라보게 한다.

## 첫 실무 단계
1. fos-openclaw 로컬 클론
2. 위 디렉터리 구조 skeleton 생성
3. 핵심 skill 1개(`fos-study-pack`)부터 옮기거나 동기화 경로 확정
4. current career-os와의 관계를 복사/동기화/참조 중 하나로 결정
