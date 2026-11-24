"""고객 전달용 'To-Be 개발 방안' PDF와 '확인 요청 사항' 엑셀을 만든다.

실행: python3 build_tobe.py
결과: 선제적양수도_ToBe_개발방안_v1.0.pdf, 선제적양수도_확인요청사항.xlsx (이 폴더)
"""
import html
import subprocess
import tempfile
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

HERE = Path(__file__).parent
PDF = HERE / "선제적양수도_ToBe_개발방안_v1.0.pdf"
XLSX = HERE / "선제적양수도_확인요청사항.xlsx"
e = html.escape


def table(head, rows, widths=None):
    col = "".join(f"<col style='width:{w}'>" for w in widths) if widths else ""
    return (f"<table><colgroup>{col}</colgroup><tr>" + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr>"
            + "".join("<tr>" + "".join(f"<td>{c if c.startswith('<') else e(c)}</td>" for c in r) + "</tr>" for r in rows) + "</table>")


def ul(items):
    return "<ul>" + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>"


# ---------------------------------------------------------------- 내용
SUMMARY = [
    ("엔진", "현행 pipeline.py를 수정 없이 사용", "Azure 컨테이너에서 실행 1건당 1회 구동. 사전 검증에서 수정 없이 실행됨을 확인"),
    ("데이터", "기간계 데이터 자동 수집", "Azure Data Factory로 수집. 접근 승인 전인 원천은 화면에서 파일 업로드"),
    ("실행", "검증 실행 / 운영 실행 2개 모드", "검증: 수정한 프로그램을 과거 데이터로 시험. 운영: 승인된 버전으로 매일 실행"),
    ("검증", "입력·결과 자동 검증", "입력 누락 시 실행 차단. 업무 규칙 5개 자동 확인. 운영 버전·직전 결과와 비교"),
    ("이상치", "이상치 질문·답변 및 재테스트", "검증 결과의 이상치를 프로그램 작성자·점별 바이어에게 질문. 답변을 반영해 재테스트하고 처리 상태 확인"),
    ("관리", "버전·파라미터·이력·승인", "프로그램 버전, 파라미터, 실행 이력을 공용 저장소에 기록. 운영 반영은 승인 후 적용"),
    ("ERP", "수동 업로드 유지", "승인된 결과만 업로드 순서대로 제공. 자동 연계는 PoC 이후 협의"),
]
ASIS = [
    ("1~3", "재고 추출·병합", "L-lit에서 카테고리별 다운로드 후 병합 스크립트 실행", "자동 수집 후 현행 합본 형식으로 자동 구성 (접근 승인 전: 파일 업로드)", "자동화"),
    ("4", "판매예측 수집", "정보계 테이블에서 주 1회 다운로드", "정보계 테이블 자동 수집", "자동화"),
    ("5", "공헌이익 수집", "L-DEX에서 월 1회 다운로드 (현재 미적용)", "선택 입력으로 유지. 적용 시 수집 대상에 추가", "유지"),
    ("6", "마스터 취합", "MD 취합 엑셀을 담당자가 폴더에 반영", "MD가 화면에서 업로드, 버전 자동 보관", "화면"),
    ("7", "코드표 5종 수집", "정보계에서 비정기 다운로드", "정보계 코드 테이블 자동 동기화", "자동화"),
    ("8", "입력 파일 배치", "로컬 INPUT 폴더에 수동 배치", "일자별 입력 묶음 자동 구성, 출처·수집 시각 기록", "자동화"),
    ("9", "실행 준비", "로컬 PC에서 Streamlit 실행", "웹 화면 접속 (설치 불필요, 사내 계정 로그인)", "화면"),
    ("10", "입력 검증", "화면의 파일 상태를 눈으로 확인", "파일·컬럼·대상 카테고리·대상 점·갱신 주기 자동 검증, 실패 시 실행 차단", "자동화"),
    ("11", "조건 설정", "화면 또는 settings.json 직접 수정", "파라미터 화면에서 조정, 변경 이력과 실행 시점 값 보관", "화면"),
    ("12", "엔진 실행", "[재고배분 실행] 버튼", "운영: 예약 또는 버튼 / 검증: 버튼", "자동화"),
    ("13~16", "배분 계산·결과 생성", "pipeline.py 자동 수행", "동일 (pipeline.py 수정 없음)", "유지"),
    ("17", "결과 검토", "요약·검토리포트를 눈으로 확인", "업무 규칙 5개 자동 확인, 건수 비교, 리포트 화면 표시 후 담당자 승인", "자동화"),
    ("18~20", "ERP 반영", "결과 엑셀을 L-lit에 수동 업로드·확정", "동일. 승인된 결과 파일을 업로드 순서대로 제공", "유지"),
    ("21", "결과 보관", "로컬 OUTPUT 폴더", "공용 저장소에 일자·실행별 보관, 실행 이력 조회", "자동화"),
    ("신규", "이상치 확인", "정해진 절차 없음", "이상치별 질문 목록 생성 → 작성자·바이어 답변 수집 → 답변 반영 재테스트", "신규"),
]
COMPONENTS = [
    ("수집", "Azure Data Factory + 수집 중계 서버(고객 내부망)", "기간계 데이터를 원본 그대로 수집"),
    ("입력 구성", "Azure Container Apps Job", "수집 원본·업로드 파일을 현행 파일 이름과 형식으로 변환"),
    ("저장소", "Azure Data Lake Storage Gen2", "입력, 마스터, 프로그램, 결과 보관"),
    ("실행기", "Azure Container Apps Job (검증용, 운영용)", "입력 검증 → pipeline.py 실행 → 업무 규칙 확인"),
    ("관리 화면", "Azure App Service", "화면 9종, 실행 요청, 결과 비교, 질문·답변, 승인"),
    ("기록 DB", "Azure SQL Database", "버전, 파라미터, 실행 이력, 승인 기록"),
    ("로그인·권한", "Microsoft Entra ID", "사내 계정 로그인, 역할별 권한"),
    ("알림", "Azure Logic Apps", "수집 실패, 검증 실패, 실행 완료, 승인 요청 통지"),
]
MODES = [
    ("시작", "현업 사용자가 요청", "매일 정해진 시각 또는 S&OP 담당자가 요청"),
    ("프로그램", "사용자가 등록한 수정본", "승인된 운영 버전"),
    ("파라미터", "운영값에서 조정 (해당 실행에만 적용)", "운영값"),
    ("데이터", "선택한 일자의 입력", "당일 수집분"),
    ("결과 용도", "운영 버전 결과와 비교 (파일명에 TEST_ 표시)", "담당자 승인 후 ERP 업로드 파일로 제공"),
    ("이상치 처리", "질문·답변 후 재테스트", "해당 없음 (검증 실행에만 적용)"),
]
FLOW_PROD = ["기간계 데이터 자동 수집 (재고, 판매예측, 코드표)", "입력 묶음 구성 및 입력 검증 — 실패 시 실행 차단, 담당자 알림",
             "pipeline.py 실행 (운영 버전, 운영 파라미터)", "업무 규칙 5개 확인, 직전 결과와 비교", "S&OP 담당자 결과 확인 후 승인",
             "ERP 업로드 파일 내려받기 → L-lit 수동 업로드 (현행과 동일)"]
