// usage: node audit.cjs <page.html>
// Checks the built page at 1440 px and 400 px. Exit 1 when a hard check fails.
//   hard:   script errors · diagrams without svg · sentences no picture links (still listed under 還沒畫進圖的原文)
//           · chips whose sentence was not found · chips with no or off-screen pop-up · overflow / sideways scroll
//   review: chips whose label shares under half its characters with the sentence they open (wrong clause?)
//           · hidden sentences no chip opens directly (only through a whole-card chip, or not at all)
const { open } = require('./pw.cjs');
const file = process.argv[2];

function inPage(total) {
  const out = { gaps: [], misses: [], popups: [], overflow: [], weak: [], indirect: [] };
  const n = s => s.replace(/\s+/g, '').replace(/原文/g, '');
  const box = e => e.getBoundingClientRect();
  const STRIP = /[\s・：:／/（）()→＋+=<>≤≥「」、，。…\-—~～0-9a-zA-Z#×✓✗↓]/g;
  out.diagrams = document.querySelectorAll('.mermaid').length;
  out.diagramsBroken = [...document.querySelectorAll('.mermaid')].filter(d => !d.querySelector('svg')).length;
  out.sections = document.querySelectorAll('.vz').length;
  out.chips = document.querySelectorAll('button.vz-chip').length;

  for (let p = 1; p <= total; p++) {
    history.replaceState(null, '', '#page-' + p);
    window.dispatchEvent(new HashChangeEvent('hashchange'));
    if (document.documentElement.scrollWidth > innerWidth + 1) out.overflow.push(p + ' sideways scroll ' + document.documentElement.scrollWidth + 'px');
    const main = document.querySelector('main.content'), mr = box(main);
    main.querySelectorAll('*').forEach(el => {
      if (el.closest('.mermaid svg, .pager-nav, #TOC, .toc-wrap') || !el.offsetParent) return;
      const r = box(el); if (!r.width) return;
      const host = el.parentElement.closest('.card, .blocks > li, .kn, .sx, .steps, blockquote, .vz-box, .vz-f, .vz-mx, .vz-cal, .vz-phone');
      const hr = host ? box(host) : mr;
      if (r.right > hr.right + 1.5 || r.left < hr.left - 1.5) out.overflow.push(p + ' ' + el.tagName + '.' + String(el.className).slice(0, 30) + ' 「' + (el.textContent || '').trim().slice(0, 20) + '」 ' + Math.round(r.right - hr.right) + 'px');
    });

    main.querySelectorAll('.vz').forEach(v => {
      if (!v.offsetParent) return;
      const id = v.previousElementSibling.id;
      if (+v.dataset.vzLeft) out.gaps.push(id + ': ' + [...v.querySelectorAll('.vz-left li')].map(l => l.textContent.trim().slice(0, 40)).join(' || '));
      v.querySelectorAll('.vz-chip.miss').forEach(x => out.misses.push(id + ': ' + x.title));
      if (+v.dataset.vzMiss && !v.querySelector('.vz-chip.miss')) out.misses.push(id + ': ' + v.dataset.vzMiss + ' card/slot lookups failed (see console warnings)');

      const direct = [], wholeCards = [];
      v.querySelectorAll('button.vz-chip').forEach(b => {
        b.scrollIntoView({ block: 'center' });
        b.click();
        const q = document.querySelector('.vz-pop');
        if (!q || q.textContent.trim().length < 4) out.popups.push(id + ': 「' + b.textContent + '」 opens nothing');
        else {
          const r = box(q);
          if (r.left < -1 || r.right > innerWidth + 1) out.popups.push(id + ': 「' + b.textContent + '」 pop-up off-screen');
          const t = q.textContent;
          if (q.querySelector('.card')) wholeCards.push(t); else direct.push(n(t));
          const ch = [...b.textContent.replace(STRIP, '')];
          if (ch.length && ch.filter(c => t.includes(c)).length / ch.length < 0.5) out.weak.push(id + ': 「' + b.textContent + '」 → ' + n(t).slice(0, 60));
        }
        document.body.click();
      });
      for (let e = v.nextElementSibling; e && !/^H[1-6]$/.test(e.tagName); e = e.nextElementSibling) {
        if (!e.classList.contains('vz-hide')) continue;
        e.querySelectorAll('li, .fv, p, .steps-tail').forEach(l => {
          if (l.querySelector('li, .fv, p, .steps-tail') || l.closest('.mermaid')) return;
          const t = n(l.textContent), card = l.closest('.card');
          if (t.length <= 3 || direct.some(d => d.includes(t))) return;
          if (card && wholeCards.length && wholeCards.some(w => n(w).includes(t))) return;   // opened as part of its card
          out.indirect.push(id + ': ' + t.slice(0, 50));
        });
      }
    });
  }
  window.scrollTo(0, 0);
  return out;
}

(async () => {
  let fail = false;
  for (const w of [1440, 400]) {
    const { b, p, errors, total } = await open(file, w);
    const r = await p.evaluate(inPage, total);
    await b.close();
    const hard = { errors, diagramsBroken: r.diagramsBroken, gaps: r.gaps, misses: r.misses, popups: r.popups, overflow: r.overflow };
    const bad = errors.length + r.diagramsBroken + r.gaps.length + r.misses.length + r.popups.length + r.overflow.length;
    fail = fail || bad > 0;
    console.log(`\n== ${w}px · ${total} pages · ${r.sections} picture sections · ${r.chips} chips · ${r.diagrams} diagrams → ${bad ? bad + ' HARD FAILURES' : 'hard checks pass'}`);
    for (const [k, v] of Object.entries(hard)) if (Array.isArray(v) ? v.length : v) console.log(k + ':', Array.isArray(v) ? '\n  ' + v.slice(0, 40).join('\n  ') : v);
    if (w === 1440) {
      console.log(`review — weak labels (${r.weak.length}): read each; fix the match when the label describes another clause` + (r.weak.length ? '\n  ' + r.weak.join('\n  ') : ''));
      console.log(`review — not opened directly (${r.indirect.length}): add a chip, unless the sentence is an old diagram's label` + (r.indirect.length ? '\n  ' + r.indirect.slice(0, 60).join('\n  ') : ''));
    }
  }
  process.exit(fail ? 1 : 0);
})();
