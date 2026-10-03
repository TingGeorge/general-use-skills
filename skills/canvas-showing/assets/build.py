# Assemble the page: pandoc output (raw.html) + source map + config + layers + this document's pictures.
# usage: python3 build.py <out.html> "<page title>"     (run in the page dir)
import os, sys
out, title = sys.argv[1], sys.argv[2]
raw = open('raw.html', encoding='utf-8').read()
raw = raw.replace('<title>raw</title>', '<title>' + title + '</title>', 1)
raw = raw.replace('<h1 class="title">raw</h1>', '<h1 class="title">' + title + '</h1>', 1)
# marked (MIT), inlined so the 原文 drawer can render markdown offline
marked = open('marked.umd.js', encoding='utf-8').read().replace('//# sourceMappingURL=marked.umd.js.map', '')
assert '</script' not in marked
parts = '<script>' + marked + '</script>\n'
# config.html and visual.html are written per document; visual.html does not exist before the picture pass
layers = ['srcmap', 'config', 'srcanno', 'enhance', 'colors', 'type', 'srcview', 'visual_core', 'visual', 'pager']
parts += ''.join(open(f + '.html', encoding='utf-8').read() for f in layers if os.path.exists(f + '.html'))
i = raw.rfind('</body>')
html = raw[:i] + parts + raw[i:]
open(out, 'w', encoding='utf-8').write(html)
print(len(html.encode()), 'bytes →', out)
