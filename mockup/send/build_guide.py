"""화면 흐름 안내 문서를 만든다 (개조식).

실행: python3 build_guide.py
결과: send/재고배분_화면흐름_안내.pdf (메일 첨부용), ../사용_흐름_안내.md
화면 캡처는 ../walkthrough_mvp/ 의 28장을 파일 이름순으로 쓴다.
"""
import html
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
MOCK = HERE.parent
SHOTS = sorted((MOCK / "walkthrough_mvp").glob("[0-9][0-9]_*.png"))

TITLE = "재고배분 실행·검증 — 화면 흐름 안내"
INTRO = [
    "목적: 프로그램 등록 → 실행 → 검증 → 승인 → ERP 업로드 파일 수령까지의 흐름을 화면 순서대로 정리",
    "근거: 전달받은 기초정보, PPT, 현행 소스·입력(11/18 기준)",
    "성격: 컨셉 예시 (화면의 수치는 실제 배분 결과가 아닌 예시)",
    "향후: 소스·데이터 수령 후 실제 로직과 데이터 기준으로 보완 예정",
]
SCREENS = [
    ("검증 실행", "S1 내 프로그램 버전", "현업 사용자", "수정한 pipeline.py 등록"),
    ("", "S2 검증 실행", "현업 사용자", "버전·입력 일자·파라미터 선택 후 실행"),
    ("", "S3 검증 결과", "현업 사용자", "건수 차이, 업무 규칙, 이상치, 수량 변경 상품 확인"),
    ("", "Q 질문·답변", "현업 사용자, 바이어", "이상치 질문 발송, 답변 수집, 재테스트"),
    ("", "S4 운영 반영 승인", "IT혁신팀", "회귀 테스트 결과 확인, 승인·반려·되돌리기"),
    ("운영 실행", "S5 마스터 데이터", "MD", "양수도 그룹, 제외·전용 SKU 업로드"),
    ("", "S6 입력 상태", "S&OP 담당자", "입력 묶음 확인, 재고 파일 업로드, 실행 계속"),
    ("", "S7 운영 실행·결과", "S&OP 담당자", "당일 실행, 결과 확인, 승인"),
    ("", "S8 결과 내려받기", "S&OP 담당자", "ERP 업로드 파일 내려받기"),
    ("기록", "실행 이력", "전체", "실행 기록 조회"),
]
ROLES = [
    ("현업 사용자", "S1 내 프로그램 버전, S2 검증 실행, S3 검증 결과, 질문·답변, 실행 이력", "프로그램 등록, 검증 실행, 질문 발송, 재테스트, 운영 반영 요청"),
    ("바이어", "질문·답변", "본인에게 온 질문 답변"),
    ("IT혁신팀", "S4 운영 반영 승인, 실행 이력", "운영 반영 승인·반려, 이전 버전으로 되돌리기"),
    ("MD", "S5 마스터 데이터", "양수도 그룹, 제외·전용 SKU 업로드"),
    ("S&OP 담당자", "S6 입력 상태, S7 운영 실행·결과, S8 결과 내려받기, 실행 이력", "재고 파일 업로드, 운영 실행, 결과 승인, ERP 업로드 파일 내려받기"),
]
# (구간 제목, [(단계 제목, [항목])])
FLOW = [
    ("1. 검증 실행: 수정한 프로그램 등록 및 실행 (접속: 현업 사용자)", [
        ("S1 내 프로그램 버전", ["운영 중인 버전 확인 (운영본 v0.3)"]),
        ("문법 오류 파일 등록", ["등록 거절", "오류 위치(행) 표시"]),
        ("수정본 등록", ["버전 번호 V-002 부여", "등록 후 파일 수정·삭제 불가"]),
        ("S2 검증 실행 조건 설정", ["프로그램 버전, 입력 일자 선택", "최소보장일수 3 → 4 조정 (해당 실행에만 적용, 운영값 유지)"]),
        ("실행 진행", ["입력 검증 → 프로그램 실행 → 규칙 확인 → 기록 저장 순으로 진행"]),
        ("S3 검증 결과", ["운영 버전 대비 건수 차이", "업무 규칙 5개 통과 여부", "이상치 4건", "수량 변경 상품 목록"]),
        ("검증 결과 파일 내려받기", ["파일명 앞에 TEST_ 표시", "ERP 업로드용 파일과 구분"]),
    ]),
    ("2. 이상치 질문·답변 및 재테스트 (접속: 현업 사용자, 바이어)", [
        ("질문 목록 생성", ["이상치별 문의 대상 자동 지정 (프로그램 작성자, 점별 바이어)", "이상치별 질문 문안 자동 생성"]),
        ("질문 발송", ["질문 목록 파일(CSV) 내려받기 또는 화면에서 발송", "발송 후 답변 입력란 활성화"]),
        ("바이어 접속", ["질문·답변 메뉴만 표시", "본인에게 온 질문만 답변 가능"]),
        ("답변 방법 ① 화면 입력 (바이어)", ["답변 유형 선택 후 사유 입력", "예: 인천공항T1 바이어 — 정상 (단체 예약 40개)"]),
        ("답변 방법 ② 파일 업로드 (현업 사용자)", ["답변을 작성한 질문 목록 파일 업로드", "허용되지 않는 답변 유형은 해당 행 안내"]),
        ("답변 반영 계획", ["전체 답변 수집 완료", "반영 내용 자동 분류: 파라미터 변경, 이동 제외, 사유 확인"]),
        ("재테스트 결과", ["이상치별 처리 상태 표시: 해소, 확인됨, 남음", "1차 테스트 대비 건수 차이 표시"]),
    ]),
    ("3. 입력·결과 차단 및 운영 반영 (접속: 현업 사용자 → IT혁신팀)", [
        ("대상 카테고리 누락 입력 선택", ["입력 검증 단계에서 중단", "누락 카테고리 표시 (FOOD)", "결과 파일 미생성"]),
        ("업무 규칙 위반", ["실행 상태 '규칙위반' 표시", "운영 반영 요청 불가"]),
        ("S4 운영 반영 승인 (IT혁신팀 접속)", ["운영 반영 승인, 실행 이력 메뉴만 표시", "기준 입력으로 회귀 테스트 자동 수행", "신규 버전과 현재 운영 버전의 결과 비교"]),
        ("운영 반영 승인 완료", ["수정본이 운영 버전으로 전환", "기존 운영본은 보관 (되돌리기 가능)"]),
    ]),
    ("4. 운영 실행: 당일 결과 생성 및 ERP 업로드 파일 수령 (접속: MD → S&OP 담당자)", [
        ("S5 마스터 데이터: 시트 누락 파일 (MD 접속)", ["마스터 데이터 메뉴만 표시", "업로드 거절", "누락 시트명 표시"]),
        ("S5 마스터 데이터: 정상 파일", ["새 버전(v6)으로 보관", "이전 버전 유지"]),
        ("S6 입력 상태 (S&OP 담당자 접속)", ["운영 실행 메뉴만 표시", "판매예측: 자동 수집 (갱신 주기 초과 경고) / 코드표: 자동 수집 완료", "재고: 파일 업로드 대기"]),
        ("부분 추출 재고 파일 업로드", ["파일 내용 확인 후 누락 카테고리 표시", "실행 차단"]),
        ("전체 추출 재고 파일 업로드", ["컬럼 72개, 대상 카테고리 3개, 점 10개 확인 통과", "입력 묶음 준비 완료"]),
        ("S7 운영 실행", ["판매예측 파일 갱신 주기 초과 → '확인대기'로 중단", "담당자 확인 후 계속 진행"]),
        ("운영 실행 결과", ["요약 건수 및 직전 운영 대비 차이", "업무 규칙 5개 통과 여부", "구간별 소요 시간"]),
        ("S8 결과 내려받기: 승인 전", ["ERP 업로드 파일 내려받기 불가"]),
        ("운영 결과 승인", ["담당자 결과 확인 후 승인", "승인자, 승인 일시 기록"]),
        ("S8 결과 내려받기: 승인 후", ["ERP 업로드 순서대로 파일 제공 (온→오프 → 양수도 → 오프→온)"]),
        ("실행 이력", ["실행자, 일시, 프로그램 버전, 입력 일자, 상태 기록", "재테스트, 회귀 실행 포함"]),
    ]),
]
POLICY = [
    ("이상치 기준", "검토리포트의 경고 2종(이동 건수 이상, 과다 이동). 미충전 부족분은 기본 범위에서 제외"),
    ("문의 대상", "프로그램·설정 관련: 작성자 / 점 수요·사정 관련: 해당 점 바이어 (판매예측 자료의 바이어명 기준)"),
    ("질문 문안", "이상치 유형별 고정 문안"),
    ("전달·회신 방법", "질문 목록 파일(CSV) 회신 기본, 화면 답변 선택"),
    ("답변 유형", "정상 / 이동 제외 / 파라미터 조정 / 로직 수정"),
    ("재테스트 반영 방식", "정상: 사유 기록 후 이상치에서 제외 / 이동 제외: 제외 마스터의 임시 사본에 추가해 실행 / 파라미터 조정: 제안값으로 실행 / 로직 수정: 새 버전 등록 후 재테스트"),
    ("이동 제외 적용 범위", "해당 재테스트에 한정 (지속 적용 시 MD가 제외·전용 SKU 마스터에 반영)"),
    ("적용 대상", "검증 실행 (운영 실행에는 미적용)"),
]
SAMPLES = [
    ("code/pipeline_수정본_최소보충변경.py", "S1", "새 버전으로 등록"),
    ("code/pipeline_문법오류.py", "S1", "문법 오류로 등록 거절"),
    ("code/pipeline_운영본_v0.3.py", "S1", "동일 내용 버전 존재 안내"),
    ("code/pipeline_규칙위반.py", "S1 → S2 → S3", "규칙 위반으로 운영 반영 요청 차단"),
    ("answers/질문목록_답변완료.csv", "Q", "답변 6건 반영"),
    ("answers/질문목록_답변일부_선택오류.csv", "Q", "허용되지 않는 답변 유형 행 안내"),
    ("master/양수도제외브랜드상품_20261112.xlsx", "S5", "새 버전으로 보관"),
    ("master/양수도제외브랜드상품_20261112_시트누락.xlsx", "S5", "시트 누락으로 거절"),
    ("input/상태별재고조회(SKU)_합본_20261117.csv", "S6", "확인 통과, 입력 묶음 준비 완료"),
    ("input/상태별재고조회(SKU)_합본_20261117_부분추출.csv", "S6", "카테고리 누락으로 실행 차단"),
]