FLOW_TEST = ["수정한 pipeline.py 등록 — 문법·라이브러리 검사, 버전 부여", "버전·입력 일자·파라미터 선택 후 검증 실행",
             "결과 확인 — 운영 버전 대비 건수 차이, 업무 규칙, 수량 변경 상품, 이상치",
             "이상치 질문 — 질문 목록 생성, 프로그램 작성자·점별 바이어에게 전달",
             "답변 수집(화면 입력 또는 파일 업로드) → 답변 반영 재테스트 → 이상치별 처리 상태 확인",
             "운영 반영 요청 — 기준 입력으로 회귀 테스트 자동 수행",
             "IT혁신팀 승인 → 다음 운영 실행부터 새 버전 적용 (되돌리기 가능)"]
FUNC = [
    ("데이터 연계", [
        ("재고 (매일)", "L-lit 상태별 재고조회(SKU). 대상 카테고리 전체를 수집해 현행 합본 CSV(72컬럼) 형식으로 구성"),
        ("판매예측 (주 1회)", "정보계 GB_20170089.MM_PRED_SL_QTY 수집"),
        ("코드표 5종", "정보계 LDFDWP 코드 테이블 동기화 (점, 브랜드, 코너, 창고, 재고유형)"),
        ("MD 마스터 2종", "양수도 그룹, 제외·전용 SKU를 화면에서 업로드. 버전 보관"),
        ("공헌이익", "현재 미적용이므로 선택 입력. 적용 시 L-DEX 수집 추가"),
        ("접근 승인 전 원천", "화면에서 파일 업로드. 이후 처리(검증·실행·결과)는 동일"),
    ]),
    ("입력 검증", [
        ("필수 파일", "재고, 판매예측, 코드표 5종 존재 여부 → 없으면 실행 차단"),
        ("재고 컬럼", "72개 컬럼의 이름·순서가 등록 기준과 같은지 → 다르면 실행 차단"),
        ("대상 카테고리·점", "등록된 대상 카테고리, 대상 10개 점 포함 여부 → 누락 시 실행 차단, 누락 항목 표시"),
        ("갱신 주기", "재고 1일, 판매예측 7일 초과 → 운영 실행은 담당자 확인 후 진행"),
    ]),
    ("실행", [
        ("엔진", "현행 pipeline.py 수정 없이 사용. 실행 1건당 컨테이너 1개 (동시 실행 가능)"),
        ("실행 환경", "Python·pandas·numpy·openpyxl 버전을 현행 PC와 동일하게 고정, 시간대 한국"),
        ("파라미터", "16개 항목을 화면에서 관리. 실행 시 settings.json으로 전달, 실행 시점 값 보관"),
        ("격리", "검증용·운영용 실행기 분리. 검증 실행은 운영 결과·입력 변경 불가, 외부 통신 차단"),
    ]),
    ("결과 검증", [
        ("업무 규칙 5개", "총량 보존, 최소보장, 그룹 내 이동, 발송 한도, 전환 한도를 결과 파일에서 자동 확인"),
        ("비교", "검증 실행: 운영 버전 결과와 비교 / 운영 실행: 직전 결과와 비교 (건수, 수량 변경 상품)"),
        ("차단", "규칙 위반 시 운영 결과 승인과 운영 반영 요청 불가"),
        ("회귀 테스트", "운영 반영 요청 시 기준 입력으로 새 버전과 운영 버전을 함께 실행해 비교"),
    ]),
    ("이상치 질문·답변", [
        ("이상치 추출", "검토리포트의 경고(이동 건수 이상, 과다 이동), 미충전 부족분에서 추출"),
        ("질문 목록", "이상치마다 문의 대상(프로그램 작성자 또는 해당 점 바이어)과 질문 문안 생성"),
        ("전달·회신", "질문 목록 파일(CSV) 내려받기 또는 화면에서 발송. 답변은 화면 입력 또는 파일 업로드"),
        ("답변 유형", "정상(사유 기록) / 이동 제외 / 파라미터 조정 / 로직 수정"),
        ("재테스트 반영", "정상: 이상치에서 제외 / 이동 제외: 제외 마스터의 임시 사본에 추가해 실행 / 파라미터 조정: 제안값으로 실행 / 로직 수정: 새 버전 등록 후 실행"),
        ("결과", "이상치별 처리 상태(해소, 확인됨, 남음)와 첫 실행 대비 차이 표시. pipeline.py 수정 없음"),
    ]),
    ("결과 전달·관리", [
        ("결과 파일", "현행과 같은 파일 구성 (양수도, 재고전환, 이동체인, 검토리포트, 일일결과리포트)"),
        ("ERP 반영", "승인 후 ① 온→오프 ② 양수도 ③ 오프→온 순서로 제공. L-lit 업로드는 현행 유지"),
        ("이력", "실행 일시, 모드, 실행자, 프로그램 버전, 파라미터, 입력 일자, 마스터 버전, 결과 요약"),
        ("버전 관리", "프로그램 버전 등록, 운영 버전 1개 지정, 이전 버전으로 되돌리기"),
    ]),
]
VERIFIED = [
    ("pipeline.py 수정 없이 Linux 실행", "확인", "변경한 것은 settings.json의 입출력 폴더 경로 2줄"),
    ("실행 시간·자원", "확인", "11/18 입력(재고 12.7만 행, 상품 13,887개) 기준 65~68초, 메모리 약 1GB"),
    ("재실행 시 동일 결과", "확인", "같은 입력으로 2회 실행한 결과 엑셀 19종이 셀 단위로 일치"),
    ("날짜 기준 고정", "확인", "프로그램 수정 없이 실행 날짜 고정 가능 (제외기한 판정 등)"),
    ("업무 규칙 5개 자동 확인", "확인", "재실행 결과 5개 규칙 통과. 최소보장은 1개 미만 단수 차이 1건"),
    ("PC 결과와 동일 여부", "미확인", "전달받은 재고가 오전 실행 이후 추출분으로 보여 대조 불가 (확인 요청 6번)"),
]
SCOPE = [
    ("구현", "데이터 수집(접근 승인 원천), 입력 구성·검증, 프로그램 등록·버전 관리, 검증 실행, 업무 규칙 확인·결과 비교, 이상치 질문 목록 생성·답변 수집·재테스트, 결과 조회·내려받기, 마스터 업로드, 파라미터·실행 이력, 운영 실행(버튼), 결과 승인, 운영 반영 요청·승인"),
    ("시연", "정해진 시각 자동 시작, 알림"),
    ("PoC 이후", "ERP 자동 연계, 배분 로직 변경·코드 정리, 재고배분 외 프로그램 수용, 마스터 화면 편집, LLM 연계, 코드에 고정된 규칙의 설정화"),
]
ACCEPT = [
    "기준 입력과 운영 파라미터로 실행한 결과가 현행 PC 결과와 동일",
    "수정한 프로그램을 등록·실행하고 운영 버전과의 차이를 화면에서 확인",
    "파라미터를 변경해 실행한 결과가 현행 PC에서 같은 값으로 실행한 결과와 동일",
    "대상 카테고리가 누락된 입력은 실행되지 않음",
    "업무 규칙 5개 자동 확인, 위반 시 승인 불가",
    "접근 승인된 원천은 수작업 없이 수집되어 입력 묶음으로 구성",
    "수집부터 결과 확인까지의 소요 시간을 현행(09:00~10:30)과 비교해 제시",
    "검증 결과의 이상치로 질문 목록을 생성하고, 답변을 반영한 재테스트에서 이상치별 처리 상태를 확인",
]
STEPS = [
    ("1", "현행 재현", "받은 소스·입력으로 실행 확인, PC 결과와 대조", "PC 실행 결과 수령 (확인 요청 6번)"),
    ("2", "실행 환경", "실행 이미지, 실행 틀, 저장소, 실행기 권한 분리", "Azure 환경 확정 (확인 요청 10번)"),
    ("3", "검증 기능", "입력 검증, 업무 규칙 5개, 결과 비교", "대상 카테고리 확정 (확인 요청 8번)"),
    ("4", "관리 화면", "프로그램 등록, 검증 실행·결과, 마스터, 파라미터", "로그인 방식 확정 (확인 요청 11번)"),
    ("5", "이상치 질문·답변", "이상치 추출, 질문 목록, 답변 수집, 재테스트", "이상치 기준·문의 대상 확정 (확인 요청 19~21번)"),
    ("6", "운영 실행·승인", "운영 실행, 결과 승인, 운영 반영 승인, 회귀 테스트", "승인 구조 확정 (확인 요청 1번)"),
    ("7", "데이터 수집", "ADF 수집, 입력 구성. 승인된 원천부터 적용", "기간계 접근 승인 (확인 요청 9번)"),
    ("8", "고객 검증", "병행 비교, 인수 기준 확인, 현업 사용 확인", "병행 기간 협의"),
]
# 확인 요청: (구분, 요청 사항, 당사 제안(기본안), 영향, 우선순위)
ASKS = [
    ("방식 확정", "검증 실행/운영 실행 2개 모드와 운영 반영 시 IT혁신팀 승인 구조", "제안대로 진행", "전체 구조, 화면, 권한", "상"),
    ("방식 확정", "데이터 연계 방식: ADF 자동 수집 기본, 접근 승인 전 원천은 파일 업로드", "제안대로 진행", "수집 범위, 일정", "상"),
    ("방식 확정", "pipeline.py 무수정 원칙 (재고 컬럼 위치 문제 포함 현행 그대로 실행)", "PoC는 무수정. 컬럼 문제는 별도 수정 시점 협의", "결과 일치 기준", "상"),
    ("방식 확정", "ERP 반영은 수동 업로드 유지", "PoC는 수동 유지", "결과 전달 방식", "중"),
    ("방식 확정", "PoC 기간에는 현행 PC를 실제 업무로 유지하고 신규 환경은 비교용으로 병행", "병행 운영", "검증 방법, 일정", "중"),
    ("자료 요청", "11/18 입력 그대로 PC에서 1회 실행한 결과 폴더와 그때의 settings.json (전달받은 재고가 오전 실행 이후 추출분으로 보임: 추출 시각 10:45, EYEWEAR 미포함)", "-", "PC와 신규 환경의 결과 일치 확인", "상"),
    ("자료 요청", "전달받은 settings.json이 운영 설정이 맞는지 (최소보장 3일, 통물 한정 꺼짐, 출력 폴더명 '재검증')", "받은 값을 초기값으로 사용", "운영 파라미터 초기값", "상"),
    ("자료 요청", "재고 추출 대상 카테고리 (전달받은 재고 3개, 11/18 결과 4개, 기초정보 6개)", "받은 재고의 3개를 초기 등록", "입력 검증 기준", "상"),
    ("환경", "L-lit 재고·L-DEX 공헌이익의 DB 직접 조회 가능 여부, 원천 테이블, DB 종류, 접근 승인 소요 기간", "승인 전에는 파일 업로드", "수집 범위, 일정", "상"),
    ("환경", "Azure 환경 제공 주체, 기간계와의 연결(전용선·VPN), 수집 중계 서버 설치 가능 여부, 실데이터 보안 기준", "-", "환경 구성, 일정", "상"),
    ("환경", "사내 계정의 Microsoft Entra ID 사용 여부, 알림 수신 채널 (메일, Teams 등)", "Entra ID 로그인, 메일 알림", "로그인, 알림", "중"),
    ("업무", "파라미터를 변경하는 상황·빈도·방법, 결과를 확정 또는 재실행하는 판단 기준", "운영 파라미터 변경은 IT혁신팀 승인", "파라미터 화면, 승인 흐름", "중"),
    ("업무", "이동체인 '수기 조정' 시트의 사용 시점, ERP 업로드 중 수량 수정 빈도", "-", "결과 승인 이후 흐름", "중"),
    ("업무", "사용자 수와 역할 (현업 사용자와 S&OP 담당자의 동일인 여부)", "역할 4종, 겸임 가능", "권한", "중"),
    ("업무", "15:00 이후 접수되는 양수도 신청 건의 처리 방식 (재실행 여부, 재고 재추출 여부)", "같은 일자 재실행 허용", "운영 실행 방식", "중"),
    ("업무", "운영 실행을 담당자 확인 없이 정해진 시각에 자동 시작해도 되는지", "PoC는 버튼 실행, 자동 시작은 시연", "운영 실행 시작 방식", "하"),
    ("기타", "프로그램 수정 위치 (개인 PC 또는 VDI), 'LLM 서비스 연계(Claude)'의 의미", "수정 위치와 무관하게 화면에서 등록. LLM 연계는 범위 밖", "등록 경로, 범위", "하"),
    ("기타", "Q&A 로그.md, 변경이력.md 공유 가능 여부, 운영 PC의 Python 버전", "-", "로직 변경 배경, 실행 환경", "하"),
    ("이상치", "이상치로 볼 항목과 기준값 (과다 이동, 이동 건수 이상, 미충전, 전일 대비 급변 등)", "검토리포트 경고 2종 + 미충전", "이상치 추출 기준", "상"),
    ("이상치", "문의 대상 지정 기준과 전달 방법 (점별 바이어 지정 방식, 바이어의 시스템 접속 여부)", "판매예측 자료의 바이어명 기준 지정. 파일(CSV) 회신 기본, 화면 답변 선택", "권한, 화면", "상"),
    ("이상치", "답변 유형과 반영 방식, 이동 제외의 적용 범위(해당 재테스트 한정 또는 제외 마스터 반영), 운영 실행 적용 여부", "유형 4종, 재테스트 한정, 검증 실행에만 적용", "재테스트 방식", "중"),
]

