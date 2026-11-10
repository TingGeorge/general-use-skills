#!/usr/bin/env python3
"""Build one intent-review page from a fragment.

    build_page.py FRAGMENT.html --out PAGE.html [--repo DIR] [--rev REV] [--base BASE] [--lang zh-TW|en]

--rev   commit the sources are read from. Left out: the working tree.
--base  commit to compare against. Given: added and removed lines are marked in the code pane,
        and every changed file must be in the fragment's `sources` or `skipped` comment.

It checks the fragment (structure, line refs), embeds the real files, and writes the page.
Anything a reader would trip over is an error; the page is written only when there are none.
Self-check: build_page.py --selfcheck
"""
import argparse, html, json, os, re, subprocess, sys, tempfile
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
VOID = {'br', 'hr', 'img', 'meta', 'link', 'input', 'path', 'rect', 'circle', 'line', 'ellipse', 'polygon', 'polyline', 'use'}

LABELS = {
    'zh-TW': {
        'code': '程式碼', 'grip': '調整程式欄寬度', 'gripTitle': '拖曳調整寬度，按兩下還原', 'close': '關閉',
        'wrapOn': '自動換行：開', 'wrapOff': '自動換行：關', 'show': '看程式：', 'zoomOpen': '放大', 'zoomClose': '縮小', 'newFile': '（新檔案）', 'range': '第 {} 行', 'sep': '、',
        'noteRev': '程式：<code>{}</code>。',
        'noteTree': '程式：目前工作目錄裡的檔案（還沒 commit 的修改也在內）。',
        'noteUse': '右邊是完整的程式檔。按每一段標題旁的「看程式」，右邊會換到那段程式，相關的行左邊有金色線，其他行變淡；捲動頁面不會改變右邊的內容。點任何 <code>檔名:行號</code> 或圖上的方框也可以。',
        'noteDiff': '這一頁看的是 <code>{}</code> 之後的修改。右邊行號旁有綠線的是新增或改過的行；紅底、沒有行號的是被刪掉的行；檔名後有綠點的是改過的檔案。整個檔案都是新的時候不畫綠線，路徑後面會寫「新檔案」。',
    },
    'en': {
        'code': 'Code', 'grip': 'Resize the code pane', 'gripTitle': 'Drag to resize, double-click to reset', 'close': 'Close',
        'wrapOn': 'Wrap: on', 'wrapOff': 'Wrap: off', 'show': 'Show code: ', 'zoomOpen': 'Enlarge', 'zoomClose': 'Close', 'newFile': ' (new file)', 'range': 'lines {}', 'sep': ', ',
        'noteRev': 'Code: <code>{}</code>.',
        'noteTree': 'Code: the files in the working tree now, uncommitted changes included.',
        'noteUse': 'The right side holds the full source files. Press "Show code" beside a heading and the right side moves to that code: its lines get a gold bar on the left and the other lines fade. Scrolling the page never changes the right side. Any <code>file:line</code> or box in a diagram is clickable too.',
        'noteDiff': 'This page covers the changes since <code>{}</code>. A green bar beside a line number marks an added or changed line; rows on red without a number are removed lines; a green dot after a file name marks a changed file. A file that is entirely new has no green bars; its path says "new file".',
    },
}
errors, warnings = [], []


def git(repo, *args, ok=(0,)):
    r = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True, errors='replace')
    return r.stdout if r.returncode in ok else None


def names_for(paths):
    """Shortest path ending that is unique on the page: auth.ts, or auth/index.ts when two index.ts are embedded."""
    out = {}
    for p in paths:
        parts = p.split('/')
        for k in range(1, len(parts) + 1):
            tail = '/'.join(parts[-k:])
            if sum(1 for q in paths if q == tail or q.endswith('/' + tail)) == 1:
                break
        out[p] = tail
    return out


