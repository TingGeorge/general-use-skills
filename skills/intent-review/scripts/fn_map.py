#!/usr/bin/env python3
"""Draw a function map for an intent-review page: files as grey containers, functions as boxes, arrows as calls.

This is a small drawing library, not a layout engine: you place the boxes and route the lines yourself, and it
refuses a drawing a reader would trip over (a line through a box or a file name, two lines crossing, a name wider
than its box) and an arrow the code does not back up (every arrow names the line where the call is).

    import sys; sys.path.insert(0, '<skill>/scripts')
    from fn_map import Map

    m = Map(height=420)
    m.file('middleware.ts', 28, 16, 194, 72)                        # container: name, x, y, w, h
    m.fn('serverNow', 40, 44, 170, ref='middleware.ts:21-24', path=True)   # box: name, x, y, w
    m.file('time.ts', 538, 16, 174, 72)
    m.fn('taiwanIso', 550, 44, 150, ref='time.ts:22')
    m.call('serverNow', 'taiwanIso', [(210, 61), (550, 61)], at='middleware.ts:23')
    m.legend(288, 120)
    m.verify(repo, rev, ['app/server/src/m0-foundation/middleware.ts', 'app/server/src/m0-foundation/time.ts'])
    print(m.figure('caption html'))

Boxes
  file(name, x, y, w, h, ref=None, dashed=False, label_right=False)   ref defaults to the name (opens the file);
        dashed: a file that belongs to another page (no ref). label_right: put the name at the right.
  fn(name, x, y, w, ref=None, path=False, changed=False, match=None)  path: on the main path (blue).
        changed: mark it as changed (diff pages). match: the text a call to it looks like in the code when that is
        not the name, e.g. match='auth.api.getSession'. No ref: a function outside this page's files.
  group(name, members, pad=8)   dashed outline around functions; a line to or from it stands for every member.
  note(text, x, y, end=False)   a small label.
Lines (points are [(x, y), ...], each step straight across or straight down; the last point gets the arrowhead)
  call(src, dst, points, at=...)       src calls dst. at: 'file.ts:23', or a list of them; one per (src, dst) pair
                                       when a group is involved. The line must sit inside src's ref and contain dst.
  call(..., kind='next')               the request moves on to dst (middleware order); at: where dst is registered.
  call(..., kind='error')              dst runs when something throws; at: where it is registered.
  A second arrow from the same src may start on the first one instead of on the box (a fork).
  src or dst may also be a file name (the line stops at the container's edge).
legend(x, y, text=None)   text: {'title', 'file', 'path', 'next', 'call', 'error', 'changed'} to translate.
verify(repo, rev, paths)  checks every `at` against the files at that commit (rev None: the working tree).
figure(caption, alt='', zoom=True) -> the <figure> html. Raises with the list of problems if the drawing has any.
Self-check: fn_map.py --selfcheck
"""
import html, os, re, subprocess, sys

BH = 34
wide = lambda s, px=7.9: sum(13 if ord(c) > 0x2e7f else px for c in s)
LEGEND = {'title': 'How to read this', 'file': 'A grey container is a file; the boxes in it are functions',
          'path': 'Blue box: on the path one request takes', 'next': 'Green: this step is done, on to the next',
          'call': 'Black: this function calls that one', 'error': 'Red dashed: runs when something throws',
          'changed': 'Green bar: changed in this diff'}