DIAGRAM = """
<div class="dg">
  <div class="zone"><div class="zt">고객 내부망 (기간계)</div>
    <div class="bx">L-lit<br><small>재고</small></div><div class="bx">정보계<br><small>판매예측, 코드표</small></div><div class="bx">L-DEX<br><small>공헌이익(선택)</small></div>
    <div class="bx gray">수집 중계 서버</div></div>
  <div class="ar">→<br><small>전용선·VPN</small></div>
  <div class="zone az"><div class="zt">Azure</div>
    <div class="rowx"><div class="bx">① 수집<br><small>Data Factory</small></div><div class="a2">→</div><div class="bx">② 입력 구성<br><small>현행 파일 형식</small></div><div class="a2">→</div><div class="bx">③ 저장소<br><small>입력·결과·프로그램</small></div></div>
    <div class="rowx"><div class="bx hi">④ 실행기 (검증용)<br><small>입력 검증 → pipeline.py → 규칙 확인</small></div><div class="bx hi">④ 실행기 (운영용)<br><small>입력 검증 → pipeline.py → 규칙 확인</small></div></div>
    <div class="rowx"><div class="bx">⑤ 관리 화면<br><small>실행·비교·질문·승인</small></div><div class="bx">⑥ 기록 DB<br><small>버전·파라미터·이력</small></div><div class="bx">⑦ 로그인·알림<br><small>Entra ID, Logic Apps</small></div></div></div>
  <div class="ar">←<br><small>웹 화면</small></div>
  <div class="zone"><div class="zt">사용자</div>
    <div class="bx">현업 사용자</div><div class="bx">바이어</div><div class="bx">S&amp;OP 담당자</div><div class="bx">MD</div><div class="bx">IT혁신팀</div>
    <div class="bx gray">ERP(L-lit)<br><small>결과 수동 업로드</small></div></div>
</div>"""

