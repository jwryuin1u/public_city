# STATE

## Decisions

### AD-001
- **Decision**: 실행기가 프로그램에 대해 아는 것은 입력 폴더, settings.json, 출력 폴더 세 가지뿐이다.
- **Reason**: 현행 pipeline.py를 고치지 않고 실행하고, 본사업에서 다른 프로그램을 같은 실행기에 올릴 수 있게 한다.
- **Trade-off**: 프로그램 내부 상태를 실행 중에 볼 수 없다. 진행률 표시는 로그에 의존한다.
- **Scope**: `runner/`, 이후 이 실행기에 올리는 모든 프로그램
- **Date**: 2026-11-17
- **Status**: active

### AD-002
- **Decision**: 검증용과 운영용 실행기를 따로 두고, 각각 자기 결과 구역에만 쓸 수 있게 Azure 권한을 나눈다.
- **Reason**: 검토 없이 올린 프로그램의 결과가 운영 결과에 섞이는 것을 코드가 아니라 권한으로 막는다.
- **Trade-off**: 실행기와 권한 설정이 두 벌이다.
- **Scope**: `infra/`, `runner/storage`, `api/services/run_service`
- **Date**: 2026-11-17
- **Status**: active

### AD-003
- **Decision**: 프로그램에 주는 입력은 현행 파일 이름·형식·인코딩 그대로 만든다. 수집 원본은 따로 보관하고 입력 구성 단계가 변환한다.
- **Reason**: 프로그램이 파일 이름과 컬럼 순서에 의존한다. 형식을 바꾸면 현행 PC와 결과를 비교할 수 없다.
- **Trade-off**: 인코딩이 섞인 현행 형식(utf-8-sig, cp949, UTF-16)을 그대로 안고 간다. 통일은 본사업 과제다.
- **Scope**: `prep/`, `adf/`, 파일 올리기 경로
- **Date**: 2026-11-17
- **Status**: active

## Handoff

