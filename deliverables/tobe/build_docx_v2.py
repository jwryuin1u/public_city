"""고객 전달 문서의 Word 디자인 개선판을 만든다. 내용은 build_docx.py(기본판)와 같고 모양만 다르다.

바꾼 것: 격자 표 → 가로 괘선만 있는 표, 여백과 간격, 글자 색 3단계와 강조색 1개(청록),
구분·결과 값 앞의 상태 점, 첫 장의 검토 결론 강조, 3장 구성도를 아키텍처 그림으로 교체.

실행: python3 build_docx_v2.py
결과: 선제적양수도_ToBe_개발방안_v1.0_디자인개선.docx (이 폴더),
      ../../mockup/send/재고배분_화면흐름_안내_디자인개선.docx
"""
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor, Twips
from PIL import Image

HERE = Path(__file__).parent
SEND = HERE.parent.parent / "mockup" / "send"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SEND))
import build_tobe as T  # noqa: E402
import build_guide as G  # noqa: E402

FONT = "맑은 고딕"
WIDTH = 17.0  # 본문 폭(cm): A4 21.0 - 좌우 여백 2.0 × 2

# 색: 회색 3단계와 강조색 1개
INK, SUB, MUTED = "171717", "525252", "737373"
HAIR, RULE = "E4E4E4", "171717"
ACCENT = "0F5C5C"


def rgb(h):
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn(k.replace("_", ":")), str(v))
    return e


def border(tag, color=None, size=4):
    if color is None:
        return el(tag, w_val="nil")
    return el(tag, w_val="single", w_sz=size, w_space=0, w_color=color)


def style_font(st, size, bold=False, color=INK):
    st.font.name = FONT; st.font.size = Pt(size); st.font.bold = bold; st.font.italic = False
    st.font.color.rgb = rgb(color)
    rpr = st.element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = el("w:rFonts"); rpr.insert(0, fonts)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        fonts.set(qn(a), FONT)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if fonts.get(qn(a)) is not None:
            del fonts.attrib[qn(a)]


def new_doc():
    d = Document()
    sec = d.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.0)
    sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(1.8)
    sec.footer_distance = Cm(0.9)
    style_font(d.styles["Normal"], 9.5)
    style_font(d.styles["Title"], 22, bold=True)
    style_font(d.styles["Heading 1"], 14, bold=True)
    style_font(d.styles["Heading 2"], 10.5, bold=True)
    style_font(d.styles["List Bullet"], 9.5, color=SUB)
    n = d.styles["Normal"].paragraph_format
    n.space_before = Pt(0); n.space_after = Pt(4); n.line_spacing = 1.3
    t = d.styles["Title"]
    bdr = t.element.pPr.find(qn("w:pBdr"))
    if bdr is not None:
        t.element.pPr.remove(bdr)
    t.paragraph_format.space_before = Pt(0); t.paragraph_format.space_after = Pt(4); t.paragraph_format.line_spacing = 1.15
    h1 = d.styles["Heading 1"].paragraph_format
    h1.space_before = Pt(28); h1.space_after = Pt(8); h1.keep_with_next = True; h1.line_spacing = 1.15
    h2 = d.styles["Heading 2"].paragraph_format
    h2.space_before = Pt(16); h2.space_after = Pt(4); h2.keep_with_next = True; h2.line_spacing = 1.15
    lb = d.styles["List Bullet"].paragraph_format
    lb.space_after = Pt(2); lb.line_spacing = 1.3
    return d


def run(p, text, size=9.5, color=INK, bold=False):
    r = p.add_run(text)
    r.font.size = Pt(size); r.font.bold = bold; r.font.name = FONT; r.font.color.rgb = rgb(color)
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    return r