CSS = """@page{size:A4;margin:15mm 14mm 14mm}
body{font:10pt/1.5 "NanumGothic","Malgun Gothic",sans-serif;color:#171717}
h1{font-size:19pt;margin:0 0 4pt}.sub{color:#525252;margin:0 0 12pt}
h2{font-size:13pt;margin:16pt 0 6pt;padding-bottom:3pt;border-bottom:1.5px solid #171717;break-after:avoid}
h3{font-size:10.5pt;margin:10pt 0 4pt;break-after:avoid}
ul,ol{margin:0 0 6pt;padding-left:15pt}li{margin:0 0 1.5pt}
table{border-collapse:collapse;width:100%;margin:4pt 0 8pt;font-size:9pt;table-layout:fixed}
th,td{border:1px solid #cfcfcf;padding:3.5pt 5pt;text-align:left;vertical-align:top;word-break:keep-all;overflow-wrap:anywhere}
th{background:#f1f1f2;font-weight:600}tr{break-inside:avoid}
.meta td:first-child,.kv td:first-child{background:#f7f7f8;font-weight:600}
.tag{display:inline-block;padding:0 5pt;border-radius:3pt;font-size:8.5pt;border:1px solid #bbb}
.t-auto{background:#e3efee;border-color:#9cc3c1;color:#0f5c5c}.t-keep{background:#f1f1f2;color:#525252}.t-ui{background:#eef2f8;border-color:#b3c3dc;color:#274a7a}.t-new{background:#fbf0d9;border-color:#e2c98a;color:#7a4f00}
.ok{color:#17794a;font-weight:600}.no{color:#c4291c;font-weight:600}
.pb{break-before:page}
.blk,.dg{break-inside:avoid}
.tag{white-space:nowrap}
.dg{display:flex;align-items:stretch;gap:5pt;margin:6pt 0 8pt}
.zone{border:1px solid #bdbdbd;border-radius:5pt;padding:5pt;display:flex;flex-direction:column;gap:4pt;width:23%}
.zone.az{width:54%;background:#f7fafa;border-color:#9cc3c1}
.zt{font-weight:600;font-size:9pt;margin-bottom:1pt}
.bx{border:1px solid #9a9a9a;border-radius:4pt;padding:3pt 4pt;background:#fff;font-size:8.5pt;text-align:center;flex:1}
.bx small{color:#525252;font-size:7.5pt}.bx.gray{background:#f1f1f2}.bx.hi{background:#e3efee;border-color:#0f5c5c}
.rowx{display:flex;gap:4pt;align-items:stretch}.a2{align-self:center;color:#525252}
.ar{align-self:center;text-align:center;font-size:12pt;color:#525252;width:9%}.ar small{font-size:7pt}
.note{font-size:8.5pt;color:#525252;margin:2pt 0 6pt}"""