STEPS = [s for _, steps in FLOW for s in steps]
assert len(STEPS) == len(SHOTS) == 29, (len(STEPS), len(SHOTS))


def table_md(head, rows):
    out = ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def build_md():
    L = [f"# {TITLE}", ""] + [f"- {x}" for x in INTRO] + [""]
    L += ["## 파일", "", table_md(["파일", "내용"], [
        ("`index_mvp.html`", "화면 (브라우저로 열기)"),
        ("`walkthrough_mvp/demo.webm`", "전체 흐름 영상 (실제 사용 속도)"),
        ("`walkthrough_mvp/demo_질문답변.webm`", "이상치 질문·답변 및 재테스트 영상"),
        ("`dummy-data/`", "화면에 올려 볼 표본 파일"),
        ("`send/`", "메일 첨부용 MP4, PDF"),
    ]), ""]
    L += ["## 화면 구성", "", table_md(["구분", "화면", "사용자", "주요 기능"], SCREENS), "", "## 접속 역할별 메뉴", "", table_md(["접속 역할", "표시 메뉴", "가능한 작업"], ROLES), "", "## 화면 흐름", ""]
    n = 0
    for sec, steps in FLOW:
        L += [f"### {sec}", ""]
        for title, items in steps:
            L += [f"**{n + 1}. {title}**", ""] + [f"- {x}" for x in items] + ["", f"![{SHOTS[n].name}](walkthrough_mvp/{SHOTS[n].name})", ""]
            n += 1
    L += ["## 표본 파일", "", table_md(["파일", "화면", "결과"], [(f"`{a}`", b, c) for a, b, c in SAMPLES]), ""]
    L += ["## 이상치 질문·답변 운영 기준 (안)", "", table_md(["항목", "기준 (안)"], POLICY), ""]
    (MOCK / "사용_흐름_안내.md").write_text("\n".join(L), encoding="utf-8")


