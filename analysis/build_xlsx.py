"""공도복 매물 판단표 생성기 (모아타운 템플릿 v2.1 구조 유지, 공도복 치환)

사용:  python3 analysis/build_xlsx.py  →  analysis/bulgwang_park_판단표.xlsx
매물·시나리오는 아래 PROPERTIES / SCENARIOS 를 고쳐서 재생성. 단위: 억원.
검증:  soffice --headless --convert-to xlsx 로 재계산 후 오류 셀 0 확인 (verify() 참고)
"""
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName

OUT = "analysis/bulgwang_park_판단표.xlsx"

BLUE = Font(color="0000FF")
GREEN = Font(color="008000")
GREY = Font(color="666666")
BOLD = Font(bold=True)
YELLOW = PatternFill("solid", fgColor="FFFF00")
RED = PatternFill("solid", fgColor="FCE4E4")
HEAD = PatternFill("solid", fgColor="DDEBF7")

# ---------------------------------------------------------------- 입력
COMMON = [  # (name, label, value, note, yellow)
    ("완공시세_59", "완공 시세 (59타입, 억)  ← 직접 입력", 13.5, "판단표 모든 행의 완공 시세·안전마진·LTV 한도가 이 값으로 재계산. 행별로 다르게 보려면 판단표 해당 열에 직접 입력", True),
    ("조합원분양가_예상", "조합원분양가(예상) = 우선공급가 (59타입, 억)  ← 직접 입력", 9.55, "증산4 59타입 9.55 준용. 판단표 분담금·총지출·필요 대출이 이 값 × 조정계수로 재계산", True),
    ("완공시세_74", "완공 시세 (74타입, 억) — 현재 미사용", 14.5, "59만 분석 (사용자 지시)", False),
    ("전세대출상한", "전세대출 상한 (1주택자 규제지역, 억)", 2.0, "", False),
    ("전세금리", "전세대출 연이자율", 0.045, "", False),
    ("월세연액", "월세 연액 (120만×12)", 0.144, "", False),
    ("월세보증금", "월세 보증금", 0.3, "", False),
    ("마통금리", "마이너스통장 금리", 0.06, "", False),
    ("생활자금", "생활안정자금 주담대 한도 (억)", 1.0, "v0.1 시나리오에서는 미사용", False),
    ("생활자금금리", "주담대(생애최초)·생활안정자금 금리", 0.05, "", False),
    ("LTV_생애최초", "생애최초 주담대 LTV (최초 매수 1회)", 0.7, "실거주·전입 전제", False),
    ("원리금계수", "잔금대출 연 원리금 계수 (30년, 5%)", 0.0644, "", False),
    ("가용저축", "가용 저축 (주거비·대출비 차감 전, 억/년)", 0.3536, "", False),
    ("보유현금", "보유 현금 (억)", 2.75, "", False),
    ("인테리어", "인테리어·가구 (구축 실거주 시, 억)", 0.2, "신축 입주는 0", False),
    ("LTV", "잔금대출 LTV (규제지역 1주택)", 0.4, "", False),
    ("DSR", "DSR 한도", 0.4, "", False),
    ("대출상한_15이하", "주담대 상한: 시세 15억 이하 (억)", 6, "10·15 대책 구간", False),
    ("대출상한_25이하", "주담대 상한: 15~25억 (억)", 4, "", False),
    ("대출상한_25초과", "주담대 상한: 25억 초과 (억)", 2, "", False),
    ("매수연도", "매수 연도", 2026, "", False),
    ("이주연도", "이주(보상·명도)·착공 연도", 2030, "사용자: 이주·착공까지 약 4년", True),
    ("완공연도", "완공·입주 연도", 2033, "사용자: 착공 후 2~3년 → 2032(낙관)/2033(기준)", True),
    ("전매제한", "전매제한 기간 (년)", 3, "미확인 — 가정", True),
    ("실거주의무", "실거주 의무 (년)", 3, "미확인 — 가정", True),
    ("분양가계수", "조합원분양가 조정계수 (민감도 0.9/1.0/1.1)", 1.0, "판단표 조합원분양가 = 조합원분양가(예상) × 이 계수", True),
    ("공시가배수", "현물보상액 ÷ 공동주택가격 (1.4/1.6/1.8)", 1.6, "증산4 빌라 사례 1건 (공시 2.06→보상 3.3)", True),
    ("지분평당가", "현물보상 대지지분 평당가 (억/평)", 0.417, "증산4 빌라 사례 3.3억÷7.9평. 불광동 개별공시지가로 보정 필요", True),
    ("보상산정법", "현물보상 산정법 (1 = 공시가×배수, 2 = 대지지분×평당가(공시지가 보정), 3 = 두 방식 평균)", 1,
     "기준 = 공시가법 (증산4 사례와 동일 기준: 공시가 2.06 → 보상 3.3 = 1.6배). 공동주택은 거래사례비교법 → 공시가 배율이 실무에 가까움. 2·3은 참고", True),
    ("보상상승률", "현물보상액 연 상승률 (보상 확정 시점까지)", 0.03, "2026 공시가 기준값을 확정 연도까지 보정", True),
    ("보상확정연도", "현물보상 확정 연도 (사업계획승인 후 감정)", 2028, "사업계획승인 2027 초 예상 → 보상 2028 가정", True),
    ("분양가상승률", "조합원분양가 연 상승률 (분양가 확정 시점까지)", 0.03, "증산4 9.55는 2026 시점 값. 기본형건축비·택지비 상승 반영", True),
    ("분양가확정연도", "조합원분양가 확정 연도 (착공·분양 즈음)", 2030, "이주·착공 2030 가정과 동일", True),
    ("이주비_비율", "LH 이주비 한도 ÷ 현물선납액(현물보상액)  — 70% (변경 가능성 → 40%도 확인)", 0.7, "사용자 확인. 이주 시 주담대 잔액만큼만 사용(MIN(한도, 잔액)). 입주 시 원금 상환", True),
    ("이주비_금리", "LH 이주비 금리 (연, 이자는 매년 현금 납부)", 0.05, "사용자 가정 5%", True),
    ("공시지가_증산", "개별공시지가 증산동 92-27 (2026, 원/㎡) — 지분법 보정 기준", 2596000, "평당 약 858만. 증산4 사례 4,170만/평 ÷ 858만 = 공시지가의 4.86배", False),
    ("기준일", "권리산정(현물보상) 기준일", "2021-06-29", "캡처 13. 2021.6.29 이전 발표 사업지는 개정법 후에도 유지", False),
]

