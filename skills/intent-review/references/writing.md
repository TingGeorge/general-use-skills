# Writing one page fragment

A page is a reading guide for a person who will judge the code themselves. It says what each part of the code is for, how it does it, and why it was done that way, and it puts the real code beside the text. It never tells the reader what to conclude.

You write an HTML fragment. `scripts/build_page.py` checks it, embeds the source files and wraps it in the shell (styles, code pane, scripts). So the fragment has no `<html>`, `<body>`, `<style>` or `<script>`.

`references/example_fragment.html` is a finished fragment from a real project (in Traditional Chinese). Read its first two topics for the structure and the amount of text, and one of its `<figure>` blocks before drawing a diagram. Copy its class names and depth, not its topics or its language.

## The form: a picture and a few short lines

Most reviewers read pictures first. A page that retells the code in paragraphs is not read, and the code is right beside the page anyway. So what the reader sees without clicking is, per topic, one sentence, one diagram and three short rows. A little more sits one click away in a fold. Everything else is left out.

    <!-- sources: src/auth/session.ts, db/migrations/001.sql -->   paths from the repo root; these files go in the code pane
    <!-- skipped: bun.lock, src/gen/types.ts -->                    diff pages only: changed files you chose not to embed
    <h1>Title</h1>
    <p class="sub">One line that says what the page covers</p>
    <nav class="toc" aria-label="…"><a href="#overview">…</a> <a href="#map">…</a> <a href="#topic-id">1 …</a> …</nav>
    <h2 id="overview">Overview</h2>     at most two sentences; then a fold holding a two-column table (topic / one line)
    <h2 id="map">Function map</h2>      one sentence, the two-level map, a fold with at most 3 bullets (see "Function map")
    <h2 id="…" data-focus="session.ts:10-40,60-80">1 Topic name</h2>
    …the topic, as below…
    … more topics …
    closing sections (see "Closing sections")

Write headings and text in the project's language. The examples here are in English only to show the shape.

Each topic, in this order, and nothing else visible:

    <p class="lead">One sentence, about 20 words at most, saying what this part does. No line refs.</p>

    <figure>…the diagram that shows this topic's mechanism…<figcaption>One sentence.</figcaption></figure>

    <div class="parts tight">
      <div class="b p"><h3>Problem</h3><p>One sentence: why this code exists.</p></div>
      <div class="b m"><h3>Method</h3><p>One sentence: what it does (<code>session.ts:12-30</code>).</p></div>
      <div class="b w"><h3>Why</h3><p>One sentence: the main reason, with its source (ADR-0012).</p></div>
    </div>

    <details class="more">
      <summary>Details: 4 results, 3 reasons</summary>
      <div class="in">
        <h4>Results</h4>  <ul><li>…at most 4…</li></ul>
        <h4>Reasons</h4>  <ul><li><b>Short label:</b> one clause and its source.</li></ul>
      </div>
    </details>

- **Every topic has a diagram.** If nothing about the topic can be drawn (a flow with decisions, a state machine, a sequence between actors, a timeline, how tables or types relate), it is probably not a topic.
- **The three rows are one sentence each**, with at most one source in brackets. The builder requires exactly these three blocks, in this order.
- **The fold is small: about 150 words at most.** Results are the behaviours a reader could not see from the diagram or guess from the code's shape: surprising cases, what happens on failure. Reasons are the ones beyond the main one, each with its source. One short sentence per bullet, each with one `file:line` ref or source. A small table (at most 5 rows) or a second figure may go in the fold when it shows something the main diagram does not.
- **The summary line says what is inside, with counts**, so the reader can decide whether to open it.
- **Leave out** what the code shows plainly at the cited lines and what repeats the diagram. Do not write a full method paragraph: the diagram is the method.
- A fold is always `<details class="more"><summary>…</summary><div class="in">…</div></details>`, never nested. The topic's diagram and its three rows are never inside a fold.

`data-focus` on the `<h2>` becomes the one "show code" button of the topic: one file and all the lines that belong to the topic. When a topic spans files, use the main file; the others stay reachable through inline refs.

## Choosing topics

Follow how the code is organised around purposes, not the file list. A topic is one thing the code is trying to achieve; it can cover part of a file or reach into several. 3 to 6 topics per page is the range that reads well. More than that means the page should be split.

## Pages about a change (diff or PR)

The code pane shows the new version of each file, with added lines marked green and removed lines shown in place on red. So the text explains the change, and the reader sees it in context.

