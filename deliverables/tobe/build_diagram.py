"""To-Be 아키텍처 예시와 흐름도(운영 실행, 검증 실행)를 HTML 한 장으로 만든다.

그림은 모두 인라인 SVG다. 외부 글꼴·스크립트를 쓰지 않아 파일 하나로 열린다.
실행: python3 build_diagram.py
결과: 선제적양수도_ToBe_아키텍처_흐름도.html (이 폴더)
"""
from html import escape as e
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "선제적양수도_ToBe_아키텍처_흐름도.html"

LH = 17  # 줄 간격


def defs(uid):
    return (f'<defs><marker id="a{uid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" class="ah"/></marker>'
            f'<marker id="d{uid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" class="ahd"/></marker></defs>')


def box(x, y, w, h, lines, cls="bx", rx=6):
    """lines: [(글, 클래스)]. 상자 안에서 세로 가운데 정렬."""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>']
    top = y + h / 2 - (len(lines) - 1) * LH / 2
    for i, (t, c) in enumerate(lines):
        out.append(f'<text x="{x + w / 2}" y="{top + i * LH + 4.5}" text-anchor="middle" class="{c}">{e(t)}</text>')
    return "".join(out)


def arrow(d, uid, dashed=False, both=False):
    m = f'd{uid}' if dashed else f'a{uid}'
    start = f' marker-start="url(#{m})"' if both else ""
    return f'<path d="{d}" class="{"ln dash" if dashed else "ln"}" marker-end="url(#{m})"{start}/>'