# 공급 구조 표: 구역 | 면적 | 소유자 | 총공급 | 우선공급 | 일반 | 공공자가 | 공공임대 | 기준가59 | 74 | 84 | 비고
SUPPLY = [
    ("불광근린공원", 88042, 2.83, 1455, 2150, 1170, 507, 215, 258, 9.55, 10.19, 11.30,
     "복합지구 지정 단계. 저층주거지형, 28층 이하. 세대 세부(우선/일반/공공자가)는 초기자료 참고만. 우선공급가: 증산4 준용(가정)"),
    ("불광동329-32", 48859, 3.86, None, 1670, None, None, None, 284, 9.55, 10.19, 11.30,
     "복합지구 지정 단계. 역세권형(준주거), 34층 이하. 시공사 2026.12 총회 예정. 소유자 수·우선공급 호수 미확인. 우선공급가: 증산4 준용(가정)"),
    ("증산4(참고)", 166531, 3.00, 655, 3568, None, None, None, 430, 9.55, 10.19, 11.30,
     "블로그 2026.09. 84 11.3억은 주민협의체 협의 중"),
]

# 매물 파라미터 (현금흐름 시트 열): 이름 → dict
PROPERTIES = {
    "A 331-160 (4.5억, 1층)": dict(
        매매가=4.5, 부대비=0.07, 승계보증금=0, 새전세=0,
        교체연도=0, 공실유지비=0.01, 월세수입전=0, 월세수입후=0, 주담대=2.03, 인테리어=0.2,
        이주지원한도="=ROUND(판단표!{권리가액}*이주비_비율,2)",
        전용=16.19, 대지지분=7.58, 공시가=1.09, 공시지가=2971000, 취득일="미확인",
        메모="1992.07 준공, 4층 중 1층(101호, 반지하 아님·지층은 별도 1호), 세입자 없음. 구역 내 유사 연식 공시가 비슷. 실거주(생애최초 주담대 2.03 = 매매가+부대비+인테리어−보유현금) → 이주 시 잔액 현금 상환 → 전세 거주 → 입주",
    ),
    "B 331-175 (4.1억, 2층)": dict(
        매매가=4.1, 부대비=0.065, 승계보증금=0, 새전세=0,
        교체연도=0, 공실유지비=0.01, 월세수입전=0, 월세수입후=0, 주담대=1.615, 인테리어=0.2,
        이주지원한도="=ROUND(판단표!{권리가액}*이주비_비율,2)",
        전용=11.57, 대지지분=5.94, 공시가=1.08, 공시지가=2883000, 취득일="미확인",
        메모="1992.10 준공, 4층 중 2층, 세입자 없음. 실거주(주담대 1.615) → 이주 시 잔액 현금 상환 → 전세 거주 → 입주",
    ),
}

