"""목업 시연용 더미 데이터 생성기.

모든 값은 가상이다. 파일 이름과 형식(인코딩, 구분자, 헤더 위치)만 고객 기초정보 PDF에 적힌
현행 형식을 따른다. 재고 파일의 72개 컬럼 중 PDF에 이름이 나온 15개만 실제 이름이고
나머지는 `미사용_NN` 자리표시다. 실행: python3 generate.py
"""
import csv
import random
from pathlib import Path

from openpyxl import Workbook

random.seed(20261117)
ROOT = Path(__file__).parent
DAY = "20261117"

STORES = ["명동본점", "월드타워", "부산", "제주", "인천공항T1", "인천공항T2", "김해공항", "김포공항", "김포공항B", "제주공항"]
CHANNELS = ["명동본점", "월드타워", "부산", "제주", "인천공항T1", "인천공항T2", "김해공항", "김포공항", "제주공항", "온라인"]
CATEGORIES = ["COS and PFM", "JEW and WATCH", "LIQUOR and TOBACCO", "ACC and GIFT", "FOOD", "ELECTRONICS"]
BRANDS = {c: [f"가상브랜드{chr(65 + i)}{j}" for j in range(1, 5)] for i, c in enumerate(CATEGORIES)}

# 재고 합본 CSV의 72개 컬럼 (0부터 센 위치). PDF 2-2에 나온 것만 실제 이름.
KNOWN = {1: "창고", 2: "점", 5: "상품코드", 6: "재고 관리유형", 7: "재고 관리년월", 8: "반입년월", 11: "상품명",
         12: "Category", 13: "Brand", 17: "매가($)", 22: "가용_일반가용", 23: "가용_온라인 일반가용",
         68: "선하증권관리ID", 69: "발주번호", 70: "코너", 71: "source_file"}
COLUMNS = [KNOWN.get(i, f"미사용_{i:02d}") for i in range(72)]


def make_skus():
    skus = []
    n = 2000000001
    for cat in CATEGORIES:
        for brand in BRANDS[cat]:
            for k in range(1, 7):
                skus.append({"code": str(n), "cat": cat, "brand": brand, "name": f"{brand} 가상상품 {k}",
                             "price": random.choice([28, 45, 72, 120, 185, 260])})
                n += 1
    return skus


SKUS = make_skus()


def inventory_rows(categories):
    rows = []
    for sku in SKUS:
        if sku["cat"] not in categories:
            continue
        for store in STORES:
            if random.random() < 0.35:
                continue
            for wh in ["2통물", f"{store}점센터", f"{store}대표매장"]:
                if wh == "2통물" and random.random() < 0.5:
                    continue
                row = [""] * 72
                row[1], row[2], row[5] = wh, store, sku["code"]
                row[6] = random.choice(["반입년월", "제조년월", "유효연월"])
                row[7] = random.choice(["202501", "202506", "202511", "202604", "202712"])
                row[8] = random.choice(["202503", "202509", "202602", "202608"])
                row[11], row[12], row[13] = sku["name"], sku["cat"], sku["brand"]
                row[17] = sku["price"]
                row[22] = random.randint(0, 40)
                row[23] = random.randint(0, 12)
                row[68] = f"BL{random.randint(100000, 999999)}"
                row[69] = f"PO{random.randint(10000, 99999)}"
                row[70] = f"{store} {sku['brand']} 코너"
                row[71] = f"상태별 재고조회(SKU)_{DAY}0902{CATEGORIES.index(sku['cat'])}.xlsx"
                rows.append(row)
    return rows


def write_csv(path, header, rows, encoding, delimiter=","):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding=encoding, newline="") as f:
        w = csv.writer(f, delimiter=delimiter)
        w.writerow(header)
        w.writerows(rows)
    return len(rows)


