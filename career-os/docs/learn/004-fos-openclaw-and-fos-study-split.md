# fos-openclaw / fos-study 역할 분리 구조안

## 결정

앞으로는 다음 두 축으로 역할을 분리한다.

### 1. fos-openclaw
오케스트레이션과 자동화의 소스 오브 트루스.

관리 대상:
- OpenClaw user-facing skills
- career-os runner / resolver / maintainer
- study-pack orchestration logic
- question-bank / master-playbook orchestration
- cron / Discord notification / artifact tracking
- 운영 learn docs / ADR / sync script

### 2. fos-study
콘텐츠와 문서 작성 규칙의 소스 오브 트루스.

관리 대상:
- 실제 게시 대상 markdown 문서
- `CLAUDE.md` 기반 문서 작성 규칙
- `.claude/skills/*` 기반 글쓰기/분석 규칙
- 폴더 배치 기준
- 민감 정보 제거 기준
- 문체 / 회고 / 코드 인용 수위 기준

## 원칙

- 문서 생성 자동화는 fos-openclaw가 담당한다.
- 문서 작성 규칙과 품질 기준은 fos-study를 따른다.
- career-os 쪽 생성 스킬은 문서 생성 전에 fos-study의 `CLAUDE.md`를 참조하는 방향으로 표준화한다.
- 실행 로직과 콘텐츠 규칙을 한 repo에 섞지 않는다.

## 추천 구조

### fos-openclaw 쪽에 둘 것
- `skills/fos-study-pack/`
- `career-os/skills/study-pack-writer/`
- `career-os/skills/study-pack-maintainer/`
- `career-os/skills/experience-question-bank-writer/`
- `career-os/skills/interview-master-writer/`
- 관련 config / scripts / learn docs

### fos-study 쪽에서 참조할 것
- `CLAUDE.md`
- `.claude/skills/blog-post-writer/SKILL.md`
- `.claude/skills/job-analyzer/SKILL.md`
- `.claude/skills/resume-writer/SKILL.md`

## 즉시 실행할 첫 단계

1. fos-study 작성 규칙을 career-os의 reference 문서로 흡수할 파일을 만든다.
2. study-pack 생성 경로가 생성 전 `fos-study/CLAUDE.md`를 참조하도록 점진적으로 강화한다.
3. 이후 fos-openclaw repo를 소스 오브 트루스로 만들고 runner/skill을 그쪽에서 관리한다.
