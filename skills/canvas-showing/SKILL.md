---
name: canvas-showing
description: Render a document as a designed "canvas" web page — a single self-contained .html in Monad editorial style (parchment canvas, serif-400 headings, mono body, Lake Blue accent) with a canvas-drawn hero, sticky TOC, and auto-generated Mermaid diagrams. MANUAL INVOCATION ONLY — invoke only when the user explicitly asks for "canvas-showing" by name; do not auto-invoke for generic document-viewing or rendering requests.
disable-model-invocation: true
---

# Canvas-Showing

Turn a document into a **canvas page**: one self-contained `.html` file — Monad editorial style (parchment `#f6f3f1`, serif headings at weight 400, monospace body/UI text, Lake Blue `#2b59d1` as the single accent, hairline `#cecac8` borders, pill radii, no shadows), canvas-drawn hero, sticky TOC, auto-generated Mermaid diagrams. The output is a single portable file: CSS, hero, and scripts are inlined, so it opens by double-click and can be shared as-is.

All assets ship in [`assets/`](assets/): `spec.css` (full theme), `hero_template.html` (announcement bar + canvas hero), `tail.html` (canvas drawing + Mermaid init in the Monad palette).

## Steps

1. **Get the source into a temp dir.** `mktemp -d` (e.g. `/tmp/canvas-page-XXXX`), write `source.md`.
   - Local file → copy it.
   - GitHub `blob/` URL → rewrite to `raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>` and fetch. On 404/private, ask the user to paste the content.
   - Pasted text → write verbatim.
2. **Copy the assets.** `spec.css` and `tail.html` go to the page dir unchanged. `hero_template.html` → `hero.html` with the announcement-bar text, kicker, `h1`, subtitle, and meta pills rewritten for this document. In `tail.html`, relabel the two pipeline label arrays (`G1`, `G2`) to a flow the document actually describes; if none fits, delete the `drawChain` block and keep only the pastel washes.
3. **Diagram pass — always on.** Walk every section; where a diagram beats prose, insert or replace with a ```` ```mermaid ```` block. Keep dense rule text, acceptance matrices, TBD lists, and code/interface blocks as-is — those are lookup material a diagram loses precision on. Mapping:

   | Content shape | Mermaid kind |
   |---|---|
   | States + transitions (incl. ASCII state art) | `stateDiagram-v2` — replace the ASCII block |
   | Step flows, pipelines, decision branches | `flowchart` (LR for short chains, TB for branching) |
   | Multi-actor request/response | `sequenceDiagram` |
   | Entities/types and their relations | `erDiagram` (relationships only, no attributes needed) |
   | Timelines, schedules, clock points | `flowchart LR` chain |
   | Routing/dispatch tables (trigger → destination) | `flowchart LR`, replace the table |
   | Architecture (components ↔ files ↔ server) | `flowchart` with `subgraph`s |
   | In-scope vs out-of-scope lists | `flowchart` with two `subgraph`s |

   Mermaid syntax rules: quote every label containing punctuation or CJK (`A["..."`), use `<br>` inside labels for line breaks, never leave parentheses in unquoted text.
4. **Build a single file.** Name the output after the source document: `SPEC.md` → `SPEC.html`, `notes.markdown` → `notes.html`. For pasted text with no filename, use a slug of the document title. Run `pandoc source.md -f gfm -t html5 -s --toc --embed-resources --highlight-style=breezedark --metadata lang=zh-Hant --metadata title="<doc title>" -c spec.css -B hero.html -A tail.html -o <source-basename>.html` — `--embed-resources` inlines the stylesheet; `-B`/`-A` content is already inline, so the result is self-contained.
   - Consecutive `>` blockquote lines collapse into one paragraph — end each line with `\` if the header metadata must stay on separate lines.
   - If the doc has a top `#` title that duplicates the hero, it is hidden by CSS already.
   - Mermaid still loads from the jsdelivr CDN in `tail.html`. For a fully offline file, download `mermaid.min.js` into the page dir and swap the CDN `src` for the local filename — `--embed-resources` will inline it.
5. **Preview.** Browser tools reject `file:` URLs, so to show it in the built-in browser run `python3 -m http.server <port>` in the page dir (backgrounded) and `browser_open http://127.0.0.1:<port>/<name>.html`. If the browser shows an unrelated page the port is taken — pick another. If no browser is needed, skip this step and just hand over the file.
   - `browser_navigate` to a `localhost` URL can be rejected as `BrowserNavigationBlocked` even when the URL is valid — and it may still commit, leaving the tab on a `chrome-error://` page if the server is down. Verify the server with `curl -sI` first, and prefer `browser_open` + `127.0.0.1`, which sidesteps the block.
6. **Verify.** `browser_screenshot` for proof. Completion check: `document.querySelectorAll('.mermaid svg').length` equals the mermaid block count and no `.mermaid` div lacks an `svg`; the fixed TOC must not overlap the hero (hero uses `margin-left`, not `padding-left` — already correct in `spec.css`).
7. **Report** the `.html` path (the deliverable — named after the source file), the preview URL if served, and that the file opens by double-click — no server needed after creation.

## Failure handling

- **Mermaid CDN unreachable** → page still works; `pre.mermaid` blocks show as readable code. Mention it in the report.
- **Pandoc missing** → `brew install pandoc` or ask the user.
- **Screenshot shows a different site** → port collision; restart on a new port and re-open.
