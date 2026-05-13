# Common Pitfalls — ai-nodes plan-and-build

task / phase 파일 작성 직후 self-check. critic 또는 verify 단계에서 반복 지적되는 패턴을 누적한다. 시간이 갈수록 두꺼워지고 critic이 할 말은 줄어든다.

축적 규칙:

- 새 사고 타입 발견 시 해당 § 에 **패턴 한 줄 + 실측 명령 + self-check** 추가.
- 같은 사고 재발 시 패턴 강화 (예시 / 체크 엄격화).
- "왜 이 가드가 필요한지" 1줄 단서는 반드시 — 미래 AI 가 의도 모르고 우회하지 않도록.
- 사고 사례는 1개로 충분, 복수 나열 금지.

| § | 카테고리 | 호출 시점 |
|---|---|---|
| § 1 | plan 작성 (critic 회피) | task / phase 파일 작성 직후 self-check |
| § 2 | ai-nodes 워크스페이스 규약 위반 | 같은 시점 |
| § 3 | docs / data 라우팅 위반 | 같은 시점 |
| § 4 | dispatcher / runner 경계 위반 | 같은 시점 |
| § 5 | git 운영 위반 | 같은 시점 |

---

## § 1. plan 작성 (critic 회피)

### 1-1. 수치 추측 (파일 수 / 줄 수)

**증상**: "약 30개 파일", "100줄 줄어듦" 같은 수치를 실측 없이 적음.
**왜**: critic 이 가장 먼저 검증하는 것은 phase 약속 수치 ↔ 실제 코드 일치 여부. 추측은 즉시 REVISE 사유.

```bash
# 실측 — phase 작성 전에 돌려서 정확한 수치 확보
find <path> -name '*.py' | wc -l
wc -l <file>
git ls-files <pattern> | xargs wc -l
```

**Self-check**:
- 모든 수치 옆에 grep/find/wc 명령을 같이 적어 두었나?
- 추정치(`~`, `약`)를 쓸 거면 plan 안에 명시했나?

### 1-2. 성공 기준이 "동작한다" 수준

**증상**: phase 성공 기준이 "정상 동작 확인" 같이 모호한 동사로 끝남.
**왜**: 자동 실행 하네스(run-phases.py)는 명령어 종료 코드를 본다. 사람이 "동작한다"를 보고 판정하는 phase는 자동화 불가.

**Self-check**:
- 성공 기준이 한 줄 실행 명령으로 표현되는가? (`bash -n script.sh`, `python3 -m py_compile file.py`, `[ -f path/to/output ]` 등)
- exit 0 = pass, 그 외 = fail로 단정할 수 있는가?

### 1-3. phase 간 컨텍스트 공유 가정

**증상**: phase-02가 phase-01에서 결정된 변수를 "위에서 결정했다"고 가정.
**왜**: run-phases.py는 phase마다 새 Claude 프로세스. 이전 대화 없음. **phase 프롬프트는 자기완결적**이어야 한다.

**Self-check**:
- 각 phase-NN.md 첫 줄부터 읽어서 다른 phase 안 보고 실행 가능한가?
- 이전 phase의 출력 파일을 사용한다면 정확한 경로를 phase 본문에 명시했나?

---

## § 2. ai-nodes 워크스페이스 규약 위반

### 2-1. 다른 워크스페이스 자산 참조

**증상**: career-os task가 `apartment/`, `stock-investment/`, `travel/` 경로를 import / read / write.
**왜**: ai-nodes/CLAUDE.md 워크스페이스 격리 원칙. 다른 워크스페이스는 별도 세션에서 독립적으로 다룬다.

**Self-check**:
- phase 파일 안의 모든 경로가 `<workspace>/` 또는 `_shared/bin/` 또는 `skills/`로 시작하는가?
- 다른 워크스페이스 디렉터리명이 phase 본문에 등장하는가? 등장하면 정당화 ADR 또는 제거.

### 2-2. config 파일을 어디서나 새로 만든다

**증상**: phase가 `<workspace>/config/<new>.json`을 새로 만들지만 docs/data-schema.md에 스키마 명세 없음.
**왜**: docs/data-schema.md가 config 파일의 단일 출처. drift 방지.

**Self-check**:
- 새 config 도입 시 `docs/data-schema.md`에 스키마 섹션 추가가 phase 안에 포함됐나? (또는 docs-first 커밋 단계에서 처리됐나?)

---

## § 3. docs / data 라우팅 위반

### 3-1. 데이터 파일을 docs/ 에 둠

**증상**: phase가 `<workspace>/docs/<some>.json` 또는 `<workspace>/docs/<some>.jsonl`을 만든다.
**왜**: ai-nodes 정책 — **docs/ 는 의사결정·학습 누적**, **데이터는 반드시 `data/`** (ADR-015).

