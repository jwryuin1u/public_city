"""tasks.md 생성기. 실행: python3 gen_tasks.py tasks.md  (작업·확인 항목 표를 고친 뒤 다시 만든다)"""
import sys
from collections import OrderedDict

OUT = sys.argv[1]

RUNS = {
    "unit": "pytest tests/unit -v",
    "api": "pytest tests/api -v",
    "azure": "pytest tests/azure -v",
}
GATE = {"quick": "pytest tests/unit -v", "full": "pytest tests/unit tests/api -v",
        "build": "ruff check .; ruff format --check .; az bicep build --file infra/main.bicep; pytest tests -v"}

PHASES = OrderedDict([
    (1, "기반과 현행 재현"), (2, "실행 틀"), (3, "입력 검증"), (4, "업무 규칙과 실행 엮기"),
    (5, "입력 구성"), (6, "Azure 환경"), (7, "기록과 API 기반"), (8, "검증 실행 서비스"),
    (9, "검증 실행 경로와 화면"), (10, "이상치 질문·답변과 재테스트"), (11, "운영 실행과 승인 서비스"),
    (12, "운영 경로와 화면"), (13, "자동 수집, 자동 시작, 알림, 측정"),
])

# task: key, phase, title, what, where, deps, reuses, req, grp(unit/api/azure/None), testfile, checks, extra_done
# check: (req, ac, claim, testname)
T = []
def t(key, phase, title, what, where, deps, reuses, req, grp, testfile, checks, extra=()):
    T.append(dict(key=key, phase=phase, title=title, what=what, where=where, deps=deps, reuses=reuses,
                  req=req, grp=grp, testfile=testfile, checks=checks, extra=list(extra)))

# ---------- Phase 1
t("a1", 1, "프로젝트 설정 파일", "테스트·코드 검사 도구와 라이브러리 버전을 고정한 프로젝트 설정을 만든다", "`pyproject.toml`",
  [], "없음", "RUN-01", None, None, [],
  ["pytest와 ruff가 설정되어 `ruff check .`이 통과한다", "pandas 3.0.5, numpy 2.5.3, openpyxl 3.1.5로 버전이 고정되어 있다"])
t("a2", 1, "기준 데이터 목록", "고객이 준 기준 입력과 현행 PC 결과 파일의 이름·행 수·내용 지문 목록을 만든다", "`tests/fixtures/baseline_manifest.json`",
  ["a1"], "고객 제공 기준 입력·결과 폴더 (후보 2026-11-18)", "RUN-01", None, None, [],
  ["기준 입력 9종과 PC 결과 파일 전부, 카테고리를 뺀 시험 입력이 목록에 있다", "실데이터는 저장소에 넣지 않고 위치만 적는다"])
t("a3", 1, "현행 재현 확인 보고서", "현행 pipeline.py를 기준 입력으로 실행해 설계의 가정 6개를 확인하고 결과를 적는다 (2026-11-23 1차 작성. Linux와 PC 결과 일치만 미확인)", "`docs/reproduction-report.md`",
  ["a2"], "고객 제공 pipeline.py, settings.json, CLAUDE.md", "RUN-01", None, None, [],
  ["가정 6개(경로만 바꿔 실행됨, settings.json 주입, 날짜 고정 가능 여부, 두 번 실행한 결과가 같음, Linux 결과가 같음, 현행 결과가 규칙 5개를 통과함)마다 확인 결과와 근거가 있다 (5개 작성됨. Linux 결과 일치는 PC 결과 수령 후)",
   "확인되지 않은 가정마다 설계에 주는 영향과 대응이 적혀 있다", "전체 추출 입력의 실행 시간과 메모리 사용량이 적혀 있다"])
t("a4", 1, "실행 이미지", "Python과 라이브러리 버전, 시간대, 제한 사용자를 고정한 실행 이미지를 정의한다", "`runner/Dockerfile`",
  ["a1"], "없음", "RUN-01", "unit", "test_environment.py",
  [("RUN-01", 2, "실행 환경이 Python 3.14.7, pandas 3.0.5, numpy 2.5.3, openpyxl 3.1.5, 시간대 Asia/Seoul이다", "test_versions_and_timezone")])

# ---------- Phase 2
t("b1", 2, "실행 지시서 읽기", "실행 지시서를 읽고 필수 항목을 확인한다", "`runner/instruction.py`",
  [], "없음", "RUN-01", "unit", "test_instruction.py", [],
  ["필수 항목(실행 ID, 모드, 프로그램 버전, 파라미터, 입력 일자, 마스터 버전)이 빠진 지시서를 거절한다"])
t("b2", 2, "저장소 접근", "구역별 읽기·쓰기 기능과 테스트용 로컬 폴더 구현을 만든다", "`runner/storage.py`",
  [], "없음", "ISO-01", "unit", "test_storage.py", [],
  ["입력 구역과 프로그램 구역에는 쓰기 기능이 없다", "결과는 지시서의 모드에 맞는 구역(`test/` 또는 `prod/`)에만 쓴다"])
t("b3", 2, "작업 폴더 구성", "입력 묶음, 마스터, 프로그램을 현행 INPUT 폴더와 같은 모양으로 놓는다", "`runner/workspace.py`",
  ["b1", "b2"], "현행 INPUT 폴더의 파일 이름 규칙", "MST-01", "unit", "test_workspace.py",
  [("MST-01", 3, "실행은 종류별로 가장 최근 마스터 버전을 쓰고 그 버전이 실행 기록에 남는다", "test_latest_master_version_used_and_recorded"),
   ("EDGE-01", 3, "올린 버전이 없는 마스터 종류는 그 파일 없이 실행하고 입력 검증 결과에 경고로 남는다", "test_missing_master_is_warning")])
t("b4", 2, "settings.json 생성", "지시서의 파라미터로 현행 settings.json을 만든다", "`runner/settings_file.py`",
  ["b1"], "현행 settings.json의 키 이름", "PARAM-01", "unit", "test_settings_file.py",
  [("PARAM-01", 3, "실행 시점의 파라미터 16개 값 전체가 실행 기록에 사본으로 남는다", "test_parameter_snapshot_in_record")])
t("b5", 2, "프로그램 실행", "pipeline.py를 제한 사용자로, 시간 상한을 두고 실행한다", "`runner/engine.py`",
  ["b3", "b4"], "고객 pipeline.py (수정 없음)", "RUN-01", "unit", "test_engine.py",
  [("RUN-01", 6, "프로그램이 오류로 끝나면 상태가 `실행오류`이고 로그 마지막 200줄이 저장된다", "test_program_error_keeps_last_200_log_lines"),
   ("RUN-01", 7, "실행이 30분을 넘으면 중단되고 상태 `실행오류`, 사유 `시간 초과`가 된다", "test_timeout_stops_run"),
   ("ISO-01", 3, "프로그램은 저장소 접근 권한이 없는 별도 사용자로 실행된다", "test_program_runs_as_restricted_user"),
   ("EDGE-01", 4, "결과 파일 없이 정상 종료하면 상태 `실행오류`, 사유 `결과 없음`이 된다", "test_no_output_is_error")])
t("b6", 2, "실행 기록 작성", "실행의 상태와 결과를 한 파일로 쓴다", "`runner/record.py`",
  ["b1"], "없음", "RUN-01", "unit", "test_record.py",
  [("RUN-01", 9, "실행 기록에 모드, 요청자, 프로그램 버전, 파라미터 사본, 입력 일자, 마스터 버전, 시작·종료 시각, 상태가 있다", "test_record_has_all_fields"),
   ("VAL-01", 9, "입력 검증 항목별 결과(통과, 경고, 실패)가 실행 기록에 저장된다", "test_input_check_results_saved")])

