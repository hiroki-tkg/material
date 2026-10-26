const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + path.resolve(__dirname, 'page4.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: path.resolve(__dirname, 'overlay.pdf'), printBackground: true, pageRanges: '1', preferCSSPageSize: true, width: '13.33in', height: '7.5in' });
  await b.close();
})();
