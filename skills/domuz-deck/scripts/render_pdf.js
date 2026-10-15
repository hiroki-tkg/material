// deck.html → deck.pdf（1128×846px・1スライド1ページ）。Playwright の Chromium で印刷する。
//   NODE_PATH=$(npm root -g) node render_pdf.js [deck.html] [deck.pdf]
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const src = path.resolve(process.argv[2] || 'deck.html');
  const out = path.resolve(process.argv[3] || 'deck.pdf');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1128, height: 846 } });
  await page.goto('file://' + src, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: out, width: '1128px', height: '846px', printBackground: true, preferCSSPageSize: true });
  await browser.close();
  console.log('saved', out);
})();
