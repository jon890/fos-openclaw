# Learn Index

짧게 보고 필요한 문서만 빠르게 여는 포인터 문서입니다.

## 언제 무엇을 읽을까

- Discord 알림이 안 간다, 세션 전송과 direct send가 헷갈린다
  - `001-discord-notification-routing.md`
- 같은 `fos-study` repo 작업이 서로 충돌한다, git push/pull 꼬임이 난다
  - `002-fos-study-git-sequencing.md`

## 운영 규칙 요약

- Discord 채널 상태 알림은 `sessions_send`가 아니라 `openclaw message send`를 우선 사용한다.
- `fos-study`에 쓰는 생성 작업은 가능한 한 순차 실행한다.
- 시작, 완료, 실패 알림은 같은 direct-send 경로로 통일한다.

## 문서 추가 규칙

- 파일명은 `NNN-topic-name.md` 형식 사용
- 첫머리에 항상 다음 3가지를 짧게 적기
  - 문제 상황
  - 결론
  - 언제 이 문서를 다시 읽어야 하는지
