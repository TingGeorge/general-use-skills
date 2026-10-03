# Build srcmap.html: the original document lines + which original lines each top-level block came from.
# Blocks are listed in document order so the page can match them to pandoc's output one by one.
import difflib, json, re, sys

orig = open(sys.argv[1], encoding='utf-8').read().split('\n')
src = open('source.md', encoding='utf-8').read().split('\n')

# source.md line -> original line (1-based), None for lines added in the diagram pass (diagrams, number tiles)
to_orig = [None] * len(src)
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, orig, src, autojunk=False).get_opcodes():
    if tag == 'equal':
        for k in range(j2 - j1):
            to_orig[j1 + k] = i1 + k + 1

LIST = re.compile(r'^(\s*)([-*+]|\d+\.)\s')

def rng(a, b):  # inclusive source.md 0-based range -> payload
    return {'s': a, 'e': b}

blocks, i, n = [], 0, len(src)
while i < n:
    line = src[i]
    if not line.strip():
        i += 1; continue
    if line.startswith('```'):
        j = i + 1
        while not src[j].startswith('```'): j += 1
        blocks.append({'kind': 'fence', **rng(i, j)}); i = j + 1; continue
    if line.startswith('#'):
        blocks.append({'kind': 'h', **rng(i, i)}); i += 1; continue
    if re.match(r'^ {0,3}([-*_])( *\1){2,} *$', line):   # thematic break (---, ***, ___) after a blank line
        blocks.append({'kind': 'hr', **rng(i, i)}); i += 1; continue
    if line.startswith('<div'):
        j = i
        while not src[j].startswith('</div>'): j += 1
        blocks.append({'kind': 'html', **rng(i, j)}); i = j + 1; continue
    if line.startswith('|'):
        j = i
        while j + 1 < n and src[j + 1].startswith('|'): j += 1
        blocks.append({'kind': 'table', **rng(i, j), 'items': [[k, k] for k in range(i + 2, j + 1)]}); i = j + 1; continue
    if line.startswith('>'):
        j = i
        while j + 1 < n and src[j + 1].startswith('>'): j += 1
        blocks.append({'kind': 'quote', **rng(i, j)}); i = j + 1; continue
    if LIST.match(line):
        items, j = [], i
        while True:
            start = j
            while j + 1 < n and src[j + 1].strip() and not LIST.match(src[j + 1]) and src[j + 1].startswith(' '):
                j += 1
            items.append([start, j])
            k = j + 1
            while k < n and not src[k].strip(): k += 1          # loose lists: blank lines between items
            if k < n and LIST.match(src[k]) and not LIST.match(src[k]).group(1):
                j = k; continue
            break
        blocks.append({'kind': 'list', **rng(i, j), 'items': items}); i = j + 1; continue
    j = i
    while j + 1 < n and src[j + 1].strip() and not re.match(r'^(#|```|\||>|<div)', src[j + 1]) and not LIST.match(src[j + 1]):
        j += 1
    blocks.append({'kind': 'p', **rng(i, j)}); i = j + 1

# every heading's own text range in the original file (up to the next heading)
heads = [k for k, l in enumerate(orig) if re.match(r'^#{1,6} ', l)]
sections = [{'text': re.sub(r'^#+\s*', '', orig[k]).strip(), 's': k + 1,
             'e': (heads[x + 1] if x + 1 < len(heads) else len(orig))}
            for x, k in enumerate(heads)]

payload = {'orig': orig, 'map': to_orig, 'src': src, 'blocks': blocks, 'sections': sections,
           'file': sys.argv[2]}
data = json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')
open('srcmap.html', 'w', encoding='utf-8').write(
    '<script type="application/json" id="src-map">' + data + '</script>\n')
print(len(blocks), 'blocks;', sum(1 for m in to_orig if m is None), 'added lines')
