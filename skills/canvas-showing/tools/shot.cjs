// usage: node shot.cjs <page.html> <width> <pages: 1,3,7 | all> [scrollY]
// → shots/w<width>-p<N>.png next to the page. scrollY given: a viewport-size shot from that offset
//   (full-page shots of long pages are scaled down too far to read at phone width).
const path = require('path'), fs = require('fs');
const { open } = require('./pw.cjs');
const [file, w = 1440, list = 'all', y = 0] = process.argv.slice(2);

(async () => {
  const { b, p, errors, total } = await open(file, +w);
  const pages = list === 'all' ? Array.from({ length: total }, (_, i) => i + 1) : list.split(',').map(Number);
  const dir = path.join(path.dirname(path.resolve(file)), 'shots');
  fs.mkdirSync(dir, { recursive: true });
  for (const n of pages) {
    await p.evaluate(n => { location.hash = 'page-' + n; scrollTo(0, 0); }, n);
    await p.waitForTimeout(500);
    if (+y) { await p.evaluate(y => scrollTo(0, y), +y); await p.waitForTimeout(200); }
    const out = path.join(dir, `w${w}-p${n}${+y ? '-y' + y : ''}.png`);
    await p.screenshot({ path: out, fullPage: !+y, timeout: 20000 });
    console.log(out);
  }
  errors.forEach(e => console.log(e));
  await b.close();
})();