# 판단표 행: (매물, 거주방식 코드 'J'전세/'W'월세/'C'현금청산, 타입, 라벨, 리스크 메모)
SCENARIOS = [
    ("A 331-160 (4.5억, 1층)", "O", 59, "S1 실거주(주담대) → 이주 시 전세 거주 → 입주 (59)", ""),
    ("B 331-175 (4.1억, 2층)", "O", 59, "S1 실거주(주담대) → 이주 시 전세 거주 → 입주 (59)", ""),
]
RISK_COMMON = ("현물보상권 승계 가능 가정(사용자 지시; 계약 전 LH 검증 45일은 필수). "
               "현물보상액 = 공시가×1.6(증산4 기준) × 2028까지 3%/년, 분양가 = 9.55 × 2030까지 3%/년. LH 이주비 한도 70%·5%. 전매제한·실거주 의무 미확인(가정 3년)")

# ---------------------------------------------------------------- 유틸
def name(wb, nm, ref):
    wb.defined_names[nm] = DefinedName(nm, attr_text=ref)


def put(ws, r, c, v, font=None, fill=None, comment=None, fmt=None):
    cell = ws.cell(row=r, column=c, value=v)
    if font: cell.font = font
    if fill: cell.fill = fill
    if comment: cell.comment = Comment(comment, "builder")
    if fmt: cell.number_format = fmt
    return cell