# ---------- Phase 3
t("c1", 3, "재고 기준 컬럼 등록", "기준 입력 합본 CSV의 72개 컬럼 이름을 순서대로 기준으로 등록한다", "`runner/baseline_columns.json`",
  [], "기준 입력 합본 CSV의 헤더", "VAL-01", None, None, [],
  ["72개 컬럼 이름이 기준 입력 합본 CSV와 같은 순서로 들어 있다"])
t("c2", 3, "입력 검증: 필수 파일", "재고·판매예측·코드표 5종의 존재를 확인한다", "`runner/input_checks.py`",
  [], "현행 파일 이름 규칙", "VAL-01", "unit", "test_input_checks.py",
  [("VAL-01", 1, "재고 스냅샷이나 판매예측 파일이 없으면 프로그램을 실행하지 않고 상태가 `입력실패`다", "test_missing_required_file_fails"),
   ("VAL-01", 2, "코드표 5종 중 하나라도 없으면 프로그램을 실행하지 않고 상태가 `입력실패`다", "test_missing_code_table_fails")])
t("c3", 3, "입력 검증: 재고 컬럼", "재고 파일의 컬럼 이름과 순서를 기준과 대조한다", "`runner/input_checks.py` (수정)",
  ["c1", "c2"], "c1의 기준 컬럼", "VAL-01", "unit", "test_input_checks.py",
  [("VAL-01", 3, "재고 컬럼의 이름이나 순서가 기준 72개와 다르면 `입력실패`이고 다른 컬럼의 위치와 이름이 남는다", "test_column_mismatch_names_position")])
t("c4", 3, "입력 검증: 카테고리와 점", "재고에 등록된 대상 카테고리와 10개 점이 모두 있는지 확인한다", "`runner/input_checks.py` (수정)",
  ["c3"], "없음", "VAL-01", "unit", "test_input_checks.py",
  [("VAL-01", 4, "등록된 대상 카테고리 중 없는 것이 있으면 `입력실패`이고 빠진 카테고리 이름이 남는다 (시험 입력: FOOD 제외)", "test_missing_category_names_category"),
   ("VAL-01", 5, "10개 점 중 없는 점이 있으면 `입력실패`이고 빠진 점 이름이 남는다", "test_missing_store_names_store")])
t("c5", 3, "입력 검증: 갱신 주기", "재고 1일, 판매예측 7일 초과를 모드에 따라 처리한다 (공헌이익은 파일이 있을 때만 35일)", "`runner/input_checks.py` (수정)",
  ["c4"], "입력 묶음 명세서의 수집 시각", "VAL-01", "unit", "test_input_checks.py",
  [("VAL-01", 6, "운영 실행에서 갱신 주기를 넘은 입력이 있으면 프로그램을 실행하지 않고 상태가 `확인대기`다", "test_stale_input_waits_in_prod_mode"),
   ("VAL-01", 8, "검증 실행에서는 갱신 주기 초과를 경고로만 기록하고 실행을 계속한다", "test_stale_input_is_warning_in_test_mode")])

# ---------- Phase 4
rules = [("c6", "총량 보존", 1, "배분 전후 총량이 다른 SKU가 있으면 `총량 보존`이 위반이고 위반 SKU 수가 남는다", "test_total_conservation_violation", []),
         ("c7", "최소보장", 2, "양도 후 보유일수가 최소보장일수보다 작은 건이 있으면 `최소보장`이 위반이고 위반 건수가 남는다 (판정: 배분후 재고 < 내림(판매량 × 일수))", "test_min_days_violation", ["c6"]),
         ("c8", "그룹 내 이동", 3, "같은 양수도 그룹이 아닌 점 사이의 이동이 있으면 `그룹 내 이동`이 위반이고 위반 건수가 남는다", "test_cross_group_transfer_violation", ["c7"]),
         ("c9", "발송 한도", 4, "한 점이 내보낸 수량의 합이 보유 수량보다 크면 `발송 한도`가 위반이고 위반 건수가 남는다", "test_send_over_stock_violation", ["c8"]),
         ("c10", "전환 한도", 5, "전환 신청수량이 배치 가용수량보다 크면 `전환 한도`가 위반이고 위반 건수가 남는다", "test_conversion_over_batch_violation", ["c9"])]
for k, name, ac, claim, tn, deps in rules:
    t(k, 4, f"업무 규칙: {name}", f"결과 파일에서 규칙 `{name}`을 확인한다", "`runner/rules.py`" + ("" if k == "c6" else " (수정)"),
      deps, "고객 CLAUDE.md의 불변식 정의", "RULE-01", "unit", "test_rules.py", [("RULE-01", ac, claim, tn)])
t("c11", 4, "업무 규칙: 종합 판정", "규칙 5개의 결과로 실행 상태를 정한다", "`runner/rules.py` (수정)",
  ["c10"], "없음", "RULE-01", "unit", "test_rules.py",
  [("RULE-01", 6, "규칙 5개 중 하나라도 위반이면 실행 상태가 `규칙위반`이다", "test_any_violation_sets_status")])
t("c12", 4, "요약 건수", "결과 파일에서 요약 건수 5개를 뽑는다", "`runner/summary.py`",
  ["c11"], "검토리포트 엑셀의 요약 시트", "RULE-01", "unit", "test_summary.py",
  [("RULE-01", 7, "규칙을 모두 통과하면 상태가 `완료`이고 요약 건수 5개가 저장된다 (2026-11-18 입력 재실행: 13,887 / 45 / 43 / 4,780 / 2,162)", "test_all_pass_saves_five_counts")])
t("c13", 4, "단계 엮기", "지시서 읽기부터 실행 기록 쓰기까지 단계를 순서대로 돌린다", "`runner/main.py`",
  ["c12"], "b1~b6, c2~c12", "RUN-01", "unit", "test_main.py",
  [("RUN-01", 3, "정상 종료한 검증 실행의 결과 파일이 `test/<실행ID>/`에 현행 파일 이름으로 저장된다", "test_test_run_output_path"),
   ("OPS-01", 3, "정상 종료한 운영 실행의 결과 파일이 `prod/YYYYMMDD/<실행ID>/`에 저장된다", "test_prod_run_output_path")])

# ---------- Phase 5
t("d1", 5, "고객 합본 스크립트 편입", "고객의 merge_excel_to_csv.py를 수정 없이 넣고 호출 경로를 만든다", "`prep/vendor/merge_excel_to_csv.py`",
  [], "고객 merge_excel_to_csv.py", "INPUT-01", "unit", "test_merge.py",
  [("INPUT-01", 3, "재고 카테고리별 엑셀을 올리면 합본 CSV 1개가 만들어진다 (기준 입력: 고객 PC 합본과 내용 지문이 같다)", "test_six_files_merge_matches_baseline")])
t("d2", 5, "재고 컬럼 배치", "수집한 재고 원본을 기준 72개 컬럼 순서로 배치한다", "`prep/inventory_layout.py`",
  [], "c1의 기준 컬럼", "INPUT-01", "unit", "test_inventory_layout.py",
  [("INPUT-01", 5, "기준 72개 컬럼을 만들 수 없으면 입력 묶음이 `실패`이고 빠진 컬럼 이름이 남는다", "test_missing_source_column_fails")])
t("d3", 5, "현행 형식으로 쓰기", "재고·판매예측·공헌이익·코드표를 현행 파일 이름과 형식으로 쓴다", "`prep/formats.py`",
  ["d2"], "고객 PDF 2-1의 파일 형식", "INPUT-01", "unit", "test_formats.py",
  [("INPUT-01", 1, "`input/YYYYMMDD/`에 기간계 입력(재고, 판매예측, 코드표 5종)이 현행 이름과 형식(재고 utf-8-sig, 코드표 cp949)으로 만들어진다", "test_eight_files_in_current_formats")])
