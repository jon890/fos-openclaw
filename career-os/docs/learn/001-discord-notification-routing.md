# 001. Discord notification routing

## 문제 상황

문서 생성 시작/완료/실패 알림을 Discord 채널에 보내려고 했는데, `sessions_send` 경로가 실제 채널 알림처럼 보이지 않았다.

## 결론

Discord 채널 알림은 `sessions_send`보다 `openclaw message send --channel discord --target channel:<id>` direct send를 우선 사용한다.

## 언제 다시 읽을까

- Discord 채널로 운영 알림을 보내야 할 때
- 세션 전송과 채널 direct send가 헷갈릴 때
- cron/manual 알림 경로를 공통화할 때

## 배운 점

- `sessions_send`는 visible channel direct-send라기보다 session injection처럼 동작할 수 있다.
- `sessions_send` timeout은 전달 실패보다 응답 대기 timeout일 수 있다.
- 실제 Discord 채널 전송 확인은 `openclaw message send` CLI가 훨씬 직접적이고 검증 가능하다.

## 검증된 명령 예시

```bash
openclaw message send \
  --channel discord \
  --target channel:1492521172099666021 \
  --message "[테스트] OpenClaw CLI로 Discord 채널 직접 전송 확인 중입니다."
```

## 운영 패턴

- 시작 알림 전송
- 실제 생성 실행
- 성공 시 완료 알림 전송
- 실패 시 실패 알림 전송

같은 direct-send 경로를 유지한다.
