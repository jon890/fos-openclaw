# 오늘 작업 기준 현재 유효한 상태 정리

## 1. 더 이상 깊게 보지 않는 축
- Discord native skill UX 문제는 현재 실사용상 충분히 잘 동작한다고 판단한다.
- `/fos_study_pack`, `/study-pack`의 표면 UX는 더 파고들기보다 다른 가치 높은 작업에 우선순위를 둔다.

## 2. 현재 유효한 study-pack 방향
study-pack은 더 이상 단순 새 문서 생성기가 아니다.
현재 유효한 방향은 다음과 같다.
- 기존 문서 확인
- 관련 사례 문서 확인
- Claude가 문서 전략 판단
- 최종 문서 전체를 Claude가 작성
- 오케스트레이터는 실행/검증/commit/push/알림 담당

## 3. 현재 지원하는 문서 전략
maintainer 흐름에서 다음 액션 모델을 지원한다.
- `create-new`
- `update-existing`
- `augment-existing`
- `create-bridge`

이 네 가지가 앞으로 study-pack 오케스트레이션의 기본 모델이다.

## 4. 알림 정책
study-pack 알림은 바깥 exec 래퍼가 아니라 `run_now.sh study-pack` 공통 진입점이 책임지는 방향으로 정리했다.
즉 시작/완료/실패 알림은 runner 계층에서 일관되게 처리하는 것이 현재 기준이다.

## 5. 소스 오브 트루스 분리
현재 유효한 구조는 다음과 같다.
- `fos-openclaw` = 오케스트레이션/자동화 소스 오브 트루스
- `fos-study` = 콘텐츠/문서 작성 규칙 소스 오브 트루스

### fos-openclaw가 담당하는 것
- user-facing skill
- runner / resolver / maintainer
- cron / Discord 알림 / artifact tracking
- learn docs / 운영 구조

### fos-study가 담당하는 것
- 실제 게시 markdown 문서
- `CLAUDE.md` 기반 작성 규칙
- `.claude/skills/*` 기반 문서 작성/분석 규칙
- 폴더 배치, 민감 정보, 문체 기준

## 6. 규칙 흡수 상태
`career-os`의 `study-pack-writer`와 `study-pack-maintainer`는 이제 `fos-study` 기반 작성/유지보수 규칙 reference를 prompt에 포함하는 방향으로 강화되었다.

## 7. fos-openclaw 상태
- GitHub repo 연결 완료
- 로컬 clone 완료
- orchestration skeleton 첫 commit/push 완료
- 이제 git 추적 가능한 소스 오브 트루스의 시작점이 마련되었다.

## 8. 다음 우선순위
다음으로 가치가 높은 일은 문서 정리 체계를 만드는 것이다.
즉 오래된 learn/decision 문서, 의미가 약해진 운영 노트, 중복 문서를 주기적으로 점검할 수 있는 `docs-audit` skill이 필요하다.
