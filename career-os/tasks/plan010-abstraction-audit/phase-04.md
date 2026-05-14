# Phase 4 — fos-study git operation 추상화 → _shared/lib/fos_study_git.ts

## 목표

`sources/fos-study/`에 대한 git pull · commit · push 패턴 4 runner 반복을 `_shared/lib/fos_study_git.ts`로 추출. study_pack_publish.ts(phase-03)와 다른 fos-study commit runner들이 같은 함수를 호출하도록.

## 의존성 / 가정

- phase-03 완료 — study_pack_publish.ts 신설됨.
- working tree clean.

## 작업

### 1. `_shared/lib/fos_study_git.ts` 신설

기본 API:

- `ensureRepo({sourceDir, remoteUrl})` — clone 또는 fetch + pull.
- `commitFile({sourceDir, relativePath, contents, message, prefix})` — 파일 쓰기 + commit (ADR-005 메시지 규약).
- `push({sourceDir, branch})` — push, 실패 시 비-0 + stderr (silent 금지).

shebang `#!/usr/bin/env bun` + import 가능 모듈.

옛 inline git 명령은 `study_pack_publish.ts` 안에서 새 모듈 호출로 교체. 4 runner(study-pack-writer · maintainer · batch · live-coding-dispatch — fos-study-pack 포함 5개도 phase-03 흐름 통과)는 자동으로 본 모듈 의존.

### 2. ADR-005 메시지 규약 보존

commit message 형식:
- `docs(<domain>): add|update draft <topic> study pack` — study-pack용.
- question-bank / master 등은 별도 prefix.

`fos_study_git.ts`의 `commitFile`의 `prefix` 인자가 이 분기를 처리.

### 3. push 실패 silent 금지

`sources/fos-study` push 실패 시 caller가 알 수 있도록 비-0 exit + stderr 에러 메시지. AGENTS.md 운영 원칙 따라 표면화.

## 검증 명령

```bash
# 1. _shared/lib/fos_study_git.ts 신설
test -f _shared/lib/fos_study_git.ts
test -x _shared/lib/fos_study_git.ts
bun --no-install build --target=bun _shared/lib/fos_study_git.ts --outdir=/tmp/plan010 >/dev/null 2>&1

# 2. study_pack_publish.ts가 fos_study_git.ts import 또는 호출
grep -q 'fos_study_git' _shared/lib/study_pack_publish.ts \
  || { echo "PHASE_FAILED: study_pack_publish가 fos_study_git 미호출"; exit 1; }

# 3. 옛 inline git 명령 잔재 — runner 안 'git -C.*sources/fos-study' 0
HITS=$(grep -lE 'git -C.*sources/fos-study' career-os/scripts/*/run_*.sh 2>/dev/null)
[ -z "$HITS" ] || { echo "PHASE_FAILED: inline git 잔재"; echo "$HITS"; exit 1; }
```

검증 실패 시 `echo 'PHASE_FAILED: <식>' && exit 1`.

## 커밋

```
feat(_shared): fos-study git operation 추상화 → _shared/lib/fos_study_git.ts

- ensureRepo / commitFile / push API
- study_pack_publish.ts가 본 모듈 호출
- 4 runner의 inline git 명령 제거
- push 실패 silent 금지 (AGENTS.md 운영 원칙)
```

## 범위 외

- update_artifacts upsert 흐름 (study_pack_publish 안에서 처리).
- 다른 git 저장소(career-os 본체 등) 추상화 (별도 plan).