class Map:
    def __init__(self, height, width=800):
        self.W, self.H = width, height
        self.files, self.fns, self.groups, self.lines, self.labels, self.extra = {}, {}, {}, [], [], []
        self.problems, self.verified = [], False

    # ---- boxes ----
    def file(self, name, x, y, w, h, ref=None, dashed=False, label_right=False):
        self.files[name] = dict(x=x, y=y, w=w, h=h, ref=None if dashed else (ref or name), dashed=dashed, right=label_right)
        tw = wide(name, 7.2)
        self.labels.append((name, (x + w - 10 - tw if label_right else x + 10), y + 6, tw, 15))

    def fn(self, name, x, y, w, ref=None, path=False, changed=False, match=None):
        if wide(name) + 12 > w:
            self.problems.append(f'fn {name}: the name needs {int(wide(name) + 12)}px, the box is {w}px')
        self.fns[name] = dict(x=x, y=y, w=w, h=BH, ref=ref, path=path, changed=changed, match=match or name)

    def group(self, name, members, pad=8):
        b = [self.fns[k] for k in members]
        x, y = min(k['x'] for k in b) - pad, min(k['y'] for k in b) - pad
        x2 = max(k['x'] + k['w'] for k in b) + pad
        # A file name right above the first box: keep the outline's top edge below it
        for text, lx, ly, lw, lh in self.labels:
            if lx < x2 and lx + lw > x and ly <= y <= ly + lh and ly + lh + 2 <= y + pad - 2:
                y = ly + lh + 2
        self.groups[name] = dict(x=x, y=y, w=x2 - x, h=max(k['y'] + BH for k in b) + pad - y, members=members)

    def note(self, text, x, y, end=False):
        tw = wide(text, 7)
        self.labels.append((text, x - tw if end else x, y - 12, tw, 16))
        self.extra.append(f'<text class="s{" end" if end else ""}" x="{x}" y="{y}">{html.escape(text)}</text>')

    def call(self, src, dst, points, at=None, kind='call'):
        assert kind in ('call', 'next', 'error'), kind
        self.lines.append(dict(src=src, dst=dst, pts=[tuple(p) for p in points], at=[at] if isinstance(at, str) else list(at or []), kind=kind))

    def legend(self, x, y, text=None):
        t = {**LEGEND, **(text or {})}
        rows = ['file', 'path', 'next', 'call', 'error'] + (['changed'] if any(f['changed'] for f in self.fns.values()) else [])
        rows = [r for r in rows if r in ('file', 'call') or (r == 'path' and any(f['path'] for f in self.fns.values()))
                or r == 'changed' or any(l['kind'] == r for l in self.lines)]
        w, h = int(max(wide(t[r], 6.2) for r in rows) * 0.95 + 96), 40 + 22 * len(rows)
        self.labels.append(('legend', x, y, w, h))
        o = [f'<rect class="box bx-none" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>',
             f'<text class="t" x="{x + 14}" y="{y + 24}">{html.escape(t["title"])}</text>']
        for i, r in enumerate(rows):
            y0 = y + 46 + 22 * i
            if r in ('file', 'path'):
                o.append(f'<rect class="box {"bx-gray" if r == "file" else "bx-blue"}" x="{x + 14}" y="{y0 - 9}" width="44" height="16" rx="4"/>')
            elif r == 'changed':
                o.append(f'<rect class="box" style="fill:var(--panel);stroke:var(--muted)" x="{x + 14}" y="{y0 - 9}" width="44" height="16" rx="4"/>'
                         f'<path style="stroke:#2E9E4F;stroke-width:4;fill:none" d="M{x + 16} {y0 - 8}V{y0 + 6}"/>')
            else:
                cls, mk = {'next': ('arw-t', 'at'), 'call': ('arw', 'a'), 'error': ('arw-r', 'ar')}[r]
                o.append(f'<path class="{cls}" marker-end="url(#{mk})" d="M{x + 14} {y0}H{x + 58}"/>')
            o.append(f'<text class="s" x="{x + 72}" y="{y0 + 4}">{html.escape(t[r])}</text>')
        self.extra += o

    # ---- checks ----
    def _rect(self, name):
        b = self.fns.get(name) or self.groups.get(name) or self.files.get(name)
        if not b:
            raise KeyError(f'no box named "{name}"')
        return b['x'], b['y'], b['x'] + b['w'], b['y'] + b['h']

    def _members(self, name):
        return self.groups[name]['members'] if name in self.groups else [name] if name in self.fns else []

    def _check(self):
        P = list(self.problems)
        segs = []  # (line index, (x1, y1, x2, y2) with x1<=x2, y1<=y2)
        on_edge = lambda p, r: (r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]) and (p[0] in (r[0], r[2]) or p[1] in (r[1], r[3]))
        for i, l in enumerate(self.lines):
            name = f'{l["src"]} -> {l["dst"]}'
            for a, b in zip(l['pts'], l['pts'][1:]):
                if a[0] != b[0] and a[1] != b[1]:
                    P.append(f'{name}: the step {a} to {b} is neither straight across nor straight down')
                segs.append((i, (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))))
            for p in l['pts']:
                if not (0 <= p[0] <= self.W and 0 <= p[1] <= self.H):
                    P.append(f'{name}: point {p} is outside the picture')
            try:
                s, d = self._rect(l['src']), self._rect(l['dst'])
            except KeyError as e:
                P.append(f'{name}: {e.args[0]}')
                continue
            fork = any(k != i and self.lines[k]['src'] == l['src'] and any(
                x1 <= l['pts'][0][0] <= x2 and y1 <= l['pts'][0][1] <= y2 for j, (x1, y1, x2, y2) in segs if j == k) for k in range(i))
            if not on_edge(l['pts'][0], s) and not fork:
                P.append(f'{name}: starts at {l["pts"][0]}, which is not on the edge of {l["src"]} {s} (nor on an earlier line from it)')
            if not on_edge(l['pts'][-1], d):
                P.append(f'{name}: ends at {l["pts"][-1]}, which is not on the edge of {l["dst"]} {d}')

        hit = lambda s, r: s[0] < r[2] and s[2] > r[0] and s[1] < r[3] and s[3] > r[1]   # open overlap; a segment has zero width
        thick = lambda s: (s[0] - 0.5, s[1] - 0.5, s[2] + 0.5, s[3] + 0.5)
        for i, s in segs:
            l = self.lines[i]
            name = f'{l["src"]} -> {l["dst"]}'
            ends = set(self._members(l['src']) + self._members(l['dst']))
            for n, f in self.fns.items():
                r = (f['x'], f['y'], f['x'] + f['w'], f['y'] + BH)
                inner = (r[0] + 1, r[1] + 1, r[2] - 1, r[3] - 1)
                if hit(thick(s), inner) and (n not in ends or (s[2] - s[0] > 1 and s[0] < inner[0] and s[2] > inner[2]) or (s[3] - s[1] > 1 and s[1] < inner[1] and s[3] > inner[3])):
                    P.append(f'{name}: runs through the box {n}')
            for text, x, y, w, h in self.labels:
                if hit(thick(s), (x, y, x + w, y + h)):
                    P.append(f'{name}: runs through the text "{text}"')
        for text, x, y, w, h in self.labels:
            if x < 0 or y < 0 or x + w > self.W or y + h > self.H:
                P.append(f'"{text}" reaches outside the picture ({int(x)}..{int(x + w)} of {self.W} wide, {int(y)}..{int(y + h)} of {self.H} high)')
            for g, r in self.groups.items():
                x1, y1, x2, y2 = r['x'], r['y'], r['x'] + r['w'], r['y'] + r['h']
                edges = [(x1, y1, x2, y1), (x1, y2, x2, y2), (x1, y1, x1, y2), (x2, y1, x2, y2)]
                if text != 'legend' and any(hit(thick(e), (x, y, x + w, y + h)) for e in edges):
                    P.append(f'the outline of group {g} runs through the text "{text}"; give the container more room above its first box')
        for a in range(len(segs)):
            for b in range(a + 1, len(segs)):
                (i, s), (j, t) = segs[a], segs[b]
                if i == j or not hit(thick(s), thick(t)):
                    continue
                li, lj = self.lines[i], self.lines[j]
                starts = lambda l, seg: seg[0] <= l['pts'][0][0] <= seg[2] and seg[1] <= l['pts'][0][1] <= seg[3]
                if li['src'] == lj['src'] and (starts(lj, s) or starts(li, t)):
                    continue  # a fork
                msg = f'{li["src"]} -> {li["dst"]} and {lj["src"]} -> {lj["dst"]} cross or overlap near ({max(s[0], t[0])}, {max(s[1], t[1])})'
                if msg not in P:
                    P.append(msg)
        return P

    def verify(self, repo, rev, paths):
        """Every arrow must point at the line of code that makes it true."""
        src = {}
        for p in paths:
            if rev:
                text = subprocess.run(['git', '-C', repo, 'show', f'{rev}:{p}'], capture_output=True, text=True).stdout
            else:
                text = open(os.path.join(repo, p), encoding='utf8').read() if os.path.isfile(os.path.join(repo, p)) else ''
            if not text:
                self.problems.append(f'verify: cannot read {p}')
            src[os.path.basename(p)] = src[p] = text.split('\n')

        def parse(ref):
            m = re.fullmatch(r'(.+?):(\d+)(?:-(\d+))?', ref or '')
            return (m[1], int(m[2]), int(m[3] or m[2])) if m else None

        for n, f in self.fns.items():
            r = parse(f['ref'])
            if f['ref'] and not r:
                self.problems.append(f'fn {n}: ref "{f["ref"]}" must be file:line or file:from-to')
            elif r and (r[0] not in src or r[2] > len(src[r[0]])):
                self.problems.append(f'fn {n}: ref {f["ref"]} is not in the files given to verify')
        for l in self.lines:
            name = f'{l["src"]} -> {l["dst"]}'
            ev = [parse(a) for a in l['at']]
            if not l['at'] or None in ev or any(e[0] not in src or e[2] > len(src[e[0]]) for e in ev):
                self.problems.append(f'{name}: needs at="file:line" pointing into the files given to verify; got {l["at"]}')
                continue
            text = lambda e: '\n'.join(src[e[0]][e[1] - 1:e[2]])
            dsts = self._members(l['dst']) or [None]
            srcs = self._members(l['src']) or [None]
            for d in dsts:
                want = self.fns[d]['match'] if d else None
                for s in srcs:
                    rng = parse(self.fns[s]['ref']) if s and l['kind'] == 'call' else None
                    ok = any((want is None or want in text(e)) and (rng is None or (e[0] == rng[0] and rng[1] <= e[1] and e[2] <= rng[2])) for e in ev)
                    if not ok:
                        inside = f' inside {s} ({self.fns[s]["ref"]})' if rng else ''
                        self.problems.append(f'{name}: no `at` line{inside} contains "{want}"' if want else f'{name}: no `at` line{inside}')
        self.verified = True

    # ---- output ----
    def svg(self, alt=''):
        if not self.verified:
            self.problems.append('call verify(repo, rev, paths) before drawing: an arrow nobody checked is worse than no map')
        P = self._check()
        if P:
            raise SystemExit('the function map has problems:\n' + '\n'.join('- ' + p for p in P))
        o = []
        for n, f in self.files.items():
            o.append(f'<rect class="box {"bx-none" if f["dashed"] else "bx-gray"}" x="{f["x"]}" y="{f["y"]}" width="{f["w"]}" height="{f["h"]}" rx="8"/>')
            attr = f' data-ref="{html.escape(f["ref"])}"' if f['ref'] else ''
            at = f'class="s end" x="{f["x"] + f["w"] - 10}"' if f['right'] else f'class="s" x="{f["x"] + 10}"'
            o.append(f'<text{attr} {at} style="font-size:13px;font-weight:500" y="{f["y"] + 18}">{html.escape(n)}</text>')
        for g in self.groups.values():
            o.append(f'<rect class="box bx-none" x="{g["x"]}" y="{g["y"]}" width="{g["w"]}" height="{g["h"]}" rx="8"/>')
        for n, f in self.fns.items():
            look = 'class="box bx-blue"' if f['path'] else 'class="box" style="fill:var(--panel);stroke:var(--muted)"'
            o.append(f'<rect {look} x="{f["x"]}" y="{f["y"]}" width="{f["w"]}" height="{BH}" rx="5"/>')
            attr = f' data-ref="{html.escape(f["ref"])}"' if f['ref'] else ''
            o.append(f'<text{attr} class="m mid" style="fill:var(--fg);font-size:13px" x="{f["x"] + f["w"] / 2}" y="{f["y"] + 22}">{html.escape(n)}</text>')
            if f['changed']:
                o.append(f'<path style="stroke:#2E9E4F;stroke-width:4;fill:none" d="M{f["x"] + 2} {f["y"] + 3}V{f["y"] + BH - 3}"/>')
        for l in self.lines:
            cls, mk = {'call': ('arw', 'a'), 'next': ('arw-t', 'at'), 'error': ('arw-r', 'ar')}[l['kind']]
            d = 'M' + 'L'.join(f'{x} {y}' for x, y in l['pts'])
            o.append(f'<path class="{cls}" marker-end="url(#{mk})" d="{d}"/>')
        o += self.extra
        body = '\n'.join('  ' + s for s in o)
        return f'<svg viewBox="0 0 {self.W} {self.H}" role="img" aria-label="{html.escape(alt)}">\n{body}\n</svg>'

    def figure(self, caption, alt='', zoom=True):
        return f'<figure{" class=\"zoom\"" if zoom else ""}>\n<div class="scroll">\n{self.svg(alt)}\n</div>\n<figcaption>{caption}</figcaption>\n</figure>\n'