t("d4", 5, "입력 묶음 명세서", "파일별 출처, 수집 시각, 행 수, 내용 지문을 명세서로 쓴다", "`prep/manifest.py`",
  [], "없음", "INPUT-01", "unit", "test_manifest.py",
  [("INPUT-01", 2, "입력 묶음마다 파일별 출처, 수집 시각, 행 수, 내용 지문이 적힌 명세서가 있다", "test_manifest_has_source_time_rows_hash")])
t("d5", 5, "입력 구성 엮기", "일자의 원본과 올린 파일로 입력 묶음을 만들고 상태를 정한다", "`prep/main.py`",
  ["d1", "d3", "d4"], "d1~d4", "INPUT-01", "unit", "test_prep_main.py",
  [("COL-01", 5, "매일 수집하지 않는 원천(판매예측)은 가장 최근 수집분이 그 일자 입력 묶음에 들어간다", "test_latest_non_daily_source_reused"),
   ("INPUT-01", 4, "자동 수집되지 않는 원천의 파일을 올리면 입력 묶음에 들어가고 명세서의 출처가 `올린 파일`이다", "test_uploaded_file_marked_in_manifest")])

# ---------- Phase 6
t("e1", 6, "저장소 정의", "저장소와 구역 4개(입력, 프로그램, 운영 결과, 검증 결과)를 정의한다", "`infra/storage.bicep`",
  [], "없음", "ISO-01", None, None, [], ["구역 4개가 만들어진다", "프로그램 구역의 파일은 덮어쓸 수 없게 설정된다"])
t("e2", 6, "실행기 ID와 구역별 권한", "검증용·운영용 실행기 ID를 만들고 구역별 읽기·쓰기 권한을 준다", "`infra/identities.bicep`",
  ["e1"], "없음", "ISO-01", "azure", "test_isolation.py",
  [("ISO-01", 1, "검증용 실행기가 운영 결과 구역이나 입력 구역에 쓰려고 하면 거절된다", "test_test_runner_cannot_write_prod_or_input")])
t("e3", 6, "네트워크와 외부 통신 차단", "실행기가 저장소 외의 주소로 나갈 수 없게 네트워크를 정의한다", "`infra/network.bicep`",
  ["e1"], "없음", "ISO-01", "azure", "test_isolation.py",
  [("ISO-01", 2, "실행 중인 프로그램이 저장소 밖의 주소로 접속하려고 하면 차단된다", "test_program_cannot_reach_outside")])
t("e4", 6, "실행기 정의", "검증용·운영용 실행기와 입력 구성 실행기를 정의한다 (시간 상한 30분)", "`infra/jobs.bicep`",
  ["e2", "e3"], "a4의 실행 이미지", "RUN-01", "azure", "test_concurrency.py",
  [("RUN-01", 8, "두 실행이 같은 시각에 돌아도 각각 별도 컨테이너에서 실행되고 결과가 단독 실행과 같다", "test_two_runs_match_single_runs")])
t("e5", 6, "기록 DB 정의", "Azure SQL Database를 정의한다", "`infra/sql.bicep`",
  [], "없음", "HIST-01", None, None, [], ["DB가 만들어지고 관리 API의 ID만 접근할 수 있다"])
t("e6", 6, "웹 앱 정의", "관리 화면·API의 웹 앱과 사내 계정 로그인을 정의한다", "`infra/webapp.bicep`",
  ["e5"], "없음", "AUTH-01", "azure", "test_login.py",
  [("AUTH-01", 1, "로그인하지 않은 요청은 사내 계정 로그인 화면으로 보내진다", "test_anonymous_request_redirects_to_login")])
t("e7", 6, "전체 배포 정의와 기준 입력 일치 확인", "모든 정의를 하나로 엮어 배포하고 기준 입력의 결과를 현행 PC와 대조한다", "`infra/main.bicep`",
  ["e4", "e6"], "e1~e6, a2의 기준 데이터 목록", "RUN-01", "azure", "test_baseline.py",
  [("RUN-01", 10, "기준 입력과 운영 파라미터로 현행 pipeline.py를 실행한 결과가 현행 PC에서 같은 날 실행한 결과와 셀 단위로 같다", "test_baseline_matches_pc_result_cell_by_cell")])

# ---------- Phase 7
t("f1", 7, "기록 테이블 정의", "프로그램 버전, 파라미터 세트, 입력 묶음, 마스터 버전, 실행, 입력 검증 결과, 규칙 결과, 비교, 승인 테이블을 정의한다", "`api/repo/models.py`",
  [], "설계서의 데이터 모델 표", "HIST-01", None, None, [], ["테이블 9개가 설계서의 항목대로 정의되어 있다"])
t("f2", 7, "DB 연결", "기록 DB 연결과 테이블 생성을 만든다", "`api/repo/db.py`",
  ["f1"], "없음", "HIST-01", None, None, [], ["빈 DB에 테이블 9개가 만들어진다"])
t("f3", 7, "로그인과 역할 확인", "요청의 사용자와 역할을 확인하고 역할 밖의 기능을 거절한다", "`api/auth.py`",
  [], "없음", "AUTH-01", "api", "test_auth.py",
  [("AUTH-01", 2, "자기 역할에 없는 기능을 호출하면 거절되고 \"권한이 없습니다\"가 보인다", "test_wrong_role_is_rejected"),
   ("AUTH-01", 3, "역할은 5개(현업 사용자, S&OP 담당자, MD, IT혁신팀, 바이어)이고 한 사용자가 여러 역할을 가질 수 있다", "test_user_can_hold_multiple_roles")])
t("f4", 7, "저장소 호출", "관리 API가 저장소에 프로그램·마스터·올린 파일을 쓰고 결과를 읽는 기능을 만든다", "`api/clients/blob_client.py`",
  [], "없음", "CODE-01", "azure", "test_blob_client.py", [],
  ["프로그램 파일을 올리고 다시 읽으면 내용 지문이 같다", "이미 있는 프로그램 버전 경로에 다시 쓰면 실패한다"])
t("f5", 7, "실행기 호출", "모드에 맞는 실행기를 시작하고 상태를 읽는 기능을 만든다", "`api/clients/job_client.py`",
  [], "없음", "RUN-01", "azure", "test_job_client.py", [],
  ["검증 모드는 검증용 실행기를, 운영 모드는 운영용 실행기를 시작한다", "시작한 실행의 상태(진행 중, 성공, 실패)를 읽는다"])
t("f6", 7, "앱 조립", "경로, 로그인, DB 연결을 하나의 웹 앱으로 엮는다", "`api/app.py`",
  ["f2", "f3"], "없음", "AUTH-01", None, None, [], ["앱이 시작되고 상태 확인 경로가 응답한다"])

# ---------- Phase 8
t("g1", 8, "프로그램 등록 검사", "올린 파일의 문법과 불러오는 라이브러리를 검사한다", "`api/services/code_check.py`",
  [], "실행 이미지의 라이브러리 목록", "CODE-01", "unit", "test_code_check.py",
  [("CODE-01", 3, "문법 오류가 있는 파일은 등록이 거절되고 오류가 난 줄 번호가 보인다", "test_syntax_error_shows_line_number"),
   ("CODE-01", 4, "실행 환경에 없는 라이브러리를 불러오는 파일은 등록이 거절되고 그 라이브러리 이름이 보인다", "test_unknown_library_is_named")])