# ---------------------------------------------------------------- 가정
def build_assumptions(wb):
    ws = wb.create_sheet("가정")
    put(ws, 1, 1, "공통 가정 (파란색 = 직접 수정 가능) — 3080 도심공공주택복합사업 불광근린공원", BOLD)
    r = 3
    for nm, label, val, note, yellow in COMMON:
        put(ws, r, 1, label)
        put(ws, r, 2, val, BLUE, YELLOW if yellow else None)
        put(ws, r, 3, note, GREY)
        name(wb, nm, f"가정!$B${r}")
        r += 1
    r += 1
    put(ws, r, 1, "사업지 개요·확인 사항", BOLD); r += 1
    for t in [
        "• 불광근린공원: 구역 88,042㎡, 토지등소유자 1,455(추정), 공급 2,150, 평균대지지분 18.3평, 현물보상 기준일 2021.06.29 (캡처 13~16)",
        "• 기존 1,471세대 = 공동주택 1,243(85%) + 단독 228(15%). 반지하 59%, 과소필지 22%, 1종주거 32%",
        "• 공급 세부(우선 1,170 / 일반 507 / 공공자가 215 / 임대 258)는 초기 자료 — 참고만, 최신안으로 교체 필요",
        "• 총공급 ÷ 소유자 = 1.48 (증산4 5.45, 증산5 1.75) → 우선공급가를 낮출 구조적 여력이 작음. 증산4 가격을 하한 쪽으로 간주",
        "• 불광근린공원: 본지구 지정 완료, 2027 초 사업계획승인(사업시행인가) 예상(사용자 확인). 이주·착공 2030, 완공 2033은 사용자 가정(±2년). 329-32는 시공사 2026.12 총회 예정",
        "• 불광동 329-32: 48,859㎡, 용적률 386%(역세권형), 공급 1,670(분양 1,386/임대 284). 소유자 수 미확인",
        "• 승계: LH 검증(약 45일) 후 '승계 가능' 확인되면 계약(캡처 19). 블로그 주장 '분양계약 후 전매 가능'은 분양가상한제 전매제한과 충돌 → 미확인",
    ]:
        put(ws, r, 1, t); r += 1
    r += 1
    put(ws, r, 1, "시나리오 전제", BOLD); r += 1
    for t in [
        "• 권리가액 열 = 현물보상액 = 공동주택가격 × 배수 (비례율 없음). 대지지분 × 평당가는 교차검증 열",
        "• 조합원분양가(59) 열 = '조합원분양가(예상)' 입력값 × 조정계수. 공급구조표의 기준가는 참고용. 59타입만 분석(사용자 지시)",
        "• 분담금 = 우선공급가 − 현물보상액, 입주 시 잔금 100% 납부 (사용자 확인)",
        "• 이주비 상환 열 = LH 이주비 사용액(한도 = 현물선납액 × 70%, 40% 병행). 이주 시 주담대 잔액 상환에 필요한 만큼만 사용, 연 5% 이자는 매년 현금 납부, 원금은 입주 시 상환(필요 대출에 포함)",
        "• 안전마진 = 완공 시세 − (매매가 + 부대비 + 인테리어 + 분담금). 필요 대출 = 분담금 + 이주 지원 상환 − 입주 시 보유현금",
        "• LTV 한도 = MIN(완공시세 × 40%, 구간 상한 6/4/2억). DSR 필요 연소득 = 필요 대출 × 0.0644 ÷ 0.4",
        "• 현금청산·공공자가(이익공유형)는 검토 제외(사용자 지시). 모든 행은 현물보상권 승계 가능 전제",
        "• 처분 가능 시점 = 완공연도 + 전매제한. 실거주 의무 기간엔 전세 수입 없음(현금흐름은 입주에서 종료)",
    ]:
        put(ws, r, 1, t); r += 1
    r += 1
    put(ws, r, 1, "색 범례: 파란 글씨 = 입력값 / 검정 = 수식 / 초록 = 다른 시트 참조(덮어쓰기 가능) / 노란 칸 = 자주 바꾸는 입력 / 붉은 칸 = 리스크", GREY)
    r += 2

    # 공급 구조 표
    put(ws, r, 1, "공급 구조 표 (사업성 블록 대체) — 파란 글씨 = 입력값", BOLD); r += 1
    heads = ["구역", "면적(㎡)", "용적률", "토지등소유자", "총공급", "우선공급", "일반분양", "공공자가", "공공임대",
             "총÷소유자", "일반÷소유자", "기준가 59", "기준가 74", "기준가 84", 59, 74, 84, "비고"]
    hr = r
    for i, h in enumerate(heads, 1):
        put(ws, r, i, h, fill=HEAD)
    ws.cell(row=r, column=15).comment = Comment("조정 우선공급가(타입별) = 기준가 × 분양가계수. 판단표가 이 3열을 타입으로 INDEX/MATCH", "builder")
    r += 1
    first = r
    for row in SUPPLY:
        zone, area, far, owners, total, pri, gen, pub, rent, p59, p74, p84, note = row
        put(ws, r, 1, zone)
        for i, v in enumerate([area, far, owners, total, pri, gen, pub, rent], 2):
            put(ws, r, i, v, BLUE)
        put(ws, r, 10, f'=IF(D{r}="","미확인",E{r}/D{r})', fmt="0.00")
        put(ws, r, 11, f'=IF(OR(G{r}="",D{r}=""),"미확인",G{r}/D{r})', fmt="0.00")
        for i, v in enumerate([p59, p74, p84], 12):
            put(ws, r, i, v, BLUE)
        put(ws, r, 15, f"=ROUND(L{r}*분양가계수,2)", fill=YELLOW)
        put(ws, r, 16, f"=ROUND(M{r}*분양가계수,2)", fill=YELLOW)
        put(ws, r, 17, f"=ROUND(N{r}*분양가계수,2)", fill=YELLOW)
        put(ws, r, 18, note, GREY)
        r += 1
    last = r - 1
    name(wb, "공급_구역", f"가정!$A${first}:$A${last}")
    name(wb, "공급_타입", f"가정!$O${hr}:$Q${hr}")
    name(wb, "공급_조정가", f"가정!$O${first}:$Q${last}")
    r += 1
    put(ws, r, 1, "민감도 축: 분양가계수 0.9/1.0/1.1 · 공시가배수 1.4/1.6/1.8 · 완공연도 ±2 · 완공시세 ±1억 — 위 노란 칸을 바꾸면 판단표·현금흐름이 자동 재계산", GREY)
    ws.column_dimensions["A"].width = 48
    ws.column_dimensions["C"].width = 60
    return ws


# ---------------------------------------------------------------- 현금흐름
YEARS = 13  # 매수연도 + 0..12