def main():
    out = {}
    inp = ROOT / "input"
    # 1. 재고: 전체 추출과 부분 추출(카테고리 2개 누락)
    out["재고 (전체 추출)"] = write_csv(inp / f"상태별재고조회(SKU)_합본_{DAY}.csv", COLUMNS, inventory_rows(CATEGORIES), "utf-8-sig")
    partial = [c for c in CATEGORIES if c not in ("COS and PFM", "FOOD")]
    out["재고 (부분 추출)"] = write_csv(inp / f"상태별재고조회(SKU)_합본_{DAY}_부분추출.csv", COLUMNS, inventory_rows(partial), "utf-8-sig")

    # 2. 판매예측: 엑셀, 1행 보조, 2행 헤더
    wb = Workbook()
    ws = wb.active
    ws.title = "채널별일예상판매수량"
    ws.append(["(보조 행) 가상 데이터"])
    ws.append(["구분", "채널", "카테고리", "브랜드", "상품코드", "바이어명", "부서명", "N-1월 판매수량", "N-2월 판매수량",
               "60일 일평균팔림세", "120일 일평균팔림세", "A등급여부", "최종일예상판매수량", "조정 사유"])
    n = 0
    for sku in SKUS:
        for ch in CHANNELS:
            if random.random() < 0.3:
                continue
            kind = "시내점" if ch in STORES[:4] else ("온라인" if ch == "온라인" else "공항")
            d60 = round(random.uniform(0, 3.5), 2)
            ws.append([kind, ch, sku["cat"], sku["brand"], sku["code"], "가상바이어", "가상부서", random.randint(0, 90),
                       random.randint(0, 90), d60, round(d60 * 0.9, 2), random.choice(["Y", "N"]), d60, ""])
            n += 1
    wb.save(inp / "일예상판매수량_20261116.xlsx")
    out["판매예측"] = n

    # 3. 공헌이익: UTF-16 탭 구분, 천단위 콤마 문자열
    rows = []
    for sku in SKUS:
        for ch in CHANNELS:
            sales = random.randint(1000, 90000)
            profit = int(sales * random.uniform(0.05, 0.4))
            rows.append([sku["code"], ch, f"{sales:,}", f"{profit:,}", f"{profit / sales * 100:.1f}"])
    out["공헌이익"] = write_csv(inp / "채널별상품공헌이익_202609.csv", ["상품코드", "채널", "순매출", "공헌이익", "공헌이익(%)"], rows, "utf-16", "\t")

    # 6~10. 코드표 5종: cp949, 원천 컬럼명
    out["점코드"] = write_csv(inp / f"점코드_{DAY}.csv", ["STR_CD", "STR_NM"], [[900 + i, s] for i, s in enumerate(STORES)], "cp949")
    brand_rows = [[f"{100000 + i:06d}", b, c] for i, (c, b) in enumerate((c, b) for c in CATEGORIES for b in BRANDS[c])]
    out["브랜드코드"] = write_csv(inp / f"브랜드코드_{DAY}.csv", ["BRNDCD", "BRND_NM", "CATE_NM"], brand_rows, "cp949")
    corner_rows = [[f"{1000 + i:04d}", f"{s} {b} 코너"] for i, (s, b) in enumerate((s, b) for s in STORES for c in CATEGORIES for b in BRANDS[c])]
    out["코너코드"] = write_csv(inp / f"코너코드_{DAY}.csv", ["SUBSTR(STR_CORNCD,4,4)", "STR_CORN_NM"], corner_rows, "cp949")
    wh_rows = [["W02", "2통물"]] + [[f"W{10 + i}", f"{s}점센터"] for i, s in enumerate(STORES)]
    out["창고코드"] = write_csv(inp / f"창고코드_{DAY}.csv", ["WHSCD", "WHS_NM"], wh_rows, "cp949")
    out["재고유형코드"] = write_csv(inp / f"재고관리년월코드_{DAY}.csv", ["IVTMGT_TYPE_CD", "IVTMGT_TYPE_NM"],
                              [[1, "반입년월"], [2, "제조년월"], [3, "유효연월"], ["z", "미입력"]], "cp949")

    # 4~5. MD 마스터
    mst = ROOT / "master"
    grp_rows = [[c, b, s, random.randint(1, 3)] for c in CATEGORIES for b in BRANDS[c] for s in STORES if random.random() < 0.7]
    out["양수도 그룹"] = write_csv(mst / "브랜드양수도그룹관리_20261110.csv", ["카테고리", "브랜드명", "지점", "양수도그룹구분"], grp_rows, "utf-8-sig")
    sheets = {
        "양수도제외브랜드": (["브랜드코드", "브랜드코드(최종)", "제외기한"], [[r[0], r[0], ""] for r in brand_rows[:5]]),
        "양수도제외상품": (["상품코드", "상품코드(최종)", "제외기한"], [[s["code"], s["code"], "20261231"] for s in SKUS[:6]]),
        "온라인전용SKU": (["상품코드"], [[s["code"]] for s in SKUS[10:14]]),
        "오프라인전용SKU": (["상품코드"], [[s["code"]] for s in SKUS[20:32]]),
        "온오프전환제외브랜드": (["브랜드코드", "점명", "제외기한"], [[r[0], random.choice(["", "명동본점"]), ""] for r in brand_rows[6:10]]),
        "온오프전환제외상품": (["상품코드", "점명", "제외기한"], [[s["code"], "", ""] for s in SKUS[40:48]]),
    }
    for fname, drop in [("양수도제외브랜드상품_20261112.xlsx", None), ("양수도제외브랜드상품_20261112_시트누락.xlsx", "온오프전환제외상품")]:
        wb = Workbook()
        wb.remove(wb.active)
        for name, (header, body) in sheets.items():
            if name == drop:
                continue
            ws = wb.create_sheet(name)
            ws.append(header)
            for r in body:
                ws.append(r)
        wb.save(mst / fname)
    out["제외·전용 SKU"] = sum(len(b) for _, b in sheets.values())

    # 시연용 프로그램 파일 (자리표시. 실제 배분 로직 없음)
    code = ROOT / "code"
    code.mkdir(exist_ok=True)
    note = '"""목업 시연용 자리표시 파일. 실제 배분 로직은 들어 있지 않다. {}"""\n'
    (code / "pipeline_운영본_v0.3.py").write_text(note.format("현행 운영본 역할.") + "DEFAULT_SETTINGS = {'hyst_min_qty': 3}\n", encoding="utf-8")
    (code / "pipeline_수정본_최소보충변경.py").write_text(note.format("최소 보충 수량 처리를 고친 수정본 역할.") + "DEFAULT_SETTINGS = {'hyst_min_qty': 2}\n", encoding="utf-8")
    (code / "pipeline_문법오류.py").write_text(note.format("등록 거절 시연용.") + "def allocate(:\n    pass\n", encoding="utf-8")
    (code / "pipeline_규칙위반.py").write_text(note.format("발송 한도 위반 시연용.") + "SEND_LIMIT_CHECK = False\n", encoding="utf-8")

    for k, v in out.items():
        print(f"{k}: {v}행")


if __name__ == "__main__":
    main()
