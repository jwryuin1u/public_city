"""아키텍처 예시와 흐름도의 디자인 개선판. 내용은 build_diagram.py(기본판)와 같고 모양만 다르다.

바꾼 것: 좌표를 8px 격자에 맞춤, 상자 크기 통일, 글자 왼쪽 정렬과 번호 열, 회색 3단계와 강조색 1개(청록),
청록은 pipeline.py가 실행되는 곳에만 사용, 그 자리에 'pipeline.py' 칩 표시.

실행: python3 build_diagram_v2.py
결과: 선제적양수도_ToBe_아키텍처_흐름도_디자인개선.html (이 폴더)
"""
from html import escape as e
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "선제적양수도_ToBe_아키텍처_흐름도_디자인개선.html"

LH = 17      # 줄 간격
PAD = 12     # 상자 안쪽 여백
NUMW = 20    # 번호 열 너비
CHIP_W = 80  # 'pipeline.py' 칩 너비


def defs(uid):
    def m(i, cls):
        return (f'<marker id="{i}{uid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M1,1.5 L9,5 L1,8.5" class="{cls}"/></marker>')
    return "<defs>" + m("a", "ah") + "</defs>"


def card(x, y, w, h, lines, num=None, cls="card"):
    """lines: [(글, 클래스)] 또는 ("chip", 뒤에 붙는 글). 글은 왼쪽 정렬, 세로 가운데."""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="{cls}"/>']
    tx = x + PAD + (NUMW if num is not None else 0)
    # 칩이 있는 줄은 위아래로 2px씩 더 띄운다
    offs, acc = [], 0
    for t, _c in lines:
        acc += 2 if t == "chip" else 0
        offs.append(acc)
        acc += LH + (2 if t == "chip" else 0)
    top = y + h / 2 - (acc - LH) / 2 + 4.5
    if num is not None:
        out.append(f'<text x="{x + PAD}" y="{top}" class="num">{e(str(num))}</text>')
    for i, (t, c) in enumerate(lines):
        by = top + offs[i]
        if t == "chip":
            out.append(f'<rect x="{tx}" y="{by - 13}" width="{CHIP_W}" height="18" rx="4" class="chip"/>')
            out.append(f'<text x="{tx + CHIP_W / 2}" y="{by - 0.5}" text-anchor="middle" class="chipt">pipeline.py</text>')
            if c:
                out.append(f'<text x="{tx + CHIP_W + 8}" y="{by}" class="sub">{e(c)}</text>')
        else:
            out.append(f'<text x="{tx}" y="{by}" class="{c}">{e(t)}</text>')
    return "".join(out)


def arrow(d, uid, dashed=False, both=False):
    start = f' marker-start="url(#a{uid})"' if both else ""
    return f'<path d="{d}" class="{"ln dash" if dashed else "ln"}" marker-end="url(#a{uid})"{start}/>'