def label(x, y, t, anchor="start", cls="lb"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{e(t)}</text>'


# ───────────────────────── 그림 1. 아키텍처 ─────────────────────────
def architecture():
    u = "1"
    W, H = 1280, 800
    s = [defs(u)]
    # 구역
    for x, w, name in [(20, 220, "고객 내부망 (기간계)"), (300, 680, "Azure"), (1040, 220, "사용자")]:
        s.append(f'<rect x="{x}" y="50" width="{w}" height="730" rx="10" class="zone"/>')
        s.append(label(x + 16, 78, name, cls="zt"))

    # 고객 내부망
    s.append(box(40, 110, 180, 70, [("수집 중계 서버", "t"), ("Self-hosted Integration Runtime", "sv s10"), ("고객 내부망에 설치", "sub")]))
    s.append('<rect x="40" y="250" width="180" height="300" rx="6" class="grp"/>')
    s.append(label(130, 272, "원천 시스템", "middle", "sub"))
    s.append(box(54, 286, 152, 72, [("L-lit", "t"), ("재고 (매일)", "sub")]))
    s.append(box(54, 370, 152, 72, [("정보계", "t"), ("판매예측 (주 1회)", "sub"), ("코드표 5종", "sub")]))
    s.append(box(54, 454, 152, 72, [("L-DEX", "t"), ("공헌이익 (선택 입력)", "sub")], cls="bx opt"))
    s.append(arrow("M130,250 V180", u))
    s.append(label(138, 220, "읽기 전용 조회"))

    # Azure 1행: 수집, 입력 구성
    s.append(box(320, 110, 200, 70, [("① 수집", "t"), ("Azure Data Factory", "sv"), ("기간계 데이터를 원본 그대로 수집", "sub")]))
    s.append(box(540, 110, 200, 70, [("② 입력 구성", "t"), ("Azure Container Apps Job", "sv"), ("현행 파일 이름·형식으로 변환", "sub")]))
    s.append(arrow("M220,145 H320", u))
    s.append(arrow("M520,145 H540", u))

    # 저장소 (가로 막대)
    s.append(box(320, 250, 640, 70, [("③ 저장소", "t"), ("Azure Data Lake Storage Gen2", "sv"),
                                     ("수집 원본 · 입력 묶음 · 마스터 · 프로그램 · 결과(검증용/운영용 분리)", "sub")]))
    s.append(arrow("M420,180 V250", u))
    s.append(label(428, 220, "수집 원본"))
    s.append(arrow("M640,180 V250", u))
    s.append(label(648, 212, "입력 묶음"))
    s.append(label(648, 228, "(현행 파일 형식)"))

    # 실행기 2개
    s.append(box(320, 390, 200, 84, [("④ 실행기 (검증용)", "t"), ("Azure Container Apps Job", "sv"),
                                     ("입력 검증 → pipeline.py → 규칙 확인", "sub"), ("운영 자료 변경 불가 · 외부 통신 차단", "sub")], cls="bx hi"))
    s.append(box(540, 390, 200, 84, [("④ 실행기 (운영용)", "t"), ("Azure Container Apps Job", "sv"),
                                     ("입력 검증 → pipeline.py → 규칙 확인", "sub"), ("승인된 운영 버전만 실행", "sub")], cls="bx hi"))
    for cx in (420, 640):
        s.append(arrow(f"M{cx - 20},320 V390", u))
        s.append(label(cx - 28, 360, "입력 읽기", "end"))
        s.append(arrow(f"M{cx + 20},390 V320", u))
        s.append(label(cx + 28, 360, "결과 쓰기"))

    # 관리 화면 (가로 막대)
    s.append(box(320, 544, 640, 70, [("⑤ 관리 화면", "t"), ("Azure App Service", "sv"),
                                     ("화면 9종 · 실행 요청 · 결과 비교 · 이상치 질문·답변 · 승인", "sub")]))
    s.append(arrow("M420,544 V474", u))
    s.append(label(428, 514, "검증 실행 시작"))
    s.append(arrow("M640,544 V474", u))
    s.append(label(648, 514, "운영 실행 시작"))
    s.append(arrow("M800,544 V320", u, both=True))
    s.append(label(810, 426, "프로그램·마스터 업로드"))
    s.append(label(810, 443, "결과 조회·내려받기"))

    # 5행: 기록 DB, 로그인, 알림, 공통
    s.append(box(320, 684, 145, 76, [("⑥ 기록 DB", "t"), ("Azure SQL Database", "sv"), ("버전·파라미터", "sub"), ("실행 이력·승인", "sub")]))
    s.append(box(485, 684, 145, 76, [("⑦ 로그인·권한", "t"), ("Microsoft Entra ID", "sv"), ("사내 계정", "sub"), ("역할 5종", "sub")]))
    s.append(box(650, 684, 145, 76, [("⑦ 알림", "t"), ("Azure Logic Apps", "sv"), ("수집·검증 실패", "sub"), ("완료·승인 요청", "sub")]))
    s.append(box(815, 684, 145, 76, [("공통", "t"), ("Key Vault", "sv"), ("Container Registry", "sv"), ("Log Analytics", "sv")], cls="bx soft"))
    s.append(arrow("M392,614 V684", u))
    s.append(label(400, 654, "기록"))
    s.append(arrow("M557,684 V614", u))
    s.append(label(565, 654, "인증"))
    s.append(arrow("M722,614 V684", u))
    s.append(label(730, 654, "알림 요청"))

    # 사용자
    s.append('<rect x="1060" y="110" width="180" height="290" rx="6" class="grp"/>')
    s.append(label(1150, 132, "역할별 메뉴", "middle", "sub"))
    for i, (role, what) in enumerate([("현업 사용자", "등록·검증 실행"), ("바이어", "질문 답변"), ("IT혁신팀", "운영 반영 승인"),
                                      ("MD", "마스터 업로드"), ("S&OP 담당자", "운영 실행·결과 승인")]):
        s.append(box(1074, 144 + i * 50, 152, 42, [(role, "t"), (what, "sub")]))
    s.append(arrow("M1130,400 V566 H960", u))
    s.append(label(1122, 480, "웹 접속", "end"))
    s.append(label(1122, 497, "(사내 계정)", "end"))
    s.append(box(1060, 690, 180, 70, [("ERP (L-lit)", "t"), ("결과 수동 업로드", "sub"), ("현행 유지", "sub")], cls="bx opt"))
    s.append(arrow("M960,592 H1190 V690", u, dashed=True))
    s.append(label(1198, 630, "승인된", cls="lb"))
    s.append(label(1198, 647, "결과 파일", cls="lb"))

    # 범례
    s.append('<rect x="776" y="118" width="18" height="12" rx="2" class="bx hi"/>')
    s.append(label(802, 129, "pipeline.py를 실행하는 곳", cls="sub"))
    s.append('<path d="M776,150 H794" class="ln dash"/>')
    s.append(label(802, 154, "수작업 또는 선택 항목", cls="sub"))
    return W, H, "".join(s)


# ───────────────────────── 그림 2·3. 흐름도 ─────────────────────────
def swimlane(uid, lanes, steps, lane_w, extra=None, start=None):
    """lanes: 이름 목록. steps: (lane, [(글, 클래스)], 클래스). 위에서 아래로 한 줄에 한 단계."""
    pad, head, bh, pitch = 20, 96 if start else 64, 62, 96
    bw = lane_w - 40
    W = pad * 2 + lane_w * len(lanes)
    H = head + pitch * len(steps) + 10
    s = [defs(uid)]
    for i, name in enumerate(lanes):
        x = pad + i * lane_w
        s.append(f'<rect x="{x}" y="16" width="{lane_w}" height="{H - 32}" class="lane{" alt" if i % 2 else ""}"/>')
        s.append(f'<text x="{x + lane_w / 2}" y="42" text-anchor="middle" class="zt">{e(name)}</text>')
    pos = []
    for r, (lane, lines, cls) in enumerate(steps):
        x = pad + lane * lane_w + 20
        y = head + r * pitch
        pos.append((x, y))
        s.append(box(x, y, bw, bh, lines, cls=cls))
    if start:
        lane, text = start
        cx = pad + lane * lane_w + lane_w / 2
        s.append(f'<rect x="{cx - bw / 2}" y="54" width="{bw}" height="24" rx="12" class="pill"/>')
        s.append(f'<text x="{cx}" y="70.5" text-anchor="middle" class="sub">{e(text)}</text>')
        s.append(arrow(f"M{cx},78 V{head}", uid))
    for r in range(len(steps) - 1):
        (x1, y1), (x2, y2) = pos[r], pos[r + 1]
        c1, c2 = x1 + bw / 2, x2 + bw / 2
        if c1 == c2:
            s.append(arrow(f"M{c1},{y1 + bh} V{y2}", uid))
        else:
            mid = y1 + bh + (pitch - bh) / 2
            s.append(arrow(f"M{c1},{y1 + bh} V{mid} H{c2} V{y2}", uid))
    if extra:
        s.append(extra(pad, head, bh, pitch, bw, lane_w, pos))
    return W, H, "".join(s)


def flow_prod():
    u = "2"
    lanes = ["시스템 (자동)", "S&OP 담당자", "ERP (L-lit)"]
    steps = [
        (0, [("① 기간계 데이터 자동 수집", "t"), ("재고(매일) · 판매예측(주 1회) · 코드표 5종", "sub")], "bx"),
        (0, [("② 입력 묶음 구성 · 입력 검증", "t"), ("파일 · 컬럼 · 대상 카테고리 · 점 · 갱신 주기", "sub")], "bx"),
        (0, [("③ pipeline.py 실행", "t"), ("운영용 실행기 · 운영 버전 · 운영 파라미터", "sub")], "bx hi"),
        (0, [("④ 업무 규칙 5개 확인 · 직전 결과 비교", "t"), ("규칙 위반 시 승인 불가", "sub")], "bx"),
        (1, [("⑤ 결과 확인 후 승인", "t"), ("요약 · 규칙 판정 · 건수 비교 · 리포트", "sub")], "bx"),
        (1, [("⑥ ERP 업로드 파일 내려받기", "t"), ("승인된 결과만 제공", "sub")], "bx"),
        (2, [("L-lit 수동 업로드 · 확정", "t"), ("순서: 온→오프, 양수도, 오프→온", "sub")], "bx opt"),
    ]

    def extra(pad, head, bh, pitch, bw, lane_w, pos):
        x, y = pos[1]
        bx2 = pad + lane_w + 20
        out = [box(bx2, y, bw, bh, [("검증 실패 시 실행 차단 · 알림 수신", "t"), ("원인 확인 후 재수집 또는 파일 업로드", "sub")], cls="bx opt")]
        out.append(arrow(f"M{x + bw},{y + bh / 2} H{bx2}", u, dashed=True))
        return "".join(out)

    return swimlane(u, lanes, steps, 340, extra, start=(0, "시작: 매일 정해진 시각 또는 담당자 요청"))


def flow_test():
    u = "3"
    lanes = ["현업 사용자", "시스템 (자동)", "프로그램 작성자 · 점별 바이어", "IT혁신팀"]
    steps = [
        (0, [("① 수정한 pipeline.py 등록", "t"), ("화면에서 파일 업로드", "sub")], "bx"),
        (1, [("문법 · 라이브러리 검사", "t"), ("통과: 버전 부여 / 실패: 등록 거절", "sub")], "bx"),
        (0, [("② 조건 선택 후 검증 실행", "t"), ("버전 · 입력 일자 · 파라미터", "sub")], "bx"),
        (1, [("검증용 실행기에서 실행", "t"), ("입력 검증 → pipeline.py → 규칙 5개", "sub")], "bx hi"),
        (0, [("③ 결과 확인", "t"), ("운영 버전 대비 차이 · 규칙 · 이상치", "sub")], "bx"),
        (0, [("④ 이상치 질문 목록 전달", "t"), ("화면 발송 또는 파일(CSV) 내려받기", "sub")], "bx"),
        (2, [("답변 작성", "t"), ("정상 / 이동 제외 /", "sub"), ("파라미터 조정 / 로직 수정", "sub")], "bx"),
        (1, [("⑤ 답변 반영 재테스트", "t"), ("이상치별 상태: 해소 · 확인됨 · 남음", "sub")], "bx hi"),
        (0, [("⑥ 운영 반영 요청", "t"), ("이상치 처리 상태 확인 후 요청", "sub")], "bx"),
        (1, [("회귀 테스트 자동 수행", "t"), ("기준 입력으로 새 버전 · 운영 버전 비교", "sub")], "bx hi"),
        (3, [("⑦ 승인 또는 반려", "t"), ("비교 결과 확인", "sub")], "bx"),
        (1, [("운영 버전 교체", "t"), ("다음 운영 실행부터 적용 · 되돌리기 가능", "sub")], "bx"),
    ]

    def extra(pad, head, bh, pitch, bw, lane_w, pos):
        (x1, y1), (x2, y2) = pos[4], pos[8]
        lx = x1 - 11
        out = [arrow(f"M{x1},{y1 + bh / 2} H{lx} V{y2 + bh / 2} H{x2}", u, dashed=True)]
        my = (y1 + y2 + bh) / 2
        out.append(label(lx + 9, my + 4, "이상치 없음"))
        return "".join(out)

    return swimlane(u, lanes, steps, 270, extra)


CSS = """
:root{color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:#fff;color:#1a1a1a;font-family:'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo','NanumGothic',sans-serif;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
main{max-width:1240px;margin:0 auto;padding:32px 16px 48px}
h1{font-size:22px;margin:0 0 4px}
.meta{color:#5a5a5a;font-size:13px;margin:0 0 28px}
h2{font-size:16px;margin:36px 0 10px;padding-bottom:6px;border-bottom:1.5px solid #1a1a1a}
figure{margin:0;break-inside:avoid}
figure.narrow{max-width:1060px}
svg{display:block;width:100%;height:auto}
figcaption{font-size:13px;color:#3a3a3a;margin-top:10px;line-height:1.6}
ul.note{font-size:13px;color:#3a3a3a;line-height:1.7;margin:10px 0 0;padding-left:18px}
.zone{fill:#f6f6f4;stroke:#cfcfcb}
.lane{fill:#f6f6f4;stroke:#cfcfcb}.lane.alt{fill:#fbfbfa}
.grp{fill:none;stroke:#b9b9b4;stroke-dasharray:2 3}
.bx{fill:#fff;stroke:#6f6f6a;stroke-width:1.1}
.bx.hi{fill:#e3efee;stroke:#0f5c5c;stroke-width:1.4}
.bx.opt{stroke-dasharray:5 3;fill:#fff}
.bx.soft{fill:#fbfbfa}
.pill{fill:#fff;stroke:#b9b9b4}
.zt{font-size:13.5px;font-weight:700;fill:#1a1a1a}
.t{font-size:13px;font-weight:700;fill:#1a1a1a}
.sv{font-size:11.5px;font-weight:600;fill:#0f5c5c}
.s10{font-size:10.5px}
.sub{font-size:11px;fill:#5a5a5a}
.lb{font-size:11px;fill:#3a3a3a;paint-order:stroke;stroke:#f6f6f4;stroke-width:4px;stroke-linejoin:round}
.ln{fill:none;stroke:#4a4a4a;stroke-width:1.3}
.ln.dash{stroke-dasharray:5 4}
.ah{fill:#4a4a4a}.ahd{fill:#4a4a4a}
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
               "현행 pipeline.py는 수정 없이 <b>Azure Container Apps Job</b>(④ 실행기)에서 실행 1건당 컨테이너 1개로 구동. "
               "검증용과 운영용 실행기를 분리해 검증 실행이 운영 결과에 영향을 주지 않음"),
        "<ul class=note><li>번호(①~⑦)는 To-Be 개발 방안 3장의 구성요소 번호와 같음</li>"
        "<li>공통 3종: Key Vault(기간계 접속 정보), Container Registry(실행 이미지), Log Analytics(실행·수집 로그)</li>"
        "<li>접근 승인 전인 원천은 ⑤ 관리 화면에서 파일 업로드. 이후 처리는 동일</li>"
        "<li>Azure 서비스는 제안이며 고객 환경과 사내 표준에 맞춰 확정</li></ul>",
        "<h2>2. 운영 실행 흐름 (매일)</h2>",
        figure("fig-prod", flow_prod(),
               "운영 실행은 데이터 자동 수집, 입력 검증, pipeline.py 실행, 규칙 확인까지 자동으로 진행되고 S&OP 담당자가 승인한 결과만 ERP에 수동 업로드됨",
               "①~④는 자동. 입력 검증에 실패하면 실행하지 않고 담당자에게 알림. S&amp;OP 담당자가 승인한 결과만 ERP 업로드 파일로 제공", "narrow"),
        "<h2>3. 검증 실행 흐름 (프로그램 수정 시)</h2>",
        figure("fig-test", flow_test(),
               "검증 실행은 수정본 등록, 검증 실행, 결과 확인, 이상치 질문과 답변, 재테스트, 운영 반영 요청, IT혁신팀 승인 순서로 진행됨",
               "원 번호(①~⑦)는 To-Be 개발 방안 4장 '검증 실행 흐름'의 단계 번호. "
               "이상치가 없으면 ④·⑤를 건너뛰고 ⑥ 운영 반영 요청으로 진행. 답변이 '로직 수정'이면 새 버전을 등록해 ①부터 다시 진행"),
    ]
    OUT.write_text("<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
                   "<title>선제적 양수도 프로세스 To-Be</title><style>" + CSS + "</style></head><body><main>"
                   + "".join(parts) + "</main></body></html>", encoding="utf-8")
    print(OUT.name)


if __name__ == "__main__":
    main()