- A topic is one intent of the change ("stop two requests from creating the same row"), not one file or one hunk. A refactor that touches ten files for one reason is one topic.
- **Problem**: what was wrong or missing before the change. **Method**: what the code did before and what it does now, pointing at the changed lines. **Why this way**: from the PR description, commit messages, linked issues, ADRs and code comments.
- `data-focus` covers the changed lines of the topic plus the unchanged lines needed to follow them.
- Every changed file is either in `sources` or in `skipped`; the builder fails otherwise. Leave the `skipped` comment out when nothing is skipped. Skip only what a person would not read: lockfiles, generated code, snapshots, binary files. A removed file cannot be embedded, so it goes in `skipped`.
- The builder prints a warning for each changed line range that no topic or ref points at (added blank lines are ignored). Each warning is a topic you missed, a line that belongs inside a ref you already have (widen the ref), or a change with no meaning of its own, such as a trailing comma or reformatting, which goes in the closing "other changes" table. Leave no warning unaccounted for: the reader trusts that the page covers the whole change.
- When the change spans several commits, add a commit column to the overview table so each topic names the commit it comes from.
- When a change states no intent (a commit that only says "bug fix", no PR text, no comment): in **Problem**, describe what the code did before as plain fact, and in **Why this way** write that the reason is not documented. Do not reconstruct the intent from the diff.

## Rules for content

These rules are the reason the page is useful. A reviewer who is handed conclusions stops reading the code.

- **No leading.** Do not tell the reader what to check, confirm or worry about. Do not judge ("this is better", "risky", "should"). Do not list bugs or findings. State what the code does and let the reader judge. If you see something that looks wrong, describe the behaviour plainly in "What follows from this" (for example "an empty string passes this check") and stop there.
- **The "why" has a source.** Reasons come only from written material: specs, ADRs or design docs, the PR description, commit messages, issues, code comments. Cite the source. If nothing records the reason, write that the reason is not documented. Do not invent a reason that sounds right: the reader will take it as the author's intent.
- **Every claim comes from code you read.** Do not describe from names. Avoid universal words (always, all, never, only) unless you checked every case. Line numbers are exact. Tests are a good way to confirm behaviour.
- **Scope.** Only this page's subject. If behaviour belongs to another page, name that page in one clause and move on.
- **Plain writing.** Short sentences, the project's language, identifiers in their original form. The first time a concept appears that the reader may not know (a transaction, an upsert, a mutex), say what it does in a few words. No filler and no slogans.
- **Don't pad.** A table or diagram that does not help someone understand is left out.

## Closing sections

Add each one only when there is real content for it. Each is an `<h2>`, one sentence giving the count, and the table inside a fold; keep every row, with cells cut to short phrases:

- **Differences from the spec**: what the spec says / what the code does / the source for the difference. Only real ones you can point at.
- **Decisions**: the ADRs or recorded decisions that govern this code: decision / what was given up / who decided.
- **Known limits**: simplifications the code itself declares (comments, ADRs): limit / when it breaks / the upgrade path the source gives.
- **Other changes** (diff pages): small changed ranges outside the topics: file and lines / what changed.
- **Not shown** (diff pages): the `skipped` files and why each is skipped.

## References the page makes clickable

- `<code>session.ts:12-20</code>`, `<code>session.ts:12</code>` or `<code>session.ts</code>` opens that file in the code pane. The name is the file's base name. When two embedded files share a base name, the name is the shortest path ending that tells them apart (`auth/index.ts`); the builder prints the names to use.
- A file cited with a line number must be in `sources`. Unchanged files may be added to `sources` just so their lines can be cited. Cite files that are not embedded (tests, docs) as plain paths without a line number, or not at all.
- Inside `<code>`, text shaped like `name.ext:12` is taken as a ref and must point at an embedded file. `localhost:4000` or `127.0.0.1:4000` is left alone.
- In SVG, `<text class="m" …>session.ts:12-20</text>` or `<text data-ref="session.ts:12-20" …>label</text>` is clickable together with the `<rect>` right before it.

## Diagrams

Inline SVG, where a picture shows the mechanism better than text: a flow with decisions, a state machine, table relations, a sequence between actors, a timeline. Every topic has one, and it is the main thing the reader looks at, so it must be clean: 5 to 8 boxes with short labels, no overlapping text, arrows that end on box edges, nothing crossing.

    <figure><div class="scroll"><svg viewBox="0 0 800 H" role="img" aria-label="one sentence">…</svg></div><figcaption>…</figcaption></figure>

- Width is always 800. Box classes: `box bx-blue|bx-teal|bx-gold|bx-rust|bx-gray|bx-none`. Text classes: `t` bold title, `s` small muted, `m` mono, `lab` edge label, `mid`/`end` anchors, `r`/`bk`/`tl` colours. Arrows: `<path class="arw" marker-end="url(#a)" d="…"/>`, also `arw-r` with `url(#ar)`, `arw-t` with `url(#at)`, `arw-g` with `url(#ag)`. The markers are already on the page.
- Use colours consistently and say what they mean in the caption when it is not obvious.
- Work out the geometry before writing it. A CJK character is about 13px wide (14px in `.t`); Latin and mono characters about 7px. Text fits inside its box with 10px to spare. Arrows start and end on box edges and do not cross boxes. Labels do not sit on a line or on another label. Everything stays inside the viewBox.

### A diagram that needs more room

