#!/usr/bin/env python3
"""Draw an ER diagram for an intent-review page: er_diagram.py SPEC.json > figure.html

Prints one <figure class="zoom"> to paste into a fragment. It holds two drawings of the same tables:
a brief one for the page (key columns and a count of the rest) and a detailed one (every column with its type)
that the page shows when the reader opens the figure over the whole window.

Layout: the hub table is one tall box in the middle, the other tables sit left and right of it, and every link
to the hub is one straight line at the height of its foreign-key row. Line ends are crow's-foot marks.

ponytail: one hub only. A link that does not go to the hub must join two tables that sit one directly above
the other in the same column (the upper one holds the foreign key). A schema without a clear hub, or with
links across columns, does not fit: draw that one by hand, or one figure per hub.

SPEC.json:
{
  "hub": "users",
  "left": ["sessions", "orders"],            order top to bottom; "right" the same
  "right": ["profiles", "audit_log"],
  "detail_left": [...], "detail_right": [...],   optional: another arrangement for the detailed drawing
  "tables": {
    "users": {"colour": "gray", "ref": "001.sql:10-19", "badge": "RLS",
              "columns": [["id", "uuid", "PK"], ["email", "text", "UQ"], ["name", "text", ""]]}
  },                                         colour: blue teal gold rust gray; ref and badge optional; tags: PK FK UQ
  "links": [
    {"from": "sessions", "column": "user_id", "to": "users", "from_end": "many", "to_end": "one"},
    {"from": "orders", "column": "item_id", "to": "items", "from_end": "many", "to_end": "maybe", "label": ["item_id", "can be null"]}
  ],                                         ends: one = exactly one, many = zero or many, maybe = zero or one
  "apart": {"audit_log": "Points at no table:"},   optional: tables set apart, with a note above them
  "caption": "<code>…</code> html for the figcaption",
  "text": {"more": "{} more columns", "legend": "Line ends", "one": "exactly one row", "many": "zero to many rows",
           "maybe": "zero or one row", "open": "Show all columns", "close": "Close", "alt": "one sentence for screen readers"}
}
Take the columns from the schema itself (migrations, schema dump) with a script, not by typing them.
Self-check: er_diagram.py --selfcheck
"""
import html, json, sys

HEAD, ROW, PAD, GAP, EDGE = 30, 20, 8, 30, 16
TAG = {'PK': 'r', 'FK': 'bk', 'UQ': 'tl'}
LINE = 'style="stroke-width:1.8"'
RING = 'style="stroke-width:1.8;fill:var(--panel)"'
TEXT = {'more': '{} more columns', 'legend': 'Line ends', 'one': 'exactly one row', 'many': 'zero to many rows',
        'maybe': 'zero or one row', 'open': 'Show all columns', 'close': 'Close', 'alt': 'ER diagram'}
# Widths: Latin mono at 13px is about 7.9px a character; CJK is about 13px
wide = lambda s: sum(13 if ord(c) > 0x2e7f else 7.9 for c in s)


def end(kind, e, y, d=1, vertical=False):
    """Marks where a line meets a box edge at e. d = +1 when the box lies after e. vertical: e is a y and y is the x."""
    pt = (lambda along, across: f'{y + across} {e - along * d}') if vertical else (lambda along, across: f'{e - along * d} {y + across}')
    bar = lambda at: f'<path class="arw" {LINE} d="M{pt(at, -6)}L{pt(at, 6)}"/>'
    ring = lambda at: '<circle class="arw" %s cx="%s" cy="%s" r="5"/>' % ((RING,) + tuple(pt(at, 0).split()))
    if kind == 'one':
        return bar(8) + bar(14)
    if kind == 'maybe':
        return bar(8) + ring(19)
    assert kind == 'many', f'unknown line end "{kind}"; use one, many or maybe'
    return f'<path class="arw" {LINE} d="M{pt(12, 0)}L{pt(0, -6)}M{pt(12, 0)}L{pt(0, 6)}"/>' + ring(18)