def build_cashflow(wb):
    ws = wb.create_sheet("현금흐름")
    put(ws, 1, 1, "매물·거주방식별 연도별 현금흐름 — 세입자 보증금·전세대출 이자·마통 이자 반영 (공도복: 이주 지원 미확인 0)", BOLD)
    put(ws, 2, 1, "순현금이 음수면 마이너스통장 잔액(다음 해 이자). 파란 글씨 = 입력값. 연도는 '가정' 매수/이주/완공연도에 연동", GREY)
    put(ws, 3, 1, "매물별 파라미터", BOLD)
    params = ["매매가", "부대비", "승계보증금", "새전세", "이주지원한도", "교체연도", "공실유지비", "월세수입전", "월세수입후", "주담대", "인테리어"]
    labels = {"매매가": "매매가", "부대비": "부대비", "승계보증금": "현 세입자 보증금 (승계)", "새전세": "새 세입자 전세 (교체 시)",
              "이주지원한도": "LH 이주비 대출 한도 (= 판단표 권리가액 × 이주비_비율)", "교체연도": "세입자 교체 연도 (0 = 없음)",
              "공실유지비": "보유비·공실 유지비 (연, 재산세 등)", "월세수입전": "세입자 월세 수입 (연, 교체 전)", "월세수입후": "세입자 월세 수입 (연, 교체 후)",
              "주담대": "매수 시 주담대 (생애최초 LTV 70% 이내, 실거주)", "인테리어": "인테리어·가구 (구축 실거주)"}
    pcol = {}
    for j, (pname, p) in enumerate(PROPERTIES.items(), 2):
        put(ws, 3, j, pname, fill=HEAD)
        pcol[pname] = j
        for i, k in enumerate(params, 4):
            v = p[k]
            if isinstance(v, str) and v.startswith("="):
                row = 4 + [sc[0] for sc in SCENARIOS].index(pname)
                v = v.format(권리가액=f"${L(HEADERS.index('권리가액') + 1)}${row}")
                put(ws, i, j, v, GREEN)
            else:
                put(ws, i, j, v, BLUE)
    for i, k in enumerate(params, 4):
        put(ws, i, 1, labels[k])
    prow = {k: 4 + i for i, k in enumerate(params)}

    r = 4 + len(params) + 1
    put(ws, r, 1, "공통 파라미터 → '가정' 시트 이름 참조", GREY)
    r += 2
    outputs = {}
    for idx, (pname, mode, typ, label, _) in enumerate(SCENARIOS):
        if mode == "C":
            continue
        c = L(pcol[pname])
        P = lambda k: f"${c}${prow[k]}"
        put(ws, r, 1, f"{pname} · {label}", BOLD); r += 1
        for i, h in enumerate(["연도", "이벤트", "가용 저축", "주거비(−월세수입)", "주담대 원리금·이주비 이자", "마통 이자", "이벤트 현금(±)", "기말 순현금", "주담대·생활자금 잔액", "이주 지원 사용"], 1):
            put(ws, r, i, h, fill=HEAD)
        r += 1
        y0 = r
        leftover = f"(보유현금-({P('매매가')}+{P('부대비')}-{P('승계보증금')}))"
        deposit_at_move = f"IF(AND({P('교체연도')}>0,{P('교체연도')}<이주연도),{P('새전세')},{P('승계보증금')})"
        rent_income = f"IF(A{{r}}>이주연도,0,IF(OR({P('교체연도')}=0,A{{r}}<{P('교체연도')}),{P('월세수입전')},{P('월세수입후')}))"
        housing = {"J": "전세대출상한*전세금리", "W": "월세연액",
                   "O": f"IF(A{{r}}<이주연도,0,전세대출상한*전세금리)"}[mode]
        for k in range(YEARS):
            put(ws, r, 1, f"=매수연도+{k}")
            buy_txt = {"J": "매수: 갭 승계, 남는 현금→전세보증금(부족분 마통)", "W": "매수: 갭 승계, 월세보증금 0.3 지출",
                       "O": "매수: 주담대 실행, 인테리어, 실거주(주거비 0)"}[mode]
            move_txt = {"J": "이주: 세입자 보증금 반환(지원 한도 초과분 현금·마통)", "W": "이주: 세입자 보증금 반환",
                        "O": "이주: 주담대 잔액 현금 상환(지원 0), 전세 거주 시작(전세대출 2.0)"}[mode]
            in_txt = {"J": "입주: 전세 현금분 회수", "W": "입주: 월세보증금 회수", "O": "입주: 전세대출 상환(순효과 0)"}[mode]
            ev = (f'=IF(A{r}=매수연도,"{buy_txt}",IF(A{r}=이주연도,"{move_txt}",IF(A{r}=완공연도,"{in_txt}",'
                  f'IF(AND({P("교체연도")}>0,A{r}={P("교체연도")}),"세입자 교체",""))))')
            put(ws, r, 2, ev, GREY)
            put(ws, r, 3, f"=IF(A{r}=매수연도,0,가용저축)")
            put(ws, r, 4, f"=IF(OR(A{r}=매수연도,A{r}>완공연도),0,{housing.format(r=r)}+IF(A{r}<이주연도,{P('공실유지비')},0)-{rent_income.format(r=r)})")
            put(ws, r, 5, 0 if (mode != "O" or k == 0) else
                f"=IF(I{r-1}>0,MIN(I{r-1}*(1+생활자금금리),{P('주담대')}*원리금계수),0)+IF(AND(A{r}>이주연도,A{r}<=완공연도),J{r-1}*이주비_금리,0)")
            put(ws, r, 6, 0 if k == 0 else f"=MAX(0,-H{r-1})*마통금리")
            buy = {"J": f"MIN(0,{leftover})", "W": f"{leftover}-월세보증금",
                   "O": f"보유현금-({P('매매가')}+{P('부대비')}+{P('인테리어')})+{P('주담대')}"}[mode]
            back = {"J": f"MAX(0,{leftover})", "W": "월세보증금", "O": "0"}[mode]
            move = (f"-{deposit_at_move}+MIN({P('이주지원한도')},{deposit_at_move})" if mode != "O"
                    else (f"-(I{r-1}*(1+생활자금금리)-E{r})+MIN({P('이주지원한도')},I{r-1}*(1+생활자금금리)-E{r})" if k > 0 else "0"))
            g = (f"=IF(A{r}=매수연도,{buy},0)"
                 f"+IF(AND({P('교체연도')}>0,A{r}={P('교체연도')}),{P('새전세')}-{P('승계보증금')},0)"
                 f"+IF(A{r}=이주연도,{move},0)"
                 f"+IF(A{r}=완공연도,{back},0)")
            put(ws, r, 7, g)
            put(ws, r, 8, f"=G{r}" if k == 0 else f"=H{r-1}+C{r}-D{r}-E{r}-F{r}+G{r}")
            if mode == "O":
                put(ws, r, 9, f"=IF(A{r}=매수연도,{P('주담대')},0)" if k == 0
                    else f"=IF(A{r}>=이주연도,0,I{r-1}*(1+생활자금금리)-E{r})")
                owed = f"MIN({P('이주지원한도')},I{r-1}*(1+생활자금금리)-E{r})" if k > 0 else "0"
            else:
                put(ws, r, 9, 0)
                owed = f"MIN({P('이주지원한도')},{deposit_at_move})"
            put(ws, r, 10, f"=IF(A{r}=이주연도,{owed},0)" if k == 0 else f"=J{r-1}+IF(A{r}=이주연도,{owed},0)")
            r += 1
        y1 = r - 1
        put(ws, r, 7, "입주 시 보유현금 →")
        put(ws, r, 8, f"=INDEX(H{y0}:H{y1},MATCH(완공연도,A{y0}:A{y1},0))", fill=YELLOW)
        put(ws, r, 9, "이주 지원 상환 →")
        put(ws, r, 10, f"=INDEX(J{y0}:J{y1},MATCH(완공연도,A{y0}:A{y1},0))", fill=YELLOW)
        outputs[idx] = (f"현금흐름!$H${r}", f"현금흐름!$J${r}")
        r += 3
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 50
    for col in "CDEFGHIJ":
        ws.column_dimensions[col].width = 14
    return outputs


