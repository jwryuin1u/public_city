"""고객 전달 문서의 Word 판을 만든다 (검토·수정용). PDF와 같은 내용을 같은 데이터에서 만든다.

실행: python3 build_docx.py
결과: 선제적양수도_ToBe_개발방안_v1.0.docx (이 폴더), ../../mockup/send/재고배분_화면흐름_안내.docx
"""
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

HERE = Path(__file__).parent
SEND = HERE.parent.parent / "mockup" / "send"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SEND))
import build_tobe as T  # noqa: E402
import build_guide as G  # noqa: E402

FONT = "맑은 고딕"
WIDTH = 17.4  # 본문 폭(cm): A4 21.0 - 좌우 여백 1.8 × 2


def new_doc():
    d = Document()
    sec = d.sections[0]
    sec.orientation = WD_ORIENT.PORTRAIT
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(1.8)
    sec.top_margin, sec.bottom_margin = Cm(1.8), Cm(1.6)
    for name, size, bold in [("Normal", 10, False), ("Title", 19, True), ("Heading 1", 13, True), ("Heading 2", 11, True),
                             ("List Bullet", 10, False)]:
        st = d.styles[name]
        st.font.name = FONT; st.font.size = Pt(size); st.font.bold = bold
        st.font.color.rgb = RGBColor(0x17, 0x17, 0x17)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        st.paragraph_format.space_after = Pt(2)
    bdr = d.styles["Title"].element.pPr.find(qn("w:pBdr"))
    if bdr is not None:
        d.styles["Title"].element.pPr.remove(bdr)
    d.styles["Title"].paragraph_format.space_after = Pt(4)
    d.styles["Normal"].paragraph_format.line_spacing = 1.25
    d.styles["Heading 1"].paragraph_format.space_before = Pt(14)
    d.styles["Heading 1"].paragraph_format.space_after = Pt(5)
    d.styles["Heading 2"].paragraph_format.space_before = Pt(8)
    d.styles["Heading 2"].paragraph_format.space_after = Pt(3)
    return d


def footer_page_number(d, label):
    p = d.sections[0].footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(label + " · "); r.font.size = Pt(7.5); r.font.color.rgb = RGBColor(0x77, 0x77, 0x77)
    for code in ("PAGE",):
        run = p.add_run(); run.font.size = Pt(7.5)
        for tag, text in (("begin", None), (None, code), ("end", None)):
            if tag:
                el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), tag)
            else:
                el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = text
            run._r.append(el)


def fix_table(t, widths):
    """열 너비를 고정하고 칸 안쪽 여백을 준다 (Word와 다른 편집기에서 같은 모양이 되도록)."""
    tblPr = t._tbl.tblPr
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
    mar = OxmlElement("w:tblCellMar")
    for side, w in (("top", 50), ("left", 90), ("bottom", 50), ("right", 90)):
        el = OxmlElement(f"w:{side}"); el.set(qn("w:w"), str(w)); el.set(qn("w:type"), "dxa"); mar.append(el)
    tblPr.append(mar)
    for i, w in enumerate(widths):
        t.columns[i].width = Cm(WIDTH * w / 100)
        for row in t.rows:
            row.cells[i].width = Cm(WIDTH * w / 100)


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def write(cell, text, bold=False, size=9, color=None, align=None):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.15
    if align:
        p.alignment = align
    r = p.add_run(text); r.font.size = Pt(size); r.font.bold = bold; r.font.name = FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    if color:
        r.font.color.rgb = RGBColor(*color)
    return r


def table(d, head, rows, widths, first_col_label=False, colors=None, parent=None):
    """widths: 비율(합 100). colors: {열번호: 값→RGB} 로 글자색 지정."""
    t = (parent or d).add_table(rows=1, cols=len(head))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    for i, h in enumerate(head):
        write(t.rows[0].cells[i], h, bold=True); shade(t.rows[0].cells[i], "E7E7E9")
    for r in rows:
        cells = t.add_row().cells
        for i, v in enumerate(r):
            col = colors.get(i, {}).get(v) if colors else None
            write(cells[i], v, bold=bool(col) or (first_col_label and i == 0), color=col)
            if first_col_label and i == 0:
                shade(cells[i], "F7F7F8")
    fix_table(t, widths)
    d.add_paragraph().paragraph_format.space_after = Pt(0)
    return t


def bullets(d, items):
    for x in items:
        p = d.add_paragraph(x, style="List Bullet"); p.paragraph_format.space_after = Pt(1)


