---
name: canvas-showing
description: Render ANY document (markdown file, spec, notes, pasted text, GitHub doc — any language, any project) as a designed "canvas" web page — a single self-contained .html where every section becomes a picture of keyword chips that open their original sentences, with a source drawer, one page per section, colour by section kind, and full-wording Mermaid diagrams. Ends with a verify → see → check → fix loop. MANUAL INVOCATION ONLY — invoke only when the user explicitly asks for "canvas-showing" by name; do not auto-invoke for generic document-viewing or rendering requests.
disable-model-invocation: true
---

# Canvas-Showing

Turn a document into a **canvas page**: one self-contained `.html` in Monad editorial style (parchment `#f6f3f1`, serif headings at weight 400, Lake Blue `#2b59d1` accent, hairline borders, pill radii). The reader sees pictures, not prose: every section is redrawn as charts, calendars, timelines, matrices or maps of short **keyword chips**, and every chip opens the sentence it stands for. Nothing is dropped; everything is one click from its original wording and from the exact source lines.

The page is built in layers on top of pandoc's HTML, all in [`assets/`](assets/):

| Layer | Does |
| --- | --- |
| `spec.css`, `hero_template.html`, `tail.html` | theme, hero, Mermaid (bundled `mermaid.min.js`) with a 「⤢ 放大」 zoom pop-up |
| `gen_srcmap.py` → `srcmap.html`, `srcanno.html` | maps every block back to its lines in the original file |
| `config.html` (from `config_template.html`) | **the only document-specific rules**: reference codes, note markers, ID tables, before → after tables, section kinds, overview tiles |
| `enhance.html` | tables → cards, lists → blocks, `A → B → C` → steps, dense text → one item per clause, overview tiles |
| `colors.html`, `type.html` | one hue per section kind + legend; reading type; diagram-first ordering |
| `srcview.html` | 「原文」 buttons and the right-side source drawer (rendered or raw markdown) |
| `visual_core.html` + your `visual.html` | the picture framework, and this document's pictures |
| `pager.html` | one page per heading, chapter covers, sticky crumb, collapsible TOC |
| `build.py` | concatenates everything into the final file |

[`tools/`](tools/) holds the verification scripts (`audit.cjs`, `shot.cjs`); [`references/pictures.md`](references/pictures.md) is the picture-pass manual.

## Design rules

These hold for every page and every picture:

- **Pictures over prose.** The reader takes in visuals far more easily than text. Every content section becomes charts, calendars, timelines, matrices or maps of short keyword chips, with every detail reachable (each chip opens its original sentence).
- **One page per TOC entry**: the whole section on one scrollable page.
- **Full width** between the sidebars: card grids and side-by-side blocks reflow as the TOC or source drawer opens and closes, so pages stay short. Text, blocks and grids share the same left and right edges.
- **Sequences top to bottom**: workflows, timelines and step chains are top-to-bottom Mermaid diagrams whose nodes carry the original wording in full.
- **Each piece of content once**: a flow drawn as a diagram is not repeated as text or steps; a section's text is hidden once its picture covers it.
- **Diagram first, then text**: a diagram that summarises a passage sits above it.
- **Always the full version**: every step below, every section pictured, the verification loop run to its exit.

## Steps

### 1. Source → page dir

`mktemp -d` (e.g. `/tmp/canvas-page-XXXX`), write `source.md`, and keep the path of the original file for the source map.
- Local file → copy it. GitHub `blob/` URL → fetch `raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>`; on 404/private, ask for the content. Pasted text → write it verbatim to a file and use that as the original.

### 2. Read the whole document, then plan with the user

Read every section before changing anything, and write down: the section list; which picture each section gets (from the vocabulary in `references/pictures.md`); and what `config.html` needs — reference codes written in brackets, note markers, tables whose first column is an ID, before → after tables, how sections group into kinds.

Bring the user every **content decision** before building: a section where a picture would drop, merge or reorder meaning; a passage that repeats another (show it once — which copy?); anything inferred rather than written (drawn hatched with `calc`). Done when each such decision has the user's answer, or there were none.

### 3. Assets and config

Copy into the page dir: `spec.css`, `tail.html`, `mermaid.min.js`, `marked.umd.js`, `gen_srcmap.py`, `build.py`, `srcanno.html`, `enhance.html`, `colors.html`, `type.html`, `srcview.html`, `visual_core.html`, `pager.html`.
- `hero_template.html` → `hero.html`, every `{{PLACEHOLDER}}` filled from this document: `ANNOUNCE_LEFT` (source breadcrumb), `ANNOUNCE_PILL` (status chip), `KICKER` (doc type + date), `TITLE`, `SUBTITLE`, `META_1..4` (draft badge + 2–4 stat chips; delete the `<span>` of any unused slot).
- In `tail.html`, relabel the two hero pipeline arrays (`G1`, `G2`) to a flow the document describes; if none fits, delete the `drawChain` block.
- `config_template.html` → `config.html`: fill the fields this document uses, delete the rest. With no `kinds`, every chapter gets its own hue automatically. `references/example/config.html` is a full worked config.
- UI strings are Traditional Chinese. For a document in another language, translate them in `tail.html` (zoom pop-up), `srcview.html` (drawer), `pager.html` (目錄, 第 N 章, 本節原文, 前言), `colors.html` (legend), `enhance.html` (default tiles) and `visual_core.html` (pop-up, 還沒畫進圖的原文, `KEY`).