t("g2", 8, "파라미터 서비스", "운영 파라미터의 초기값, 범위 확인, 변경 이력을 만든다", "`api/services/parameter_service.py`",
  [], "고객 PDF 4-2의 현재값과 입력 범위", "PARAM-01", "api", "test_parameter_service.py",
  [("PARAM-01", 1, "운영 파라미터 16개가 초기값(기본커버 7, 최소보장 3, 프리미엄 0/0/0, 이동생략 0.0, 최소보충 3, 제조경과 21, 유효임박 6, 통물 한정 false, 점센터 보호 3, 경고 민감도 2.0, 과다 이동 10, 미등록 브랜드 양수도 제외, 반입경과 22, 헤더 행 2, 점센터 이동 제외 점 인천공항T1·인천공항T2, 점센터 이동 제외 카테고리 EYEWEAR)으로 시작한다", "test_initial_prod_parameters"),
   ("PARAM-01", 4, "허용 범위 밖의 값은 저장이 거절되고 허용 범위가 보인다 (예: 최소보장일수 31)", "test_out_of_range_value_rejected"),
   ("PARAM-01", 5, "운영 파라미터를 바꾸면 이전 값, 변경자, 변경 일시, 사유가 이력에 남는다", "test_prod_change_keeps_history")])
t("g3", 8, "마스터 서비스", "마스터 파일을 버전으로 보관하고 시트 구성을 확인한다", "`api/services/master_service.py`",
  [], "고객 PDF 2-5의 시트 목록", "MST-01", "api", "test_master_service.py",
  [("MST-01", 1, "마스터 파일을 올리면 새 버전으로 보관되고 이전 버전이 남아 있다", "test_upload_creates_new_version_keeps_old"),
   ("MST-01", 2, "제외·전용 SKU 파일에 6개 시트 중 없는 것이 있으면 거절되고 빠진 시트 이름이 보인다", "test_missing_sheet_is_named")])
t("g4", 8, "실행 생성", "검증 실행 요청으로 실행 ID와 지시서를 만들고 검증용 실행기를 시작한다", "`api/services/run_service.py`",
  ["g2", "g3"], "f4, f5", "RUN-01", "api", "test_run_service.py",
  [("RUN-01", 1, "버전·입력 일자·파라미터로 검증 실행을 요청하면 실행 ID가 생기고 검증용 실행기가 시작된다", "test_test_run_starts_test_runner"),
   ("PARAM-01", 2, "검증 실행에서 조정한 파라미터는 그 실행에만 적용되고 운영 파라미터는 그대로다 (최소보장 5로 실행 후 운영값 3)", "test_adjusted_parameter_does_not_change_prod"),
   ("EDGE-01", 1, "입력 묶음이 없는 일자를 고르면 요청이 거절되고 선택할 수 있는 일자 목록이 보인다", "test_unknown_input_date_lists_available_dates"),
   ("EDGE-01", 5, "실행기를 시작하지 못하면 상태 `실행오류`, 사유 `실행기 시작 실패`가 된다", "test_runner_start_failure_recorded")])
t("g5", 8, "실행 상태 동기화", "실행기 상태와 결과 폴더의 실행 기록을 읽어 기록 DB에 반영한다", "`api/services/run_sync.py`",
  ["g4"], "설계서의 실행 기록 항목", "HIST-01", "api", "test_run_sync.py", [],
  ["실행 기록의 상태, 요약 건수, 입력 검증 결과, 규칙 결과가 DB에 반영된다", "같은 실행을 두 번 동기화해도 기록이 중복되지 않는다"])
t("g6", 8, "결과 비교", "두 실행의 건수 차이와 달라진 SKU를 계산한다", "`api/services/compare.py`",
  ["g5"], "양수도·재고전환 엑셀의 컬럼", "CMP-01", "api", "test_compare.py",
  [("CMP-01", 2, "두 실행의 건수 4종(점간 이동 지시, 온·오프 전환 지시, 미충전 부족분, 발주 검토 대상) 차이가 보인다", "test_four_count_differences"),
   ("CMP-01", 3, "이동 수량이나 전환 수량이 달라진 SKU의 목록이 보인다", "test_changed_sku_list"),
   ("CMP-01", 4, "비교 상대의 실행일이 다르면 \"실행일이 달라 날짜 판정 차이가 섞일 수 있음\"이 표시된다", "test_different_run_date_warning"),
   ("CMP-01", 5, "두 결과가 모두 같으면 \"차이 없음\"이 표시된다", "test_identical_results_show_no_difference")])
t("g7", 8, "비교용 동반 실행", "같은 날의 운영 버전 결과가 없으면 운영 버전을 같은 입력으로 함께 실행한다", "`api/services/run_service.py` (수정)",
  ["g4"], "g4", "CMP-01", "api", "test_run_service.py",
  [("CMP-01", 1, "검증 실행이 완료되고 같은 입력 일자·같은 실행일의 운영 버전 결과가 없으면 운영 버전이 같은 입력으로 함께 실행된다", "test_companion_prod_version_run_created")])
t("g8", 8, "검증 결과 내려받기", "검증 실행 결과에 검증용 표시를 붙여 내려준다", "`api/services/download.py`",
  ["g5"], "없음", "RUN-01", "api", "test_download.py",
  [("RUN-01", 4, "검증 실행 결과 파일은 이름 앞에 `TEST_`가 붙어 내려받아진다", "test_test_run_file_has_prefix"),
   ("RUN-01", 5, "검증 실행 결과 엑셀은 각 시트 첫 줄에 \"검증 실행 결과 - ERP 업로드 금지\"가 들어간다", "test_test_run_sheet_has_first_row_notice")])

# ---------- Phase 9
t("h1", 9, "프로그램 버전 경로", "프로그램 등록과 버전 목록 경로를 만든다", "`api/routes/code_versions.py`",
  [], "g1, f4", "CODE-01", "api", "test_code_versions.py",
  [("CODE-01", 1, "pipeline.py를 이름·메모와 함께 등록하면 새 버전 ID가 생기고 상태가 `등록됨`이다", "test_register_creates_version"),
   ("CODE-01", 2, "등록된 버전의 파일을 바꾸거나 지우는 요청은 거절된다", "test_registered_file_cannot_change"),
   ("CODE-01", 5, "내용이 같은 버전이 이미 있으면 새 버전이 생기지 않고 기존 버전 이름이 보인다", "test_same_content_returns_existing_version")])
t("h2", 9, "파라미터 경로", "운영 파라미터 조회와 변경 경로를 만든다", "`api/routes/parameters.py`",
  [], "g2", "PARAM-01", "api", "test_parameters_route.py", [],
  ["조회는 모든 역할이 할 수 있다", "변경은 IT혁신팀만 할 수 있다"])
t("h3", 9, "마스터 경로", "마스터 올리기와 버전 목록 경로를 만든다", "`api/routes/masters.py`",
  [], "g3", "MST-01", "api", "test_masters_route.py", [],
  ["올리기는 MD만 할 수 있다", "버전 목록이 최신순으로 보인다"])
t("h4", 9, "실행 경로", "실행 요청, 이력, 상세, 실행 계속 경로를 만든다", "`api/routes/runs.py`",
  [], "g4, g5, g6", "HIST-01", "api", "test_runs_route.py",
  [("VAL-01", 7, "`확인대기` 실행에 [실행 계속]을 누르면 프로그램 실행이 시작된다", "test_continue_starts_waiting_run"),
   ("HIST-01", 1, "실행 이력에 일시, 모드, 실행자, 프로그램 버전, 입력 일자, 마스터 버전, 요약 건수, 소요 시간, 상태가 최신순으로 보인다", "test_history_fields_newest_first"),
   ("HIST-01", 2, "입력 묶음, 결과 파일, 실행 기록을 지우는 경로가 없다", "test_no_delete_routes")])
