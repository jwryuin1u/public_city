// 사용 흐름을 자동으로 조작하고 단계별 화면과 영상을 저장한다.
// 실행: node operate.js        (index.html → walkthrough/)
//       node operate.js v2     (index_v2.html → walkthrough_v2/)
//       node operate.js mvp slow   (index_mvp.html → walkthrough_mvp/, 사람이 쓰는 속도)
// 결과: walkthrough/NN_이름.png, walkthrough/demo.webm (전체), walkthrough/demo_질문답변.webm (질문·답변과 재테스트만)
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const ROOT = __dirname;
const VARIANT = ['v2', 'mvp'].includes(process.argv[2]) ? process.argv[2] : 'v1';
const SLOW = process.argv.includes('slow'); // 사람이 쓰는 속도: 커서 이동, 한 글자씩 입력, 결과를 읽는 스크롤
const PAGE = { v1: 'index.html', v2: 'index_v2.html', mvp: 'index_mvp.html' }[VARIANT];
const OUT = path.join(ROOT, { v1: 'walkthrough', v2: 'walkthrough_v2', mvp: 'walkthrough_mvp' }[VARIANT]);
// 파일은 내용을 읽어 넘긴다 (경로로 넘기면 일부 환경에서 선택되지 않는다)
const D = (...p) => {
  const f = path.join(ROOT, 'dummy-data', ...p);
  return { name: path.basename(f), mimeType: 'application/octet-stream', buffer: fs.readFileSync(f) };
};
const PAUSE = SLOW ? 1700 : 900;

async function session(browser, videoName, body) {
  const ctx = await browser.newContext({
    viewport: { width: 1360, height: 860 }, deviceScaleFactor: 2, locale: 'ko-KR', timezoneId: 'Asia/Seoul',
    recordVideo: { dir: OUT, size: { width: 1360, height: 860 } },
  });
  if (SLOW) {
    // 녹화용 커서 표시 (화면 파일에는 들어가지 않는다)
    await ctx.addInitScript(() => {
      window.addEventListener('DOMContentLoaded', () => {
        const c = document.createElement('div');
        c.style.cssText = 'position:fixed;left:0;top:0;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;background:rgba(23,23,23,.75);border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.3);z-index:99999;pointer-events:none;transform:translate(680px,430px)';
        document.body.appendChild(c);
        window.addEventListener('mousemove', (e) => { c.style.transform = `translate(${e.clientX}px,${e.clientY}px)`; }, true);
      });
    });
  }
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto('file://' + path.join(ROOT, PAGE));
  // 로딩 표시가 끝난 뒤에 다음 동작을 한다
  page.idle = () => page.waitForFunction(() => !document.body.classList.contains('busy'));
  const raw = {};
  for (const m of ['click', 'fill', 'selectOption', 'setInputFiles']) raw[m] = page[m].bind(page);
  const moveTo = async (sel) => {
    const loc = page.locator(sel).first();
    if (!(await loc.count())) return;
    await loc.scrollIntoViewIfNeeded();
    const b = await loc.boundingBox();
    if (b) await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2, { steps: 30 });
    await page.waitForTimeout(350);
  };
  page.click = async (sel, ...r) => {
    await page.idle();
    if (SLOW) await moveTo(sel);
    await raw.click(sel, ...r);
    if (SLOW) await page.waitForTimeout(500);
  };
  page.fill = async (sel, text) => {
    await page.idle();
    if (!SLOW) return raw.fill(sel, text);
    await moveTo(sel);
    await raw.click(sel);
    const fb = await page.locator(sel).first().boundingBox(); // 커서가 글자를 가리지 않게 입력란 아래로 비킨다
    if (fb) await page.mouse.move(fb.x + fb.width / 2 + 24, fb.y + fb.height + 14, { steps: 8 });
    await page.keyboard.press('Control+A');
    await page.locator(sel).pressSequentially(text, { delay: 85 });
    await page.waitForTimeout(400);
  };
  page.selectOption = async (sel, v) => {
    await page.idle();
    if (SLOW) { await moveTo(sel); await page.waitForTimeout(400); }
    await raw.selectOption(sel, v);
    if (SLOW) await page.waitForTimeout(700);
  };
  page.setInputFiles = async (sel, f) => {
    await page.idle();
    if (SLOW) { await moveTo(`label.file:has(${sel}) .btn`); await page.waitForTimeout(700); }
    await raw.setInputFiles(sel, f);
    if (SLOW) await page.waitForTimeout(900);
  };
  // 결과를 읽듯이 아래로 훑고 다시 위로
  page.look = async () => {
    if (!SLOW) return;
    const h = await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight);
    for (let y = 520; y < h + 520; y += 520) {
      await page.evaluate((to) => window.scrollTo({ top: to, behavior: 'smooth' }), Math.min(y, h));
      await page.waitForTimeout(1500);
    }
    if (h > 0) { await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' })); await page.waitForTimeout(900); }
  };
  await body(page);
  const video = page.video();
  await ctx.close();
  fs.renameSync(await video.path(), path.join(OUT, videoName));
  return errors;
}

