// Optional browser smoke test: NODE_PATH must resolve an installed playwright.
// Usage: node tests/explorer.browser.cjs DEMO_HTML REAL_HTML OUTPUT_DIRECTORY
const { chromium } = require('playwright');
const { pathToFileURL } = require('node:url');
const path = require('node:path');
const fs = require('node:fs');
(async () => {
  const [demo, real, output] = process.argv.slice(2);
  if (!demo || !real || !output) throw Error('Expected demo HTML, real HTML and output directory');
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ headless: true,
    ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE } : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 1100 }, deviceScaleFactor: 1 });
    const errors = [];
    let network = 0;
    page.on('pageerror', e => errors.push(e.message));
    page.on('request', r => { if (/^https?:/.test(r.url())) network++; });
    await page.goto(pathToFileURL(path.resolve(demo)).href);
    if (!(await page.title()).includes('Big-Repo')) throw Error('Brand');
    await page.selectOption('#kind', 'skill');
    if (await page.locator('#ability-list article').count() !== 8) throw Error('Eight skills');
    await page.selectOption('#goal', 'skills');
    if (await page.locator('#ability-list article').count() !== 2) throw Error('Goal filter');
    await page.selectOption('#goal', 'all');
    await page.selectOption('#kind', 'template');
    if (await page.locator('#ability-list article').count() !== 6) throw Error('Six templates');
    await page.selectOption('#kind', 'all');
    await page.locator('#template-options input').first().check();
    const preview = await page.locator('#template-preview').inputValue();
    if (!preview.includes('技能草稿') || !preview.includes('提交说明')) throw Error('Template combination');
    await page.click('#copy-template');
    if (!(await page.locator('#template-status').textContent())) throw Error('Clipboard feedback');
    const templateDownload = page.waitForEvent('download');
    await page.click('#download-template');
    const templatePath = path.join(output, 'template-draft.md');
    await (await templateDownload).saveAs(templatePath);
    if (fs.readFileSync(templatePath, 'utf8') !== preview) throw Error('Template export');
    if (await page.locator('#version-list .version').count() < 5) throw Error('Timeline');
    if (!(await page.locator('#timeline-source').textContent()).includes('快照')) throw Error('Timeline provenance');
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: path.join(output, 'explorer-demo.png'), fullPage: false });
    for (const [scenario, stop] of [['happy', 5], ['tests', 2], ['review', 3], ['ci', 4]]) {
      await page.selectOption('#scenario', scenario);
      for (let i = 0; i < stop; i++) await page.click('#next');
      if (!(await page.isDisabled('#next'))) throw Error('Expected gate ' + scenario);
      if (scenario !== 'happy') {
        await page.click('#hint');
        if (!(await page.locator('#hint-text').isVisible())) throw Error('Challenge hint');
        await page.click('#resolve');
        for (let i = stop; i < 5; i++) await page.click('#next');
      }
      if (!(await page.locator('#result').textContent()).includes('模拟交付完成')) throw Error('Incomplete ' + scenario);
      if (scenario !== 'happy' && !(await page.locator('#challenge').textContent()).includes('挑战完成')) throw Error('Challenge completion');
      await page.click('#reset');
      if (await page.isDisabled('#next')) throw Error('Reset');
    }
    for (const filter of ['offline', 'public']) {
      await page.selectOption('#filter', filter);
      if (await page.locator('#catalog article:visible').count() !== 3) throw Error('Filter ' + filter);
    }
    const download = page.waitForEvent('download');
    await page.click('#export');
    const exported = path.join(output, 'snapshot.md');
    await (await download).saveAs(exported);
    if (!fs.readFileSync(exported, 'utf8').includes('数据类型：演示')) throw Error('Export provenance');
    await page.setViewportSize({ width: 390, height: 844 });
    if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw Error('Mobile overflow');
    await page.screenshot({ path: path.join(output, 'explorer-mobile.png'), fullPage: true });
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.screenshot({ path: path.join(output, 'explorer-dark.png'), fullPage: true });
    await page.goto(pathToFileURL(path.resolve(real)).href);
    if (!(await page.locator('#snapshot').textContent()).includes('本地真实快照')) throw Error('Real snapshot');
    if (network || errors.length) throw Error(JSON.stringify({ network, errors }));
    console.log('PASS: capability filters, template composition/copy/download, timeline, four scenarios, three challenges, reset, export, mobile, dark mode, real snapshot; no external requests or page errors');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