t("h5", 9, "내려받기 경로", "결과 파일 목록과 내려받기 경로를 만든다", "`api/routes/downloads.py`",
  [], "g8", "RUN-01", "api", "test_downloads_route.py", [],
  ["검증 실행 결과는 그 실행을 요청한 현업 사용자와 IT혁신팀이 내려받을 수 있다"])
t("h6", 9, "화면 경로", "화면 8개의 주소와 역할별 메뉴를 만든다", "`api/routes/pages.py`",
  [], "f3", "AUTH-01", "api", "test_pages.py", [],
  ["역할에 해당하는 화면만 메뉴에 보인다"])
for k, f, name, req, items in [
    ("h7", "code_versions.html", "S1 내 프로그램 버전", "CODE-01", "파일 선택, 이름, 메모, [등록], 버전 목록(이름, 상태, 등록 일시)"),
    ("h8", "run_new.html", "S2 검증 실행", "RUN-01", "프로그램 버전, 입력 일자, 비교 대상, 파라미터 16개(운영값이 채워진 상태, 목록 값 2개 포함), [검증 실행]"),
    ("h9", "run_result.html", "S3 검증 결과", "CMP-01", "상태, 입력 검증 결과, 규칙 5개 결과, 요약 건수, 건수 차이, 달라진 SKU, 일일결과리포트, 내려받기, [운영 반영 요청]"),
    ("h10", "masters.html", "S5 마스터 데이터", "MST-01", "종류 선택, 파일 선택, [올리기], 버전 목록")]:
    t(k, 9, f"화면: {name}", f"{name} 화면을 만든다", f"`api/templates/{f}`", ["h6"], "없음", req, "api", "test_pages.py", [],
      [f"화면에 다음이 있다: {items}", "빈 목록, 처리 중, 오류, 권한 없음 상태가 각각 문구로 보인다"])

# ---------- Phase 10: 이상치 질문·답변과 재테스트
t("q1", 10, "이상치 추출", "결과 파일의 검토리포트에서 이상치(이동 건수 이상, 과다 이동, 미충전 부족분)를 뽑아 실행 기록에 넣는다", "`runner/anomalies.py`",
  [], "검토리포트 엑셀의 모니터1·모니터2·미충전 부족분 시트", "QA-01", "unit", "test_anomalies.py",
  [("QA-01", 1, "검증 실행이 완료되면 이상치(이동 건수 이상, 과다 이동, 미충전 부족분)가 종류·상품·내용·문의 대상과 함께 보인다", "test_anomalies_extracted_from_review_report")])
t("q2", 10, "임시 제외 반영", "지시서의 임시 제외 상품을 제외·전용 SKU 마스터의 사본에 추가해 작업 폴더에 놓는다", "`runner/workspace.py` (수정)",
  [], "b3, 제외·전용 SKU 엑셀의 양수도제외상품·온오프전환제외상품 시트", "QA-01", "unit", "test_workspace.py",
  [("QA-01", 11, "이동 제외 답변은 제외·전용 SKU 마스터의 임시 사본에만 추가되고 등록된 마스터 버전은 그대로다", "test_temp_exclusion_does_not_change_master")])
t("q3", 10, "질문 목록 만들기와 보내기", "이상치로 질문 목록을 만들고 CSV로 내보내고 보냄 상태로 바꾼다", "`api/services/question_service.py`",
  [], "g5, g6", "QA-01", "api", "test_question_service.py",
  [("QA-01", 2, "질문 목록을 만들면 이상치마다 문의 대상(프로그램 작성자 또는 해당 점 바이어)과 질문 문안이 생긴다", "test_question_list_has_recipient_and_text"),
   ("QA-01", 3, "질문 목록을 내려받으면 질문번호, 받는 사람, 상품코드, 상품명, 이상 내용, 질문, 답변 선택, 답변 내용 열을 가진 CSV가 나온다", "test_question_csv_columns"),
   ("QA-01", 4, "질문을 보내면 질문 목록의 상태가 `보냄`이 되고 보낸 시각이 기록된다", "test_send_sets_status_and_time")])
t("q4", 10, "답변 기록", "화면 입력과 파일 업로드로 들어온 답변을 기록한다", "`api/services/question_service.py` (수정)",
  ["q3"], "없음", "QA-01", "api", "test_question_service.py",
  [("QA-01", 5, "화면에서 답변 유형과 내용을 저장하면 답변자, 일시와 함께 기록된다", "test_screen_answer_recorded_with_who_and_when"),
   ("QA-01", 6, "답변이 적힌 질문 목록 파일을 올리면 질문번호가 같은 질문에 그 행의 답변이 기록된다", "test_uploaded_answers_matched_by_number"),
   ("QA-01", 7, "허용되지 않은 답변 유형이 적힌 행은 기록되지 않고 질문번호와 허용 유형이 보인다", "test_invalid_answer_type_reported"),
   ("QA-01", 8, "바이어가 자기에게 온 질문이 아닌 질문에 답하면 거절된다", "test_buyer_cannot_answer_others_question")])
t("q5", 10, "답변 반영 계획", "답변 유형별로 반영 계획을 만든다", "`api/services/question_service.py` (수정)",
  ["q4"], "없음", "QA-01", "api", "test_question_service.py",
  [("QA-01", 9, "답변이 1건 이상이면 반영 계획(파라미터 변경, 이동 제외 상품, 사유 확인 항목, 프로그램 수정 필요 항목, 미답변 항목)이 보인다", "test_plan_groups_answers_by_type")])
t("q6", 10, "답변 반영 재테스트", "반영 계획으로 지시서를 만들어 검증 실행을 시작한다", "`api/services/run_service.py` (수정)",
  ["q5", "q2"], "g4", "QA-01", "api", "test_run_service.py",
  [("QA-01", 10, "재테스트는 원래 실행의 프로그램 버전·입력 일자에 파라미터 조정 답변의 제안값과 이동 제외 답변의 상품을 반영해 시작된다", "test_retest_applies_parameter_and_exclusions")])
t("q7", 10, "이상치 처리 상태", "재테스트 결과에서 이상치별 처리 상태와 원래 실행 대비 차이를 계산한다", "`api/services/compare.py` (수정)",
  ["q6"], "g6", "QA-01", "api", "test_compare.py",
  [("QA-01", 12, "재테스트가 완료되면 이상치마다 처리 상태(해소, 확인됨, 남음)와 원래 실행 대비 건수 차이가 보인다", "test_anomaly_status_after_retest")])
t("q8", 10, "질문·답변 경로", "질문 목록 만들기, 내려받기, 보내기, 답변, 파일 올리기, 재테스트 경로를 만든다", "`api/routes/questions.py`",
  ["q7"], "q3~q7", "QA-01", "api", "test_questions_route.py", [],
  ["만들기·보내기·파일 올리기·재테스트는 현업 사용자만 할 수 있다", "바이어는 질문·답변 화면만 볼 수 있다"])
t("q9", 10, "화면: 질문·답변", "질문·답변 화면을 만든다", "`api/templates/questions.html`",
  ["q8"], "없음", "QA-01", "api", "test_pages.py", [],
  ["화면에 다음이 있다: 진행 단계(만들기, 보내기, 답변 받기, 재테스트), 질문과 답변 표, 질문 목록 내려받기, [질문 보내기], 답변 입력란, 파일 올리기, 반영 계획, [답변 반영해 재테스트]", "빈 목록, 처리 중, 오류, 권한 없음 상태가 각각 문구로 보인다"])