def diff_marks(patch):
    """From `git diff -U0`: ([[first, last], ...] of added lines, {new line the removed lines sat before: [text, ...]})."""
    add, gone, at = [], {}, None
    for line in patch.split('\n'):
        m = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', line)
        if m:
            start, count = int(m[1]), int(m[2] if m[2] is not None else 1)
            if count:
                add.append([start, start + count - 1])
            # With nothing added, git gives the line the removal comes after
            at = start if count else start + 1
        elif at and line.startswith('-') and not line.startswith('---'):
            gone.setdefault(at, []).append(line[1:])
    return add, gone


class Check(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.parts, self.focus, self.refs, self.ids = [], [], [], [], []
        self.in_code = self.in_h1 = False
        self.title = ''

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get('class') or '').split()
        if a.get('id'):
            self.ids.append(a['id'])
        if tag == 'h2' and 'data-focus' in a:
            self.focus.append(a['data-focus'])
        if tag == 'div' and 'parts' in cls:
            self.parts.append([])
        elif tag == 'div' and 'b' in cls and 'parts' in self.stack:
            self.parts[-1].append(' '.join(c for c in cls if c != 'b'))
        if 'data-ref' in a:
            self.refs.append(a['data-ref'])
        if tag == 'code' or (tag == 'text' and 'm' in cls):
            self.in_code, self.buf = True, ''
        if tag == 'h1':
            self.in_h1 = True
        if tag in ('script', 'style'):
            errors.append(f'line {self.getpos()[0]}: no <{tag}> in a fragment; the shell brings its own')
        if tag not in VOID:
            self.stack.append('parts' if tag == 'div' and 'parts' in cls else tag)

    def handle_startendtag(self, tag, attrs):
        if dict(attrs).get('data-ref'):
            self.refs.append(dict(attrs)['data-ref'])

    def handle_endtag(self, tag):
        if tag in ('code', 'text') and self.in_code:
            self.in_code = False
            self.refs.append(self.buf)
        if tag == 'h1':
            self.in_h1 = False
        if tag in VOID:
            return
        if not self.stack or (self.stack[-1] != tag and not (tag == 'div' and self.stack[-1] == 'parts')):
            errors.append(f'line {self.getpos()[0]}: closing </{tag}> but open tags are {self.stack[-3:]}')
            return
        self.stack.pop()

    def handle_data(self, d):
        if self.in_code:
            self.buf += d
        if self.in_h1:
            self.title += d


def comment_list(frag, key):
    m = re.search(r'<!--\s*' + key + r':\s*(.*?)-->', frag, re.S)
    return [p.strip() for p in m[1].replace('\n', ',').split(',') if p.strip()] if m else None