### 4. Diagram pass on `source.md`

Where the document describes something sequential or structural, add a ```` ```mermaid ```` block:

| Content shape | Mermaid kind |
|---|---|
| States + transitions (incl. ASCII state art) | `stateDiagram-v2` — replace the ASCII block |
| Step flows, pipelines, decision branches | `flowchart TB` |
| Multi-actor request/response | `sequenceDiagram` |
| Entities and their relations | `erDiagram` (relationships only) |
| Architecture (components ↔ files ↔ server) | `flowchart TB` with `subgraph`s |

- Nodes carry the original wording in full, top to bottom. A diagram that redraws an `A → B → C` sentence (or a list item of one) starts with `%% steps-of: <bold title of that item>` (or `%% steps-of: (previous)` for the paragraph right above): the chain is then shown once, as the diagram, keeping its title, tail text and 原文 button.
- Syntax: quote every label with punctuation or CJK (`A["..."]`), `<br>` for line breaks, `#lt;`/`#gt;` for `<`/`>`, and in `stateDiagram-v2` declare CJK states with ASCII ids (`state "第 1 張" as P1`).
- Lines you add have no source line; the drawer says so and shows their code.

### 5. First build

```sh
pandoc source.md -f gfm -t html5 -s --toc --embed-resources --highlight-style=breezedark \
  --metadata lang=<doc-lang> --metadata title=raw -c spec.css -B hero.html -A tail.html -o raw.html
python3 gen_srcmap.py <original file> "<path shown in the drawer>"
python3 build.py <source-basename>.html "<page title>"
node <skill>/tools/audit.cjs <source-basename>.html
```

- `title=raw` is a placeholder `build.py` replaces. `--embed-resources` inlines `spec.css` and `mermaid.min.js`; fonts stay linked from Google Fonts on purpose (inlining them adds ~13 MB).
- Consecutive `>` lines collapse into one paragraph: end each with `\` to keep them apart.
- Done when the audit's hard checks pass (0 picture sections at this point). They include the layers' own warnings: a source map out of line with pandoc's blocks, a `steps-of` diagram with no chain to replace, a `build()` whose heading id does not exist.

### 6. Picture pass

Read [`references/pictures.md`](references/pictures.md), then write `visual.html`: one `build()` per content section, choosing each picture from the vocabulary and the worked examples. Rebuild with `build.py` after each few sections and run the audit to keep coverage at zero gaps as you go.

Done when every section has a build, except chapter covers and sections that already are full-wording diagrams — name those exemptions in the report.

### 7. Verify → see → check → fix

Run this loop until an entire round finds nothing to fix:

1. **Verify**: `node <skill>/tools/audit.cjs <page>.html`. Hard checks (script errors, broken diagrams, sentences no chip links, chips whose sentence was not found, chips with no or off-screen pop-up, overflow or sideways scroll at 1440 px and 400 px) must all pass. Then read every **review** line: a weak label usually means the chip opens the wrong clause; a sentence not opened directly needs its own chip.
2. **See**: `node <skill>/tools/shot.cjs <page>.html 1440 all` and look at every screenshot; then `node <skill>/tools/shot.cjs <page>.html 400 <dense pages> 300` for phone width (viewport shots — full-page phone shots are too small to judge). Look for: empty columns beside short rows, diagrams too small to read, markers on the wrong chip, chips wrapping one character per line, anything clipped, overlapping, or misaligned with its neighbours. Zoom into each diagram (`.zoom-stage`) and check its symbols read as their standard notation: arrowheads on flowcharts, crow's feet and double bars on ER diagrams. Page CSS that restyles Mermaid can silently break them.
3. **Check**: open a sample of pop-ups in each section and read them against their chips; confirm the audit printed no `pageerror` (a syntax error in `visual.html` stops every picture after it).
4. **Fix** what the round found, rebuild with `build.py`, and start the next round from step 1. Run edits and the rebuild one after another, never in parallel: a build that starts before an edit lands ships without it.

Exit when, in one full round, the hard checks pass at both widths, every review line is fixed or explained, every page has been seen, and nothing needed fixing.

The scripts open the file directly in headless Chrome (they find `playwright-core` and Chrome on their own; set `PLAYWRIGHT_CORE` / `CHROME` to override). When the host also has a built-in browser, show the page there for the user: serve the dir with `python3 -m http.server <port>` (backgrounded), open `http://127.0.0.1:<port>/<name>.html`, add `?v=N` after a rebuild. A built-in browser can hang on a page this size; the scripts are the source of truth for the loop.

### 8. Report

The `.html` path (named after the source file; opens by double-click, no server needed), the preview URL if served, the loop's last-round numbers (pages, picture sections, chips, diagrams, hard checks at both widths), the content decisions and exemptions, and anything inferred.

## Failure handling

- **Pandoc missing** → `brew install pandoc`, or ask the user.
- **Output much larger than ~3 MB** → something big got inlined; find it with a `data:[^;]+;base64,` size scan.
- **Audit warning `source map: …`** → `gen_srcmap.py` split `source.md` into blocks differently from pandoc; 原文 buttons stop at the first mismatch. Compare the block it names with the markdown around it, adjust the markdown shape, rerun `gen_srcmap.py` and `build.py`.
- **`playwright-core not found`** → `npm i -g playwright-core`, or point `PLAYWRIGHT_CORE` at one.
- **Preview shows a different site** → port collision; restart the server on another port.
