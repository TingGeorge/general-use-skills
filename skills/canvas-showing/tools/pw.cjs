// Find playwright-core and a Chrome to drive it, without installing anything.
// ponytail: searches the npx cache by directory listing; set PLAYWRIGHT_CORE / CHROME to skip the search.
const fs = require('fs'), os = require('os'), path = require('path');

function playwright() {
  for (const t of [process.env.PLAYWRIGHT_CORE, 'playwright-core', 'playwright']) {
    if (!t) continue;
    try { return require(t); } catch (e) {}
  }
  const npx = path.join(os.homedir(), '.npm/_npx');
  for (const d of fs.existsSync(npx) ? fs.readdirSync(npx) : []) {
    const p = path.join(npx, d, 'node_modules/playwright-core');
    if (fs.existsSync(p)) try { return require(p); } catch (e) {}
  }
  throw new Error('playwright-core not found. Run `npm i -g playwright-core`, or set PLAYWRIGHT_CORE=/path/to/playwright-core');
}

function chrome() {
  const c = [process.env.CHROME, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'].filter(Boolean);
  return c.find(p => fs.existsSync(p));   // undefined → playwright's own downloaded chromium
}

async function open(file, width) {
  const b = await playwright().chromium.launch({ executablePath: chrome() });
  const p = await b.newPage({ viewport: { width, height: 900 } });
  const errors = [];
  p.on('pageerror', e => errors.push('pageerror ' + e.message));
  p.on('console', m => {
    const t = m.text();
    if (m.type() === 'error' && !/favicon|Failed to load resource/.test(t)) errors.push('console ' + t.slice(0, 200));
    // layer warnings that mean something was silently skipped: a misaligned source map, a steps-of diagram
    // with no chain to replace, a build() whose heading id does not exist
    if (m.type() === 'warning' && /^(source map|steps-of|vz: no section)/.test(t)) errors.push('warning ' + t.slice(0, 200));
  });
  p.on('requestfailed', r => { if (!/favicon/.test(r.url())) errors.push('request failed ' + r.url()); });
  await p.goto('file://' + path.resolve(file), { waitUntil: 'load' });
  await p.waitForTimeout(2500);   // mermaid renders after load
  const total = await p.evaluate(() => +((/\/\s*(\d+)/.exec((document.querySelector('.pager-crumb .crumb-r') || {}).textContent || '') || [0, 1])[1]));
  return { b, p, errors, total };
}

module.exports = { open };