# ---------------------------------------------------------------- 보유현금 산출
def build_cash(wb, outputs):
    ws = wb.create_sheet("보유현금 산출")
    heads = ["구분", "매수 후 남는 현금", "저축1 연액", "년수1", "저축2 연액", "년수2", "저축3 연액", "년수3", "기타 유입(+)", "유출(−)", "입주 시 예상 보유현금", "메모"]
    for i, h in enumerate(heads, 1):
        put(ws, 1, i, h, fill=HEAD)
    refs = {}
    r = 2
    for idx, (pname, mode, typ, label, _) in enumerate(SCENARIOS):
        put(ws, r, 1, f"{pname} · {label}")
        if mode == "C":
            for i in range(2, 11): put(ws, r, i, "—", GREY)
            put(ws, r, 11, 0, GREY)
            put(ws, r, 12, "현금청산: 입주 없음", GREY)
        else:
            for i in range(2, 11): put(ws, r, i, "—", GREY)
            put(ws, r, 11, "=" + outputs[idx][0], GREEN)
            put(ws, r, 12, "→ '현금흐름' 시트 연도별 계산값 참조")
        refs[idx] = f"'보유현금 산출'!$K${r}"
        r += 1
    ws.column_dimensions["A"].width = 55
    return refs


# ---------------------------------------------------------------- 판단표
HEADERS = ["순위", "사업지", "상세구역", "매물", "거주 방식", "타입", "매매가", "전용(평)", "대지지분(평)", "부대비", "인테리어", "공시가", "공시지가(원/㎡)",
           "권리가액", "현물보상(지분법)", "조합원분양가(59)", "분담금(예상)", "완공 시세(59)", "예상 보유현금", "분담금 − 보유현금",
           "이주비 상환", "필요 대출", "총지출", "안전마진", "LTV 한도", "LTV 여유", "DSR 필요 연소득(억)",
           "대지지분 평당가", "공시가 배수", "취득일/기준일", "예외 요건(최초거래·무주택·1회승계)", "처분 가능 시점", "리스크·비고"]