def draw(spec, detail):
    tables, hub, text = spec['tables'], spec['hub'], {**TEXT, **spec.get('text', {})}
    left = spec.get('detail_left', spec['left']) if detail else spec['left']
    right = spec.get('detail_right', spec['right']) if detail else spec['right']
    placed = left + right + [hub]
    assert sorted(placed) == sorted(tables), f'left + right + hub must name every table once: {sorted(set(placed) ^ set(tables))}'

    cols = lambda n: [c for c in tables[n]['columns'] if detail or c[2]]
    more = lambda n: len(tables[n]['columns']) - len(cols(n))
    height = lambda n: HEAD + ROW * (len(cols(n)) + (1 if more(n) else 0)) + PAD

    need = max(62 + wide(c[0]) + (wide(c[1]) + 24 if detail else 0) + 12 for n in tables for c in cols(n))
    need = max(need, max(24 + wide(n) * 1.05 + (wide(tables[n].get('badge', '')) + 16) for n in tables))
    if detail:
        W = int(max(need, 260))
        width = 3 * W + 2 * EDGE + 2 * 74
    else:
        W, width = 210, 800
        assert need <= W, f'a name needs {int(need)}px but the brief boxes are {W}px wide: this schema does not fit, draw it by hand'
    mid, right_x = (width - W) // 2, width - EDGE - W

    def table(n, x, y, h=None):
        t, h = tables[n], h or height(n)
        ref = f' data-ref="{html.escape(t["ref"])}"' if t.get('ref') else ''
        o = [f'<rect class="box bx-{t.get("colour", "gray")}" x="{x}" y="{y}" width="{W}" height="{h}" rx="6"/>',
             f'<text{ref} class="t" style="font-size:15px" x="{x + 12}" y="{y + 20}">{html.escape(n)}</text>']
        if t.get('badge'):
            o.append(f'<text class="s end" x="{x + W - 12}" y="{y + 20}">{html.escape(t["badge"])}</text>')
        o.append(f'<path class="arw" style="stroke-width:1;opacity:.35" d="M{x} {y + HEAD}H{x + W}M{x + 54} {y + HEAD}V{y + h}"/>')
        for i, (col, typ, tags) in enumerate(cols(n)):
            ty, tx = y + HEAD + ROW * i + 16, x + 12
            for tag in tags.split():
                o.append(f'<text class="s {TAG[tag]}" style="font-weight:700" x="{tx}" y="{ty}">{tag}</text>')
                tx += 22
            bold = ';font-weight:700;text-decoration:underline' if 'PK' in tags else ''
            o.append(f'<text class="m" style="fill:var(--fg);font-size:13px{bold}" x="{x + 62}" y="{ty}">{html.escape(col)}</text>')
            if detail and typ:
                o.append(f'<text class="m end" x="{x + W - 12}" y="{ty}">{html.escape(typ)}</text>')
        if more(n):
            o.append(f'<text class="s" x="{x + 62}" y="{y + HEAD + ROW * len(cols(n)) + 16}">{html.escape(text["more"].format(more(n)))}</text>')
        return o

    links = spec.get('links', [])
    to_hub = {l['from']: l for l in links if l['to'] == hub}
    others = [l for l in links if l['to'] != hub]
    apart = spec.get('apart', {})

    top, o = {}, []
    for x, names in ((EDGE, left), (right_x, right)):
        y = EDGE
        for i, n in enumerate(names):
            if n in apart:
                y += 66
            top[n] = (x, y)
            y += height(n) + (96 if any(l['from'] == n for l in others) else GAP)
    for l in others:
        col = left if l['from'] in left else right
        assert l['to'] in col and col.index(l['to']) == col.index(l['from']) + 1, \
            f'{l["from"]} -> {l["to"]}: a link that skips the hub needs "{l["to"]}" right below "{l["from"]}" in the same column'

    row_y = lambda n, c: top[n][1] + HEAD + ROW * [k[0] for k in cols(n)].index(c) + 10
    fk_y = {n: row_y(n, l['column']) for n, l in to_hub.items()}

    uh = max([max(fk_y.values(), default=0) + 30 - EDGE, height(hub)])
    o += table(hub, mid, EDGE, uh)
    for n, y in fk_y.items():
        l = to_hub[n]
        if top[n][0] == EDGE:
            o.append(f'<path class="arw" {LINE} d="M{EDGE + W} {y}H{mid}"/>' + end(l['from_end'], EDGE + W, y, -1) + end(l['to_end'], mid, y, 1))
        else:
            o.append(f'<path class="arw" {LINE} d="M{mid + W} {y}H{right_x}"/>' + end(l['to_end'], mid + W, y, -1) + end(l['from_end'], right_x, y, 1))

    for n, (x, y) in top.items():
        o += table(n, x, y)
        if n in apart:
            o.append(f'<text class="s" x="{x}" y="{y - 12}">{html.escape(apart[n])}</text>')

    for l in others:
        x = top[l['from']][0] + W // 2
        a, b = top[l['from']][1] + height(l['from']), top[l['to']][1]
        o.append(f'<path class="arw" {LINE} d="M{x} {a}V{b}"/>' + end(l['from_end'], a, x, -1, True) + end(l['to_end'], b, x, 1, True))
        for i, line in enumerate(l.get('label', [])):
            o.append(f'<text class="lab" x="{x + 16}" y="{(a + b) // 2 - 4 + 16 * i}">{html.escape(line)}</text>')

    lw = int(max(wide(text[k]) for k in ('one', 'many', 'maybe')) * 0.93 + 92)
    lx, ly = mid, EDGE + uh + 40
    o.append(f'<rect class="box bx-none" x="{lx}" y="{ly}" width="{lw}" height="106" rx="8"/>')
    o.append(f'<text class="t" x="{lx + 14}" y="{ly + 24}">{html.escape(text["legend"])}</text>')
    for i, kind in enumerate(('one', 'many', 'maybe')):
        y0 = ly + 46 + 22 * i
        o.append(f'<path class="arw" {LINE} d="M{lx + 14} {y0}H{lx + 62}"/>' + end(kind, lx + 62, y0))
        o.append(f'<text class="s" x="{lx + 78}" y="{y0 + 4}">{html.escape(text[kind])}</text>')

    H = max([y + height(n) for n, (x, y) in top.items()] + [ly + 106]) + EDGE
    body = '\n'.join('  ' + s for s in o)
    return f'<svg viewBox="0 0 {width} {H}" role="img" aria-label="{html.escape(text["alt"])}">\n{body}\n</svg>'