Add `class="zoom"` to a `<figure>` and the page puts a button on it that opens the figure over the whole window (Esc closes it). Use it for a diagram that is readable in the page but nicer large.

A zoom figure may hold two drawings of the same thing: `<div class="scroll brief">` is shown in the page and `<div class="scroll detail">` only in the window. Use the pair when the full picture cannot fit the page width without becoming cramped: the brief one keeps what the reader needs to follow the text, the detailed one has everything. `data-open` and `data-close` on the figure set the button's two labels, so the label can say what opening adds ("Show all columns") and not just "Enlarge". Opening a figure that only gets bigger gives the reader nothing new, so when you have a detail drawing, make sure it really shows more.

### Function map

A page about code gets one function map near the top, before the first topic: grey containers are files, the boxes in them are functions, arrows are calls. It answers what the topics do not: which function calls which, and in which file. A reviewer looks at it first to know where things are, and comes back to it while reading.

Draw it with `scripts/fn_map.py`: a small library, not a layout engine. You write a short Python script that places the boxes and routes the lines, and the library refuses a drawing with a line through a box or a name, crossing lines, or a name wider than its box. It also refuses arrows nobody checked: every `call` names the line of code where the call is (`at='file.ts:23'`), and `verify` checks that this line sits inside the caller and contains the callee. So the script cannot finish until every arrow is true. The file's docstring has the API and a small example.

How to lay it out so it reads well:

- **One main path.** Find the path the page is about (a request coming in, a job running, a message being handled) and put its functions in one column, top to bottom, with `path=True`. That column is what the reader follows.
- **Helpers beside their callers.** Put the functions the path calls to the right, at the same height as the caller, in their own file containers. Most arrows then run straight across. Shared helpers that many things call (errors, logging) go in a row along the bottom.
- **Two levels.** In the page the map shows only the main path: 8 to 10 boxes, no groups, about 10 arrows. The full map (about 20 functions at most) sits behind the figure's button: build both and join them with `fn_map.pair(brief, detail, caption, …)`. Readers found the full map alone too busy to start from.
- **In the full map, about 20 functions at most.** Only the ones the page's topics talk about. Leave out what is called from everywhere (an error class, a logger) and say in the caption what is left out; an honest gap is better than a full, unreadable picture.
- **Three kinds of line**: `call` (black) for a direct call, `kind='next'` (green) when control passes on without a direct call (middleware order, a queue, an event), `kind='error'` (red dashed) for what runs when something throws.
- **No crossings.** Reroute, reorder the boxes, or use the two tools the library gives: a `group` around functions that share callers or callees (one line to the group stands for all of them), and a fork (a second arrow from the same function may start on its first arrow). If it still cannot be drawn without crossings, the map has too much in it.
- **Functions outside the page** (called by or calling this page's code) go in a `dashed=True` container with no ref.
- **Diff pages**: mark the functions the change touches with `changed=True`, so the reader sees where the change sits.

Leave room: columns about 250px apart, rows about 50px apart, 30px between a container's top and its first box (the file name sits there). Run the script, read the problems it lists, fix, and repeat until it prints the figure. Then put the figure in the fragment under its own heading, with one paragraph before it saying how to read it, and a caption that explains anything the picture cannot (a group, a fork, what is left out). Translate the legend with `legend(x, y, text={...})`.

A page with fewer than about four functions that call each other (a schema, a list of types) does not need a map: say so in your report and leave it out.

### ER diagram for database pages

A page about a database schema gets one ER diagram of all its tables, near the top. Readers find one picture easier than a figure per group, and what makes a single picture unreadable is listing every column, not the number of tables.

`scripts/er_diagram.py SPEC.json` draws it and prints the `<figure class="zoom">` to paste into the fragment: the brief drawing lists only key columns (PK, FK, UQ) with a count of the rest, the detailed one lists every column with its type. The file's docstring describes the spec. What matters when writing the spec:

- Fill `columns` from the schema itself with a small script (migrations, a schema dump), not by typing; a diagram that disagrees with the SQL is worse than none.
- The layout wants a hub: the table most others point at goes in the middle as one tall box, and every link to it is a straight line. Put related tables next to each other and give each group one colour. A link that skips the hub only works between two tables stacked in the same column. If the schema has no clear hub, draw it by hand in the same style.
- Line ends are crow's-foot marks (`one`, `many`, `maybe`); derive them from the constraints: a foreign key that is also the whole primary key or unique is `maybe` on its own side, a nullable foreign key is `maybe` on the far side.
- Translate the `text` labels into the page's language, write the caption (what the colours mean, composite keys, on-delete rules), and above the figure explain PK / FK / UQ and the line ends in a sentence each for a reader new to ER diagrams.

Other building blocks from the shell: `<div class="tbl"><table>…</table></div>` for tables, `<p class="note">` for a side note.

## Before you finish

Reread the fragment against the code, claim by claim, and fix what the code does not show. Recheck each diagram's coordinates for overlap. Run the builder until it prints OK and every warning is accounted for.