NOTES = {
    "타입": "59 고정 (사용자 지시). 74는 가정 시트에 값만 보관",
    "권리가액": "공도복: 현물보상액 (비례율 없음) = 2026 기준값(보상산정법 1 공시가×1.6 기본) × (1+보상상승률)^(보상확정연도−매수연도)",
    "현물보상(지분법)": "지분법(공시지가 보정) 값. 권리가액은 보상산정법 스위치(1 공시가법 / 2 지분법 / 3 평균)",
    "조합원분양가(59)": "공도복: 우선공급가 = '가정' 조합원분양가(예상) × 조정계수 × (1+분양가상승률)^(분양가확정연도−매수연도). 행별 직접 입력 시 덮어쓰기",
    "완공 시세(59)": "= '가정' 완공시세_59. 행별로 숫자를 직접 입력하면 덮어쓰기",
    "이주비 상환": "LH 이주비 사용액(한도 = 현물선납액 × 이주비_비율, 연 5% 이자 매년 납부). 입주 시 원금 상환 → 필요 대출에 포함",
    "취득일/기준일": "현 소유자 취득일(등기부 갑구) vs 2021.06.29. 기준일 이후 취득이면 붉은 칸",
    "예외 요건(최초거래·무주택·1회승계)": "2025.8.1 시행 개정법 예외. 미확인이면 우선공급 행 + 현금청산 행 병기",
    "처분 가능 시점": "완공연도 + 전매제한 (미확인, 가정)",
}