def figure(spec):
    text = {**TEXT, **spec.get('text', {})}
    return (f'<figure class="zoom" data-open="{html.escape(text["open"])}" data-close="{html.escape(text["close"])}">\n'
            f'<div class="scroll brief">\n{draw(spec, False)}\n</div>\n<div class="scroll detail">\n{draw(spec, True)}\n</div>\n'
            f'<figcaption>{spec.get("caption", "")}</figcaption>\n</figure>\n')


def selfcheck():
    spec = {
        'hub': 'users', 'left': ['orders', 'items'], 'right': ['profiles', 'log'],
        'tables': {
            'users': {'columns': [['id', 'uuid', 'PK'], ['name', 'text', '']]},
            'orders': {'ref': 'a.sql:1-5', 'columns': [['id', 'uuid', 'PK'], ['user_id', 'uuid', 'FK'], ['item_id', 'uuid', 'FK'], ['note', 'text', '']]},
            'items': {'columns': [['id', 'uuid', 'PK']]},
            'profiles': {'badge': 'RLS', 'columns': [['user_id', 'uuid', 'PK FK'], ['bio', 'text', '']]},
            'log': {'columns': [['id', 'uuid', 'PK']]},
        },
        'links': [{'from': 'orders', 'column': 'user_id', 'to': 'users', 'from_end': 'many', 'to_end': 'one'},
                  {'from': 'profiles', 'column': 'user_id', 'to': 'users', 'from_end': 'maybe', 'to_end': 'one'},
                  {'from': 'orders', 'column': 'item_id', 'to': 'items', 'from_end': 'many', 'to_end': 'maybe', 'label': ['item_id']}],
        'apart': {'log': 'Points at no table:'},
    }
    out = figure(spec)
    brief, detail = out.split('<div class="scroll detail">')
    assert brief.count('<rect class="box bx-gray"') == 5 and detail.count('<rect class="box bx-gray"') == 5
    assert '>note<' not in brief and '>note<' in detail, 'non-key columns belong only to the detailed drawing'
    assert '1 more columns' in brief and 'more columns' not in detail
    assert brief.count('<circle') == detail.count('<circle') == 6, 'four link ends with a ring, plus two in the legend'
    assert 'data-ref="a.sql:1-5"' in out and 'data-open="Show all columns"' in out

    spec['left'] = ['items', 'orders']
    try:
        figure(spec)
    except AssertionError as e:
        assert 'right below' in str(e)
    else:
        raise AssertionError('a link to a table above must be refused')
    print('selfcheck passed')


if __name__ == '__main__':
    if sys.argv[1:] == ['--selfcheck']:
        selfcheck()
    elif len(sys.argv) == 2:
        sys.stdout.write(figure(json.load(open(sys.argv[1], encoding='utf8'))))
    else:
        sys.exit(__doc__)