def build_pdf():
    e = html.escape
    tmp = Path(tempfile.mkdtemp())
    (tmp / "img").mkdir()

    def table(head, rows):
        return ("<table><tr>" + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr>"
                + "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in rows) + "</table>")

    B = [f"<h1>{e(TITLE)}</h1>", "<ul class=intro>" + "".join(f"<li>{e(x)}</li>" for x in INTRO) + "</ul>",
         "<h2>접속 역할별 메뉴</h2>", table(["접속 역할", "표시 메뉴", "가능한 작업"], ROLES),
         "<ul class=intro><li>사내 계정 로그인 후 역할에 해당하는 메뉴만 표시</li><li>역할에 없는 기능은 화면과 서버 양쪽에서 차단</li></ul>",
         "<h2 class=flow>화면 흐름</h2>"]  # 화면 구성 표는 PDF에 넣지 않는다 (md에만 있다)
    n = 0
    for sec, steps in FLOW:
        B.append(f"<h3>{e(sec)}</h3>")
        for title, items in steps:
            im = Image.open(SHOTS[n]).convert("RGB")
            im = im.resize((1360, round(im.height * 1360 / im.width)), Image.LANCZOS)
            name = f"{n + 1:02d}.jpg"
            im.save(tmp / "img" / name, quality=82)
            B.append(f"<figure><p class=step><b>{n + 1}. {e(title)}</b></p><ul>" + "".join(f"<li>{e(x)}</li>" for x in items)
                     + f"</ul><img src='img/{name}'></figure>")
            n += 1
    B += ["<h2>이상치 질문·답변 운영 기준 (안)</h2>", table(["항목", "기준 (안)"], POLICY), "<ul class=intro><li>PoC 구현 범위에 포함. 기준의 확정은 To-Be 개발 방안의 확인 요청 19~21번 회신 후</li></ul>"]
    css = """@page{size:A4;margin:16mm 14mm}
body{font:10.5pt/1.55 "NanumGothic","Malgun Gothic",sans-serif;color:#171717}
h1{font-size:18pt;margin:0 0 10pt}
h2{font-size:13pt;margin:18pt 0 8pt;border-bottom:1px solid #d4d4d4;padding-bottom:3pt}
h3{font-size:11.5pt;margin:18pt 0 8pt;padding:4pt 8pt;background:#f4f4f5;break-after:avoid}
ul{margin:0 0 6pt;padding-left:14pt}li{margin:0 0 1pt}
ul.intro{margin-bottom:4pt}
table{border-collapse:collapse;width:100%;margin:4pt 0 10pt;font-size:9.5pt}
th,td{border:1px solid #d4d4d4;padding:4pt 6pt;text-align:left;vertical-align:top}
th{background:#f4f4f5;font-weight:600}
td:first-child{white-space:nowrap}
figure{margin:0 0 14pt;break-inside:avoid}
figure img{display:block;max-width:90%;max-height:200mm;border:1px solid #d4d4d4;margin:0 auto}
h2.flow{break-before:page}
p.step{margin:0 0 2pt;font-size:11pt}b{font-weight:600}"""
    (tmp / "guide.html").write_text(f"<!doctype html><meta charset=utf-8><style>{css}</style>" + "\n".join(B), encoding="utf-8")
    out = HERE / "재고배분_화면흐름_안내.pdf"
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();"
          f"await p.goto('file://{tmp}/guide.html');await p.pdf({{path:{str(out)!r},format:'A4',printBackground:true}});await b.close()}})()")
    subprocess.run(["node", "-e", js], check=True)
    return out


if __name__ == "__main__":
    build_md()
    print(build_pdf())