const go = (page, p) => page.click(`nav button[data-page="${p}"]`);
// 접속 역할을 바꾼다 (mvp 화면은 역할에 해당하는 메뉴만 보인다)
const as = (page, role) => page.selectOption('#role', role);
// 대상 카테고리가 빠진 입력 일자
const PARTIAL = VARIANT === 'mvp' ? '20261111' : '20260813';

// 수정본 등록 → 검증 실행 → 결과
async function registerAndRun(page, shot) {
  await page.setInputFiles('#codeFile', D('code', 'pipeline_수정본_최소보충변경.py'));
  await page.fill('#codeName', '최소보충 수정본');
  await page.fill('#codeMemo', '최소 보충 수량 미만 이동 처리 수정');
  await page.click('#btnRegister');
  await shot('S1_등록됨', '수정본이 V-002로 등록된다. 올린 파일은 바꾸거나 지울 수 없다');
  await go(page, 's2');
  await page.selectOption('#tDate', '20261116');
  await page.fill('#p_min_days', '4');
  await page.dispatchEvent('#p_min_days', 'change');
  await shot('S2_검증실행_설정', 'S2 검증 실행. 버전, 입력 일자를 고르고 최소보장일수를 4로 바꿔 본다 (이 실행에만 적용)');
  await page.click('#btnTestRun');
  await page.waitForTimeout(250);
  await shot('S3_실행중', '실행하면 입력 검증 → 프로그램 실행 → 규칙 확인 → 기록 저장 순으로 진행된다');
  await page.waitForSelector('#btnPromote:not([disabled])');
  await shot('S3_검증결과_이상치', 'S3 검증 결과. 운영 버전과의 건수 차이, 규칙 5개, 이상치 6건, 달라진 SKU가 보인다');
}

