// 목업 시연 시나리오를 자동으로 조작하고 단계별 화면을 저장한다.
// 실행: node operate.js   (결과: walkthrough/NN_이름.png, walkthrough/demo.webm)
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const ROOT = __dirname;
const OUT = path.join(ROOT, 'walkthrough');
// 파일은 내용을 읽어 넘긴다 (경로로 넘기면 일부 환경에서 선택되지 않는다)
const D = (...p) => {
  const f = path.join(ROOT, 'dummy-data', ...p);
  return { name: path.basename(f), mimeType: 'application/octet-stream', buffer: fs.readFileSync(f) };
};
const PAUSE = 900;

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  for (const f of fs.readdirSync(OUT)) fs.unlinkSync(path.join(OUT, f));
  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: 1360, height: 860 }, deviceScaleFactor: 2, locale: 'ko-KR',
    recordVideo: { dir: OUT, size: { width: 1360, height: 860 } },
  });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto('file://' + path.join(ROOT, 'index.html'));

  let n = 0;
  const log = [];
  const shot = async (name, caption) => {
    n += 1;
    const file = String(n).padStart(2, '0') + '_' + name + '.png';
    await page.waitForTimeout(PAUSE);
    await page.screenshot({ path: path.join(OUT, file), fullPage: true });
    log.push({ file, caption });
  };
  const go = (p) => page.click(`nav button[data-page="${p}"]`);

  // ===== A. 검증 실행: 고친 프로그램을 올려 돌려 보고 운영에 반영 =====
  await shot('S1_처음', 'S1 내 프로그램 버전. 운영본 v0.3 하나가 운영 중이다');

  await page.setInputFiles('#codeFile', D('code', 'pipeline_문법오류.py'));
  await page.click('#btnRegister');
  await shot('S1_문법오류_거절', '문법 오류가 있는 파일은 등록이 거절되고 오류 위치가 보인다');

  await page.setInputFiles('#codeFile', D('code', 'pipeline_수정본_최소보충변경.py'));
  await page.fill('#codeName', '최소보충 수정본');
  await page.fill('#codeMemo', '최소 보충 수량 미만 이동 처리 수정');
  await page.click('#btnRegister');
  await shot('S1_등록됨', '수정본이 V-002로 등록된다. 올린 파일은 바꾸거나 지울 수 없다');

  await go('s2');
  await page.selectOption('#tDate', '20261116');
  await page.fill('#p_min_days', '4');
  await page.dispatchEvent('#p_min_days', 'change');
  await shot('S2_검증실행_설정', 'S2 검증 실행. 버전, 입력 일자를 고르고 최소보장일수를 5에서 4로 바꿔 본다 (이 실행에만 적용)');

  await page.click('#btnTestRun');
  await page.waitForTimeout(250);
  await shot('S3_실행중', '실행하면 입력 검증 → 프로그램 실행 → 규칙 확인 → 기록 저장 순으로 진행된다');
  await page.waitForSelector('#btnPromote:not([disabled])');
  await shot('S3_검증결과', 'S3 검증 결과. 운영 버전과의 건수 차이, 규칙 5개 통과, 달라진 SKU가 보인다');

  const dl = page.waitForEvent('download');
  await page.click('button[data-dl^="양수도_명동본점"]');
  await (await dl).saveAs(path.join(OUT, 'TEST_양수도_명동본점_20261116.csv'));
  await shot('S3_TEST_내려받기', '검증 실행 결과는 TEST_가 붙은 이름으로만 내려받아진다');

  await go('s2');
  await page.selectOption('#tDate', '20260813');
  await page.click('#btnTestRun');
  await page.waitForSelector('.msg.bad');
  await shot('S3_0813_입력실패', '부분 추출된 0813 입력을 고르면 입력 검증에서 멈춘다. 빠진 카테고리 이름이 보이고 결과 파일은 없다');

  await go('s1');
  await page.setInputFiles('#codeFile', D('code', 'pipeline_규칙위반.py'));
  await page.fill('#codeName', '발송한도 실험본');
  await page.click('#btnRegister');
  await go('s2');
  await page.selectOption('#tVer', 'V-003');
  await page.selectOption('#tDate', '20261116');
  await page.click('#btnTestRun');
  await page.waitForSelector('text=규칙 위반이 있어 운영 반영을 요청할 수 없습니다');
  await shot('S3_규칙위반', '규칙을 어기는 결과가 나오면 상태가 규칙위반이 되고 운영 반영 요청이 막힌다');

  // 정상 실행으로 돌아가 운영 반영 요청
  const okRun = await page.evaluate(() => S.runs.find((r) => r.ver === 'V-002' && r.status === '완료').id);
  await page.selectOption('#pickRun', okRun);
  await page.click('#btnPromote');
  await go('s4');
  await page.waitForSelector('button[data-approve]:not([disabled])');
  await shot('S4_회귀결과', 'S4 운영 반영 승인. 0812 기준 입력으로 새 버전과 운영 버전을 함께 돌린 회귀 결과가 보인다');

  await page.fill('input[id^="opinion_"]', '회귀 결과 확인. 반영 승인');
  await page.click('button[data-approve]');
  await shot('S4_승인됨', '승인하면 수정본이 운영 버전이 되고 이전 운영본은 보관된다. 되돌리기도 할 수 있다');

  // ===== B. 운영 실행: 오늘의 결과를 만들고 ERP 업로드 파일을 받는다 =====
  await go('s5');
  await page.setInputFiles('#mFile', D('master', '양수도제외브랜드상품_20261112_시트누락.xlsx'));
  await page.click('#btnMaster');
  await shot('S5_시트누락_거절', 'S5 마스터 데이터. 시트가 빠진 파일은 거절되고 빠진 시트 이름이 보인다');
  await page.setInputFiles('#mFile', D('master', '양수도제외브랜드상품_20261112.xlsx'));
  await page.click('#btnMaster');
  await shot('S5_마스터_새버전', '온전한 파일은 새 버전(v6)으로 보관된다. 이전 버전은 남아 있다');

  await go('s6');
  await shot('S6_입력상태_처음', 'S6 입력 상태. 판매예측과 코드표는 자동 수집됐고, 재고는 파일을 기다린다');
  await page.setInputFiles('#invFile', D('input', '상태별재고조회(SKU)_합본_20261117_부분추출.csv'));
  await page.click('#btnInv');
  await shot('S6_부분추출_실패', '부분 추출된 재고 파일을 올리면 실제로 파일을 읽어 빠진 카테고리를 알려 주고 실행을 막는다');
  await page.setInputFiles('#invFile', D('input', '상태별재고조회(SKU)_합본_20261117.csv'));
  await page.click('#btnInv');
  await shot('S6_전체추출_준비됨', '전체 추출 파일을 올리면 컬럼 72개, 카테고리 6개, 점 10개를 통과하고 입력 묶음이 준비된다');

  await go('s7');
  await page.click('#btnProdRun');
  await page.waitForSelector('#btnContinue');
  await shot('S7_확인대기', 'S7 운영 실행. 공헌이익 파일이 오래되어 확인대기로 멈춘다. 담당자가 확인해야 진행된다');
  await page.click('#btnContinue');
  await page.waitForSelector('#btnApprove');
  await shot('S7_운영결과', '실행이 끝나면 요약 건수, 전일 대비 차이, 규칙 5개, 구간별 걸린 시간이 보인다');

  await go('s8');
  await shot('S8_승인전_막힘', 'S8 결과 내려받기. 승인 전에는 ERP 업로드 파일을 받을 수 없다');
  await go('s7');
  await page.click('#btnApprove');
  await shot('S7_승인됨', '담당자가 결과를 확인하고 승인한다');
  await go('s8');
  await shot('S8_ERP파일_순서', '승인 뒤에는 ERP 업로드 파일이 올리는 순서(온→오프, 양수도, 오프→온)대로 놓인다');

  await go('hist');
  await shot('실행이력', '실행 이력. 누가 언제 어떤 버전과 입력으로 실행했는지 모두 남는다');

  await ctx.close();
  const video = fs.readdirSync(OUT).find((f) => f.endsWith('.webm'));
  if (video) fs.renameSync(path.join(OUT, video), path.join(OUT, 'demo.webm'));
  await browser.close();
  fs.writeFileSync(path.join(OUT, 'captions.json'), JSON.stringify(log, null, 2));
  console.log(n + ' shots, page errors: ' + errors.length);
  errors.forEach((e) => console.log('  ' + e));
})().catch((e) => { console.error(e); process.exit(1); });
