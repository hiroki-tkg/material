// HTML デッキを Chromium で PDF にする。 node render.js in.html out.pdf
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const [inHtml, outPdf] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1128, height: 846 } });
  await page.goto('file://' + path.resolve(inHtml), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);
  await page.pdf({
    path: outPdf,
    width: '1128px',
    height: '846px',
    printBackground: true,
    preferCSSPageSize: true,
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  await browser.close();
})();