def build_pdf():
    tag = {"자동화": "t-auto", "유지": "t-keep", "화면": "t-ui", "신규": "t-new"}
    B = []
    B.append("<h1>선제적 양수도 프로세스 To-Be 개발 방안</h1>")
    B.append("<p class=sub>판매 차질 방지 Agent(S&amp;OP팀) PoC · v1.0 · 2026-11-24 · 인포유</p>")
    B.append("<table class=meta><colgroup><col style='width:18%'><col></colgroup>"
             "<tr><td>목적</td><td>선제적 양수도(재고배분) 프로세스의 To-Be 개발 방식 확정</td></tr>"
             "<tr><td>근거 자료</td><td>기초정보(11/5), 과제 추진 방안 PPT, 현행 소스·입력·결과(11/18 기준), AS-IS 프로세스(S&amp;OP 첨언)</td></tr>"
             "<tr><td>확정 절차</td><td>본 문서의 방식(1~7장)에 대한 의견과 8장 확인 요청 사항 회신 → 반영 후 최종 확정</td></tr></table>")

    B.append("<h2>1. 개발 방식 요약</h2>")
    B.append(table(["구분", "방식", "내용"], SUMMARY, ["11%", "27%", "62%"]))

    B.append("<h2>2. AS-IS → To-Be</h2>")
    B.append("<p class=note>단계 번호는 전달받은 AS-IS 프로세스(21단계) 기준</p>")
    B.append(table(["단계", "업무", "AS-IS", "To-Be", "구분"],
                   [(a, b, c, d, f"<span class='tag {tag[g]}'>{g}</span>") for a, b, c, d, g in ASIS], ["8%", "14%", "30%", "37%", "11%"]))
    B.append("<p class=note>자동화 8개 업무, 화면 전환 3개 업무, 현행 유지 3개 업무 (공헌이익, 배분 계산, ERP 반영), 신규 1개 업무 (이상치 확인)</p>")

    B.append("<h2>3. To-Be 구성</h2>")
    B.append(DIAGRAM)
    B.append(table(["구성요소", "Azure 서비스 (제안)", "역할"], COMPONENTS, ["16%", "40%", "44%"]))
    B.append("<p class=note>Azure 서비스는 제안이며 고객 환경과 사내 표준 확인 후 확정 (확인 요청 10번)</p>")

    B.append("<h2>4. To-Be 프로세스</h2>")
    B.append("<div class=blk><h3>실행 모드</h3>" + table(["항목", "검증 실행", "운영 실행"], MODES, ["16%", "42%", "42%"]) + "</div>")
    B.append("<div class=blk style='display:flex;gap:14pt'><div style='flex:1'><h3>운영 실행 흐름</h3><ol>" + "".join(f"<li>{e(x)}</li>" for x in FLOW_PROD)
             + "</ol></div><div style='flex:1'><h3>검증 실행 흐름</h3><ol>" + "".join(f"<li>{e(x)}</li>" for x in FLOW_TEST) + "</ol></div></div>")

    B.append("<h2>5. 기능별 개발 방식</h2>")
    for name, rows in FUNC:
        B.append(f"<div class=blk><h3>{e(name)}</h3>" + table(["항목", "방식"], rows, ["22%", "78%"]).replace("<table>", "<table class=kv>") + "</div>")

    B.append("<h2>6. 사전 검증 결과</h2>")
    B.append("<p class=note>전달받은 현행 소스와 11/18 입력으로 당사 환경(Linux)에서 확인한 내용</p>")
    B.append(table(["확인 항목", "결과", "내용"],
                   [(a, f"<span class='{'ok' if b == '확인' else 'no'}'>{b}</span>", c) for a, b, c in VERIFIED], ["30%", "10%", "60%"]))
    B.append(ul(["전달받은 재고 파일: 원본 추출 시각 10:45, 11/18 결과에서 수량이 바뀐 423건 중 331건이 이동 후 수량과 일치, EYEWEAR 미포함",
                 "같은 입력으로 PC에서 실행한 결과를 받으면 PC와 신규 환경의 결과 일치 여부를 바로 확인 가능"]))

    B.append("<h2>7. PoC 범위·인수 기준·진행 단계</h2>")
    B.append("<h3>범위</h3>" + table(["구분", "항목"], SCOPE, ["12%", "88%"]).replace("<table>", "<table class=kv>"))
    B.append("<h3>인수 기준 (안)</h3><ol>" + "".join(f"<li>{e(x)}</li>" for x in ACCEPT) + "</ol>")
    B.append("<div class=blk><h3>진행 단계</h3>" + table(["단계", "구분", "내용", "선행 조건"], STEPS, ["7%", "15%", "45%", "33%"]) + "</div>")
    B.append("<p class=note>기간과 투입 인력은 8장 확인 요청 사항 중 우선순위 '상' 항목 회신 후 산정</p>")

    B.append("<h2>8. 확정을 위한 확인 요청 사항</h2>")
    B.append("<p class=note>회신은 첨부 엑셀(선제적양수도_확인요청사항.xlsx)의 회신란에 기재. '당사 제안'은 회신이 없을 때 적용하는 기본안</p>")
    B.append(table(["No", "구분", "확인 요청 사항", "당사 제안 (기본안)", "우선"],
                   [(str(i + 1), a, b, c, p) for i, (a, b, c, d, p) in enumerate(ASKS)], ["5%", "10%", "50%", "28%", "7%"]))

    tmp = Path(tempfile.mkdtemp())
    (tmp / "doc.html").write_text(f"<!doctype html><meta charset=utf-8><style>{CSS}</style>" + "\n".join(B), encoding="utf-8")
    foot = "<div style='font-size:7pt;color:#777;width:100%;text-align:center'>선제적 양수도 프로세스 To-Be 개발 방안 v1.0 · <span class=pageNumber></span> / <span class=totalPages></span></div>"
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();"
          f"await p.goto('file://{tmp}/doc.html');await p.pdf({{path:{str(PDF)!r},format:'A4',printBackground:true,displayHeaderFooter:true,"
          f"headerTemplate:'<span></span>',footerTemplate:{foot!r},margin:{{top:'15mm',bottom:'14mm',left:'14mm',right:'14mm'}}}});await b.close()}})()")
    subprocess.run(["node", "-e", js], check=True)