def build(fragment, out, repo='.', rev=None, base=None, lang='en'):
    del errors[:], warnings[:]
    L = LABELS[lang]
    frag = open(fragment, encoding='utf8').read()

    paths = comment_list(frag, 'sources')
    if not paths:
        sys.exit('the fragment must start with <!-- sources: path, path --> (paths from the repo root)')
    skipped = comment_list(frag, 'skipped') or []
    names = names_for(paths)

    src = {}
    for p in paths:
        if rev:
            text = git(repo, 'show', f'{rev}:{p}')
        else:
            full = os.path.join(repo, p)
            text = open(full, encoding='utf8', errors='replace').read() if os.path.isfile(full) else None
        if text is None:
            errors.append(f'sources: no such file {"at " + rev if rev else "in the working tree"}: {p}')
            continue
        entry = {'path': p, 'text': text}
        if base:
            patch = git(repo, 'diff', '-U0', '--no-color', base, *([rev] if rev else []), '--', p)
            if patch is None:
                sys.exit(f'git diff against {base} failed; is the base commit fetched?')
            # A brand-new file would be green from top to bottom, which marks nothing; the tab dot and a label say it is new
            if git(repo, 'cat-file', '-e', f'{base}:{p}') is None:
                entry['new'] = True
            else:
                entry['add'], entry['del'] = diff_marks(patch)
        src[names[p]] = entry

    if base:
        changed = git(repo, 'diff', '--name-only', base, *([rev] if rev else []))
        if changed is None:
            sys.exit(f'git diff against {base} failed; is the base commit fetched?')
        for p in filter(None, changed.split('\n')):
            if p not in paths and p not in skipped:
                errors.append(f'changed file is neither in sources nor in <!-- skipped: ... -->: {p}')

    c = Check()
    c.feed(frag)
    c.close()
    if c.stack:
        errors.append(f'unclosed tags at the end: {c.stack[-5:]}')
    if not c.title.strip():
        errors.append('the fragment needs an <h1> title')
    if 'class="sub"' not in frag:
        errors.append('the fragment needs <p class="sub"> right after the <h1>')
    dup = {i for i in c.ids if c.ids.count(i) > 1}
    if dup:
        errors.append(f'duplicate ids: {sorted(dup)}')
    for href in re.findall(r'href="#([\w-]+)"', frag):
        if href not in c.ids:
            errors.append(f'link to a missing id: #{href}')

    if not c.parts:
        errors.append('need at least one <div class="parts"> topic')
    for i, p in enumerate(c.parts, 1):
        if p != ['p', 'm', 'w']:
            errors.append(f'topic {i}: a parts block holds exactly "b p", "b m", "b w" in this order; got {p}')
    if len(c.focus) != len(c.parts):
        errors.append(f'{len(c.focus)} h2[data-focus] but {len(c.parts)} parts blocks; each topic has one of each')

    count = {k: len(v['text'].rstrip('\n').split('\n')) for k, v in src.items()}
    seen = {k: [] for k in src}

    def use(name, a, b, where):
        if name not in src:
            errors.append(f'{where}: "{name}" is not an embedded file. Names on this page: {sorted(src)}')
        elif not 1 <= a <= b <= count[name]:
            errors.append(f'{where}: {name}:{a}-{b} is out of range (the file has {count[name]} lines)')
        else:
            seen[name].append((a, b))

    for f in c.focus:
        name, _, ranges = f.partition(':')
        if not re.fullmatch(r'\d+(-\d+)?(,\d+(-\d+)?)*', ranges):
            errors.append(f'data-focus must be file:10-40,60-80; got "{f}"')
            continue
        for r in ranges.split(','):
            a, _, b = r.partition('-')
            use(name, int(a), int(b or a), f'data-focus {f}')

    nrefs = 0
    for t in c.refs:
        m = re.fullmatch(r'([^\s:]+):(\d+)(?:-(\d+))?', t.strip())
        # Only a file name counts as a ref (an embedded one, or one ending in a letter extension, which catches typos);
        # "12:30", "localhost:4000" and "127.0.0.1:4000" are ordinary text
        if m and (m[1] in src or re.search(r'\.[A-Za-z]\w*$', m[1])):
            nrefs += 1
            use(m[1], int(m[2]), int(m[3] or m[2]), f'ref {t.strip()}')

    for name, e in src.items():
        for a, b in e.get('add', []):
            text = e['text'].split('\n')
            # A blank line that was added needs no explanation
            miss = [n for n in range(a, b + 1) if text[n - 1].strip() and not any(x <= n <= y for x, y in seen[name])]
            if miss:
                warnings.append(f'{name}:{miss[0]}-{miss[-1]} changed but no topic or ref points at it')

    if errors:
        print('FAILED')
        print('\n'.join('- ' + e for e in errors))
        return False

    shell = open(os.path.join(HERE, '..', 'assets', 'shell.html'), encoding='utf8').read()
    where = L['noteRev'].format(html.escape((git(repo, 'rev-parse', '--short', rev) or rev).strip())) if rev else L['noteTree']
    note = f'<p class="note">{where}</p>\n'
    if base:
        note += '<p class="note">' + L['noteDiff'].format(html.escape((git(repo, 'rev-parse', '--short', base) or base).strip())) + '</p>\n'
    note += f'<p class="note">{L["noteUse"]}</p>\n'

    body = re.sub(r'<!--\s*(sources|skipped):.*?-->\s*', '', frag, flags=re.S)
    k = body.index('</p>', body.index('class="sub"')) + 4
    body = body[:k] + '\n' + note + body[k:]

    labels = {k: v for k, v in L.items() if not k.startswith('note')}
    data = json.dumps(src, ensure_ascii=False).replace('<', '\\u003c')
    page = shell
    for key, val in (('@@TITLE@@', html.escape(c.title.strip())), ('@@LABELS@@', json.dumps(labels, ensure_ascii=False)),
                     ('@@BODY@@', body), ('@@SRC@@', data)):
        assert page.count(key) == 1, key
        page = page.replace(key, val)
    open(out, 'w', encoding='utf8').write(page)

    print(f'OK {out}: {len(c.parts)} topics, {nrefs} line refs, {len(page) // 1024} KB')
    print('file names to use in refs: ' + ', '.join(sorted(src)))
    for w in warnings:
        print('warning: ' + w)
    return True