**Self-check**:
- phase 산출물이 `*.json`, `*.jsonl`, `*.csv` 등 데이터 형식인가? → `<workspace>/data/` 아래 경로로 강제.
- phase 산출물이 의사결정·회고·이력 마크다운인가? → `<workspace>/docs/{adr,learn,hand-off}` 아래.

### 3-2. 새 ADR을 개별 파일로 만든다

**증상**: phase가 `<workspace>/docs/decisions/NNN-<topic>.md` 새 파일을 만든다.
**왜**: 통합 후 `docs/adr.md` 단일 파일에 누적 (5문서 컨벤션). 개별 ADR 파일 신설 금지. legacy `decisions/` 디렉터리는 history 보존용.

**Self-check**:
- 새 결정을 기록한다면 `<workspace>/docs/adr.md` 맨 아래에 append하는 형태인가?

### 3-3. docs 갱신을 phase 안에서 한다

**증상**: phase-04가 docs/code-architecture.md를 수정한다.
**왜**: docs-first 원칙 — task 생성 *전*에 별도 커밋. phase에서 docs를 또 만지면 history가 섞이고 task 실패 시 docs도 같이 잃는다.

**Self-check**:
- 모든 docs 변경이 task 생성 전 별도 커밋에 들어가 있는가?
- phase 본문에 `docs/*.md` 파일 수정이 있다면 그 phase는 의도된 docs-update phase인가? 아니면 빼야 한다.

---

## § 4. dispatcher / runner 경계 위반

### 4-1. dispatcher 우회 직접 호출

**증상**: phase가 `bash <workspace>/skills/*/scripts/run_*.sh`를 직접 호출한다.
**왜**: `run_now.sh` 우회 시 `track_task.sh` 래핑이 빠져 logs/task-runs.jsonl 기록 누락 + Discord 알림 빠짐 + 잠금 회피.

**Self-check**:
- task가 실행하는 명령이 `bash <workspace>/skills/cj-oliveyoung-java-backend-prep/scripts/run_now.sh <command>` 형태인가?
- 직접 호출이 필요하면 phase에 정당화 한 줄 명시.

### 4-2. 새 runner 추가하면서 claude_persist_usage 호출 누락

**증상**: 새 runner가 `claude --print --output-format json`을 호출하지만 `claude_lib.sh`의 `claude_persist_usage`를 안 부른다.
**왜**: ADR-014. usage 전파 누락 시 logs/task-runs.jsonl의 cost_usd / model이 null로 기록되어 비용 추적 불가.

**Self-check**:
- 새 runner의 `attempt()` 함수에 `claude_persist_usage "$RAW_RESULT_JSON"`이 `run_once` 직후 (extractor 호출 전)에 있는가?
- runner 상단에 `source "$HOME/ai-nodes/_shared/bin/claude_lib.sh"`가 있는가?

### 4-3. notify는 직접 webhook 부르기

**증상**: phase가 curl로 Discord webhook을 직접 부른다.
**왜**: 알림은 `<workspace>/skills/*/scripts/notify_discord.sh` 단일 진입점으로 통일 (ADR-008). 각 task의 webhook URL은 `<workspace>/config/.env`에서.

**Self-check**:
- 알림이 필요하면 `<workspace>/skills/cj-oliveyoung-java-backend-prep/scripts/notify_discord.sh` 또는 run_now.sh의 `run_tracked` 헬퍼 경유로?

---

## § 5. git 운영 위반

### 5-1. force push / hooks skip

**증상**: phase가 `--no-verify`, `--force`, `git push --force`를 시도.
**왜**: ai-nodes/CLAUDE.md의 git 안전 규약. 명시적 user 승인 없이 destructive 금지.

**Self-check**:
- phase 안에 `--no-verify`, `--force`, `--no-edit`, `--no-gpg-sign`이 있는가? 있으면 정당화하거나 제거.

### 5-2. 한 phase에서 여러 무관한 커밋

**증상**: phase가 docs 수정 + 코드 수정 + 새 ADR을 한 커밋에 묶음.
**왜**: 변경 history가 섞이고 revert 어려움. docs-first 원칙 위반.

**Self-check**:
- phase가 생성하는 커밋들이 각각 단일 관심사인가?
- 커밋 메시지 헤더가 conventional commits 형식인가? (`<type>[(scope)]: <subject>`)

### 5-3. sources/fos-study에 임시 변경

**증상**: phase가 `sources/fos-study/`에 직접 git commit한다.
**왜**: fos-study는 외부 동기 저장소. study-pack-class runner들이 검증된 출력을 올리는 경로일 뿐, task가 임의로 만지면 안 된다.

**Self-check**:
- phase 안의 `git -C sources/fos-study ...` 작업이 study-pack-class runner를 거치는가? 아니면 명시적 정당화.

---

## 변경 이력

- 2026-05-13: 초안 — fos-blog `_shared/common-pitfalls.md`의 §1 패턴을 베이스로, ai-nodes 워크스페이스 규약(§2~§5)을 추가.