# ---------- Phase 11
t("i1", 11, "운영 실행 시작", "운영 버전·운영 파라미터·당일 입력 묶음으로 운영용 실행기를 시작한다", "`api/services/run_service.py` (수정)",
  [], "g4", "OPS-01", "api", "test_run_service_prod.py",
  [("OPS-01", 1, "[지금 실행]을 누르면 운영 버전, 운영 파라미터, 당일 입력 묶음으로 운영용 실행기가 시작된다", "test_prod_run_uses_prod_version_and_parameters"),
   ("OPS-01", 2, "당일 입력 묶음이 `준비됨`이 아니면 실행이 시작되지 않고 입력 묶음의 상태가 보인다", "test_prod_run_needs_ready_input"),
   ("OPS-01", 9, "같은 일자에 운영 실행을 다시 하면 새 실행 ID로 저장되고 이전 실행의 결과가 남아 있다", "test_rerun_keeps_previous_result"),
   ("ISO-01", 4, "상태가 `운영`이 아닌 버전을 지정한 운영 실행 요청은 거절된다", "test_prod_run_rejects_non_prod_version"),
   ("EDGE-01", 2, "운영 버전이 없으면 운영 실행 요청이 거절되고 \"운영 버전이 지정되지 않았습니다\"가 보인다", "test_prod_run_without_prod_version")])
t("i2", 11, "직전 운영 결과와 비교", "운영 실행을 직전 운영 실행과 비교한다", "`api/services/compare.py` (수정)",
  [], "g6", "OPS-01", "api", "test_compare_prod.py",
  [("OPS-01", 4, "운영 실행이 완료되면 직전 운영 실행 결과와의 건수 4종 차이가 보인다", "test_prod_run_compared_with_previous")])
t("i3", 11, "운영 결과 승인", "운영 실행의 승인과 거절 조건을 만든다", "`api/services/approval.py`",
  ["i1"], "없음", "OPS-01", "api", "test_approval.py",
  [("OPS-01", 5, "`완료`된 운영 실행을 승인하면 상태가 `승인됨`이 되고 승인자와 일시가 기록된다", "test_approve_records_approver_and_time"),
   ("OPS-01", 6, "상태가 `규칙위반`인 실행의 승인 요청은 거절된다", "test_rule_violation_cannot_be_approved")])
t("i4", 11, "운영 결과 내려받기", "승인된 운영 결과만 ERP 업로드 순서대로 내려준다", "`api/services/download.py` (수정)",
  ["i3"], "g8", "OPS-01", "api", "test_download_prod.py",
  [("OPS-01", 7, "`승인됨`이 아닌 운영 실행의 ERP 업로드 파일 내려받기는 거절된다", "test_download_requires_approval"),
   ("OPS-01", 8, "승인된 실행의 내려받기 화면에 파일이 ① 재고전환_온오프 ② 양수도 ③ 재고전환_오프온 순서로 보인다", "test_files_in_erp_upload_order")])
t("i5", 11, "운영 반영 요청과 회귀 실행", "운영 반영 요청을 받아 기준 입력으로 새 버전과 운영 버전을 실행한다", "`api/services/promotion.py`",
  ["i1"], "g4, g6", "PROMO-01", "api", "test_promotion.py",
  [("PROMO-01", 1, "검증 실행이 완료된 버전에 운영 반영을 요청하면 기준 입력으로 그 버전과 현재 운영 버전이 함께 실행된다", "test_request_starts_two_regression_runs"),
   ("PROMO-01", 2, "가장 최근 검증 실행이 `완료`가 아닌 버전의 운영 반영 요청은 거절된다", "test_request_needs_completed_test_run"),
   ("PROMO-01", 3, "회귀 실행 두 건이 끝나면 IT혁신팀에게 두 결과의 비교와 규칙 5개 결과가 보인다", "test_regression_result_shown_to_it")])
t("i6", 11, "운영 반영 승인과 반려", "운영 반영의 승인, 반려, 거절 조건을 만든다", "`api/services/promotion.py` (수정)",
  ["i5"], "없음", "PROMO-01", "api", "test_promotion.py",
  [("PROMO-01", 4, "승인하면 그 버전이 `운영`, 이전 운영 버전이 `보관`이 된다", "test_approve_switches_prod_version"),
   ("PROMO-01", 5, "반려하면 그 버전이 `반려`가 되고 의견이 기록된다", "test_reject_records_comment"),
   ("PROMO-01", 6, "새 버전의 회귀 실행이 `규칙위반`이나 `실행오류`면 승인이 거절된다", "test_failed_regression_cannot_be_approved"),
   ("CODE-01", 6, "상태가 `운영`인 버전은 항상 1개다", "test_exactly_one_prod_version")])
t("i7", 11, "이전 버전으로 되돌리기", "보관된 버전을 다시 운영 버전으로 지정한다", "`api/services/promotion.py` (수정)",
  ["i6"], "없음", "PROMO-01", "api", "test_promotion.py",
  [("PROMO-01", 7, "`보관` 버전을 되돌리면 그 버전이 `운영`, 현재 운영 버전이 `보관`이 된다", "test_rollback_switches_versions")])

# ---------- Phase 12
t("i8", 12, "운영 반영 경로", "운영 반영 요청, 승인, 반려, 되돌리기 경로를 만든다", "`api/routes/promotions.py`",
  [], "i5~i7", "PROMO-01", "api", "test_promotions_route.py", [],
  ["요청은 현업 사용자만, 승인·반려·되돌리기는 IT혁신팀만 할 수 있다"])
t("i9", 12, "입력 묶음 경로", "입력 묶음 목록, 파일 올리기, 재수집 요청 경로를 만든다", "`api/routes/input_sets.py`",
  [], "d5, f4", "INPUT-01", "api", "test_input_sets_route.py", [],
  ["파일을 올리면 그 일자의 입력 구성이 시작된다", "파일 올리기와 재수집 요청은 S&OP 담당자만 할 수 있다"])
for k, f, name, req, items in [
    ("i10", "promotion.html", "S4 운영 반영 승인", "PROMO-01", "요청 버전과 메모, 회귀 비교(건수 차이, 달라진 SKU), 규칙 5개 결과, 의견 입력, [승인], [반려]"),
    ("i11", "input_status.html", "S6 입력 상태", "VAL-01", "일자별 입력 묶음 상태, 파일별 출처와 수집 시각, 실패·경고 내용, [실행 계속], [재수집 요청], 파일 올리기"),
    ("i12", "prod_run.html", "S7 운영 실행·결과", "OPS-01", "[지금 실행], 상태, 요약 건수, 직전 결과와의 차이, 규칙 5개 결과, 일일결과리포트, 구간별 소요 시간, [승인]"),
    ("i13", "downloads.html", "S8 결과 내려받기", "OPS-01", "ERP 업로드 순서 안내, 순서대로 놓인 파일 목록, 리포트 파일")]:
    t(k, 12, f"화면: {name}", f"{name} 화면을 만든다", f"`api/templates/{f}`", ["i8", "i9"] if k == "i10" else [], "없음", req, "api", "test_pages_prod.py", [],
      [f"화면에 다음이 있다: {items}", "빈 목록, 처리 중, 오류, 권한 없음 상태가 각각 문구로 보인다"])

# ---------- Phase 13
t("j1", 13, "Data Factory 정의", "Data Factory, 수집 중계 서버 연결, 접속 정보 보관소를 정의한다", "`infra/adf.bicep`",
  [], "없음", "COL-01", None, None, [], ["Data Factory가 수집 중계 서버를 통해 접근이 승인된 원천에 연결된다", "접속 정보는 Key Vault에만 있다"])