// 이상치 → 질문 목록 → 보내기 → 답변 받기 → 재테스트
async function questionLoop(page, shot) {
  await page.click('#btnMakeQ');
  await shot('Q_질문목록_생성', '질문·답변. 이상치마다 물어볼 사람(프로그램 작성자, 점별 바이어)과 질문이 자동으로 만들어진다');
  const dl = page.waitForEvent('download');
  await page.click('#btnQDown');
  await (await dl).saveAs(path.join(OUT, '질문목록_내려받은파일.csv'));
  await page.click('#btnQSend');
  await shot('Q_보냄_답변대기', '질문 목록을 파일로 내려받거나 받는 사람에게 보낸다. 보낸 뒤에는 답변 칸이 열린다');

  await as(page, 'buyer');
  await shot('Q_바이어_접속', '바이어로 접속하면 질문·답변 메뉴만 보이고 자기에게 온 질문에만 답할 수 있다');
  await page.selectOption('select[data-qa-choice="Q-01"]', '정상');
  await page.fill('input[data-qa-text="Q-01"]', '11/20 단체 예약 40개가 있어 필요함');
  await page.click('#btnQSave');
  await shot('Q_화면에서_답변', '답변 방법 1: 받는 사람이 화면에서 직접 고르고 적는다 (인천공항T1 바이어의 답변)');

  await as(page, 'user');
  await page.setInputFiles('#qaFile', D('answers', '질문목록_답변일부_선택오류.csv'));
  await page.click('#btnQUp');
  await shot('Q_답변파일_선택오류', '답변 방법 2: 답변이 적힌 파일을 올린다. 쓸 수 없는 답변 선택이 있으면 그 줄을 알려 준다');
  await page.setInputFiles('#qaFile', D('answers', '질문목록_답변완료.csv'));
  await page.click('#btnQUp');
  await shot('Q_답변완료_반영계획', '답변이 모두 들어오면 반영 계획이 나온다: 파라미터 변경, 이동 제외, 사유 확인, 프로그램 수정 필요');

  await page.click('#btnRetest');
  await page.waitForSelector('text=이상치가 모두 해소되거나 사유가 확인되었습니다');
  await shot('S3_재테스트_결과', '답변을 반영한 재테스트 결과. 이상치마다 해소, 확인됨, 남음이 표시되고 첫 테스트와의 차이가 보인다');
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  for (const f of fs.readdirSync(OUT)) fs.unlinkSync(path.join(OUT, f));
  const browser = await chromium.launch();
  let n = 0;
  const log = [];

  // ===== 전체 시나리오 (화면 저장 + demo.webm) =====
  const errors = await session(browser, 'demo.webm', async (page) => {
    const shot = async (name, caption) => {
      n += 1;
      const file = String(n).padStart(2, '0') + '_' + name + '.png';
      await page.idle();
      await page.waitForTimeout(PAUSE);
      await page.look();
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.screenshot({ path: path.join(OUT, file), fullPage: true });
      log.push({ file, caption, part: shot.part });
    };

    shot.part = 'A';
    await as(page, 'user');
    await shot('S1_처음', 'S1 내 프로그램 버전. 운영본 v0.3 하나가 운영 중이다');
    await page.setInputFiles('#codeFile', D('code', 'pipeline_문법오류.py'));
    await page.click('#btnRegister');
    await shot('S1_문법오류_거절', '문법 오류가 있는 파일은 등록이 거절되고 오류 위치가 보인다');
    await registerAndRun(page, shot);
    const dl = page.waitForEvent('download');
    await page.click('button[data-dl^="양수도_명동본점"]');
    await (await dl).saveAs(path.join(OUT, 'TEST_양수도_명동본점_20261116.csv'));
    await shot('S3_TEST_내려받기', '검증 실행 결과는 TEST_가 붙은 이름으로만 내려받아진다');

    shot.part = 'B';
    await questionLoop(page, shot);

    shot.part = 'C';
    await go(page, 's2');
    await page.selectOption('#tDate', PARTIAL);
    await page.click('#btnTestRun');
    await page.waitForSelector('.msg.bad');
    await shot('S3_카테고리누락_입력실패', '대상 카테고리가 빠진 입력을 고르면 입력 검증에서 멈춘다. 빠진 카테고리 이름이 보이고 결과 파일은 없다');

    await go(page, 's1');
    await page.setInputFiles('#codeFile', D('code', 'pipeline_규칙위반.py'));
    await page.fill('#codeName', '발송한도 실험본');
    await page.click('#btnRegister');
    await go(page, 's2');
    await page.selectOption('#tVer', 'V-003');
    await page.selectOption('#tDate', '20261116');
    await page.click('#btnTestRun');
    await page.waitForSelector('text=규칙 위반이 있어 운영 반영을 요청할 수 없습니다');
    await shot('S3_규칙위반', '규칙을 어기는 결과가 나오면 상태가 규칙위반이 되고 운영 반영 요청이 막힌다');

    const okRun = await page.evaluate(() => S.runs.find((r) => r.ver === 'V-002' && r.status === '완료').id);
    await page.selectOption('#pickRun', okRun);
    await page.click('#btnPromote');
    await as(page, 'it');
    await go(page, 's4');
    await page.waitForSelector('button[data-approve]:not([disabled])');
    await shot('S4_회귀결과', 'IT혁신팀으로 접속. S4 운영 반영 승인. 기준 입력으로 돌린 회귀 테스트 결과를 보고 승인한다');
    await page.fill('input[id^="opinion_"]', '회귀 결과 확인. 반영 승인');
    await page.click('button[data-approve]');
    await shot('S4_승인됨', '승인하면 수정본이 운영 버전이 되고 이전 운영본은 보관된다. 되돌리기도 할 수 있다');

    shot.part = 'D';
    await as(page, 'md');
    await go(page, 's5');
    await page.setInputFiles('#mFile', D('master', '양수도제외브랜드상품_20261112_시트누락.xlsx'));
    await page.click('#btnMaster');
    await shot('S5_시트누락_거절', 'S5 마스터 데이터. 시트가 빠진 파일은 거절되고 빠진 시트 이름이 보인다');
    await page.setInputFiles('#mFile', D('master', '양수도제외브랜드상품_20261112.xlsx'));
    await page.click('#btnMaster');
    await shot('S5_마스터_새버전', '온전한 파일은 새 버전(v6)으로 보관된다. 이전 버전은 남아 있다');

    await as(page, 'sop');
    await go(page, 's6');
    await shot('S6_입력상태_처음', 'S6 입력 상태. 판매예측과 코드표는 자동 수집됐고, 재고는 파일을 기다린다');
    await page.setInputFiles('#invFile', D('input', '상태별재고조회(SKU)_합본_20261117_부분추출.csv'));
    await page.click('#btnInv');
    await shot('S6_부분추출_실패', '부분 추출된 재고 파일을 올리면 실제로 파일을 읽어 빠진 카테고리를 알려 주고 실행을 막는다');
    await page.setInputFiles('#invFile', D('input', '상태별재고조회(SKU)_합본_20261117.csv'));
    await page.click('#btnInv');
    await shot('S6_전체추출_준비됨', '전체 추출 파일을 올리면 컬럼 72개, 카테고리 6개, 점 10개를 통과하고 입력 묶음이 준비된다');

    await go(page, 's7');
    await page.click('#btnProdRun');
    await page.waitForSelector('#btnContinue');
    await shot('S7_확인대기', 'S7 운영 실행. 판매예측 파일이 갱신 주기를 넘어 확인대기로 멈춘다. 담당자가 확인해야 진행된다');
    await page.click('#btnContinue');
    await page.waitForSelector('#btnApprove');
    await shot('S7_운영결과', '실행이 끝나면 요약 건수, 전일 대비 차이, 규칙 5개, 구간별 걸린 시간이 보인다');
    await go(page, 's8');
    await shot('S8_승인전_막힘', 'S8 결과 내려받기. 승인 전에는 ERP 업로드 파일을 받을 수 없다');
    await go(page, 's7');
    await page.click('#btnApprove');
    await shot('S7_승인됨', '담당자가 결과를 확인하고 승인한다');
    await go(page, 's8');
    await shot('S8_ERP파일_순서', '승인 뒤에는 ERP 업로드 파일이 올리는 순서(온→오프, 양수도, 오프→온)대로 놓인다');
    await go(page, 'hist');
    await shot('실행이력', '실행 이력. 재테스트와 회귀 실행까지 누가 언제 어떤 버전과 입력으로 실행했는지 모두 남는다');
  });

  // ===== 질문·답변과 재테스트만 담은 짧은 영상 =====
  const errors2 = await session(browser, 'demo_질문답변.webm', async (page) => {
    const wait = async () => { await page.idle(); await page.waitForTimeout(SLOW ? 2000 : 1400); };
    await as(page, 'user');
    await wait();
    await registerAndRun(page, wait);
    await page.evaluate(() => document.querySelector('#btnMakeQ').scrollIntoView({ block: 'center' }));
    await wait();
    await questionLoop(page, async () => {
      await wait();
      await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }));
      await wait();
      await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
    });
    await wait();
  });

  await browser.close();
  fs.writeFileSync(path.join(OUT, 'captions.json'), JSON.stringify(log, null, 2));
  const all = errors.concat(errors2);
  console.log(n + ' shots, page errors: ' + all.length);
  all.forEach((e) => console.log('  ' + e));
})().catch((e) => { console.error(e); process.exit(1); });