def build_xlsx():
    wb = Workbook()
    ws = wb.active
    ws.title = "확인 요청 사항"
    head = ["No", "구분", "확인 요청 사항", "당사 제안 (기본안)", "영향 범위", "우선순위", "회신 (고객 기재)", "회신자", "회신일"]
    ws.append(["선제적 양수도 프로세스 To-Be 개발 방안 — 확인 요청 사항 (2026-11-24, 인포유)"])
    ws.append(["'당사 제안'은 회신이 없을 때 적용하는 기본안입니다. 우선순위 '상' 항목부터 회신 부탁드립니다."])
    ws.append([])
    ws.append(head)
    for i, (a, b, c, d, p) in enumerate(ASKS, 1):
        ws.append([i, a, b, c, d, p, "", "", ""])
    thin = Side(style="thin", color="BFBFBF")
    ws["A1"].font = Font(bold=True, size=13)
    ws["A2"].font = Font(color="595959")
    for c in ws[4]:
        c.font = Font(bold=True); c.fill = PatternFill("solid", fgColor="E7E6E6")
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
    for row in ws.iter_rows(min_row=5, max_row=4 + len(ASKS)):
        for c in row:
            c.alignment = Alignment(vertical="top", wrap_text=True, horizontal="center" if c.column in (1, 2, 6) else "left")
            c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
        row[6].fill = PatternFill("solid", fgColor="FFF9E5")
        if row[5].value == "상":
            row[5].font = Font(bold=True, color="C00000")
    for col, w in zip("ABCDEFGHI", [5, 11, 62, 34, 24, 9, 44, 11, 11]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:I{4 + len(ASKS)}"
    ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(XLSX)


if __name__ == "__main__":
    build_pdf()
    build_xlsx()
    print(PDF.name, XLSX.name, len(ASKS), "개 요청")
