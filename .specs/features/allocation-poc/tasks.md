# 롯데면세점 재고배분 PoC Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, the walk, check_proofs, the Verifier and the screens sub-agent).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

이 문서는 설계 산출물이다. 구현(Execute)은 이번 범위가 아니며, 소스와 데이터를 받고 고객 확인 사항의 답을 받은 뒤 시작한다.

---

**Design**: `.specs/features/allocation-poc/design.md`
**Status**: Approved
**Approved**: 2026-11-17 - user: "승인할게. 다음 작업 이어서 진행해줘"
**Revised**: 2026-11-23 - user: "모두 너에게 맡길게. 가장 최적의 방안을 검토해서 작업 진행해줘" — 고객 자료 수령 반영 (기준 입력, 대상 카테고리, 파라미터 16개, 공헌이익 선택 입력). 근거는 `docs/reproduction-report.md`
**Revised**: 2026-11-24 - user: "PoC 구현 범위에 넣어서 전부 고쳐줘" — 이상치 질문·답변과 재테스트(QA-01) 추가: Phase 10, 작업 9개, 확인 항목 12개
**Build**: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep`
**Run unit**: `pytest tests/unit -v`
**Run api**: `pytest tests/api -v`
**Run azure**: `pytest tests/azure -v`

읽는 법: 작업은 T번호, 확인 항목은 C번호다. 확인 항목 하나가 명세의 수용 기준 하나에 대응하고, `Proof`는 그것을 증명하는 테스트다. 파일 경로는 새로 만들 프로젝트 저장소 기준이다.

작업 88개, 단계 13개, 확인 항목 105개.

---

## Test Coverage Matrix

> Generated from codebase, project guidelines, and spec - confirm before Execute. Guidelines found: none - strong defaults applied. 이 저장소에는 대상 코드와 기존 테스트가 없다. 테스트 도구는 명세의 가정(pytest)을 따른다. 아래 명령은 제안이며 프로젝트 저장소를 만들 때 확정한다.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| 실행 틀 (`runner/*.py`): 입력 검증, 업무 규칙, 실행, 기록 | unit | 수용 기준과 1:1, 예외 상황 전부 | `tests/unit/test_*.py` | `pytest tests/unit -v` |
| 입력 구성 (`prep/*.py`) | unit | 수용 기준과 1:1, 기준 입력 표본 대조 | `tests/unit/test_*.py` | `pytest tests/unit -v` |
| 프로그램 등록 검사 (`api/services/code_check.py`) | unit | 수용 기준과 1:1 | `tests/unit/test_code_check.py` | `pytest tests/unit -v` |
| 관리 API 서비스·경로·화면 (`api/services`, `api/routes`, `api/auth.py`, `api/templates`) | integration | 경로마다 정상, 예외, 거절. 시험용 DB와 가짜 저장소·실행기 사용 | `tests/api/test_*.py` | `pytest tests/api -v` |
| Azure 호출과 정의 (`api/clients`, `infra/*.bicep` 중 권한·네트워크·실행기·웹 앱·전체 배포, `adf/`) | integration | 배포된 PoC 환경에서 격리, 동시 실행, 로그인, 수집, 기준 입력 일치 | `tests/azure/test_*.py` | `pytest tests/azure -v` |
| 설정·정의만 있는 파일 (`pyproject.toml`, 기준 데이터 목록, 기준 컬럼, 보고서, `api/repo`, `api/app.py`, 저장소·DB·Data Factory·Logic Apps 정의) | none | - (build gate only) | - | build gate only |

## Gate Check Commands

> Generated from codebase - confirm before Execute. 저장소에 기존 명령이 없어 제안값이다.

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | unit 테스트만 있는 작업 뒤 | `pytest tests/unit -v` |
| Full | 관리 API 테스트가 있는 작업 뒤 | `pytest tests/unit tests/api -v` |
| Build | 단계가 끝났을 때, Azure 환경 테스트가 있는 작업, 설정·정의만 있는 작업 뒤 | `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v` |

---

## Execution Plan

단계는 순서대로 진행한다. 화살표는 같은 단계 안의 선후 관계이고, 화살표가 없는 작업은 그 단계 안에서 다른 작업을 기다리지 않는다.

### Phase 1: 기반과 현행 재현

```
T1 → T2
T2 → T3
T1 → T4
```

### Phase 2: 실행 틀

```
T5 → T7
T6 → T7
T5 → T8
T7 → T9
T8 → T9
T5 → T10
```

### Phase 3: 입력 검증

```
T11 → T13
T12 → T13
T13 → T14
T14 → T15
```

### Phase 4: 업무 규칙과 실행 엮기

```
T16 → T17
T17 → T18
T18 → T19
T19 → T20
T20 → T21
T21 → T22
T22 → T23
```

### Phase 5: 입력 구성

```
T25 → T26
T24 → T28
T26 → T28
T27 → T28
```

### Phase 6: Azure 환경

```
T29 → T30
T29 → T31
T30 → T32
T31 → T32
T33 → T34
T32 → T35
T34 → T35
```

### Phase 7: 기록과 API 기반

```
T36 → T37
T37 → T41
T38 → T41
단독: T39, T40
```

### Phase 8: 검증 실행 서비스

```
T43 → T45
T44 → T45
T45 → T46
T46 → T47
T45 → T48
T46 → T49
단독: T42
```

### Phase 9: 검증 실행 경로와 화면

```
T55 → T56
T55 → T57
T55 → T58
T55 → T59
단독: T50, T51, T52, T53, T54
```

### Phase 10: 이상치 질문·답변과 재테스트

```
T62 → T63
T63 → T64
T64 → T65
T61 → T65
T65 → T66
T66 → T67
T67 → T68
단독: T60
```

### Phase 11: 운영 실행과 승인 서비스

```
T69 → T71
T71 → T72
T69 → T73
T73 → T74
T74 → T75
단독: T70
```

### Phase 12: 운영 경로와 화면

```
T76 → T78
T77 → T78
단독: T79, T80, T81
```

### Phase 13: 자동 수집, 자동 시작, 알림, 측정

```
T82 → T83
T83 → T84
T86 → T87
단독: T85, T88
```

---

## Task Breakdown

### Phase 1: 기반과 현행 재현

#### T1: 프로젝트 설정 파일

**What**: 테스트·코드 검사 도구와 라이브러리 버전을 고정한 프로젝트 설정을 만든다
**Where**: `pyproject.toml`
**Depends on**: None
**Reuses**: 없음
**Requirement**: RUN-01

**Done when**:

- [ ] pytest와 ruff가 설정되어 `ruff check .`이 통과한다
- [ ] pandas 3.0.5, numpy 2.5.3, openpyxl 3.1.5로 버전이 고정되어 있다
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`

**Tests**: none
**Gate**: build

---

#### T2: 기준 데이터 목록

**What**: 고객이 준 기준 입력과 현행 PC 결과 파일의 이름·행 수·내용 지문 목록을 만든다
**Where**: `tests/fixtures/baseline_manifest.json`
**Depends on**: T1
**Reuses**: 고객 제공 기준 입력·결과 폴더 (후보 2026-11-18)
**Requirement**: RUN-01

**Done when**:

- [ ] 기준 입력 9종과 PC 결과 파일 전부, 카테고리를 뺀 시험 입력이 목록에 있다
- [ ] 실데이터는 저장소에 넣지 않고 위치만 적는다
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`

**Tests**: none
**Gate**: build

---

#### T3: 현행 재현 확인 보고서

**What**: 현행 pipeline.py를 기준 입력으로 실행해 설계의 가정 6개를 확인하고 결과를 적는다 (2026-11-23 1차 작성. Linux와 PC 결과 일치만 미확인)
**Where**: `docs/reproduction-report.md`
**Depends on**: T2
**Reuses**: 고객 제공 pipeline.py, settings.json, CLAUDE.md
**Requirement**: RUN-01

**Done when**:

- [ ] 가정 6개(경로만 바꿔 실행됨, settings.json 주입, 날짜 고정 가능 여부, 두 번 실행한 결과가 같음, Linux 결과가 같음, 현행 결과가 규칙 5개를 통과함)마다 확인 결과와 근거가 있다 (5개 작성됨. Linux 결과 일치는 PC 결과 수령 후)
- [ ] 확인되지 않은 가정마다 설계에 주는 영향과 대응이 적혀 있다
- [ ] 전체 추출 입력의 실행 시간과 메모리 사용량이 적혀 있다
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`

**Tests**: none
**Gate**: build

---

#### T4: 실행 이미지

**What**: Python과 라이브러리 버전, 시간대, 제한 사용자를 고정한 실행 이미지를 정의한다
**Where**: `runner/Dockerfile`
**Depends on**: T1
**Reuses**: 없음
**Requirement**: RUN-01

**Done when**:

- [ ] 실행 환경이 Python 3.14.7, pandas 3.0.5, numpy 2.5.3, openpyxl 3.1.5, 시간대 Asia/Seoul이다 (C35)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_environment.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

### Phase 2: 실행 틀

#### T5: 실행 지시서 읽기

**What**: 실행 지시서를 읽고 필수 항목을 확인한다
**Where**: `runner/instruction.py`
**Depends on**: None
**Reuses**: 없음
**Requirement**: RUN-01

**Done when**:

- [ ] 필수 항목(실행 ID, 모드, 프로그램 버전, 파라미터, 입력 일자, 마스터 버전)이 빠진 지시서를 거절한다
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_instruction.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T6: 저장소 접근

**What**: 구역별 읽기·쓰기 기능과 테스트용 로컬 폴더 구현을 만든다
**Where**: `runner/storage.py`
**Depends on**: None
**Reuses**: 없음
**Requirement**: ISO-01

**Done when**:

- [ ] 입력 구역과 프로그램 구역에는 쓰기 기능이 없다
- [ ] 결과는 지시서의 모드에 맞는 구역(`test/` 또는 `prod/`)에만 쓴다
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_storage.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T7: 작업 폴더 구성

**What**: 입력 묶음, 마스터, 프로그램을 현행 INPUT 폴더와 같은 모양으로 놓는다
**Where**: `runner/workspace.py`
**Depends on**: T5, T6
**Reuses**: 현행 INPUT 폴더의 파일 이름 규칙
**Requirement**: MST-01

**Done when**:

- [ ] 실행은 종류별로 가장 최근 마스터 버전을 쓰고 그 버전이 실행 기록에 남는다 (C33)
- [ ] 올린 버전이 없는 마스터 종류는 그 파일 없이 실행하고 입력 검증 결과에 경고로 남는다 (C103)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_workspace.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T8: settings.json 생성

**What**: 지시서의 파라미터로 현행 settings.json을 만든다
**Where**: `runner/settings_file.py`
**Depends on**: T5
**Reuses**: 현행 settings.json의 키 이름
**Requirement**: PARAM-01

**Done when**:

- [ ] 실행 시점의 파라미터 16개 값 전체가 실행 기록에 사본으로 남는다 (C28)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_settings_file.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T9: 프로그램 실행

**What**: pipeline.py를 제한 사용자로, 시간 상한을 두고 실행한다
**Where**: `runner/engine.py`
**Depends on**: T7, T8
**Reuses**: 고객 pipeline.py (수정 없음)
**Requirement**: RUN-01

**Done when**:

- [ ] 프로그램이 오류로 끝나면 상태가 `실행오류`이고 로그 마지막 200줄이 저장된다 (C39)
- [ ] 실행이 30분을 넘으면 중단되고 상태 `실행오류`, 사유 `시간 초과`가 된다 (C40)
- [ ] 프로그램은 저장소 접근 권한이 없는 별도 사용자로 실행된다 (C70)
- [ ] 결과 파일 없이 정상 종료하면 상태 `실행오류`, 사유 `결과 없음`이 된다 (C104)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_engine.py`에 이 작업의 테스트 4개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T10: 실행 기록 작성

**What**: 실행의 상태와 결과를 한 파일로 쓴다
**Where**: `runner/record.py`
**Depends on**: T5
**Reuses**: 없음
**Requirement**: RUN-01

**Done when**:

- [ ] 실행 기록에 모드, 요청자, 프로그램 버전, 파라미터 사본, 입력 일자, 마스터 버전, 시작·종료 시각, 상태가 있다 (C42)
- [ ] 입력 검증 항목별 결과(통과, 경고, 실패)가 실행 기록에 저장된다 (C19)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_record.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

### Phase 3: 입력 검증

#### T11: 재고 기준 컬럼 등록

**What**: 기준 입력 합본 CSV의 72개 컬럼 이름을 순서대로 기준으로 등록한다
**Where**: `runner/baseline_columns.json`
**Depends on**: None
**Reuses**: 기준 입력 합본 CSV의 헤더
**Requirement**: VAL-01

**Done when**:

- [ ] 72개 컬럼 이름이 기준 입력 합본 CSV와 같은 순서로 들어 있다
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`

**Tests**: none
**Gate**: build

---

#### T12: 입력 검증: 필수 파일

**What**: 재고·판매예측·코드표 5종의 존재를 확인한다
**Where**: `runner/input_checks.py`
**Depends on**: None
**Reuses**: 현행 파일 이름 규칙
**Requirement**: VAL-01

**Done when**:

- [ ] 재고 스냅샷이나 판매예측 파일이 없으면 프로그램을 실행하지 않고 상태가 `입력실패`다 (C11)
- [ ] 코드표 5종 중 하나라도 없으면 프로그램을 실행하지 않고 상태가 `입력실패`다 (C12)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_input_checks.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T13: 입력 검증: 재고 컬럼

**What**: 재고 파일의 컬럼 이름과 순서를 기준과 대조한다
**Where**: `runner/input_checks.py` (수정)
**Depends on**: T11, T12
**Reuses**: c1의 기준 컬럼
**Requirement**: VAL-01

**Done when**:

- [ ] 재고 컬럼의 이름이나 순서가 기준 72개와 다르면 `입력실패`이고 다른 컬럼의 위치와 이름이 남는다 (C13)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_input_checks.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T14: 입력 검증: 카테고리와 점

**What**: 재고에 등록된 대상 카테고리와 10개 점이 모두 있는지 확인한다
**Where**: `runner/input_checks.py` (수정)
**Depends on**: T13
**Reuses**: 없음
**Requirement**: VAL-01

**Done when**:

- [ ] 등록된 대상 카테고리 중 없는 것이 있으면 `입력실패`이고 빠진 카테고리 이름이 남는다 (시험 입력: FOOD 제외) (C14)
- [ ] 10개 점 중 없는 점이 있으면 `입력실패`이고 빠진 점 이름이 남는다 (C15)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_input_checks.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T15: 입력 검증: 갱신 주기

**What**: 재고 1일, 판매예측 7일 초과를 모드에 따라 처리한다 (공헌이익은 파일이 있을 때만 35일)
**Where**: `runner/input_checks.py` (수정)
**Depends on**: T14
**Reuses**: 입력 묶음 명세서의 수집 시각
**Requirement**: VAL-01

**Done when**:

- [ ] 운영 실행에서 갱신 주기를 넘은 입력이 있으면 프로그램을 실행하지 않고 상태가 `확인대기`다 (C16)
- [ ] 검증 실행에서는 갱신 주기 초과를 경고로만 기록하고 실행을 계속한다 (C18)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_input_checks.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

### Phase 4: 업무 규칙과 실행 엮기

#### T16: 업무 규칙: 총량 보존

**What**: 결과 파일에서 규칙 `총량 보존`을 확인한다
**Where**: `runner/rules.py`
**Depends on**: None
**Reuses**: 고객 CLAUDE.md의 불변식 정의
**Requirement**: RULE-01

**Done when**:

- [ ] 배분 전후 총량이 다른 SKU가 있으면 `총량 보존`이 위반이고 위반 SKU 수가 남는다 (C44)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_rules.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T17: 업무 규칙: 최소보장

**What**: 결과 파일에서 규칙 `최소보장`을 확인한다
**Where**: `runner/rules.py` (수정)
**Depends on**: T16
**Reuses**: 고객 CLAUDE.md의 불변식 정의
**Requirement**: RULE-01

**Done when**:

- [ ] 양도 후 보유일수가 최소보장일수보다 작은 건이 있으면 `최소보장`이 위반이고 위반 건수가 남는다 (판정: 배분후 재고 < 내림(판매량 × 일수)) (C45)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_rules.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T18: 업무 규칙: 그룹 내 이동

**What**: 결과 파일에서 규칙 `그룹 내 이동`을 확인한다
**Where**: `runner/rules.py` (수정)
**Depends on**: T17
**Reuses**: 고객 CLAUDE.md의 불변식 정의
**Requirement**: RULE-01

**Done when**:

- [ ] 같은 양수도 그룹이 아닌 점 사이의 이동이 있으면 `그룹 내 이동`이 위반이고 위반 건수가 남는다 (C46)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_rules.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T19: 업무 규칙: 발송 한도

**What**: 결과 파일에서 규칙 `발송 한도`을 확인한다
**Where**: `runner/rules.py` (수정)
**Depends on**: T18
**Reuses**: 고객 CLAUDE.md의 불변식 정의
**Requirement**: RULE-01

**Done when**:

- [ ] 한 점이 내보낸 수량의 합이 보유 수량보다 크면 `발송 한도`가 위반이고 위반 건수가 남는다 (C47)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_rules.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T20: 업무 규칙: 전환 한도

**What**: 결과 파일에서 규칙 `전환 한도`을 확인한다
**Where**: `runner/rules.py` (수정)
**Depends on**: T19
**Reuses**: 고객 CLAUDE.md의 불변식 정의
**Requirement**: RULE-01

**Done when**:

- [ ] 전환 신청수량이 배치 가용수량보다 크면 `전환 한도`가 위반이고 위반 건수가 남는다 (C48)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_rules.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T21: 업무 규칙: 종합 판정

**What**: 규칙 5개의 결과로 실행 상태를 정한다
**Where**: `runner/rules.py` (수정)
**Depends on**: T20
**Reuses**: 없음
**Requirement**: RULE-01

**Done when**:

- [ ] 규칙 5개 중 하나라도 위반이면 실행 상태가 `규칙위반`이다 (C49)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_rules.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T22: 요약 건수

**What**: 결과 파일에서 요약 건수 5개를 뽑는다
**Where**: `runner/summary.py`
**Depends on**: T21
**Reuses**: 검토리포트 엑셀의 요약 시트
**Requirement**: RULE-01

**Done when**:

- [ ] 규칙을 모두 통과하면 상태가 `완료`이고 요약 건수 5개가 저장된다 (2026-11-18 입력 재실행: 13,887 / 45 / 43 / 4,780 / 2,162) (C50)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_summary.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T23: 단계 엮기

**What**: 지시서 읽기부터 실행 기록 쓰기까지 단계를 순서대로 돌린다
**Where**: `runner/main.py`
**Depends on**: T22
**Reuses**: b1~b6, c2~c12
**Requirement**: RUN-01

**Done when**:

- [ ] 정상 종료한 검증 실행의 결과 파일이 `test/<실행ID>/`에 현행 파일 이름으로 저장된다 (C36)
- [ ] 정상 종료한 운영 실행의 결과 파일이 `prod/YYYYMMDD/<실행ID>/`에 저장된다 (C77)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_main.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

### Phase 5: 입력 구성

#### T24: 고객 합본 스크립트 편입

**What**: 고객의 merge_excel_to_csv.py를 수정 없이 넣고 호출 경로를 만든다
**Where**: `prep/vendor/merge_excel_to_csv.py`
**Depends on**: None
**Reuses**: 고객 merge_excel_to_csv.py
**Requirement**: INPUT-01

**Done when**:

- [ ] 재고 카테고리별 엑셀을 올리면 합본 CSV 1개가 만들어진다 (기준 입력: 고객 PC 합본과 내용 지문이 같다) (C8)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_merge.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T25: 재고 컬럼 배치

**What**: 수집한 재고 원본을 기준 72개 컬럼 순서로 배치한다
**Where**: `prep/inventory_layout.py`
**Depends on**: None
**Reuses**: c1의 기준 컬럼
**Requirement**: INPUT-01

**Done when**:

- [ ] 기준 72개 컬럼을 만들 수 없으면 입력 묶음이 `실패`이고 빠진 컬럼 이름이 남는다 (C10)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_inventory_layout.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T26: 현행 형식으로 쓰기

**What**: 재고·판매예측·공헌이익·코드표를 현행 파일 이름과 형식으로 쓴다
**Where**: `prep/formats.py`
**Depends on**: T25
**Reuses**: 고객 PDF 2-1의 파일 형식
**Requirement**: INPUT-01

**Done when**:

- [ ] `input/YYYYMMDD/`에 기간계 입력(재고, 판매예측, 코드표 5종)이 현행 이름과 형식(재고 utf-8-sig, 코드표 cp949)으로 만들어진다 (C6)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_formats.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T27: 입력 묶음 명세서

**What**: 파일별 출처, 수집 시각, 행 수, 내용 지문을 명세서로 쓴다
**Where**: `prep/manifest.py`
**Depends on**: None
**Reuses**: 없음
**Requirement**: INPUT-01

**Done when**:

- [ ] 입력 묶음마다 파일별 출처, 수집 시각, 행 수, 내용 지문이 적힌 명세서가 있다 (C7)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_manifest.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T28: 입력 구성 엮기

**What**: 일자의 원본과 올린 파일로 입력 묶음을 만들고 상태를 정한다
**Where**: `prep/main.py`
**Depends on**: T24, T26, T27
**Reuses**: d1~d4
**Requirement**: INPUT-01

**Done when**:

- [ ] 매일 수집하지 않는 원천(판매예측)은 가장 최근 수집분이 그 일자 입력 묶음에 들어간다 (C5)
- [ ] 자동 수집되지 않는 원천의 파일을 올리면 입력 묶음에 들어가고 명세서의 출처가 `올린 파일`이다 (C9)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_prep_main.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

### Phase 6: Azure 환경

#### T29: 저장소 정의

**What**: 저장소와 구역 4개(입력, 프로그램, 운영 결과, 검증 결과)를 정의한다
**Where**: `infra/storage.bicep`
**Depends on**: None
**Reuses**: 없음
**Requirement**: ISO-01

**Done when**:

- [ ] 구역 4개가 만들어진다
- [ ] 프로그램 구역의 파일은 덮어쓸 수 없게 설정된다
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`

**Tests**: none
**Gate**: build

---

#### T30: 실행기 ID와 구역별 권한

**What**: 검증용·운영용 실행기 ID를 만들고 구역별 읽기·쓰기 권한을 준다
**Where**: `infra/identities.bicep`
**Depends on**: T29
**Reuses**: 없음
**Requirement**: ISO-01

**Done when**:

- [ ] 검증용 실행기가 운영 결과 구역이나 입력 구역에 쓰려고 하면 거절된다 (C68)
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`
- [ ] Test count: `tests/azure/test_isolation.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: build

---

#### T31: 네트워크와 외부 통신 차단

**What**: 실행기가 저장소 외의 주소로 나갈 수 없게 네트워크를 정의한다
**Where**: `infra/network.bicep`
**Depends on**: T29
**Reuses**: 없음
**Requirement**: ISO-01

**Done when**:

- [ ] 실행 중인 프로그램이 저장소 밖의 주소로 접속하려고 하면 차단된다 (C69)
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`
- [ ] Test count: `tests/azure/test_isolation.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: build

---

#### T32: 실행기 정의

**What**: 검증용·운영용 실행기와 입력 구성 실행기를 정의한다 (시간 상한 30분)
**Where**: `infra/jobs.bicep`
**Depends on**: T30, T31
**Reuses**: a4의 실행 이미지
**Requirement**: RUN-01

**Done when**:

- [ ] 두 실행이 같은 시각에 돌아도 각각 별도 컨테이너에서 실행되고 결과가 단독 실행과 같다 (C41)
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`
- [ ] Test count: `tests/azure/test_concurrency.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: build

---

#### T33: 기록 DB 정의

**What**: Azure SQL Database를 정의한다
**Where**: `infra/sql.bicep`
**Depends on**: None
**Reuses**: 없음
**Requirement**: HIST-01

**Done when**:

- [ ] DB가 만들어지고 관리 API의 ID만 접근할 수 있다
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`

**Tests**: none
**Gate**: build

---

#### T34: 웹 앱 정의

**What**: 관리 화면·API의 웹 앱과 사내 계정 로그인을 정의한다
**Where**: `infra/webapp.bicep`
**Depends on**: T33
**Reuses**: 없음
**Requirement**: AUTH-01

**Done when**:

- [ ] 로그인하지 않은 요청은 사내 계정 로그인 화면으로 보내진다 (C72)
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`
- [ ] Test count: `tests/azure/test_login.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: build

---

#### T35: 전체 배포 정의와 기준 입력 일치 확인

**What**: 모든 정의를 하나로 엮어 배포하고 기준 입력의 결과를 현행 PC와 대조한다
**Where**: `infra/main.bicep`
**Depends on**: T32, T34
**Reuses**: e1~e6, a2의 기준 데이터 목록
**Requirement**: RUN-01

**Done when**:

- [ ] 기준 입력과 운영 파라미터로 현행 pipeline.py를 실행한 결과가 현행 PC에서 같은 날 실행한 결과와 셀 단위로 같다 (C43)
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`
- [ ] Test count: `tests/azure/test_baseline.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: build

---

### Phase 7: 기록과 API 기반

#### T36: 기록 테이블 정의

**What**: 프로그램 버전, 파라미터 세트, 입력 묶음, 마스터 버전, 실행, 입력 검증 결과, 규칙 결과, 비교, 승인 테이블을 정의한다
**Where**: `api/repo/models.py`
**Depends on**: None
**Reuses**: 설계서의 데이터 모델 표
**Requirement**: HIST-01

**Done when**:

- [ ] 테이블 9개가 설계서의 항목대로 정의되어 있다
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`

**Tests**: none
**Gate**: build

---

#### T37: DB 연결

**What**: 기록 DB 연결과 테이블 생성을 만든다
**Where**: `api/repo/db.py`
**Depends on**: T36
**Reuses**: 없음
**Requirement**: HIST-01

**Done when**:

- [ ] 빈 DB에 테이블 9개가 만들어진다
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`

**Tests**: none
**Gate**: build

---

#### T38: 로그인과 역할 확인

**What**: 요청의 사용자와 역할을 확인하고 역할 밖의 기능을 거절한다
**Where**: `api/auth.py`
**Depends on**: None
**Reuses**: 없음
**Requirement**: AUTH-01

**Done when**:

- [ ] 자기 역할에 없는 기능을 호출하면 거절되고 "권한이 없습니다"가 보인다 (C73)
- [ ] 역할은 5개(현업 사용자, S&OP 담당자, MD, IT혁신팀, 바이어)이고 한 사용자가 여러 역할을 가질 수 있다 (C74)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_auth.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T39: 저장소 호출

**What**: 관리 API가 저장소에 프로그램·마스터·올린 파일을 쓰고 결과를 읽는 기능을 만든다
**Where**: `api/clients/blob_client.py`
**Depends on**: None
**Reuses**: 없음
**Requirement**: CODE-01

**Done when**:

- [ ] 프로그램 파일을 올리고 다시 읽으면 내용 지문이 같다
- [ ] 이미 있는 프로그램 버전 경로에 다시 쓰면 실패한다
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`
- [ ] Test count: `tests/azure/test_blob_client.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: build

---

#### T40: 실행기 호출

**What**: 모드에 맞는 실행기를 시작하고 상태를 읽는 기능을 만든다
**Where**: `api/clients/job_client.py`
**Depends on**: None
**Reuses**: 없음
**Requirement**: RUN-01

**Done when**:

- [ ] 검증 모드는 검증용 실행기를, 운영 모드는 운영용 실행기를 시작한다
- [ ] 시작한 실행의 상태(진행 중, 성공, 실패)를 읽는다
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`
- [ ] Test count: `tests/azure/test_job_client.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: build

---

#### T41: 앱 조립

**What**: 경로, 로그인, DB 연결을 하나의 웹 앱으로 엮는다
**Where**: `api/app.py`
**Depends on**: T37, T38
**Reuses**: 없음
**Requirement**: AUTH-01

**Done when**:

- [ ] 앱이 시작되고 상태 확인 경로가 응답한다
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`

**Tests**: none
**Gate**: build

---

### Phase 8: 검증 실행 서비스

#### T42: 프로그램 등록 검사

**What**: 올린 파일의 문법과 불러오는 라이브러리를 검사한다
**Where**: `api/services/code_check.py`
**Depends on**: None
**Reuses**: 실행 이미지의 라이브러리 목록
**Requirement**: CODE-01

**Done when**:

- [ ] 문법 오류가 있는 파일은 등록이 거절되고 오류가 난 줄 번호가 보인다 (C22)
- [ ] 실행 환경에 없는 라이브러리를 불러오는 파일은 등록이 거절되고 그 라이브러리 이름이 보인다 (C23)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_code_check.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T43: 파라미터 서비스

**What**: 운영 파라미터의 초기값, 범위 확인, 변경 이력을 만든다
**Where**: `api/services/parameter_service.py`
**Depends on**: None
**Reuses**: 고객 PDF 4-2의 현재값과 입력 범위
**Requirement**: PARAM-01

**Done when**:

- [ ] 운영 파라미터 16개가 초기값(기본커버 7, 최소보장 3, 프리미엄 0/0/0, 이동생략 0.0, 최소보충 3, 제조경과 21, 유효임박 6, 통물 한정 false, 점센터 보호 3, 경고 민감도 2.0, 과다 이동 10, 미등록 브랜드 양수도 제외, 반입경과 22, 헤더 행 2, 점센터 이동 제외 점 인천공항T1·인천공항T2, 점센터 이동 제외 카테고리 EYEWEAR)으로 시작한다 (C26)
- [ ] 허용 범위 밖의 값은 저장이 거절되고 허용 범위가 보인다 (예: 최소보장일수 31) (C29)
- [ ] 운영 파라미터를 바꾸면 이전 값, 변경자, 변경 일시, 사유가 이력에 남는다 (C30)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_parameter_service.py`에 이 작업의 테스트 3개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T44: 마스터 서비스

**What**: 마스터 파일을 버전으로 보관하고 시트 구성을 확인한다
**Where**: `api/services/master_service.py`
**Depends on**: None
**Reuses**: 고객 PDF 2-5의 시트 목록
**Requirement**: MST-01

**Done when**:

- [ ] 마스터 파일을 올리면 새 버전으로 보관되고 이전 버전이 남아 있다 (C31)
- [ ] 제외·전용 SKU 파일에 6개 시트 중 없는 것이 있으면 거절되고 빠진 시트 이름이 보인다 (C32)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_master_service.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T45: 실행 생성

**What**: 검증 실행 요청으로 실행 ID와 지시서를 만들고 검증용 실행기를 시작한다
**Where**: `api/services/run_service.py`
**Depends on**: T43, T44
**Reuses**: f4, f5
**Requirement**: RUN-01

**Done when**:

- [ ] 버전·입력 일자·파라미터로 검증 실행을 요청하면 실행 ID가 생기고 검증용 실행기가 시작된다 (C34)
- [ ] 검증 실행에서 조정한 파라미터는 그 실행에만 적용되고 운영 파라미터는 그대로다 (최소보장 5로 실행 후 운영값 3) (C27)
- [ ] 입력 묶음이 없는 일자를 고르면 요청이 거절되고 선택할 수 있는 일자 목록이 보인다 (C101)
- [ ] 실행기를 시작하지 못하면 상태 `실행오류`, 사유 `실행기 시작 실패`가 된다 (C105)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_run_service.py`에 이 작업의 테스트 4개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T46: 실행 상태 동기화

**What**: 실행기 상태와 결과 폴더의 실행 기록을 읽어 기록 DB에 반영한다
**Where**: `api/services/run_sync.py`
**Depends on**: T45
**Reuses**: 설계서의 실행 기록 항목
**Requirement**: HIST-01

**Done when**:

- [ ] 실행 기록의 상태, 요약 건수, 입력 검증 결과, 규칙 결과가 DB에 반영된다
- [ ] 같은 실행을 두 번 동기화해도 기록이 중복되지 않는다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_run_sync.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T47: 결과 비교

**What**: 두 실행의 건수 차이와 달라진 SKU를 계산한다
**Where**: `api/services/compare.py`
**Depends on**: T46
**Reuses**: 양수도·재고전환 엑셀의 컬럼
**Requirement**: CMP-01

**Done when**:

- [ ] 두 실행의 건수 4종(점간 이동 지시, 온·오프 전환 지시, 미충전 부족분, 발주 검토 대상) 차이가 보인다 (C52)
- [ ] 이동 수량이나 전환 수량이 달라진 SKU의 목록이 보인다 (C53)
- [ ] 비교 상대의 실행일이 다르면 "실행일이 달라 날짜 판정 차이가 섞일 수 있음"이 표시된다 (C54)
- [ ] 두 결과가 모두 같으면 "차이 없음"이 표시된다 (C55)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_compare.py`에 이 작업의 테스트 4개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T48: 비교용 동반 실행

**What**: 같은 날의 운영 버전 결과가 없으면 운영 버전을 같은 입력으로 함께 실행한다
**Where**: `api/services/run_service.py` (수정)
**Depends on**: T45
**Reuses**: g4
**Requirement**: CMP-01

**Done when**:

- [ ] 검증 실행이 완료되고 같은 입력 일자·같은 실행일의 운영 버전 결과가 없으면 운영 버전이 같은 입력으로 함께 실행된다 (C51)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_run_service.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T49: 검증 결과 내려받기

**What**: 검증 실행 결과에 검증용 표시를 붙여 내려준다
**Where**: `api/services/download.py`
**Depends on**: T46
**Reuses**: 없음
**Requirement**: RUN-01

**Done when**:

- [ ] 검증 실행 결과 파일은 이름 앞에 `TEST_`가 붙어 내려받아진다 (C37)
- [ ] 검증 실행 결과 엑셀은 각 시트 첫 줄에 "검증 실행 결과 - ERP 업로드 금지"가 들어간다 (C38)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_download.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

### Phase 9: 검증 실행 경로와 화면

#### T50: 프로그램 버전 경로

**What**: 프로그램 등록과 버전 목록 경로를 만든다
**Where**: `api/routes/code_versions.py`
**Depends on**: None
**Reuses**: g1, f4
**Requirement**: CODE-01

**Done when**:

- [ ] pipeline.py를 이름·메모와 함께 등록하면 새 버전 ID가 생기고 상태가 `등록됨`이다 (C20)
- [ ] 등록된 버전의 파일을 바꾸거나 지우는 요청은 거절된다 (C21)
- [ ] 내용이 같은 버전이 이미 있으면 새 버전이 생기지 않고 기존 버전 이름이 보인다 (C24)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_code_versions.py`에 이 작업의 테스트 3개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T51: 파라미터 경로

**What**: 운영 파라미터 조회와 변경 경로를 만든다
**Where**: `api/routes/parameters.py`
**Depends on**: None
**Reuses**: g2
**Requirement**: PARAM-01

**Done when**:

- [ ] 조회는 모든 역할이 할 수 있다
- [ ] 변경은 IT혁신팀만 할 수 있다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_parameters_route.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T52: 마스터 경로

**What**: 마스터 올리기와 버전 목록 경로를 만든다
**Where**: `api/routes/masters.py`
**Depends on**: None
**Reuses**: g3
**Requirement**: MST-01

**Done when**:

- [ ] 올리기는 MD만 할 수 있다
- [ ] 버전 목록이 최신순으로 보인다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_masters_route.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T53: 실행 경로

**What**: 실행 요청, 이력, 상세, 실행 계속 경로를 만든다
**Where**: `api/routes/runs.py`
**Depends on**: None
**Reuses**: g4, g5, g6
**Requirement**: HIST-01

**Done when**:

- [ ] `확인대기` 실행에 [실행 계속]을 누르면 프로그램 실행이 시작된다 (C17)
- [ ] 실행 이력에 일시, 모드, 실행자, 프로그램 버전, 입력 일자, 마스터 버전, 요약 건수, 소요 시간, 상태가 최신순으로 보인다 (C91)
- [ ] 입력 묶음, 결과 파일, 실행 기록을 지우는 경로가 없다 (C92)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_runs_route.py`에 이 작업의 테스트 3개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T54: 내려받기 경로

**What**: 결과 파일 목록과 내려받기 경로를 만든다
**Where**: `api/routes/downloads.py`
**Depends on**: None
**Reuses**: g8
**Requirement**: RUN-01

**Done when**:

- [ ] 검증 실행 결과는 그 실행을 요청한 현업 사용자와 IT혁신팀이 내려받을 수 있다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_downloads_route.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T55: 화면 경로

**What**: 화면 8개의 주소와 역할별 메뉴를 만든다
**Where**: `api/routes/pages.py`
**Depends on**: None
**Reuses**: f3
**Requirement**: AUTH-01

**Done when**:

- [ ] 역할에 해당하는 화면만 메뉴에 보인다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_pages.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T56: 화면: S1 내 프로그램 버전

**What**: S1 내 프로그램 버전 화면을 만든다
**Where**: `api/templates/code_versions.html`
**Depends on**: T55
**Reuses**: 없음
**Requirement**: CODE-01

**Done when**:

- [ ] 화면에 다음이 있다: 파일 선택, 이름, 메모, [등록], 버전 목록(이름, 상태, 등록 일시)
- [ ] 빈 목록, 처리 중, 오류, 권한 없음 상태가 각각 문구로 보인다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_pages.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T57: 화면: S2 검증 실행

**What**: S2 검증 실행 화면을 만든다
**Where**: `api/templates/run_new.html`
**Depends on**: T55
**Reuses**: 없음
**Requirement**: RUN-01

**Done when**:

- [ ] 화면에 다음이 있다: 프로그램 버전, 입력 일자, 비교 대상, 파라미터 16개(운영값이 채워진 상태, 목록 값 2개 포함), [검증 실행]
- [ ] 빈 목록, 처리 중, 오류, 권한 없음 상태가 각각 문구로 보인다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_pages.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T58: 화면: S3 검증 결과

**What**: S3 검증 결과 화면을 만든다
**Where**: `api/templates/run_result.html`
**Depends on**: T55
**Reuses**: 없음
**Requirement**: CMP-01

**Done when**:

- [ ] 화면에 다음이 있다: 상태, 입력 검증 결과, 규칙 5개 결과, 요약 건수, 건수 차이, 달라진 SKU, 일일결과리포트, 내려받기, [운영 반영 요청]
- [ ] 빈 목록, 처리 중, 오류, 권한 없음 상태가 각각 문구로 보인다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_pages.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T59: 화면: S5 마스터 데이터

**What**: S5 마스터 데이터 화면을 만든다
**Where**: `api/templates/masters.html`
**Depends on**: T55
**Reuses**: 없음
**Requirement**: MST-01

**Done when**:

- [ ] 화면에 다음이 있다: 종류 선택, 파일 선택, [올리기], 버전 목록
- [ ] 빈 목록, 처리 중, 오류, 권한 없음 상태가 각각 문구로 보인다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_pages.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

### Phase 10: 이상치 질문·답변과 재테스트

#### T60: 이상치 추출

**What**: 결과 파일의 검토리포트에서 이상치(이동 건수 이상, 과다 이동)를 뽑아 실행 기록에 넣는다
**Where**: `runner/anomalies.py`
**Depends on**: None
**Reuses**: 검토리포트 엑셀의 모니터1·모니터2 시트
**Requirement**: QA-01

**Done when**:

- [ ] 검증 실행이 완료되면 이상치(이동 건수 이상, 과다 이동)가 종류·상품·내용·문의 대상과 함께 보인다 (C56)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_anomalies.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T61: 임시 제외 반영

**What**: 지시서의 임시 제외 상품을 제외·전용 SKU 마스터의 사본에 추가해 작업 폴더에 놓는다
**Where**: `runner/workspace.py` (수정)
**Depends on**: None
**Reuses**: b3, 제외·전용 SKU 엑셀의 양수도제외상품·온오프전환제외상품 시트
**Requirement**: QA-01

**Done when**:

- [ ] 이동 제외 답변은 제외·전용 SKU 마스터의 임시 사본에만 추가되고 등록된 마스터 버전은 그대로다 (C66)
- [ ] Gate check passes: `pytest tests/unit -v`
- [ ] Test count: `tests/unit/test_workspace.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: unit
**Gate**: quick

---

#### T62: 질문 목록 만들기와 보내기

**What**: 이상치로 질문 목록을 만들고 CSV로 내보내고 보냄 상태로 바꾼다
**Where**: `api/services/question_service.py`
**Depends on**: None
**Reuses**: g5, g6
**Requirement**: QA-01

**Done when**:

- [ ] 질문 목록을 만들면 이상치마다 문의 대상(프로그램 작성자 또는 해당 점 바이어)과 질문 문안이 생긴다 (C57)
- [ ] 질문 목록을 내려받으면 질문번호, 받는 사람, 상품코드, 상품명, 이상 내용, 질문, 답변 선택, 답변 내용 열을 가진 CSV가 나온다 (C58)
- [ ] 질문을 보내면 질문 목록의 상태가 `보냄`이 되고 보낸 시각이 기록된다 (C59)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_question_service.py`에 이 작업의 테스트 3개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T63: 답변 기록

**What**: 화면 입력과 파일 업로드로 들어온 답변을 기록한다
**Where**: `api/services/question_service.py` (수정)
**Depends on**: T62
**Reuses**: 없음
**Requirement**: QA-01

**Done when**:

- [ ] 화면에서 답변 유형과 내용을 저장하면 답변자, 일시와 함께 기록된다 (C60)
- [ ] 답변이 적힌 질문 목록 파일을 올리면 질문번호가 같은 질문에 그 행의 답변이 기록된다 (C61)
- [ ] 허용되지 않은 답변 유형이 적힌 행은 기록되지 않고 질문번호와 허용 유형이 보인다 (C62)
- [ ] 바이어가 자기에게 온 질문이 아닌 질문에 답하면 거절된다 (C63)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_question_service.py`에 이 작업의 테스트 4개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T64: 답변 반영 계획

**What**: 답변 유형별로 반영 계획을 만든다
**Where**: `api/services/question_service.py` (수정)
**Depends on**: T63
**Reuses**: 없음
**Requirement**: QA-01

**Done when**:

- [ ] 답변이 1건 이상이면 반영 계획(파라미터 변경, 이동 제외 상품, 사유 확인 항목, 프로그램 수정 필요 항목, 미답변 항목)이 보인다 (C64)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_question_service.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T65: 답변 반영 재테스트

**What**: 반영 계획으로 지시서를 만들어 검증 실행을 시작한다
**Where**: `api/services/run_service.py` (수정)
**Depends on**: T64, T61
**Reuses**: g4
**Requirement**: QA-01

**Done when**:

- [ ] 재테스트는 원래 실행의 프로그램 버전·입력 일자에 파라미터 조정 답변의 제안값과 이동 제외 답변의 상품을 반영해 시작된다 (C65)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_run_service.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T66: 이상치 처리 상태

**What**: 재테스트 결과에서 이상치별 처리 상태와 원래 실행 대비 차이를 계산한다
**Where**: `api/services/compare.py` (수정)
**Depends on**: T65
**Reuses**: g6
**Requirement**: QA-01

**Done when**:

- [ ] 재테스트가 완료되면 이상치마다 처리 상태(해소, 확인됨, 남음)와 원래 실행 대비 건수 차이가 보인다 (C67)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_compare.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T67: 질문·답변 경로

**What**: 질문 목록 만들기, 내려받기, 보내기, 답변, 파일 올리기, 재테스트 경로를 만든다
**Where**: `api/routes/questions.py`
**Depends on**: T66
**Reuses**: q3~q7
**Requirement**: QA-01

**Done when**:

- [ ] 만들기·보내기·파일 올리기·재테스트는 현업 사용자만 할 수 있다
- [ ] 바이어는 질문·답변 화면만 볼 수 있다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_questions_route.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T68: 화면: 질문·답변

**What**: 질문·답변 화면을 만든다
**Where**: `api/templates/questions.html`
**Depends on**: T67
**Reuses**: 없음
**Requirement**: QA-01

**Done when**:

- [ ] 화면에 다음이 있다: 진행 단계(만들기, 보내기, 답변 받기, 재테스트), 질문과 답변 표, 질문 목록 내려받기, [질문 보내기], 답변 입력란, 파일 올리기, 반영 계획, [답변 반영해 재테스트]
- [ ] 빈 목록, 처리 중, 오류, 권한 없음 상태가 각각 문구로 보인다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_pages.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

### Phase 11: 운영 실행과 승인 서비스

#### T69: 운영 실행 시작

**What**: 운영 버전·운영 파라미터·당일 입력 묶음으로 운영용 실행기를 시작한다
**Where**: `api/services/run_service.py` (수정)
**Depends on**: None
**Reuses**: g4
**Requirement**: OPS-01

**Done when**:

- [ ] [지금 실행]을 누르면 운영 버전, 운영 파라미터, 당일 입력 묶음으로 운영용 실행기가 시작된다 (C75)
- [ ] 당일 입력 묶음이 `준비됨`이 아니면 실행이 시작되지 않고 입력 묶음의 상태가 보인다 (C76)
- [ ] 같은 일자에 운영 실행을 다시 하면 새 실행 ID로 저장되고 이전 실행의 결과가 남아 있다 (C83)
- [ ] 상태가 `운영`이 아닌 버전을 지정한 운영 실행 요청은 거절된다 (C71)
- [ ] 운영 버전이 없으면 운영 실행 요청이 거절되고 "운영 버전이 지정되지 않았습니다"가 보인다 (C102)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_run_service_prod.py`에 이 작업의 테스트 5개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T70: 직전 운영 결과와 비교

**What**: 운영 실행을 직전 운영 실행과 비교한다
**Where**: `api/services/compare.py` (수정)
**Depends on**: None
**Reuses**: g6
**Requirement**: OPS-01

**Done when**:

- [ ] 운영 실행이 완료되면 직전 운영 실행 결과와의 건수 4종 차이가 보인다 (C78)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_compare_prod.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T71: 운영 결과 승인

**What**: 운영 실행의 승인과 거절 조건을 만든다
**Where**: `api/services/approval.py`
**Depends on**: T69
**Reuses**: 없음
**Requirement**: OPS-01

**Done when**:

- [ ] `완료`된 운영 실행을 승인하면 상태가 `승인됨`이 되고 승인자와 일시가 기록된다 (C79)
- [ ] 상태가 `규칙위반`인 실행의 승인 요청은 거절된다 (C80)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_approval.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T72: 운영 결과 내려받기

**What**: 승인된 운영 결과만 ERP 업로드 순서대로 내려준다
**Where**: `api/services/download.py` (수정)
**Depends on**: T71
**Reuses**: g8
**Requirement**: OPS-01

**Done when**:

- [ ] `승인됨`이 아닌 운영 실행의 ERP 업로드 파일 내려받기는 거절된다 (C81)
- [ ] 승인된 실행의 내려받기 화면에 파일이 ① 재고전환_온오프 ② 양수도 ③ 재고전환_오프온 순서로 보인다 (C82)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_download_prod.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T73: 운영 반영 요청과 회귀 실행

**What**: 운영 반영 요청을 받아 기준 입력으로 새 버전과 운영 버전을 실행한다
**Where**: `api/services/promotion.py`
**Depends on**: T69
**Reuses**: g4, g6
**Requirement**: PROMO-01

**Done when**:

- [ ] 검증 실행이 완료된 버전에 운영 반영을 요청하면 기준 입력으로 그 버전과 현재 운영 버전이 함께 실행된다 (C84)
- [ ] 가장 최근 검증 실행이 `완료`가 아닌 버전의 운영 반영 요청은 거절된다 (C85)
- [ ] 회귀 실행 두 건이 끝나면 IT혁신팀에게 두 결과의 비교와 규칙 5개 결과가 보인다 (C86)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_promotion.py`에 이 작업의 테스트 3개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T74: 운영 반영 승인과 반려

**What**: 운영 반영의 승인, 반려, 거절 조건을 만든다
**Where**: `api/services/promotion.py` (수정)
**Depends on**: T73
**Reuses**: 없음
**Requirement**: PROMO-01

**Done when**:

- [ ] 승인하면 그 버전이 `운영`, 이전 운영 버전이 `보관`이 된다 (C87)
- [ ] 반려하면 그 버전이 `반려`가 되고 의견이 기록된다 (C88)
- [ ] 새 버전의 회귀 실행이 `규칙위반`이나 `실행오류`면 승인이 거절된다 (C89)
- [ ] 상태가 `운영`인 버전은 항상 1개다 (C25)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_promotion.py`에 이 작업의 테스트 4개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T75: 이전 버전으로 되돌리기

**What**: 보관된 버전을 다시 운영 버전으로 지정한다
**Where**: `api/services/promotion.py` (수정)
**Depends on**: T74
**Reuses**: 없음
**Requirement**: PROMO-01

**Done when**:

- [ ] `보관` 버전을 되돌리면 그 버전이 `운영`, 현재 운영 버전이 `보관`이 된다 (C90)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_promotion.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

### Phase 12: 운영 경로와 화면

#### T76: 운영 반영 경로

**What**: 운영 반영 요청, 승인, 반려, 되돌리기 경로를 만든다
**Where**: `api/routes/promotions.py`
**Depends on**: None
**Reuses**: i5~i7
**Requirement**: PROMO-01

**Done when**:

- [ ] 요청은 현업 사용자만, 승인·반려·되돌리기는 IT혁신팀만 할 수 있다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_promotions_route.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T77: 입력 묶음 경로

**What**: 입력 묶음 목록, 파일 올리기, 재수집 요청 경로를 만든다
**Where**: `api/routes/input_sets.py`
**Depends on**: None
**Reuses**: d5, f4
**Requirement**: INPUT-01

**Done when**:

- [ ] 파일을 올리면 그 일자의 입력 구성이 시작된다
- [ ] 파일 올리기와 재수집 요청은 S&OP 담당자만 할 수 있다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_input_sets_route.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T78: 화면: S4 운영 반영 승인

**What**: S4 운영 반영 승인 화면을 만든다
**Where**: `api/templates/promotion.html`
**Depends on**: T76, T77
**Reuses**: 없음
**Requirement**: PROMO-01

**Done when**:

- [ ] 화면에 다음이 있다: 요청 버전과 메모, 회귀 비교(건수 차이, 달라진 SKU), 규칙 5개 결과, 의견 입력, [승인], [반려]
- [ ] 빈 목록, 처리 중, 오류, 권한 없음 상태가 각각 문구로 보인다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_pages_prod.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T79: 화면: S6 입력 상태

**What**: S6 입력 상태 화면을 만든다
**Where**: `api/templates/input_status.html`
**Depends on**: None
**Reuses**: 없음
**Requirement**: VAL-01

**Done when**:

- [ ] 화면에 다음이 있다: 일자별 입력 묶음 상태, 파일별 출처와 수집 시각, 실패·경고 내용, [실행 계속], [재수집 요청], 파일 올리기
- [ ] 빈 목록, 처리 중, 오류, 권한 없음 상태가 각각 문구로 보인다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_pages_prod.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T80: 화면: S7 운영 실행·결과

**What**: S7 운영 실행·결과 화면을 만든다
**Where**: `api/templates/prod_run.html`
**Depends on**: None
**Reuses**: 없음
**Requirement**: OPS-01

**Done when**:

- [ ] 화면에 다음이 있다: [지금 실행], 상태, 요약 건수, 직전 결과와의 차이, 규칙 5개 결과, 일일결과리포트, 구간별 소요 시간, [승인]
- [ ] 빈 목록, 처리 중, 오류, 권한 없음 상태가 각각 문구로 보인다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_pages_prod.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T81: 화면: S8 결과 내려받기

**What**: S8 결과 내려받기 화면을 만든다
**Where**: `api/templates/downloads.html`
**Depends on**: None
**Reuses**: 없음
**Requirement**: OPS-01

**Done when**:

- [ ] 화면에 다음이 있다: ERP 업로드 순서 안내, 순서대로 놓인 파일 목록, 리포트 파일
- [ ] 빈 목록, 처리 중, 오류, 권한 없음 상태가 각각 문구로 보인다
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_pages_prod.py`에 이 작업의 테스트 2개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

### Phase 13: 자동 수집, 자동 시작, 알림, 측정

#### T82: Data Factory 정의

**What**: Data Factory, 수집 중계 서버 연결, 접속 정보 보관소를 정의한다
**Where**: `infra/adf.bicep`
**Depends on**: None
**Reuses**: 없음
**Requirement**: COL-01

**Done when**:

- [ ] Data Factory가 수집 중계 서버를 통해 접근이 승인된 원천에 연결된다
- [ ] 접속 정보는 Key Vault에만 있다
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`

**Tests**: none
**Gate**: build

---

#### T83: 수집 파이프라인

**What**: 원천 조회, 원본 저장, 입력 구성 시작, 입력 준비됨 알림을 파이프라인으로 정의한다
**Where**: `adf/pl_collect_daily.json`
**Depends on**: T82
**Reuses**: d5의 입력 구성
**Requirement**: COL-01

**Done when**:

- [ ] 수집 시각이 되면 접근이 승인된 원천의 원본이 `raw/<원천>/YYYYMMDD/`에 저장된다 (C1)
- [ ] 한 일자의 수집이 끝나면 그 일자의 입력 구성이 시작된다 (C2)
- [ ] 원천 조회가 실패하면 입력 묶음이 `실패`이고 실패한 원천 이름이 남는다 (C3)
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`
- [ ] Test count: `tests/azure/test_collect.py`에 이 작업의 테스트 3개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: build

---

#### T84: 재수집 호출

**What**: 관리 API가 그 일자의 수집 파이프라인을 다시 실행시키는 기능을 만든다
**Where**: `api/clients/adf_client.py`
**Depends on**: T83
**Reuses**: 없음
**Requirement**: COL-01

**Done when**:

- [ ] 재수집을 요청하면 그 일자의 수집이 다시 실행되고 이전 수집분이 남아 있다 (C4)
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`
- [ ] Test count: `tests/azure/test_recollect.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: build

---

#### T85: 입력 준비됨 수신과 자동 시작

**What**: 수집 파이프라인의 알림을 받아 자동 시작 설정에 따라 운영 실행을 시작한다
**Where**: `api/routes/internal.py`
**Depends on**: None
**Reuses**: i1
**Requirement**: SCHED-01

**Done when**:

- [ ] 자동 시작이 켜져 있을 때 입력 준비됨 알림이 오면 그 일자의 운영 실행이 시작된다 (C93)
- [ ] 자동 시작이 꺼져 있으면 입력 준비됨 알림이 와도 운영 실행이 시작되지 않는다 (C94)
- [ ] 같은 일자의 입력 준비됨 알림이 다시 와도 자동 실행이 다시 시작되지 않는다 (C95)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_internal.py`에 이 작업의 테스트 3개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T86: 알림 보내기

**What**: 수집 실패, 입력실패, 실행 종료, 승인 요청 알림을 만든다
**Where**: `api/services/notify.py`
**Depends on**: None
**Reuses**: 없음
**Requirement**: NOTI-01

**Done when**:

- [ ] 수집이 실패하면 S&OP 담당자에게 실패한 원천 이름이 담긴 알림이 간다 (C96)
- [ ] 운영 실행이 `입력실패`가 되면 S&OP 담당자에게 실패한 검증 항목이 담긴 알림이 간다 (C97)
- [ ] 운영 실행이 `완료`나 `규칙위반`으로 끝나면 S&OP 담당자에게 상태와 요약 건수가 담긴 알림이 간다 (C98)
- [ ] 회귀 실행이 끝나면 IT혁신팀에게 승인 요청 알림이 간다 (C99)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_notify.py`에 이 작업의 테스트 4개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

#### T87: 알림 연결 정의

**What**: 메일을 보내는 Logic Apps를 정의한다
**Where**: `infra/logicapp.bicep`
**Depends on**: T86
**Reuses**: 없음
**Requirement**: NOTI-01

**Done when**:

- [ ] 관리 API가 호출하면 지정한 수신자에게 메일이 간다
- [ ] Gate check passes: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v`

**Tests**: none
**Gate**: build

---

#### T88: 구간별 시각 기록

**What**: 운영 실행의 구간별 시각을 기록하고 소요 시간을 계산한다
**Where**: `api/services/timing.py`
**Depends on**: None
**Reuses**: 입력 묶음 명세서, 실행 기록
**Requirement**: MEAS-01

**Done when**:

- [ ] 운영 실행마다 수집 시작, 입력 준비됨, 실행 시작, 실행 종료, 승인의 시각이 기록되고 구간별 소요 시간이 보인다 (C100)
- [ ] Gate check passes: `pytest tests/unit tests/api -v`
- [ ] Test count: `tests/api/test_timing.py`에 이 작업의 테스트 1개 이상이 통과한다 (기존 테스트를 지우지 않는다)

**Tests**: integration
**Gate**: full

---

## Checks

확인 항목마다 명세의 요구사항 ID와 수용 기준 번호를 적었다. `Proof`의 테스트 이름과 출력 줄은 계획이며, 구현하면서 실제 실행 결과의 줄로 바꾼다.

### COL-01

**C1** - 수집 시각이 되면 접근이 승인된 원천의 원본이 `raw/<원천>/YYYYMMDD/`에 저장된다 (COL-01, AC 1)
Proof: run azure | tests/azure/test_collect.py::test_scheduled_collect_writes_raw PASSED

**C2** - 한 일자의 수집이 끝나면 그 일자의 입력 구성이 시작된다 (COL-01, AC 2)
Proof: run azure | tests/azure/test_collect.py::test_collect_starts_prep PASSED

**C3** - 원천 조회가 실패하면 입력 묶음이 `실패`이고 실패한 원천 이름이 남는다 (COL-01, AC 3)
Proof: run azure | tests/azure/test_collect.py::test_source_failure_recorded_with_name PASSED

**C4** - 재수집을 요청하면 그 일자의 수집이 다시 실행되고 이전 수집분이 남아 있다 (COL-01, AC 4)
Proof: run azure | tests/azure/test_recollect.py::test_recollect_keeps_previous_raw PASSED

**C5** - 매일 수집하지 않는 원천(판매예측)은 가장 최근 수집분이 그 일자 입력 묶음에 들어간다 (COL-01, AC 5)
Proof: run unit | tests/unit/test_prep_main.py::test_latest_non_daily_source_reused PASSED

### INPUT-01

**C6** - `input/YYYYMMDD/`에 기간계 입력(재고, 판매예측, 코드표 5종)이 현행 이름과 형식(재고 utf-8-sig, 코드표 cp949)으로 만들어진다 (INPUT-01, AC 1)
Proof: run unit | tests/unit/test_formats.py::test_eight_files_in_current_formats PASSED

**C7** - 입력 묶음마다 파일별 출처, 수집 시각, 행 수, 내용 지문이 적힌 명세서가 있다 (INPUT-01, AC 2)
Proof: run unit | tests/unit/test_manifest.py::test_manifest_has_source_time_rows_hash PASSED

**C8** - 재고 카테고리별 엑셀을 올리면 합본 CSV 1개가 만들어진다 (기준 입력: 고객 PC 합본과 내용 지문이 같다) (INPUT-01, AC 3)
Proof: run unit | tests/unit/test_merge.py::test_six_files_merge_matches_baseline PASSED

**C9** - 자동 수집되지 않는 원천의 파일을 올리면 입력 묶음에 들어가고 명세서의 출처가 `올린 파일`이다 (INPUT-01, AC 4)
Proof: run unit | tests/unit/test_prep_main.py::test_uploaded_file_marked_in_manifest PASSED

**C10** - 기준 72개 컬럼을 만들 수 없으면 입력 묶음이 `실패`이고 빠진 컬럼 이름이 남는다 (INPUT-01, AC 5)
Proof: run unit | tests/unit/test_inventory_layout.py::test_missing_source_column_fails PASSED

### VAL-01

**C11** - 재고 스냅샷이나 판매예측 파일이 없으면 프로그램을 실행하지 않고 상태가 `입력실패`다 (VAL-01, AC 1)
Proof: run unit | tests/unit/test_input_checks.py::test_missing_required_file_fails PASSED

**C12** - 코드표 5종 중 하나라도 없으면 프로그램을 실행하지 않고 상태가 `입력실패`다 (VAL-01, AC 2)
Proof: run unit | tests/unit/test_input_checks.py::test_missing_code_table_fails PASSED

**C13** - 재고 컬럼의 이름이나 순서가 기준 72개와 다르면 `입력실패`이고 다른 컬럼의 위치와 이름이 남는다 (VAL-01, AC 3)
Proof: run unit | tests/unit/test_input_checks.py::test_column_mismatch_names_position PASSED

**C14** - 등록된 대상 카테고리 중 없는 것이 있으면 `입력실패`이고 빠진 카테고리 이름이 남는다 (시험 입력: FOOD 제외) (VAL-01, AC 4)
Proof: run unit | tests/unit/test_input_checks.py::test_missing_category_names_category PASSED

**C15** - 10개 점 중 없는 점이 있으면 `입력실패`이고 빠진 점 이름이 남는다 (VAL-01, AC 5)
Proof: run unit | tests/unit/test_input_checks.py::test_missing_store_names_store PASSED

**C16** - 운영 실행에서 갱신 주기를 넘은 입력이 있으면 프로그램을 실행하지 않고 상태가 `확인대기`다 (VAL-01, AC 6)
Proof: run unit | tests/unit/test_input_checks.py::test_stale_input_waits_in_prod_mode PASSED

**C17** - `확인대기` 실행에 [실행 계속]을 누르면 프로그램 실행이 시작된다 (VAL-01, AC 7)
Proof: run api | tests/api/test_runs_route.py::test_continue_starts_waiting_run PASSED

**C18** - 검증 실행에서는 갱신 주기 초과를 경고로만 기록하고 실행을 계속한다 (VAL-01, AC 8)
Proof: run unit | tests/unit/test_input_checks.py::test_stale_input_is_warning_in_test_mode PASSED

**C19** - 입력 검증 항목별 결과(통과, 경고, 실패)가 실행 기록에 저장된다 (VAL-01, AC 9)
Proof: run unit | tests/unit/test_record.py::test_input_check_results_saved PASSED

### CODE-01

**C20** - pipeline.py를 이름·메모와 함께 등록하면 새 버전 ID가 생기고 상태가 `등록됨`이다 (CODE-01, AC 1)
Proof: run api | tests/api/test_code_versions.py::test_register_creates_version PASSED

**C21** - 등록된 버전의 파일을 바꾸거나 지우는 요청은 거절된다 (CODE-01, AC 2)
Proof: run api | tests/api/test_code_versions.py::test_registered_file_cannot_change PASSED

**C22** - 문법 오류가 있는 파일은 등록이 거절되고 오류가 난 줄 번호가 보인다 (CODE-01, AC 3)
Proof: run unit | tests/unit/test_code_check.py::test_syntax_error_shows_line_number PASSED

**C23** - 실행 환경에 없는 라이브러리를 불러오는 파일은 등록이 거절되고 그 라이브러리 이름이 보인다 (CODE-01, AC 4)
Proof: run unit | tests/unit/test_code_check.py::test_unknown_library_is_named PASSED

**C24** - 내용이 같은 버전이 이미 있으면 새 버전이 생기지 않고 기존 버전 이름이 보인다 (CODE-01, AC 5)
Proof: run api | tests/api/test_code_versions.py::test_same_content_returns_existing_version PASSED

**C25** - 상태가 `운영`인 버전은 항상 1개다 (CODE-01, AC 6)
Proof: run api | tests/api/test_promotion.py::test_exactly_one_prod_version PASSED

### PARAM-01

**C26** - 운영 파라미터 16개가 초기값(기본커버 7, 최소보장 3, 프리미엄 0/0/0, 이동생략 0.0, 최소보충 3, 제조경과 21, 유효임박 6, 통물 한정 false, 점센터 보호 3, 경고 민감도 2.0, 과다 이동 10, 미등록 브랜드 양수도 제외, 반입경과 22, 헤더 행 2, 점센터 이동 제외 점 인천공항T1·인천공항T2, 점센터 이동 제외 카테고리 EYEWEAR)으로 시작한다 (PARAM-01, AC 1)
Proof: run api | tests/api/test_parameter_service.py::test_initial_prod_parameters PASSED

**C27** - 검증 실행에서 조정한 파라미터는 그 실행에만 적용되고 운영 파라미터는 그대로다 (최소보장 5로 실행 후 운영값 3) (PARAM-01, AC 2)
Proof: run api | tests/api/test_run_service.py::test_adjusted_parameter_does_not_change_prod PASSED

**C28** - 실행 시점의 파라미터 16개 값 전체가 실행 기록에 사본으로 남는다 (PARAM-01, AC 3)
Proof: run unit | tests/unit/test_settings_file.py::test_parameter_snapshot_in_record PASSED

**C29** - 허용 범위 밖의 값은 저장이 거절되고 허용 범위가 보인다 (예: 최소보장일수 31) (PARAM-01, AC 4)
Proof: run api | tests/api/test_parameter_service.py::test_out_of_range_value_rejected PASSED

**C30** - 운영 파라미터를 바꾸면 이전 값, 변경자, 변경 일시, 사유가 이력에 남는다 (PARAM-01, AC 5)
Proof: run api | tests/api/test_parameter_service.py::test_prod_change_keeps_history PASSED

### MST-01

**C31** - 마스터 파일을 올리면 새 버전으로 보관되고 이전 버전이 남아 있다 (MST-01, AC 1)
Proof: run api | tests/api/test_master_service.py::test_upload_creates_new_version_keeps_old PASSED

**C32** - 제외·전용 SKU 파일에 6개 시트 중 없는 것이 있으면 거절되고 빠진 시트 이름이 보인다 (MST-01, AC 2)
Proof: run api | tests/api/test_master_service.py::test_missing_sheet_is_named PASSED

**C33** - 실행은 종류별로 가장 최근 마스터 버전을 쓰고 그 버전이 실행 기록에 남는다 (MST-01, AC 3)
Proof: run unit | tests/unit/test_workspace.py::test_latest_master_version_used_and_recorded PASSED

### RUN-01

**C34** - 버전·입력 일자·파라미터로 검증 실행을 요청하면 실행 ID가 생기고 검증용 실행기가 시작된다 (RUN-01, AC 1)
Proof: run api | tests/api/test_run_service.py::test_test_run_starts_test_runner PASSED

**C35** - 실행 환경이 Python 3.14.7, pandas 3.0.5, numpy 2.5.3, openpyxl 3.1.5, 시간대 Asia/Seoul이다 (RUN-01, AC 2)
Proof: run unit | tests/unit/test_environment.py::test_versions_and_timezone PASSED

**C36** - 정상 종료한 검증 실행의 결과 파일이 `test/<실행ID>/`에 현행 파일 이름으로 저장된다 (RUN-01, AC 3)
Proof: run unit | tests/unit/test_main.py::test_test_run_output_path PASSED

**C37** - 검증 실행 결과 파일은 이름 앞에 `TEST_`가 붙어 내려받아진다 (RUN-01, AC 4)
Proof: run api | tests/api/test_download.py::test_test_run_file_has_prefix PASSED

**C38** - 검증 실행 결과 엑셀은 각 시트 첫 줄에 "검증 실행 결과 - ERP 업로드 금지"가 들어간다 (RUN-01, AC 5)
Proof: run api | tests/api/test_download.py::test_test_run_sheet_has_first_row_notice PASSED

**C39** - 프로그램이 오류로 끝나면 상태가 `실행오류`이고 로그 마지막 200줄이 저장된다 (RUN-01, AC 6)
Proof: run unit | tests/unit/test_engine.py::test_program_error_keeps_last_200_log_lines PASSED

**C40** - 실행이 30분을 넘으면 중단되고 상태 `실행오류`, 사유 `시간 초과`가 된다 (RUN-01, AC 7)
Proof: run unit | tests/unit/test_engine.py::test_timeout_stops_run PASSED

**C41** - 두 실행이 같은 시각에 돌아도 각각 별도 컨테이너에서 실행되고 결과가 단독 실행과 같다 (RUN-01, AC 8)
Proof: run azure | tests/azure/test_concurrency.py::test_two_runs_match_single_runs PASSED

**C42** - 실행 기록에 모드, 요청자, 프로그램 버전, 파라미터 사본, 입력 일자, 마스터 버전, 시작·종료 시각, 상태가 있다 (RUN-01, AC 9)
Proof: run unit | tests/unit/test_record.py::test_record_has_all_fields PASSED

**C43** - 기준 입력과 운영 파라미터로 현행 pipeline.py를 실행한 결과가 현행 PC에서 같은 날 실행한 결과와 셀 단위로 같다 (RUN-01, AC 10)
Proof: run azure | tests/azure/test_baseline.py::test_baseline_matches_pc_result_cell_by_cell PASSED

### RULE-01

**C44** - 배분 전후 총량이 다른 SKU가 있으면 `총량 보존`이 위반이고 위반 SKU 수가 남는다 (RULE-01, AC 1)
Proof: run unit | tests/unit/test_rules.py::test_total_conservation_violation PASSED

**C45** - 양도 후 보유일수가 최소보장일수보다 작은 건이 있으면 `최소보장`이 위반이고 위반 건수가 남는다 (판정: 배분후 재고 < 내림(판매량 × 일수)) (RULE-01, AC 2)
Proof: run unit | tests/unit/test_rules.py::test_min_days_violation PASSED

**C46** - 같은 양수도 그룹이 아닌 점 사이의 이동이 있으면 `그룹 내 이동`이 위반이고 위반 건수가 남는다 (RULE-01, AC 3)
Proof: run unit | tests/unit/test_rules.py::test_cross_group_transfer_violation PASSED

**C47** - 한 점이 내보낸 수량의 합이 보유 수량보다 크면 `발송 한도`가 위반이고 위반 건수가 남는다 (RULE-01, AC 4)
Proof: run unit | tests/unit/test_rules.py::test_send_over_stock_violation PASSED

**C48** - 전환 신청수량이 배치 가용수량보다 크면 `전환 한도`가 위반이고 위반 건수가 남는다 (RULE-01, AC 5)
Proof: run unit | tests/unit/test_rules.py::test_conversion_over_batch_violation PASSED

**C49** - 규칙 5개 중 하나라도 위반이면 실행 상태가 `규칙위반`이다 (RULE-01, AC 6)
Proof: run unit | tests/unit/test_rules.py::test_any_violation_sets_status PASSED

**C50** - 규칙을 모두 통과하면 상태가 `완료`이고 요약 건수 5개가 저장된다 (2026-11-18 입력 재실행: 13,887 / 45 / 43 / 4,780 / 2,162) (RULE-01, AC 7)
Proof: run unit | tests/unit/test_summary.py::test_all_pass_saves_five_counts PASSED

### CMP-01

**C51** - 검증 실행이 완료되고 같은 입력 일자·같은 실행일의 운영 버전 결과가 없으면 운영 버전이 같은 입력으로 함께 실행된다 (CMP-01, AC 1)
Proof: run api | tests/api/test_run_service.py::test_companion_prod_version_run_created PASSED

**C52** - 두 실행의 건수 4종(점간 이동 지시, 온·오프 전환 지시, 미충전 부족분, 발주 검토 대상) 차이가 보인다 (CMP-01, AC 2)
Proof: run api | tests/api/test_compare.py::test_four_count_differences PASSED

**C53** - 이동 수량이나 전환 수량이 달라진 SKU의 목록이 보인다 (CMP-01, AC 3)
Proof: run api | tests/api/test_compare.py::test_changed_sku_list PASSED

**C54** - 비교 상대의 실행일이 다르면 "실행일이 달라 날짜 판정 차이가 섞일 수 있음"이 표시된다 (CMP-01, AC 4)
Proof: run api | tests/api/test_compare.py::test_different_run_date_warning PASSED

**C55** - 두 결과가 모두 같으면 "차이 없음"이 표시된다 (CMP-01, AC 5)
Proof: run api | tests/api/test_compare.py::test_identical_results_show_no_difference PASSED

### QA-01

**C56** - 검증 실행이 완료되면 이상치(이동 건수 이상, 과다 이동)가 종류·상품·내용·문의 대상과 함께 보인다 (QA-01, AC 1)
Proof: run unit | tests/unit/test_anomalies.py::test_anomalies_extracted_from_review_report PASSED

**C57** - 질문 목록을 만들면 이상치마다 문의 대상(프로그램 작성자 또는 해당 점 바이어)과 질문 문안이 생긴다 (QA-01, AC 2)
Proof: run api | tests/api/test_question_service.py::test_question_list_has_recipient_and_text PASSED

**C58** - 질문 목록을 내려받으면 질문번호, 받는 사람, 상품코드, 상품명, 이상 내용, 질문, 답변 선택, 답변 내용 열을 가진 CSV가 나온다 (QA-01, AC 3)
Proof: run api | tests/api/test_question_service.py::test_question_csv_columns PASSED

**C59** - 질문을 보내면 질문 목록의 상태가 `보냄`이 되고 보낸 시각이 기록된다 (QA-01, AC 4)
Proof: run api | tests/api/test_question_service.py::test_send_sets_status_and_time PASSED

**C60** - 화면에서 답변 유형과 내용을 저장하면 답변자, 일시와 함께 기록된다 (QA-01, AC 5)
Proof: run api | tests/api/test_question_service.py::test_screen_answer_recorded_with_who_and_when PASSED

**C61** - 답변이 적힌 질문 목록 파일을 올리면 질문번호가 같은 질문에 그 행의 답변이 기록된다 (QA-01, AC 6)
Proof: run api | tests/api/test_question_service.py::test_uploaded_answers_matched_by_number PASSED

**C62** - 허용되지 않은 답변 유형이 적힌 행은 기록되지 않고 질문번호와 허용 유형이 보인다 (QA-01, AC 7)
Proof: run api | tests/api/test_question_service.py::test_invalid_answer_type_reported PASSED

**C63** - 바이어가 자기에게 온 질문이 아닌 질문에 답하면 거절된다 (QA-01, AC 8)
Proof: run api | tests/api/test_question_service.py::test_buyer_cannot_answer_others_question PASSED

**C64** - 답변이 1건 이상이면 반영 계획(파라미터 변경, 이동 제외 상품, 사유 확인 항목, 프로그램 수정 필요 항목, 미답변 항목)이 보인다 (QA-01, AC 9)
Proof: run api | tests/api/test_question_service.py::test_plan_groups_answers_by_type PASSED

**C65** - 재테스트는 원래 실행의 프로그램 버전·입력 일자에 파라미터 조정 답변의 제안값과 이동 제외 답변의 상품을 반영해 시작된다 (QA-01, AC 10)
Proof: run api | tests/api/test_run_service.py::test_retest_applies_parameter_and_exclusions PASSED

**C66** - 이동 제외 답변은 제외·전용 SKU 마스터의 임시 사본에만 추가되고 등록된 마스터 버전은 그대로다 (QA-01, AC 11)
Proof: run unit | tests/unit/test_workspace.py::test_temp_exclusion_does_not_change_master PASSED

**C67** - 재테스트가 완료되면 이상치마다 처리 상태(해소, 확인됨, 남음)와 원래 실행 대비 건수 차이가 보인다 (QA-01, AC 12)
Proof: run api | tests/api/test_compare.py::test_anomaly_status_after_retest PASSED

### ISO-01

**C68** - 검증용 실행기가 운영 결과 구역이나 입력 구역에 쓰려고 하면 거절된다 (ISO-01, AC 1)
Proof: run azure | tests/azure/test_isolation.py::test_test_runner_cannot_write_prod_or_input PASSED

**C69** - 실행 중인 프로그램이 저장소 밖의 주소로 접속하려고 하면 차단된다 (ISO-01, AC 2)
Proof: run azure | tests/azure/test_isolation.py::test_program_cannot_reach_outside PASSED

**C70** - 프로그램은 저장소 접근 권한이 없는 별도 사용자로 실행된다 (ISO-01, AC 3)
Proof: run unit | tests/unit/test_engine.py::test_program_runs_as_restricted_user PASSED

**C71** - 상태가 `운영`이 아닌 버전을 지정한 운영 실행 요청은 거절된다 (ISO-01, AC 4)
Proof: run api | tests/api/test_run_service_prod.py::test_prod_run_rejects_non_prod_version PASSED

### AUTH-01

**C72** - 로그인하지 않은 요청은 사내 계정 로그인 화면으로 보내진다 (AUTH-01, AC 1)
Proof: run azure | tests/azure/test_login.py::test_anonymous_request_redirects_to_login PASSED

**C73** - 자기 역할에 없는 기능을 호출하면 거절되고 "권한이 없습니다"가 보인다 (AUTH-01, AC 2)
Proof: run api | tests/api/test_auth.py::test_wrong_role_is_rejected PASSED

**C74** - 역할은 5개(현업 사용자, S&OP 담당자, MD, IT혁신팀, 바이어)이고 한 사용자가 여러 역할을 가질 수 있다 (AUTH-01, AC 3)
Proof: run api | tests/api/test_auth.py::test_user_can_hold_multiple_roles PASSED

### OPS-01

**C75** - [지금 실행]을 누르면 운영 버전, 운영 파라미터, 당일 입력 묶음으로 운영용 실행기가 시작된다 (OPS-01, AC 1)
Proof: run api | tests/api/test_run_service_prod.py::test_prod_run_uses_prod_version_and_parameters PASSED

**C76** - 당일 입력 묶음이 `준비됨`이 아니면 실행이 시작되지 않고 입력 묶음의 상태가 보인다 (OPS-01, AC 2)
Proof: run api | tests/api/test_run_service_prod.py::test_prod_run_needs_ready_input PASSED

**C77** - 정상 종료한 운영 실행의 결과 파일이 `prod/YYYYMMDD/<실행ID>/`에 저장된다 (OPS-01, AC 3)
Proof: run unit | tests/unit/test_main.py::test_prod_run_output_path PASSED

**C78** - 운영 실행이 완료되면 직전 운영 실행 결과와의 건수 4종 차이가 보인다 (OPS-01, AC 4)
Proof: run api | tests/api/test_compare_prod.py::test_prod_run_compared_with_previous PASSED

**C79** - `완료`된 운영 실행을 승인하면 상태가 `승인됨`이 되고 승인자와 일시가 기록된다 (OPS-01, AC 5)
Proof: run api | tests/api/test_approval.py::test_approve_records_approver_and_time PASSED

**C80** - 상태가 `규칙위반`인 실행의 승인 요청은 거절된다 (OPS-01, AC 6)
Proof: run api | tests/api/test_approval.py::test_rule_violation_cannot_be_approved PASSED

**C81** - `승인됨`이 아닌 운영 실행의 ERP 업로드 파일 내려받기는 거절된다 (OPS-01, AC 7)
Proof: run api | tests/api/test_download_prod.py::test_download_requires_approval PASSED

**C82** - 승인된 실행의 내려받기 화면에 파일이 ① 재고전환_온오프 ② 양수도 ③ 재고전환_오프온 순서로 보인다 (OPS-01, AC 8)
Proof: run api | tests/api/test_download_prod.py::test_files_in_erp_upload_order PASSED

**C83** - 같은 일자에 운영 실행을 다시 하면 새 실행 ID로 저장되고 이전 실행의 결과가 남아 있다 (OPS-01, AC 9)
Proof: run api | tests/api/test_run_service_prod.py::test_rerun_keeps_previous_result PASSED

### PROMO-01

**C84** - 검증 실행이 완료된 버전에 운영 반영을 요청하면 기준 입력으로 그 버전과 현재 운영 버전이 함께 실행된다 (PROMO-01, AC 1)
Proof: run api | tests/api/test_promotion.py::test_request_starts_two_regression_runs PASSED

**C85** - 가장 최근 검증 실행이 `완료`가 아닌 버전의 운영 반영 요청은 거절된다 (PROMO-01, AC 2)
Proof: run api | tests/api/test_promotion.py::test_request_needs_completed_test_run PASSED

**C86** - 회귀 실행 두 건이 끝나면 IT혁신팀에게 두 결과의 비교와 규칙 5개 결과가 보인다 (PROMO-01, AC 3)
Proof: run api | tests/api/test_promotion.py::test_regression_result_shown_to_it PASSED

**C87** - 승인하면 그 버전이 `운영`, 이전 운영 버전이 `보관`이 된다 (PROMO-01, AC 4)
Proof: run api | tests/api/test_promotion.py::test_approve_switches_prod_version PASSED

**C88** - 반려하면 그 버전이 `반려`가 되고 의견이 기록된다 (PROMO-01, AC 5)
Proof: run api | tests/api/test_promotion.py::test_reject_records_comment PASSED

**C89** - 새 버전의 회귀 실행이 `규칙위반`이나 `실행오류`면 승인이 거절된다 (PROMO-01, AC 6)
Proof: run api | tests/api/test_promotion.py::test_failed_regression_cannot_be_approved PASSED

**C90** - `보관` 버전을 되돌리면 그 버전이 `운영`, 현재 운영 버전이 `보관`이 된다 (PROMO-01, AC 7)
Proof: run api | tests/api/test_promotion.py::test_rollback_switches_versions PASSED

### HIST-01

**C91** - 실행 이력에 일시, 모드, 실행자, 프로그램 버전, 입력 일자, 마스터 버전, 요약 건수, 소요 시간, 상태가 최신순으로 보인다 (HIST-01, AC 1)
Proof: run api | tests/api/test_runs_route.py::test_history_fields_newest_first PASSED

**C92** - 입력 묶음, 결과 파일, 실행 기록을 지우는 경로가 없다 (HIST-01, AC 2)
Proof: run api | tests/api/test_runs_route.py::test_no_delete_routes PASSED

### SCHED-01

**C93** - 자동 시작이 켜져 있을 때 입력 준비됨 알림이 오면 그 일자의 운영 실행이 시작된다 (SCHED-01, AC 1)
Proof: run api | tests/api/test_internal.py::test_auto_start_on_input_ready PASSED

**C94** - 자동 시작이 꺼져 있으면 입력 준비됨 알림이 와도 운영 실행이 시작되지 않는다 (SCHED-01, AC 2)
Proof: run api | tests/api/test_internal.py::test_no_auto_start_when_off PASSED

**C95** - 같은 일자의 입력 준비됨 알림이 다시 와도 자동 실행이 다시 시작되지 않는다 (SCHED-01, AC 3)
Proof: run api | tests/api/test_internal.py::test_duplicate_input_ready_ignored PASSED

### NOTI-01

**C96** - 수집이 실패하면 S&OP 담당자에게 실패한 원천 이름이 담긴 알림이 간다 (NOTI-01, AC 1)
Proof: run api | tests/api/test_notify.py::test_collect_failure_notice_names_source PASSED

**C97** - 운영 실행이 `입력실패`가 되면 S&OP 담당자에게 실패한 검증 항목이 담긴 알림이 간다 (NOTI-01, AC 2)
Proof: run api | tests/api/test_notify.py::test_input_failure_notice_names_check PASSED

**C98** - 운영 실행이 `완료`나 `규칙위반`으로 끝나면 S&OP 담당자에게 상태와 요약 건수가 담긴 알림이 간다 (NOTI-01, AC 3)
Proof: run api | tests/api/test_notify.py::test_run_end_notice_has_status_and_counts PASSED

**C99** - 회귀 실행이 끝나면 IT혁신팀에게 승인 요청 알림이 간다 (NOTI-01, AC 4)
Proof: run api | tests/api/test_notify.py::test_regression_end_notifies_it PASSED

### MEAS-01

**C100** - 운영 실행마다 수집 시작, 입력 준비됨, 실행 시작, 실행 종료, 승인의 시각이 기록되고 구간별 소요 시간이 보인다 (MEAS-01, AC 1)
Proof: run api | tests/api/test_timing.py::test_five_timestamps_and_durations PASSED

### EDGE-01

**C101** - 입력 묶음이 없는 일자를 고르면 요청이 거절되고 선택할 수 있는 일자 목록이 보인다 (EDGE-01, AC 1)
Proof: run api | tests/api/test_run_service.py::test_unknown_input_date_lists_available_dates PASSED

**C102** - 운영 버전이 없으면 운영 실행 요청이 거절되고 "운영 버전이 지정되지 않았습니다"가 보인다 (EDGE-01, AC 2)
Proof: run api | tests/api/test_run_service_prod.py::test_prod_run_without_prod_version PASSED

**C103** - 올린 버전이 없는 마스터 종류는 그 파일 없이 실행하고 입력 검증 결과에 경고로 남는다 (EDGE-01, AC 3)
Proof: run unit | tests/unit/test_workspace.py::test_missing_master_is_warning PASSED

**C104** - 결과 파일 없이 정상 종료하면 상태 `실행오류`, 사유 `결과 없음`이 된다 (EDGE-01, AC 4)
Proof: run unit | tests/unit/test_engine.py::test_no_output_is_error PASSED

**C105** - 실행기를 시작하지 못하면 상태 `실행오류`, 사유 `실행기 시작 실패`가 된다 (EDGE-01, AC 5)
Proof: run api | tests/api/test_run_service.py::test_runner_start_failure_recorded PASSED

---

## Handoff

**Settled mid-build:** none
**Dispatched:** none
**Walked:** none

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8 → Phase 9 → Phase 10 → Phase 11 → Phase 12 → Phase 13

Phase  1 (기반과 현행 재현): T1, T2, T3, T4
Phase  2 (실행 틀): T5, T6, T7, T8, T9, T10
Phase  3 (입력 검증): T11, T12, T13, T14, T15
Phase  4 (업무 규칙과 실행 엮기): T16, T17, T18, T19, T20, T21, T22, T23
Phase  5 (입력 구성): T24, T25, T26, T27, T28
Phase  6 (Azure 환경): T29, T30, T31, T32, T33, T34, T35
Phase  7 (기록과 API 기반): T36, T37, T38, T39, T40, T41
Phase  8 (검증 실행 서비스): T42, T43, T44, T45, T46, T47, T48, T49
Phase  9 (검증 실행 경로와 화면): T50, T51, T52, T53, T54, T55, T56, T57, T58, T59
Phase 10 (이상치 질문·답변과 재테스트): T60, T61, T62, T63, T64, T65, T66, T67, T68
Phase 11 (운영 실행과 승인 서비스): T69, T70, T71, T72, T73, T74, T75
Phase 12 (운영 경로와 화면): T76, T77, T78, T79, T80, T81
Phase 13 (자동 수집, 자동 시작, 알림, 측정): T82, T83, T84, T85, T86, T87, T88
```

고객 답과 자료에 걸려 있는 단계:

| 단계 | 시작 조건 |
| --- | --- |
| Phase 1 | 소스와 2026-11-18 입력·결과는 받았다. 같은 입력으로 PC에서 실행한 결과 한 벌이 더 필요하다 (Q17) |
| Phase 2~5 | Linux에서 수정 없이 실행됨은 확인했다. PC와 결과가 같다는 확인이 남았다. 다르면 실행기 선택을 다시 한다 |
| Phase 6 | Azure 환경 제공 주체와 보안 기준이 정해진다 (Q7) |
| Phase 9, 12 | 로그인 방식이 정해진다 (Q16) |
| Phase 10 | 이상치 기준, 문의 대상, 답변 반영 방식이 정해진다 (Q23~Q25) |
| Phase 11~12 | 운영 반영에 IT혁신팀 승인을 두는 데 고객이 동의한다 (Q3) |
| Phase 13 | 기간계 원천의 접근이 승인된다 (Q1). 승인된 원천만 파이프라인에 넣는다 |

Phase 13은 접근 승인에 시간이 걸리므로 승인 절차는 Phase 1과 동시에 시작한다.

---

## Requirement Coverage

| Requirement ID | 수용 기준 수 | 확인 항목 | 작업 |
| --- | --- | --- | --- |
| COL-01 | 5 | C1~C5 | T28, T83, T84 |
| INPUT-01 | 5 | C6~C10 | T24, T25, T26, T27, T28 |
| VAL-01 | 9 | C11~C19 | T10, T12, T13, T14, T15, T53 |
| CODE-01 | 6 | C20~C25 | T42, T50, T74 |
| PARAM-01 | 5 | C26~C30 | T8, T43, T45 |
| MST-01 | 3 | C31~C33 | T7, T44 |
| RUN-01 | 10 | C34~C43 | T4, T9, T10, T23, T32, T35, T45, T49 |
| RULE-01 | 7 | C44~C50 | T16, T17, T18, T19, T20, T21, T22 |
| CMP-01 | 5 | C51~C55 | T47, T48 |
| QA-01 | 12 | C56~C67 | T60, T61, T62, T63, T64, T65, T66 |
| ISO-01 | 4 | C68~C71 | T9, T30, T31, T69 |
| AUTH-01 | 3 | C72~C74 | T34, T38 |
| OPS-01 | 9 | C75~C83 | T23, T69, T70, T71, T72 |
| PROMO-01 | 7 | C84~C90 | T73, T74, T75 |
| HIST-01 | 2 | C91~C92 | T53 |
| SCHED-01 | 3 | C93~C95 | T85 |
| NOTI-01 | 4 | C96~C99 | T86 |
| MEAS-01 | 1 | C100~C100 | T88 |
| EDGE-01 | 5 | C101~C105 | T7, T9, T45, T69 |

**Coverage:** 요구사항 19개, 수용 기준 105개가 모두 확인 항목과 작업에 연결되어 있다.