t("j2", 13, "수집 파이프라인", "원천 조회, 원본 저장, 입력 구성 시작, 입력 준비됨 알림을 파이프라인으로 정의한다", "`adf/pl_collect_daily.json`",
  ["j1"], "d5의 입력 구성", "COL-01", "azure", "test_collect.py",
  [("COL-01", 1, "수집 시각이 되면 접근이 승인된 원천의 원본이 `raw/<원천>/YYYYMMDD/`에 저장된다", "test_scheduled_collect_writes_raw"),
   ("COL-01", 2, "한 일자의 수집이 끝나면 그 일자의 입력 구성이 시작된다", "test_collect_starts_prep"),
   ("COL-01", 3, "원천 조회가 실패하면 입력 묶음이 `실패`이고 실패한 원천 이름이 남는다", "test_source_failure_recorded_with_name")])
t("j3", 13, "재수집 호출", "관리 API가 그 일자의 수집 파이프라인을 다시 실행시키는 기능을 만든다", "`api/clients/adf_client.py`",
  ["j2"], "없음", "COL-01", "azure", "test_recollect.py",
  [("COL-01", 4, "재수집을 요청하면 그 일자의 수집이 다시 실행되고 이전 수집분이 남아 있다", "test_recollect_keeps_previous_raw")])
t("j4", 13, "입력 준비됨 수신과 자동 시작", "수집 파이프라인의 알림을 받아 자동 시작 설정에 따라 운영 실행을 시작한다", "`api/routes/internal.py`",
  [], "i1", "SCHED-01", "api", "test_internal.py",
  [("SCHED-01", 1, "자동 시작이 켜져 있을 때 입력 준비됨 알림이 오면 그 일자의 운영 실행이 시작된다", "test_auto_start_on_input_ready"),
   ("SCHED-01", 2, "자동 시작이 꺼져 있으면 입력 준비됨 알림이 와도 운영 실행이 시작되지 않는다", "test_no_auto_start_when_off"),
   ("SCHED-01", 3, "같은 일자의 입력 준비됨 알림이 다시 와도 자동 실행이 다시 시작되지 않는다", "test_duplicate_input_ready_ignored")])
t("j5", 13, "알림 보내기", "수집 실패, 입력실패, 실행 종료, 승인 요청 알림을 만든다", "`api/services/notify.py`",
  [], "없음", "NOTI-01", "api", "test_notify.py",
  [("NOTI-01", 1, "수집이 실패하면 S&OP 담당자에게 실패한 원천 이름이 담긴 알림이 간다", "test_collect_failure_notice_names_source"),
   ("NOTI-01", 2, "운영 실행이 `입력실패`가 되면 S&OP 담당자에게 실패한 검증 항목이 담긴 알림이 간다", "test_input_failure_notice_names_check"),
   ("NOTI-01", 3, "운영 실행이 `완료`나 `규칙위반`으로 끝나면 S&OP 담당자에게 상태와 요약 건수가 담긴 알림이 간다", "test_run_end_notice_has_status_and_counts"),
   ("NOTI-01", 4, "회귀 실행이 끝나면 IT혁신팀에게 승인 요청 알림이 간다", "test_regression_end_notifies_it")])
t("j6", 13, "알림 연결 정의", "메일을 보내는 Logic Apps를 정의한다", "`infra/logicapp.bicep`",
  ["j5"], "없음", "NOTI-01", None, None, [], ["관리 API가 호출하면 지정한 수신자에게 메일이 간다"])
t("j7", 13, "구간별 시각 기록", "운영 실행의 구간별 시각을 기록하고 소요 시간을 계산한다", "`api/services/timing.py`",
  [], "입력 묶음 명세서, 실행 기록", "MEAS-01", "api", "test_timing.py",
  [("MEAS-01", 1, "운영 실행마다 수집 시작, 입력 준비됨, 실행 시작, 실행 종료, 승인의 시각이 기록되고 구간별 소요 시간이 보인다", "test_five_timestamps_and_durations")])

# ---------- numbering
ids = {x["key"]: f"T{i+1}" for i, x in enumerate(T)}
phase_of = {x["key"]: x["phase"] for x in T}
for x in T:
    for d in x["deps"]:
        assert d in ids, d
        assert phase_of[d] <= x["phase"], (x["key"], d)

REQ_ORDER = ["COL-01", "INPUT-01", "VAL-01", "CODE-01", "PARAM-01", "MST-01", "RUN-01", "RULE-01", "CMP-01", "QA-01", "ISO-01",
             "AUTH-01", "OPS-01", "PROMO-01", "HIST-01", "SCHED-01", "NOTI-01", "MEAS-01", "EDGE-01"]
EXPECT = dict(zip(REQ_ORDER, [5, 5, 9, 6, 5, 3, 10, 7, 5, 12, 4, 3, 9, 7, 2, 3, 4, 1, 5]))
checks = []
for x in T:
    for (req, ac, claim, tn) in x["checks"]:
        checks.append((REQ_ORDER.index(req), ac, req, claim, x["grp"], x["testfile"], tn, x["key"]))
checks.sort()
seen = {}
for c in checks:
    seen.setdefault(c[2], []).append(c[1])
for r in REQ_ORDER:
    assert sorted(seen.get(r, [])) == list(range(1, EXPECT[r] + 1)), (r, sorted(seen.get(r, [])))
cid = {}
for i, c in enumerate(checks):
    cid[(c[2], c[1])] = f"C{i+1}"

def tests_gate(x):
    if x["grp"] is None:
        return "none", "build"
    if x["grp"] == "unit":
        return "unit", "quick"
    if x["grp"] == "api":
        return "integration", "full"
    return "integration", "build"

L = []
A = L.append
A("# 롯데면세점 재고배분 PoC Tasks\n")
A("## Execution Protocol (MANDATORY -- do not skip)\n")
A("Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, the walk, check_proofs, the Verifier and the screens sub-agent).\n")
A("**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**\n")
A("이 문서는 설계 산출물이다. 구현(Execute)은 이번 범위가 아니며, 소스와 데이터를 받고 고객 확인 사항의 답을 받은 뒤 시작한다.\n")
A("---\n")
A("**Design**: `.specs/features/allocation-poc/design.md`")
A("**Status**: Approved")
A('**Approved**: 2026-11-17 - user: "승인할게. 다음 작업 이어서 진행해줘"')
A('**Revised**: 2026-11-23 - user: "모두 너에게 맡길게. 가장 최적의 방안을 검토해서 작업 진행해줘" — 고객 자료 수령 반영 (기준 입력, 대상 카테고리, 파라미터 16개, 공헌이익 선택 입력). 근거는 `docs/reproduction-report.md`')
A('**Revised**: 2026-11-24 - user: "PoC 구현 범위에 넣어서 전부 고쳐줘" — 이상치 질문·답변과 재테스트(QA-01) 추가: Phase 10, 작업 9개, 확인 항목 12개')
A(f"**Build**: `ruff check .; ruff format --check .; az bicep build --file infra/main.bicep`")
for n, cmd in RUNS.items():
    A(f"**Run {n}**: `{cmd}`")