def footer(d, label):
    p = d.sections[0].footer.paragraphs[0]
    for pos in (4680, 9360):  # 바닥글 스타일의 기본 탭(가운데, 오른쪽)을 지운다
        p.paragraph_format.tab_stops.add_tab_stop(Twips(pos), WD_TAB_ALIGNMENT.CLEAR)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(WIDTH), WD_TAB_ALIGNMENT.RIGHT)
    run(p, label + "\t", 8, MUTED)
    r = run(p, "", 8, MUTED)
    for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            e = el("w:fldChar", w_fldCharType=tag)
        else:
            e = el("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = text
        r._r.append(e)


def gap(d, pt):
    """높이를 정한 빈 줄. 표 뒤 간격에 쓴다."""
    p = d.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(pt)
    return p


def meta(d, text, after=4, keep=False):
    """작은 설명 줄. keep: 바로 아래 표와 같은 쪽에 둔다."""
    p = d.add_paragraph(); p.paragraph_format.space_after = Pt(after); p.paragraph_format.keep_with_next = keep
    run(p, text, 8.5, MUTED)
    return p


def h1(d, text):
    return d.add_heading(text, 1)


def h2(d, text):
    return d.add_heading(text, 2)


def tbl_setup(t, widths, hair=True, pad=(70, 0, 70, 170)):
    """열 너비 고정, 세로선 없음, 가로 괘선만. 글자가 본문 왼쪽 선에 맞도록 칸 왼쪽 여백은 0."""
    t.alignment = WD_TABLE_ALIGNMENT.LEFT; t.autofit = False
    pr = t._tbl.tblPr
    b = el("w:tblBorders")
    for side in ("top", "left"):
        b.append(border(f"w:{side}"))
    b.append(border("w:bottom", HAIR if hair else None))
    b.append(border("w:right"))
    b.append(border("w:insideH", HAIR if hair else None))
    b.append(border("w:insideV"))
    mar = el("w:tblCellMar")
    for side, w in zip(("top", "left", "bottom", "right"), pad):
        mar.append(el(f"w:{side}", w_w=w, w_type="dxa"))
    # Word는 표 속성의 순서를 지켜야 연다: tblBorders → tblLayout → tblCellMar → tblLook
    lay = pr.find(qn("w:tblLayout"))  # autofit = False 가 만든 것
    lay.addprevious(b)
    lay.addnext(mar)
    for row in t.rows:
        row._tr.get_or_add_trPr().append(el("w:cantSplit"))
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(WIDTH * w / 100)
    for i, w in enumerate(widths):
        t.columns[i].width = Cm(WIDTH * w / 100)


def cell_border(cell, **sides):
    """sides: bottom=(색, 굵기) 처럼 준다."""
    pr = cell._tc.get_or_add_tcPr()
    b = el("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        if side in sides:
            b.append(border(f"w:{side}", *sides[side]))
    w = pr.find(qn("w:tcW"))
    if w is not None:
        w.addnext(b)
    else:
        pr.insert(0, b)


def cell_text(cell, parts, size=9, align=None, keep=False):
    """parts: [(글, 색, 굵게)]. keep: 이 줄을 다음 줄과 같은 쪽에 둔다."""
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.25; p.paragraph_format.keep_with_next = keep
    if align:
        p.alignment = align
    for text, color, bold in parts:
        run(p, text, size, color, bold)
    return p


def dot(value, kinds):
    """값 앞에 상태 점을 붙인다. kinds: 값 → (점 글자, 점 색, 글자 색)"""
    mark, mc, tc = kinds[value]
    return [(mark + " ", mc, False), (value, tc, False)]


def table(d, head, rows, widths, label_col=False, render=None):
    """가로 괘선 표. label_col: 첫 열을 항목 이름으로 보고 흐리게 쓴다. render: {열: 값→parts}"""
    t = d.add_table(rows=1, cols=len(head))
    for i, h in enumerate(head):
        cell_text(t.rows[0].cells[i], [(h, MUTED, False)], 8.5, keep=True)
    t.rows[0]._tr.get_or_add_trPr().append(el("w:tblHeader"))
    for r in rows:
        cells = t.add_row().cells
        for i, v in enumerate(r):
            if render and i in render:
                cell_text(cells[i], render[i](v))
            elif label_col and i == 0:
                cell_text(cells[i], [(v, INK, True)])
            else:
                cell_text(cells[i], [(v, INK, False)])
    tbl_setup(t, widths)
    for c in t.rows[0].cells:
        cell_border(c, bottom=(RULE, 6))
    gap(d, 8)
    return t


def kv(d, rows, widths=(16, 84)):
    """머리줄 없는 항목-내용 표."""
    t = d.add_table(rows=0, cols=2)
    for n, (k, v) in enumerate(rows):
        cells = t.add_row().cells
        cell_text(cells[0], [(k, MUTED, False)], keep=n == 0)
        cell_text(cells[1], [(v, INK, False)], keep=n == 0)
    tbl_setup(t, widths)
    for c in t.rows[0].cells:
        cell_border(c, top=(HAIR, 4))
    gap(d, 8)
    return t


def callout(d, label, headline, detail):
    """왼쪽에 강조색 세로선이 있는 한 칸. 문서에서 가장 먼저 읽혀야 할 결론에만 쓴다."""
    t = d.add_table(rows=1, cols=1)
    c = t.rows[0].cells[0]
    cell_text(c, [(label, MUTED, False)], 8.5)
    p = c.add_paragraph(); p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(2); p.paragraph_format.line_spacing = 1.15
    run(p, headline, 15, INK, True)
    p = c.add_paragraph(); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.25
    run(p, detail, 9.5, SUB)
    tbl_setup(t, [100], hair=False, pad=(60, 240, 60, 0))
    cell_border(c, left=(ACCENT, 18))
    gap(d, 12)


def numbered(d, items):
    for i, x in enumerate(items, 1):
        p = d.add_paragraph()
        f = p.paragraph_format
        f.left_indent = Cm(0.7); f.first_line_indent = Cm(-0.7); f.space_after = Pt(3)
        f.tab_stops.add_tab_stop(Cm(0.7))
        run(p, f"{i}\t", 9.5, MUTED)
        run(p, x, 9.5, INK)


def bullets(d, items, keep=False):
    for x in items:
        p = d.add_paragraph(style="List Bullet")
        p.paragraph_format.keep_with_next = keep
        run(p, x, 9.5, SUB)


def picture(d, path, width_cm, frame=False, keep=False):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(4); p.paragraph_format.space_after = Pt(4); p.paragraph_format.keep_with_next = keep
    p.paragraph_format.line_spacing = 1.0
    shape = p.add_run().add_picture(str(path), width=Cm(width_cm))
    if frame:
        sp = shape._inline.graphic.graphicData.pic.spPr
        ln = OxmlElement("a:ln"); ln.set("w", "6350")
        clr = OxmlElement("a:srgbClr"); clr.set("val", HAIR)
        fill = OxmlElement("a:solidFill"); fill.append(clr); ln.append(fill)
        sp.append(ln)
    return p


KIND = {"자동화": ("●", ACCENT, INK), "화면": ("●", MUTED, INK), "신규": ("●", INK, INK), "유지": ("○", MUTED, SUB)}
RESULT = {"확인": ("●", ACCENT, INK), "착수 시 확인": ("○", MUTED, SUB)}


def build_tobe():
    d = new_doc()
    footer(d, "선제적 양수도 프로세스 To-Be 개발 방안 v1.0")
    d.add_paragraph("선제적 양수도 프로세스 To-Be 개발 방안", style="Title")
    meta(d, "판매 차질 방지 Agent(S&OP팀) PoC · v1.0 · 2026-11-25 · 인포유", after=16)
    callout(d, "검토 결론", "PoC 진행 가능", "현행 pipeline.py가 수정 없이 실행되고 재실행 결과가 동일함을 확인")
    kv(d, [
        ("목적", "선제적 양수도(재고배분) 프로세스의 To-Be 개발 방식 확정"),
        ("근거 자료", "기초정보(11/5), 과제 추진 방안 PPT, 현행 소스·입력·결과(11/18 기준), AS-IS 프로세스(S&OP 첨언)"),
        ("확정 절차", "개발 방식은 본 문서 기준. 세부 항목(8장)은 프로젝트 착수 시 협의하여 확정"),
    ])

    h1(d, "1. 개발 방식 요약")
    table(d, ["구분", "방식", "내용"], T.SUMMARY, [11, 28, 61], label_col=True)

    h1(d, "2. AS-IS → To-Be")
    meta(d, "단계 번호는 전달받은 AS-IS 프로세스(21단계) 기준", keep=True)
    table(d, ["단계", "업무", "AS-IS", "To-Be", "구분"], T.ASIS, [8, 15, 30, 35, 12],
          render={0: lambda v: [(v, MUTED, False)], 4: lambda v: dot(v, KIND)})
    meta(d, "자동화 8개 업무, 화면 전환 3개 업무, 현행 유지 3개 업무 (공헌이익, 배분 계산, ERP 반영), 신규 1개 업무 (이상치 확인)")

    h1(d, "3. To-Be 구성")
    picture(d, HERE / "diagram" / "1_아키텍처_예시.png", WIDTH)
    meta(d, "색으로 표시한 ④ 실행기가 pipeline.py를 실행하는 곳. 공통 3종은 접속 정보(Key Vault), 실행 이미지(Container Registry), "
            "로그(Log Analytics) 관리용", after=12)
    table(d, ["구성요소", "Azure 서비스 (제안)", "역할"], T.COMPONENTS, [16, 40, 44], label_col=True)
    meta(d, "Azure 서비스는 제안이며 고객 환경과 사내 표준에 맞춰 확정 (협의 사항 10번)")

    h1(d, "4. To-Be 프로세스")
    h2(d, "실행 모드")
    table(d, ["항목", "검증 실행", "운영 실행"], T.MODES, [16, 42, 42], render={0: lambda v: [(v, MUTED, False)]})
    h2(d, "운영 실행 흐름"); numbered(d, T.FLOW_PROD)
    h2(d, "검증 실행 흐름"); numbered(d, T.FLOW_TEST)

    h1(d, "5. 기능별 개발 방식")
    for name, rows in T.FUNC:
        h2(d, name)
        kv(d, rows, widths=(20, 80))

    h1(d, "6. 사전 검증 결과")
    meta(d, "전달받은 현행 소스와 11/18 입력으로 당사 환경(Linux)에서 실행해 확인한 내용", keep=True)
    table(d, ["확인 항목", "결과", "내용"], T.VERIFIED, [28, 16, 56], render={1: lambda v: dot(v, RESULT)})

    h1(d, "7. PoC 범위·인수 기준·진행 단계")
    h2(d, "범위")
    kv(d, T.SCOPE, widths=(12, 88))
    h2(d, "인수 기준 (안)"); numbered(d, T.ACCEPT)
    h2(d, "진행 단계")
    table(d, ["단계", "구분", "내용", "선행 조건"], T.STEPS, [7, 16, 44, 33],
          render={0: lambda v: [(v, MUTED, False)], 1: lambda v: [(v, INK, True)], 3: lambda v: [(v, SUB, False)]})
    meta(d, "기간과 투입 인력은 본 방안 기준으로 산정하여 별도 제시. 기간계 접근 방식과 Azure 환경 구성에 따라 변동")

    h1(d, "8. 프로젝트 착수 시 협의 사항")
    meta(d, "착수 시 협의하여 확정할 항목. 협의 전에는 '당사 기본안'으로 진행 (첨부 엑셀과 같은 내용)", keep=True)
    table(d, ["No", "구분", "협의 사항", "당사 기본안", "우선"],
          [(str(i + 1), a, b, c, p) for i, (a, b, c, _d, p) in enumerate(T.ASKS)], [6, 10, 47, 30, 7],
          render={0: lambda v: [(v, MUTED, False)], 1: lambda v: [(v, SUB, False)], 3: lambda v: [(v, SUB, False)],
                  4: lambda v: [(v, INK if v == "상" else MUTED, v == "상")]})
    out = HERE / "선제적양수도_ToBe_개발방안_v1.0_디자인개선.docx"
    d.save(out)
    return out


def build_guide():
    d = new_doc()
    footer(d, "재고배분 실행·검증 — 화면 흐름 안내")
    d.add_paragraph(G.TITLE, style="Title").paragraph_format.space_after = Pt(16)
    kv(d, [tuple(x.split(": ", 1)) for x in G.INTRO], widths=(12, 88))

    h1(d, "접속 역할별 메뉴")
    table(d, ["접속 역할", "표시 메뉴", "가능한 작업"], G.ROLES, [16, 44, 40], label_col=True)
    bullets(d, ["사내 계정 로그인 후 역할에 해당하는 메뉴만 표시", "역할에 없는 기능은 화면과 서버 양쪽에서 차단"])

    d.add_page_break()
    h1(d, "화면 흐름").paragraph_format.space_before = Pt(0)
    tmp = Path(tempfile.mkdtemp()); n = 0
    for sec, steps in G.FLOW:
        h2(d, sec)
        for title, items in steps:
            p = d.add_paragraph()
            f = p.paragraph_format
            f.keep_with_next = True; f.space_before = Pt(12); f.space_after = Pt(4)
            f.left_indent = Cm(0.8); f.first_line_indent = Cm(-0.8); f.tab_stops.add_tab_stop(Cm(0.8))
            run(p, f"{n + 1}\t", 10.5, ACCENT, True)
            run(p, title, 10.5, INK, True)
            for x in items:
                b = d.add_paragraph(style="List Bullet")
                b.paragraph_format.keep_with_next = True; b.paragraph_format.left_indent = Cm(1.2)
                run(b, x, 9.5, SUB)
            im = Image.open(G.SHOTS[n]).convert("RGB")
            im = im.resize((1360, round(im.height * 1360 / im.width)), Image.LANCZOS)
            shot = tmp / f"{n + 1:02d}.jpg"; im.save(shot, quality=82)
            w = WIDTH - 0.8; h = w * im.height / im.width
            if h > 19.0:  # 세로로 긴 화면은 한 쪽 안에 들어가게 줄인다
                h = 19.0; w = h * im.width / im.height
            pic = picture(d, shot, w, frame=True)
            pic.paragraph_format.left_indent = Cm(0.8)
            n += 1

    h1(d, "이상치 질문·답변 운영 기준 (안)")
    kv(d, G.POLICY, widths=(20, 80))
    bullets(d, ["PoC 구현 범위에 포함. 세부 기준은 프로젝트 착수 시 협의 (To-Be 개발 방안 협의 사항 19~21번)"])
    out = SEND / "재고배분_화면흐름_안내_디자인개선.docx"
    d.save(out)
    return out


if __name__ == "__main__":
    print(build_tobe())
    print(build_guide())