def selfcheck():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        open(f'{d}/a.ts', 'w').write('function one() {\n  two();\n}\nfunction two() {\n  return 1;\n}\nuse(one);\n')

        def base():
            m = Map(200)
            m.file('a.ts', 20, 10, 400, 150)
            m.fn('one', 40, 40, 100, ref='a.ts:1-3', path=True)
            m.fn('two', 280, 40, 100, ref='a.ts:4-6')
            m.fn('mid', 160, 90, 100)
            return m

        m = base()
        m.call('one', 'two', [(140, 57), (280, 57)], at='a.ts:2')
        m.legend(300, 80)
        m.verify(d, None, ['a.ts'])
        assert m.figure('c').count('marker-end') == 2  # the arrow, and the one in the legend

        def problems(build):
            m = base()
            build(m)
            m.verify(d, None, ['a.ts'])
            return '\n'.join(m._check())

        assert 'contains "two"' in problems(lambda m: m.call('one', 'two', [(140, 57), (280, 57)], at='a.ts:5')), 'evidence outside the caller'
        assert 'runs through the box mid' in problems(lambda m: m.call('one', 'two', [(90, 74), (90, 107), (330, 107), (330, 74)], at='a.ts:2'))
        assert 'runs through the text "a.ts"' in problems(lambda m: m.call('one', 'two', [(45, 40), (45, 20), (330, 20), (330, 40)], at='a.ts:2'))
        assert 'not on the edge' in problems(lambda m: m.call('one', 'two', [(150, 57), (280, 57)], at='a.ts:2'))
        both = lambda m: (m.call('one', 'two', [(140, 50), (280, 50)], at='a.ts:2'), m.call('mid', 'two', [(210, 90), (210, 30), (330, 30), (330, 40)], at='a.ts:2'))
        assert 'cross or overlap' in problems(both)
    print('selfcheck passed')


if __name__ == '__main__':
    selfcheck() if sys.argv[1:] == ['--selfcheck'] else sys.exit(__doc__)
