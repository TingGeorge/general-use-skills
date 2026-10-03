# Pictures: one section → one visual

The picture pass writes `visual.html` in the page dir: one `build()` per section. A build replaces the section's text with a picture made of short **keyword chips**; every chip opens its original sentence in a pop-up (with a 「原文 ↗」 link into the source drawer), so no detail is lost, only moved one click away. Any sentence no chip links stays visible under 「還沒畫進圖的原文」, so a gap is loud, never silent.

The worked example is the 找點事 PRD: [`example/visual.html`](example/visual.html) (29 sections) and its [`example/config.html`](example/config.html). Each build there starts with a `// ==== <section> → <picture> ====` header; search those headers for a picture before writing one from scratch.

## File shape

```html
<script>
(function () {
  var build = VZ.build, KEY = VZ.KEY, norm = VZ.norm;

  build('<heading id>', function (c) {
    return c.box('Title', [['keyword', 'phrase from the sentence'], ['another', 'other phrase']]) + KEY;
  });
})();
</script>
```

- `<heading id>` is the pandoc id of the section heading (`document.querySelectorAll('main.content h2, main.content h3')` lists them). A build covers everything from that heading to the next heading of any level.
- End every build with `KEY` (the 「點任一個詞看原文全句」 legend line).
- Leave out: chapter covers (an `h2` with no text of its own; the pager makes it a card grid), and sections that already are full-wording diagrams with no prose.

## The `c` API

| Call | Returns / does |
| --- | --- |
| `c.chip(label, match, cls, scope)` | one chip; `match` is a phrase (below) or an element (a card) |
| `c.chips(items, scope, flow)` | a wrapping row. Item: `[label, match, cls]`; a bare string = small sub-heading; `'→'` = arrow; `flow` true = arrows between all items |
| `c.box(title, items, cls)` | a titled box holding `c.chips(items)` |
| `c.group(title, html)` | a labelled group whose children sit in an auto-fit grid |
| `c.card(key)` | the card whose ID pill or title equals `key` (use as `scope`, or as a chip's match to open the whole card) |
| `c.cards()` | every card in the section, in order (for boards and row-per-card pictures) |
| `c.slot(selector, n)` | moves the n-th existing element (a `.mermaid` diagram, `.stats`, `.legend`, `.keynums`) into the picture instead of hiding it |
| `c.use(match)` | marks a label-only line (e.g. 「標記：」) as shown by a box title; returns '' |
| `c.find(match, scope)` | the sentence element itself, for custom markup |
| `c.misses` | push a string to report a failed lookup of your own (e.g. row counts that differ) |

Chip classes: `no` struck through (excluded / replaced), `tg` bold target, `calc` hatched (inferred, not written in the source), `dl` deadline red, `ok` done green; in time lanes `n` (this period), `a` (next period). The gold / dashed-red marker dots come by themselves from the sentence's note markers.

## Matching: how a chip finds its sentence

The text is matched after `enhance.html` has run, so match what the page shows, not the markdown:

- A match is a **substring** of one sentence; the **first** sentence in section order that contains it wins. Pick a phrase only the intended sentence has. Prefix `=` for an exact match of the whole sentence (trailing 。；， ignored).
- Long table cells and paragraphs are split into separate sentences at top-level 。 and ；. A label about the second clause must match words in the second clause, or the chip opens the wrong half.
- Reference codes become chips without brackets: `回覆期限一週（R:A-1.4）` reads `回覆期限一週R:A-1.4`.
- Note markers become words: 🟡〔…〕 reads as the note label followed by the text.
- `scope` (usually `c.card(id)`) limits the search to one card, for sections where many cards share wording.

## Picture vocabulary

Choose by the shape of the content. Every detail stays reachable through a chip, so pick the picture for the overview it gives, not for how much text it can hold.

| Content shape | Picture | Classes / helpers | Example build |
| --- | --- | --- | --- |
| Themed rules or requirements | boxes of chips, grouped by topic | `c.group`, `c.box` | 3 核心規則, 5.x |
| Numbered items with sub-points (features, IDs) | grouped tiles with ID pills | `.vz-fg`, `.vz-f`, `.vz-id` | 2.1 功能 |
| Many small numbered cases (acceptance criteria, answers) | board: rows of tiles + size meter, tile opens its card | `.vz-acr`, `.vz-ac`, `c.cards()` | 9 驗收條件, 附錄 A |
| Dates, weeks, deadlines, worked examples with days | month calendars, week strip, duration bars | `.vz-cal`, `.vz-week`, `.vz-bar` | 3.1 週曆制 |
| Timing per variant (send → deadline → event) | time lanes with proportional segments | `.vz-lane`, `.vz-track`, `--f` | 3.2 延伸揪團規則 |
| Variants × attributes | matrix (stacks on narrow screens) | `.vz-mx`, `.vz-mr`, `data-h` | 3.2 |
| Screens or views | phone frames listing what each shows | `.vz-phones`, `.vz-phone` | 4.4 畫面需求 |
| Old → new, problem → fix tables | before → after rows | `.vz-ba` | 12 追溯 |
| Situation → feature / need → answer | two-column map with arrows | `.vz-map` | 1 定位 |
| A handful of questions or goals | numbered tiles | `.vz-f` + `.vz-id` | 1.1 |
| Excluded scope | struck-through chips (`no`) with ✓ chips for what is done instead | `c.box` | 2.2 |
| Existing state / ER / flow diagram + rules | slot the diagram, chips for the rules beside it | `c.slot('.mermaid', n)` | 6.1, 7 |
| Overview page | slot `.stats` and `.legend`, boxes for document facts | `c.slot` | 前言 |

Layout: `.vz-grid` auto-fits columns of ≥ 330px and stretches a short last row across the width. Put diagrams full width (stack them in a plain grid); a diagram in a third-width column shrinks to unreadable.

## Mistakes the verification loop catches

Each of these happened on the example document; the audit or the screenshots surfaced them:

- One match reused for several chips that describe later clauses → those chips open the first clause. Audit: "weak labels"; coverage: the later clauses stay uncovered.
- A whole-card chip hides that no chip points at a card's second sentence. Audit: "not opened directly".
- Matching with the brackets of a reference code → lookup fails (a dashed red chip).
- A chip with both marker dots, a struck-through chip carrying a marker that belongs to the other side of a before → after row, an empty third column next to two boxes, a diagram squeezed into a narrow column: visible only in screenshots.