def numbered(d, items):
    for i, x in enumerate(items, 1):
        p = d.add_paragraph(f"{i}. {x}"); p.paragraph_format.left_indent = Cm(0.4); p.paragraph_format.space_after = Pt(1)


def note(d, text):
    p = d.add_paragraph(); r = p.add_run(text); r.font.size = Pt(8.5); r.font.color.rgb = RGBColor(0x52, 0x52, 0x52)


def diagram(d):
    """구성도를 표로 그린다 (Word에서 글자를 바로 고칠 수 있다)."""
    t = d.add_table(rows=2, cols=5); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    heads = ["고객 내부망 (기간계)", "", "Azure", "", "사용자"]
    body = ["L-lit (재고)\n정보계 (판매예측, 코드표)\nL-DEX (공헌이익, 선택)\n\n수집 중계 서버",
            "→\n전용선·VPN",
            "① 수집 (Data Factory)  →  ② 입력 구성 (현행 파일 형식)  →  ③ 저장소 (입력·결과·프로그램)\n\n"
            "④ 실행기 — 검증용 / 운영용\n입력 검증 → pipeline.py → 업무 규칙 확인\n\n"
            "⑤ 관리 화면 (실행·비교·질문·승인)   ⑥ 기록 DB (버전·파라미터·이력)   ⑦ 로그인·알림 (Entra ID, Logic Apps)",
            "←\n웹 화면",
            "현업 사용자\n바이어\nS&OP 담당자\nMD\nIT혁신팀\n\nERP(L-lit): 결과 수동 업로드"]
    for i, (h, b) in enumerate(zip(heads, body)):
        write(t.rows[0].cells[i], h, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        write(t.rows[1].cells[i], b, size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        if i in (0, 2, 4):
            shade(t.rows[0].cells[i], "E3EFEE" if i == 2 else "F1F1F2")
    fix_table(t, [22, 9, 44, 8, 17])
    d.add_paragraph().paragraph_format.space_after = Pt(0)


def build_tobe():
    d = new_doc()
    footer_page_number(d, "선제적 양수도 프로세스 To-Be 개발 방안 v1.0")
    d.add_paragraph("선제적 양수도 프로세스 To-Be 개발 방안", style="Title")
    note(d, "판매 차질 방지 Agent(S&OP팀) PoC · v1.0 · 2026-11-25 · 인포유")
    table(d, ["항목", "내용"], [
        ("목적", "선제적 양수도(재고배분) 프로세스의 To-Be 개발 방식 확정"),
        ("근거 자료", "기초정보(11/5), 과제 추진 방안 PPT, 현행 소스·입력·결과(11/18 기준), AS-IS 프로세스(S&OP 첨언)"),
        ("검토 결론", "PoC 진행 가능. 현행 pipeline.py가 수정 없이 실행되고 재실행 결과가 동일함을 확인"),
        ("확정 절차", "개발 방식은 본 문서 기준. 세부 항목(8장)은 프로젝트 착수 시 협의하여 확정"),
    ], [18, 82], first_col_label=True)

    d.add_heading("1. 개발 방식 요약", 1)
    table(d, ["구분", "방식", "내용"], T.SUMMARY, [11, 27, 62])

    d.add_heading("2. AS-IS → To-Be", 1)
    note(d, "단계 번호는 전달받은 AS-IS 프로세스(21단계) 기준")
    table(d, ["단계", "업무", "AS-IS", "To-Be", "구분"], T.ASIS, [8, 14, 30, 37, 11],
          colors={4: {"자동화": (0x0F, 0x5C, 0x5C), "화면": (0x27, 0x4A, 0x7A), "유지": (0x52, 0x52, 0x52), "신규": (0x7A, 0x4F, 0x00)}})
    note(d, "자동화 8개 업무, 화면 전환 3개 업무, 현행 유지 3개 업무 (공헌이익, 배분 계산, ERP 반영), 신규 1개 업무 (이상치 확인)")

    d.add_heading("3. To-Be 구성", 1)
    diagram(d)
    table(d, ["구성요소", "Azure 서비스 (제안)", "역할"], T.COMPONENTS, [16, 40, 44])
    note(d, "Azure 서비스는 제안이며 고객 환경과 사내 표준에 맞춰 확정 (협의 사항 10번)")

    d.add_heading("4. To-Be 프로세스", 1)
    d.add_heading("실행 모드", 2)
    table(d, ["항목", "검증 실행", "운영 실행"], T.MODES, [16, 42, 42])
    d.add_heading("운영 실행 흐름", 2); numbered(d, T.FLOW_PROD)
    d.add_heading("검증 실행 흐름", 2); numbered(d, T.FLOW_TEST)

    d.add_heading("5. 기능별 개발 방식", 1)
    for name, rows in T.FUNC:
        d.add_heading(name, 2)
        table(d, ["항목", "방식"], rows, [22, 78], first_col_label=True)

    d.add_heading("6. 사전 검증 결과", 1)
    note(d, "전달받은 현행 소스와 11/18 입력으로 당사 환경(Linux)에서 실행해 확인한 내용")
    table(d, ["확인 항목", "결과", "내용"], T.VERIFIED, [27, 14, 59],
          colors={1: {"확인": (0x17, 0x79, 0x4A), "착수 시 확인": (0x52, 0x52, 0x52)}})

    d.add_heading("7. PoC 범위·인수 기준·진행 단계", 1)
    d.add_heading("범위", 2)
    table(d, ["구분", "항목"], T.SCOPE, [12, 88], first_col_label=True)
    d.add_heading("인수 기준 (안)", 2); numbered(d, T.ACCEPT)
    d.add_heading("진행 단계", 2)
    table(d, ["단계", "구분", "내용", "선행 조건"], T.STEPS, [7, 15, 45, 33])
    note(d, "기간과 투입 인력은 본 방안 기준으로 산정하여 별도 제시. 기간계 접근 방식과 Azure 환경 구성에 따라 변동")

    d.add_page_break()
    d.add_heading("8. 프로젝트 착수 시 협의 사항", 1)
    note(d, "착수 시 협의하여 확정할 항목. 협의 전에는 '당사 기본안'으로 진행 (첨부 엑셀과 같은 내용)")
    table(d, ["No", "구분", "협의 사항", "당사 기본안", "우선"],
          [(str(i + 1), a, b, c, p) for i, (a, b, c, _d, p) in enumerate(T.ASKS)], [5, 10, 50, 28, 7],
          colors={})
    out = HERE / "선제적양수도_ToBe_개발방안_v1.0.docx"
    d.save(out)
    return out


def build_guide():
    d = new_doc()
    footer_page_number(d, "재고배분 실행·검증 — 화면 흐름 안내")
    d.add_paragraph(G.TITLE, style="Title")
    bullets(d, G.INTRO)
    d.add_heading("접속 역할별 메뉴", 1)
    table(d, ["접속 역할", "표시 메뉴", "가능한 작업"], G.ROLES, [16, 44, 40])
    bullets(d, ["사내 계정 로그인 후 역할에 해당하는 메뉴만 표시", "역할에 없는 기능은 화면과 서버 양쪽에서 차단"])
    d.add_page_break()
    d.add_heading("화면 흐름", 1)
    tmp = Path(tempfile.mkdtemp()); n = 0
    for sec, steps in G.FLOW:
        d.add_heading(sec, 2)
        for title, items in steps:
            p = d.add_paragraph(); p.paragraph_format.keep_with_next = True; p.paragraph_format.space_before = Pt(6)
            r = p.add_run(f"{n + 1}. {title}"); r.bold = True; r.font.size = Pt(10.5)
            for x in items:
                b = d.add_paragraph(x, style="List Bullet"); b.paragraph_format.space_after = Pt(1); b.paragraph_format.keep_with_next = True
            im = Image.open(G.SHOTS[n]).convert("RGB")
            im = im.resize((1360, round(im.height * 1360 / im.width)), Image.LANCZOS)
            f = tmp / f"{n + 1:02d}.jpg"; im.save(f, quality=82)
            w = 15.6; h = w * im.height / im.width
            if h > 20.0:  # 세로로 긴 화면은 한 쪽 안에 들어가게 줄인다
                h = 20.0; w = h * im.width / im.height
            pic = d.add_paragraph(); pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pic.add_run().add_picture(str(f), width=Cm(w))
            n += 1
    d.add_heading("이상치 질문·답변 운영 기준 (안)", 1)
    table(d, ["항목", "기준 (안)"], G.POLICY, [24, 76], first_col_label=True)
    bullets(d, ["PoC 구현 범위에 포함. 세부 기준은 프로젝트 착수 시 협의 (To-Be 개발 방안 협의 사항 19~21번)"])
    out = SEND / "재고배분_화면흐름_안내.docx"
    d.save(out)
    return out


if __name__ == "__main__":
    print(build_tobe())
    print(build_guide())
