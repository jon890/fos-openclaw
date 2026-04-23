# 002. fos-study git sequencing

## 문제 상황

여러 생성 작업이 같은 `fos-study` repo에서 동시에 pull/push/commit 하면서 git 충돌이 날 수 있다.

## 결론

`fos-study`에 쓰는 작업은 가능한 한 순차 실행하고, 같은 시간대의 생성 cron도 동시 실행을 피한다.

## 언제 다시 읽을까

- 여러 study-pack/question-bank/job을 같은 아침 시간대에 돌릴 때
- git fast-forward 오류가 다시 날 때
- 같은 repo에 여러 자동화가 동시에 쓰려고 할 때

## 배운 점

- 동일 repo를 대상으로 하는 생성 작업은 병렬성보다 일관성이 중요하다.
- 문서 생성 후 즉시 commit/push 하는 구조라면, 충돌 가능성이 더 커진다.
- 아침 자동화는 순서와 역할을 분리하는 쪽이 안전하다.

## 대표 오류

- `fatal: Cannot fast-forward to multiple branches.`

## 운영 규칙

- 같은 repo 대상 job은 순차 실행
- 생성 성공 후 artifact history 갱신
- question bank는 기존 문서 업데이트, study-pack/live-coding은 새 문서 우선