def build_table(wb, cash_refs, outputs):
    ws = wb.create_sheet("판단표", 0)
    put(ws, 1, 1, "공도복 매물 시나리오 판단표 v1.0 (단위: 억원) — 불광근린공원 331-160·331-175 / 증산4 준용 가정 / 2026.11", BOLD)
    col = {h: i for i, h in enumerate(HEADERS, 1)}
    C = lambda h, r: f"{L(col[h])}{r}"
    for h, i in col.items():
        put(ws, 3, i, h, fill=HEAD, comment=NOTES.get(h))
    r = 4
    for idx, (pname, mode, typ, label, risk) in enumerate(SCENARIOS):
        p = PROPERTIES[pname]
        cash = mode == "C"
        put(ws, r, col["순위"], f"=RANK({C('안전마진', r)},${L(col['안전마진'])}$4:${L(col['안전마진'])}$199,0)")
        put(ws, r, col["사업지"], "불광근린공원")
        put(ws, r, col["상세구역"], "불광근린공원")
        put(ws, r, col["매물"], pname, fill=RED)
        put(ws, r, col["거주 방식"], label)
        put(ws, r, col["타입"], typ, BLUE, YELLOW)
        put(ws, r, col["매매가"], p["매매가"], BLUE)
        put(ws, r, col["전용(평)"], p["전용"], BLUE)
        put(ws, r, col["대지지분(평)"], p["대지지분"], BLUE)
        put(ws, r, col["부대비"], p["부대비"], BLUE)
        put(ws, r, col["인테리어"], 0 if cash else p.get("인테리어", 0), BLUE)
        put(ws, r, col["공시가"], p["공시가"], BLUE)
        put(ws, r, col["공시지가(원/㎡)"], p["공시지가"], BLUE)
        gong = f"ROUND({C('공시가', r)}*공시가배수,2)"
        jibun = f"ROUND({C('대지지분(평)', r)}*지분평당가*{C('공시지가(원/㎡)', r)}/공시지가_증산,2)"
        put(ws, r, col["권리가액"], f"=ROUND(CHOOSE(보상산정법,{gong},{jibun},({gong}+{jibun})/2)*(1+보상상승률)^(보상확정연도-매수연도),2)", GREEN, YELLOW)
        put(ws, r, col["현물보상(지분법)"], f"={jibun}", GREEN, comment="대지지분 × 증산4 평당가(4,170만) × (매물 공시지가 ÷ 증산동 92-27 공시지가)")
        put(ws, r, col["조합원분양가(59)"], 0 if cash else "=ROUND(조합원분양가_예상*분양가계수*(1+분양가상승률)^(분양가확정연도-매수연도),2)", GREEN, YELLOW)
        put(ws, r, col["분담금(예상)"], 0 if cash else f"={C('조합원분양가(59)', r)}-{C('권리가액', r)}")
        put(ws, r, col["완공 시세(59)"],
            f"={C('권리가액', r)}" if cash else "=완공시세_59",
            GREEN, YELLOW)
        put(ws, r, col["예상 보유현금"], f"={cash_refs[idx]}", GREEN, YELLOW)
        put(ws, r, col["분담금 − 보유현금"], f"={C('분담금(예상)', r)}-{C('예상 보유현금', r)}")
        put(ws, r, col["이주비 상환"], 0 if cash else f"={outputs[idx][1]}", GREEN)
        put(ws, r, col["필요 대출"], 0 if cash else f"={C('분담금(예상)', r)}+{C('이주비 상환', r)}-{C('예상 보유현금', r)}")
        put(ws, r, col["총지출"], f"={C('매매가', r)}+{C('부대비', r)}+{C('인테리어', r)}+{C('분담금(예상)', r)}")
        put(ws, r, col["안전마진"], f"={C('완공 시세(59)', r)}-{C('총지출', r)}")
        n = C('완공 시세(59)', r)
        put(ws, r, col["LTV 한도"], 0 if cash else f"=MIN({n}*LTV,IF({n}>25,대출상한_25초과,IF({n}>15,대출상한_25이하,대출상한_15이하)))")
        put(ws, r, col["LTV 여유"], 0 if cash else f"={C('LTV 한도', r)}-{C('필요 대출', r)}")
        put(ws, r, col["DSR 필요 연소득(억)"], 0 if cash else f"={C('필요 대출', r)}*원리금계수/DSR")
        put(ws, r, col["대지지분 평당가"], f"=ROUND({C('매매가', r)}/{C('대지지분(평)', r)},3)")
        put(ws, r, col["공시가 배수"], f"=ROUND({C('매매가', r)}/{C('공시가', r)},2)")
        put(ws, r, col["취득일/기준일"], f"{p['취득일']} / 2021.06.29", fill=RED)
        put(ws, r, col["예외 요건(최초거래·무주택·1회승계)"], "승계 가능 (가정) — 계약 전 LH 검증 45일 필수", fill=RED)
        put(ws, r, col["처분 가능 시점"], "—" if cash else "=완공연도+전매제한")
        put(ws, r, col["리스크·비고"], (risk + " " if risk else "") + RISK_COMMON + " | " + p["메모"], fill=RED)
        for h in ("매매가", "부대비", "공시가", "권리가액", "현물보상(지분법)", "조합원분양가(59)", "분담금(예상)", "완공 시세(59)",
                  "예상 보유현금", "분담금 − 보유현금", "이주비 상환", "필요 대출", "총지출", "안전마진", "LTV 한도", "LTV 여유", "DSR 필요 연소득(억)"):
            ws.cell(row=r, column=col[h]).number_format = "0.00"
        r += 1
    ws.freeze_panes = "F4"
    ws.column_dimensions["D"].width = 24
    ws.column_dimensions["E"].width = 38
    ws.column_dimensions[L(col["리스크·비고"])].width = 90
    ws.column_dimensions[L(col["예외 요건(최초거래·무주택·1회승계)"])].width = 40
    return ws


def main():
    wb = Workbook()
    wb.remove(wb.active)
    build_assumptions(wb)
    outputs = build_cashflow(wb)
    cash_refs = build_cash(wb, outputs)
    build_table(wb, cash_refs, outputs)
    wb.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