def label(x, y, t, anchor="start", cls="lb"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{e(t)}</text>'


# ───────────────────────── 그림 1. 아키텍처 ─────────────────────────
def architecture():
    u = "1"
    W, H = 1280, 760
    s = [defs(u)]
    for x, w, name in [(16, 232, "고객 내부망 (기간계)"), (288, 704, "Azure"), (1032, 232, "사용자")]:
        s.append(f'<rect x="{x}" y="16" width="{w}" height="728" rx="12" class="zone"/>')
        s.append(label(x + 16, 46, name, cls="zt"))

    # 고객 내부망
    s.append(card(32, 72, 200, 72, [("수집 중계 서버", "t"), ("Self-hosted Integration Runtime", "sv"), ("고객 내부망에 설치", "sub")]))
    s.append(label(32, 204, "원천 시스템", cls="cap"))
    s.append(card(32, 216, 200, 56, [("L-lit", "t"), ("재고 (매일)", "sub")]))
    s.append(card(32, 280, 200, 72, [("정보계", "t"), ("판매예측 (주 1회)", "sub"), ("코드표 5종", "sub")]))
    s.append(card(32, 360, 200, 56, [("L-DEX", "t"), ("공헌이익 (선택 입력)", "sub")], cls="card opt"))
    s.append(arrow("M132,216 V144", u))
    s.append(label(140, 184, "읽기 전용 조회"))
    s.append(arrow("M232,108 H312", u))

    # Azure 1행
    s.append(card(312, 72, 208, 72, [("수집", "t"), ("Azure Data Factory", "sv"), ("기간계 데이터를 원본 그대로 수집", "sub")], num=1))
    s.append(card(536, 72, 208, 72, [("입력 구성", "t"), ("Azure Container Apps Job", "sv"), ("현행 파일 이름·형식으로 변환", "sub")], num=2))
    s.append(arrow("M520,108 H536", u))

    # 저장소
    s.append(card(312, 208, 656, 72, [("저장소", "t"), ("Azure Data Lake Storage Gen2", "sv"),
                                      ("수집 원본 · 입력 묶음 · 마스터 · 프로그램 · 결과(검증용/운영용 분리)", "sub")], num=3))
    s.append(arrow("M416,144 V208", u))
    s.append(label(424, 180, "수집 원본"))
    s.append(arrow("M640,144 V208", u))
    s.append(label(648, 172, "입력 묶음"))
    s.append(label(648, 188, "(현행 파일 형식)"))

    # 실행기
    s.append(card(312, 344, 208, 96, [("실행기 (검증용)", "t"), ("Azure Container Apps Job", "sv"), ("chip", "수정 없이 실행"),
                                      ("운영 결과 변경 불가 · 외부 차단", "sub")], num=4, cls="card hi"))
    s.append(card(536, 344, 208, 96, [("실행기 (운영용)", "t"), ("Azure Container Apps Job", "sv"), ("chip", "수정 없이 실행"),
                                      ("승인된 운영 버전만 실행", "sub")], num=4, cls="card hi"))
    for cx in (416, 640):
        s.append(arrow(f"M{cx - 16},280 V344", u))
        s.append(label(cx - 24, 316, "입력 읽기", "end"))
        s.append(arrow(f"M{cx + 16},344 V280", u))
        s.append(label(cx + 24, 316, "결과 쓰기"))

    # 관리 화면
    s.append(card(312, 496, 656, 72, [("관리 화면", "t"), ("Azure App Service", "sv"),
                                      ("화면 9종 · 실행 요청 · 결과 비교 · 이상치 질문·답변 · 승인", "sub")], num=5))
    s.append(arrow("M416,496 V440", u))
    s.append(label(424, 472, "검증 실행 시작"))
    s.append(arrow("M640,496 V440", u))
    s.append(label(648, 472, "운영 실행 시작"))
    s.append(arrow("M820,496 V280", u, both=True))
    s.append(label(830, 384, "프로그램·마스터 업로드"))
    s.append(label(830, 400, "결과 조회·내려받기"))

    # 5행
    s.append(card(312, 632, 152, 88, [("기록 DB", "t"), ("Azure SQL Database", "sv"), ("버전 · 파라미터", "sub"), ("실행 이력 · 승인", "sub")], num=6))
    s.append(card(480, 632, 152, 88, [("로그인·권한", "t"), ("Microsoft Entra ID", "sv"), ("사내 계정 로그인", "sub"), ("역할 5종", "sub")], num=7))
    s.append(card(648, 632, 152, 88, [("알림", "t"), ("Azure Logic Apps", "sv"), ("수집·검증 실패", "sub"), ("실행 완료 · 승인 요청", "sub")], num=7))
    s.append(card(816, 632, 152, 88, [("공통", "t"), ("Key Vault", "sv"), ("Container Registry", "sv"), ("Log Analytics", "sv")]))
    s.append(arrow("M388,568 V632", u))
    s.append(label(396, 604, "기록"))
    s.append(arrow("M556,632 V568", u))
    s.append(label(564, 604, "인증"))
    s.append(arrow("M724,568 V632", u))
    s.append(label(732, 604, "알림 요청"))

    # 사용자
    for i, (role, what) in enumerate([("현업 사용자", "프로그램 등록 · 검증 실행"), ("바이어", "질문 답변"), ("IT혁신팀", "운영 반영 승인"),
                                      ("MD", "마스터 업로드"), ("S&OP 담당자", "운영 실행 · 결과 승인")]):
        s.append(card(1048, 72 + i * 56, 200, 48, [(role, "t"), (what, "sub")]))
    s.append(arrow("M1148,344 V512 Q1148,520 1140,520 H968", u))
    s.append(label(1140, 428, "웹 접속", "end"))
    s.append(label(1140, 444, "(사내 계정)", "end"))
    s.append(card(1048, 648, 200, 72, [("ERP (L-lit)", "t"), ("결과 수동 업로드", "sub"), ("현행 유지", "sub")], cls="card opt"))
    s.append(arrow("M968,544 H1192 Q1200,544 1200,552 V648", u, dashed=True))
    s.append(label(1192, 596, "승인된", "end"))
    s.append(label(1192, 612, "결과 파일", "end"))

    # 범례
    s.append('<rect x="776" y="80" width="16" height="16" rx="4" class="card hi"/>')
    s.append(label(800, 92, "pipeline.py가 실행되는 곳", cls="sub"))
    s.append('<path d="M776,112 H792" class="ln dash"/>')
    s.append(label(800, 116, "수작업 또는 선택 항목", cls="sub"))
    return W, H, "".join(s)


# ───────────────────────── 그림 2·3. 흐름도 ─────────────────────────
def swimlane(uid, lanes, steps, lane_w, start, extra=None):
    """lanes: 이름 목록. steps: (lane, 번호 또는 None, [(글, 클래스)], 클래스). 위에서 아래로 한 줄에 한 단계."""
    pad, head, bh, pitch = 16, 112, 64, 96
    bw = lane_w - 40
    W = pad * 2 + lane_w * len(lanes)
    H = head + pitch * (len(steps) - 1) + bh + 40
    s = [defs(uid), f'<rect x="{pad}" y="16" width="{W - pad * 2}" height="{H - 32}" rx="12" class="zone"/>']
    for i, name in enumerate(lanes):
        x = pad + i * lane_w
        if i:
            s.append(f'<path d="M{x},16 V{H - 16}" class="sep"/>')
        s.append(label(x + 20, 46, name, cls="zt"))
    pos = []
    for r, (lane, num, lines, cls) in enumerate(steps):
        x = pad + lane * lane_w + 20
        y = head + r * pitch
        pos.append((x, y))
        s.append(card(x, y, bw, bh, lines, num=num, cls=cls))
    lane, text = start
    cx = pad + lane * lane_w + lane_w / 2
    s.append(f'<circle cx="{cx}" cy="76" r="4" class="startdot"/>')
    s.append(label(cx + 12, 80, text, cls="sub"))
    s.append(arrow(f"M{cx},80 V{head}", uid))
    for r in range(len(steps) - 1):
        (x1, y1), (x2, y2) = pos[r], pos[r + 1]
        c1, c2 = x1 + bw / 2, x2 + bw / 2
        if c1 == c2:
            s.append(arrow(f"M{c1},{y1 + bh} V{y2}", uid))
        else:
            mid = y1 + bh + (pitch - bh) / 2
            k = 8 if c2 > c1 else -8
            s.append(arrow(f"M{c1},{y1 + bh} V{mid - 8} Q{c1},{mid} {c1 + k},{mid} H{c2 - k} Q{c2},{mid} {c2},{mid + 8} V{y2}", uid))
    if extra:
        s.append(extra(pad, head, bh, pitch, bw, lane_w, pos))
    return W, H, "".join(s)


def flow_prod():
    u = "2"
    lanes = ["시스템 (자동)", "S&OP 담당자", "ERP (L-lit)"]
    steps = [
        (0, 1, [("기간계 데이터 자동 수집", "t"), ("재고(매일) · 판매예측(주 1회) · 코드표 5종", "sub")], "card"),
        (0, 2, [("입력 묶음 구성 · 입력 검증", "t"), ("파일 · 컬럼 · 대상 카테고리 · 점 · 갱신 주기", "sub")], "card"),
        (0, 3, [("프로그램 실행", "t"), ("chip", "운영 버전 · 운영 파라미터")], "card hi"),
        (0, 4, [("업무 규칙 5개 확인 · 직전 결과 비교", "t"), ("규칙 위반 시 승인 불가", "sub")], "card"),
        (1, 5, [("결과 확인 후 승인", "t"), ("요약 · 규칙 판정 · 건수 비교 · 리포트", "sub")], "card"),
        (1, 6, [("ERP 업로드 파일 내려받기", "t"), ("승인된 결과만 제공", "sub")], "card"),
        (2, None, [("L-lit 수동 업로드 · 확정", "t"), ("순서: 온→오프, 양수도, 오프→온", "sub")], "card opt"),
    ]

    def extra(pad, head, bh, pitch, bw, lane_w, pos):
        x, y = pos[1]
        bx2 = pad + lane_w + 20
        out = [card(bx2, y, bw, bh, [("검증 실패 시 실행 차단 · 알림 수신", "t"), ("원인 확인 후 재수집 또는 파일 업로드", "sub")], cls="card opt")]
        out.append(arrow(f"M{x + bw},{y + bh / 2} H{bx2}", u, dashed=True))
        return "".join(out)

    return swimlane(u, lanes, steps, 344, (0, "정해진 시각 또는 담당자 요청"), extra)


def flow_test():
    u = "3"
    lanes = ["현업 사용자", "시스템 (자동)", "프로그램 작성자 · 점별 바이어", "IT혁신팀"]
    steps = [
        (0, 1, [("수정한 pipeline.py 등록", "t"), ("화면에서 파일 업로드", "sub")], "card"),
        (1, None, [("문법 · 라이브러리 검사", "t"), ("통과: 버전 부여 / 실패: 등록 거절", "sub")], "card"),
        (0, 2, [("조건 선택 후 검증 실행", "t"), ("버전 · 입력 일자 · 파라미터", "sub")], "card"),
        (1, None, [("검증용 실행기에서 실행", "t"), ("chip", "입력 검증 · 규칙 확인")], "card hi"),
        (0, 3, [("결과 확인", "t"), ("운영 버전 대비 차이 · 규칙 · 이상치", "sub")], "card"),
        (0, 4, [("이상치 질문 목록 전달", "t"), ("화면 발송 또는 파일(CSV)", "sub")], "card"),
        (2, None, [("답변 작성", "t"), ("정상 · 이동 제외 · 파라미터 · 로직 수정", "sub")], "card"),
        (1, 5, [("답변 반영 재테스트", "t"), ("chip", "해소 · 확인됨 · 남음")], "card hi"),
        (0, 6, [("운영 반영 요청", "t"), ("이상치 처리 상태 확인 후 요청", "sub")], "card"),
        (1, None, [("회귀 테스트 자동 수행", "t"), ("chip", "새 버전 · 운영 버전 비교")], "card hi"),
        (3, 7, [("승인 또는 반려", "t"), ("비교 결과 확인", "sub")], "card"),
        (1, None, [("운영 버전 교체", "t"), ("다음 운영 실행부터 적용 · 되돌리기 가능", "sub")], "card"),
    ]

    def extra(pad, head, bh, pitch, bw, lane_w, pos):
        (x1, y1), (x2, y2) = pos[4], pos[8]
        lx = x1 - 10
        a, b = y1 + bh / 2, y2 + bh / 2
        out = [arrow(f"M{x1},{a} H{lx + 6} Q{lx},{a} {lx},{a + 6} V{b - 6} Q{lx},{b} {lx + 6},{b} H{x2}", u, dashed=True)]
        out.append(label(lx + 10, (a + b) / 2 + 28, "이상치 없음"))
        return "".join(out)

    return swimlane(u, lanes, steps, 272, (0, "프로그램을 수정했을 때"), extra)


CSS = """
:root{color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:#fff;color:#171717;font-family:'Pretendard','Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo','NanumGothic',sans-serif;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
main{max-width:1248px;margin:0 auto;padding:40px 16px 64px}
h1{font-size:24px;font-weight:600;margin:0 0 8px;line-height:1.3}
.meta{color:#737373;font-size:13px;margin:0 0 40px}
h2{font-size:16px;font-weight:600;margin:48px 0 16px}
figure{margin:0;break-inside:avoid}
figure.narrow{max-width:1064px}
svg{display:block;width:100%;height:auto}
figcaption{font-size:13px;color:#525252;margin-top:12px;line-height:1.6}
ul.note{font-size:13px;color:#525252;line-height:1.7;margin:8px 0 0;padding-left:20px}
.zone{fill:#f6f6f6}
.sep{stroke:#e2e2e2;stroke-width:1;fill:none}
.card{fill:#fff;stroke:#dcdcdc;stroke-width:1}
.card.hi{fill:#e7f1f0;stroke:#0f5c5c;stroke-width:1.25}
.card.opt{stroke:#a3a3a3;stroke-dasharray:4 3}
.chip{fill:#fff;stroke:#0f5c5c;stroke-opacity:.45}
.chipt{font-family:ui-monospace,'Cascadia Mono',Consolas,'DejaVu Sans Mono',monospace;font-size:10.5px;fill:#0f5c5c}
.zt{font-size:13px;font-weight:600;fill:#171717}
.t{font-size:13px;font-weight:600;fill:#171717}
.sv{font-size:11px;fill:#525252}
.sub{font-size:11px;fill:#737373}
.cap{font-size:11px;fill:#737373}
.num{font-family:ui-monospace,'Cascadia Mono',Consolas,'DejaVu Sans Mono',monospace;font-size:11px;fill:#737373}
.lb{font-size:11px;fill:#525252}
.ln{fill:none;stroke:#525252;stroke-width:1.2}
.ln.dash{stroke-dasharray:4 3;stroke:#737373}
.ah{fill:none;stroke:#525252;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
.startdot{fill:#171717}
@media print{main{padding:0}h2{break-before:page}h2:first-of-type{break-before:auto}}
"""


def figure(fid, svg, aria, caption, cls=""):
    w, h, body = svg
    return (f'<figure id="{fid}" class="{cls}"><svg viewBox="0 0 {w} {h}" role="img" aria-label="{e(aria)}">{body}</svg>'
            f'<figcaption>{caption}</figcaption></figure>')


def main():
    parts = [
        "<h1>선제적 양수도 프로세스 To-Be</h1>",
        "<h2>1. 아키텍처 예시</h2>",
        figure("fig-arch", architecture(),
               "기간계 데이터를 Data Factory로 수집해 Data Lake Storage에 두고, Container Apps Job 실행기가 pipeline.py를 실행하며, 사용자는 App Service 관리 화면으로 접속하는 구성",
               "현행 pipeline.py는 수정 없이 Azure Container Apps Job(4 실행기)에서 실행 1건당 컨테이너 1개로 구동. "
               "검증용과 운영용 실행기를 분리해 검증 실행이 운영 결과에 영향을 주지 않음"),
        "<ul class=note><li>번호(1~7)는 To-Be 개발 방안 3장 구성도의 번호(①~⑦)와 같음</li>"
        "<li>공통 3종: Key Vault(기간계 접속 정보), Container Registry(실행 이미지), Log Analytics(실행·수집 로그)</li>"
        "<li>접근 승인 전인 원천은 5 관리 화면에서 파일 업로드. 이후 처리는 동일</li>"
        "<li>Azure 서비스는 제안이며 고객 환경과 사내 표준에 맞춰 확정</li></ul>",
        "<h2>2. 운영 실행 흐름 (매일)</h2>",
        figure("fig-prod", flow_prod(),
               "운영 실행은 데이터 자동 수집, 입력 검증, pipeline.py 실행, 규칙 확인까지 자동으로 진행되고 S&OP 담당자가 승인한 결과만 ERP에 수동 업로드됨",
               "1~4는 자동. 입력 검증에 실패하면 실행하지 않고 담당자에게 알림. S&amp;OP 담당자가 승인한 결과만 ERP 업로드 파일로 제공", "narrow"),
        "<h2>3. 검증 실행 흐름 (프로그램 수정 시)</h2>",
        figure("fig-test", flow_test(),
               "검증 실행은 수정본 등록, 검증 실행, 결과 확인, 이상치 질문과 답변, 재테스트, 운영 반영 요청, IT혁신팀 승인 순서로 진행됨",
               "번호(1~7)는 To-Be 개발 방안 4장 '검증 실행 흐름'의 단계 번호. 답변 유형은 정상, 이동 제외, 파라미터 조정, 로직 수정 4종. "
               "이상치가 없으면 4·5를 건너뛰고 6 운영 반영 요청으로 진행. 답변이 '로직 수정'이면 새 버전을 등록해 1부터 다시 진행"),
    ]
    OUT.write_text("<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
                   "<title>선제적 양수도 프로세스 To-Be</title><style>" + CSS + "</style></head><body><main>"
                   + "".join(parts) + "</main></body></html>", encoding="utf-8")
    print(OUT.name)


if __name__ == "__main__":
    main()
