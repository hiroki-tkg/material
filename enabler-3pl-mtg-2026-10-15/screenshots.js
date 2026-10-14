// 各スライドを PNG に書き出して確認する（開発用）。
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');
(async () => {
  const src = path.resolve(process.argv[2] || 'deck.html');
  const dir = path.resolve(process.argv[3] || 'shots');
  fs.mkdirSync(dir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1180, height: 900 }, deviceScaleFactor: 1 });
  await page.goto('file://' + src, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const n = await page.locator('.slide').count();
  for (let i = 0; i < n; i++) {
    await page.locator('.slide').nth(i).screenshot({ path: path.join(dir, `s${String(i + 1).padStart(2, '0')}.png`) });
  }
  await browser.close();
  console.log('shots', n);
})();