def selfcheck():
    assert names_for(['a/index.ts', 'b/index.ts', 'b/x.ts']) == {'a/index.ts': 'a/index.ts', 'b/index.ts': 'b/index.ts', 'b/x.ts': 'x.ts'}
    with tempfile.TemporaryDirectory() as d:
        def run(*a):
            subprocess.run(['git', '-C', d, '-c', 'user.name=t', '-c', 'user.email=t@t', *a], check=True, capture_output=True)
        run('init', '-q')
        open(f'{d}/a.ts', 'w').write('one\ntwo\nthree\nfour\n')
        open(f'{d}/gone.ts', 'w').write('x\n')
        run('add', '.'); run('commit', '-qm', 'base')
        open(f'{d}/a.ts', 'w').write('one\nTWO\nfour\nfive\n')   # line 2 changed, old line 3 removed, line 4 added
        open(f'{d}/new.ts', 'w').write('n\n')
        os.remove(f'{d}/gone.ts')
        run('add', '-A'); run('commit', '-qm', 'change')

        part = ('<h1>T</h1><p class="sub">s</p><h2 id="x" data-focus="a.ts:2-4">1</h2>'
                '<div class="parts"><div class="b p"></div><div class="b m"><code>a.ts:2</code></div><div class="b w"></div></div>')
        open(f'{d}/f.html', 'w').write('<!-- sources: a.ts, new.ts -->' + part)
        assert not build(f'{d}/f.html', f'{d}/o.html', d, 'HEAD', 'HEAD~1'), 'a removed file left out of skipped must fail'

        open(f'{d}/f.html', 'w').write('<!-- sources: a.ts, new.ts --><!-- skipped: gone.ts -->' + part)
        assert build(f'{d}/f.html', f'{d}/o.html', d, 'HEAD', 'HEAD~1')
        page = open(f'{d}/o.html').read()
        src = json.loads(re.search(r'<script id="src" type="application/json">(.*?)</script>', page, re.S)[1])
        assert src['a.ts']['add'] == [[2, 2], [4, 4]], src['a.ts']['add']
        assert src['a.ts']['del'] == {'2': ['two', 'three']}, src['a.ts']['del']
        assert src['new.ts'].get('new') and '@@' not in page.split('<script id="src"')[0]

        open(f'{d}/f.html', 'w').write('<!-- sources: a.ts -->' + part.replace('<code>a.ts:2</code>', '<code>127.0.0.1:4000</code><code>localhost:80</code>'))
        assert build(f'{d}/f.html', f'{d}/o.html', d), 'host:port is text, not a line ref'

        open(f'{d}/f.html', 'w').write('<!-- sources: a.ts -->' + part.replace('2-4', '2-9'))
        assert not build(f'{d}/f.html', f'{d}/o.html', d), 'a line range past the end of the file must fail'
    print('selfcheck passed')


if __name__ == '__main__':
    if sys.argv[1:] == ['--selfcheck']:
        selfcheck()
        sys.exit()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('fragment')
    ap.add_argument('--out', required=True)
    ap.add_argument('--repo', default='.')
    ap.add_argument('--rev')
    ap.add_argument('--base')
    ap.add_argument('--lang', default='en', choices=sorted(LABELS))
    a = ap.parse_args()
    sys.exit(0 if build(a.fragment, a.out, a.repo, a.rev, a.base, a.lang) else 1)