A("")
A("읽는 법: 작업은 T번호, 확인 항목은 C번호다. 확인 항목 하나가 명세의 수용 기준 하나에 대응하고, `Proof`는 그것을 증명하는 테스트다. 파일 경로는 새로 만들 프로젝트 저장소 기준이다.\n")
A(f"작업 {len(T)}개, 단계 {len(PHASES)}개, 확인 항목 {len(checks)}개.\n")
A("---\n")
A("## Test Coverage Matrix\n")
A("> Generated from codebase, project guidelines, and spec - confirm before Execute. Guidelines found: none - strong defaults applied. 이 저장소에는 대상 코드와 기존 테스트가 없다. 테스트 도구는 명세의 가정(pytest)을 따른다. 아래 명령은 제안이며 프로젝트 저장소를 만들 때 확정한다.\n")
A("| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |")
A("| --- | --- | --- | --- | --- |")
A("| 실행 틀 (`runner/*.py`): 입력 검증, 업무 규칙, 실행, 기록 | unit | 수용 기준과 1:1, 예외 상황 전부 | `tests/unit/test_*.py` | `pytest tests/unit -v` |")
A("| 입력 구성 (`prep/*.py`) | unit | 수용 기준과 1:1, 기준 입력 표본 대조 | `tests/unit/test_*.py` | `pytest tests/unit -v` |")
A("| 프로그램 등록 검사 (`api/services/code_check.py`) | unit | 수용 기준과 1:1 | `tests/unit/test_code_check.py` | `pytest tests/unit -v` |")
A("| 관리 API 서비스·경로·화면 (`api/services`, `api/routes`, `api/auth.py`, `api/templates`) | integration | 경로마다 정상, 예외, 거절. 시험용 DB와 가짜 저장소·실행기 사용 | `tests/api/test_*.py` | `pytest tests/api -v` |")
A("| Azure 호출과 정의 (`api/clients`, `infra/*.bicep` 중 권한·네트워크·실행기·웹 앱·전체 배포, `adf/`) | integration | 배포된 PoC 환경에서 격리, 동시 실행, 로그인, 수집, 기준 입력 일치 | `tests/azure/test_*.py` | `pytest tests/azure -v` |")
A("| 설정·정의만 있는 파일 (`pyproject.toml`, 기준 데이터 목록, 기준 컬럼, 보고서, `api/repo`, `api/app.py`, 저장소·DB·Data Factory·Logic Apps 정의) | none | - (build gate only) | - | build gate only |")
A("")
A("## Gate Check Commands\n")
A("> Generated from codebase - confirm before Execute. 저장소에 기존 명령이 없어 제안값이다.\n")
A("| Gate Level | When to Use | Command |")
A("| --- | --- | --- |")
A(f"| Quick | unit 테스트만 있는 작업 뒤 | `{GATE['quick']}` |")
A(f"| Full | 관리 API 테스트가 있는 작업 뒤 | `{GATE['full']}` |")
A(f"| Build | 단계가 끝났을 때, Azure 환경 테스트가 있는 작업, 설정·정의만 있는 작업 뒤 | `{GATE['build']}` |")
A("")
A("---\n")
A("## Execution Plan\n")
A("단계는 순서대로 진행한다. 화살표는 같은 단계 안의 선후 관계이고, 화살표가 없는 작업은 그 단계 안에서 다른 작업을 기다리지 않는다.\n")
for p, name in PHASES.items():
    A(f"### Phase {p}: {name}\n")
    A("```")
    members = [x for x in T if x["phase"] == p]
    edges = [(d, x["key"]) for x in members for d in x["deps"] if phase_of[d] == p]
    lone = [x["key"] for x in members if not any(x["key"] in e for e in edges)]
    for a, b in edges:
        A(f"{ids[a]} → {ids[b]}")
    if lone:
        A("단독: " + ", ".join(ids[k] for k in lone))
    A("```\n")
A("---\n")
A("## Task Breakdown\n")
for p, name in PHASES.items():
    A(f"### Phase {p}: {name}\n")
    for x in [x for x in T if x["phase"] == p]:
        tests, gate = tests_gate(x)
        A(f"#### {ids[x['key']]}: {x['title']}\n")
        A(f"**What**: {x['what']}")
        A(f"**Where**: {x['where']}")
        A("**Depends on**: " + (", ".join(ids[d] for d in x["deps"]) if x["deps"] else "None"))
        A(f"**Reuses**: {x['reuses']}")
        A(f"**Requirement**: {x['req']}\n")
        A("**Done when**:\n")
        for (req, ac, claim, tn) in x["checks"]:
            A(f"- [ ] {claim} ({cid[(req, ac)]})")
        for e in x["extra"]:
            A(f"- [ ] {e}")
        n = len(x["checks"]) + (len(x["extra"]) if x["grp"] else 0)
        A(f"- [ ] Gate check passes: `{GATE[gate]}`")
        if x["grp"]:
            A(f"- [ ] Test count: `tests/{x['grp']}/{x['testfile']}`에 이 작업의 테스트 {n}개 이상이 통과한다 (기존 테스트를 지우지 않는다)")
        A("")
        A(f"**Tests**: {tests}")
        A(f"**Gate**: {gate}\n")
        A("---\n")
A("## Checks\n")
A("확인 항목마다 명세의 요구사항 ID와 수용 기준 번호를 적었다. `Proof`의 테스트 이름과 출력 줄은 계획이며, 구현하면서 실제 실행 결과의 줄로 바꾼다.\n")
last = None
for c in checks:
    _, ac, req, claim, grp, tf, tn, key = c
    if req != last:
        A(f"### {req}\n")
        last = req
    A(f"**{cid[(req, ac)]}** - {claim} ({req}, AC {ac})")
    A(f"Proof: run {grp} | tests/{grp}/{tf}::{tn} PASSED\n")
A("---\n")
A("## Handoff\n")
A("**Settled mid-build:** none")
A("**Dispatched:** none")
A("**Walked:** none\n")
A("---\n")
A("## Phase Execution Map\n")
A("```")
A("Phase " + " → Phase ".join(str(p) for p in PHASES))
A("")
for p, name in PHASES.items():
    A(f"Phase {p:>2} ({name}): " + ", ".join(ids[x["key"]] for x in T if x["phase"] == p))
A("```\n")
A("고객 답과 자료에 걸려 있는 단계:\n")
A("| 단계 | 시작 조건 |")
A("| --- | --- |")
A("| Phase 1 | 소스와 2026-11-18 입력·결과는 받았다. 같은 입력으로 PC에서 실행한 결과 한 벌이 더 필요하다 (Q17) |")
A("| Phase 2~5 | Linux에서 수정 없이 실행됨은 확인했다. PC와 결과가 같다는 확인이 남았다. 다르면 실행기 선택을 다시 한다 |")
A("| Phase 6 | Azure 환경 제공 주체와 보안 기준이 정해진다 (Q7) |")
A("| Phase 9, 12 | 로그인 방식이 정해진다 (Q16) |")
A("| Phase 10 | 이상치 기준, 문의 대상, 답변 반영 방식이 정해진다 (Q23~Q25) |")
A("| Phase 11~12 | 운영 반영에 IT혁신팀 승인을 두는 데 고객이 동의한다 (Q3) |")
A("| Phase 13 | 기간계 원천의 접근이 승인된다 (Q1). 승인된 원천만 파이프라인에 넣는다 |")
A("")
A("Phase 13은 접근 승인에 시간이 걸리므로 승인 절차는 Phase 1과 동시에 시작한다.\n")
A("---\n")
A("## Requirement Coverage\n")
A("| Requirement ID | 수용 기준 수 | 확인 항목 | 작업 |")
A("| --- | --- | --- | --- |")
for r in REQ_ORDER:
    cs = [c for c in checks if c[2] == r]
    ts = sorted({ids[c[7]] for c in cs}, key=lambda s: int(s[1:]))
    A(f"| {r} | {EXPECT[r]} | {cid[(r, 1)]}~{cid[(r, EXPECT[r])]} | {', '.join(ts)} |")
A("")
A(f"**Coverage:** 요구사항 19개, 수용 기준 {len(checks)}개가 모두 확인 항목과 작업에 연결되어 있다.")

open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print(len(T), "tasks", len(checks), "checks")
