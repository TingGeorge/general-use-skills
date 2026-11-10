# Writing one page fragment

A page is a reading guide for a person who will judge the code themselves. It says what each part of the code is for, how it does it, and why it was done that way, and it puts the real code beside the text. It never tells the reader what to conclude.

You write an HTML fragment. `scripts/build_page.py` checks it, embeds the source files and wraps it in the shell (styles, code pane, scripts). So the fragment has no `<html>`, `<body>`, `<style>` or `<script>`.

`references/example_fragment.html` is a finished fragment from a real project (in Traditional Chinese). Read its first 120 lines for the structure and one of its `<figure>` blocks before drawing a diagram. Copy its class names and depth, not its topics or its language.

## Layout, in this order

    <!-- sources: src/auth/session.ts, db/migrations/001.sql -->   paths from the repo root; these files go in the code pane
    <!-- skipped: bun.lock, src/gen/types.ts -->                    diff pages only: changed files you chose not to embed
    <h1>Title</h1>
    <p class="sub">One line that says what the page covers</p>
    <nav class="toc" aria-label="…"><a href="#overview">…</a> <a href="#topic-id">1 …</a> …</nav>
    <h2 id="overview">Overview</h2>     one short paragraph, then a table with one row per topic: topic / problem / method / file (add a column when it helps)
    <h2 id="…" data-focus="session.ts:10-40,60-80">1 Topic name</h2>
    <div class="parts"> … </div>         then the diagrams and tables that belong to this topic
    … more topics …
    closing sections (see "Closing sections")

Write headings and text in the project's language. The examples here are in English only to show the shape.

Each topic has exactly one `parts` block, with exactly these three blocks in this order:

    <div class="parts">
      <div class="b p"><h3>Problem</h3><p>…</p></div>
      <div class="b m"><h3>Method</h3><p>…</p><h4>What follows from this</h4><ul><li>…</li></ul></div>
      <div class="b w"><h3>Why this way</h3><ul><li><b>Short label:</b> reason (ADR-0012, <code>session.ts:12</code>).</li></ul></div>
    </div>

- **Problem** says why this code exists, in product or system terms. One or two sentences.
- **Method** says what the code does, in the order it happens. "What follows from this" is optional: use it for behaviour a reader cannot see from those lines alone (for example "a 400 for bad input is stored as done too"). Present tense only, nothing about the future.
- **Why this way** gives the reasons, each with its source.

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

Add each one only when there is real content for it, with these as `<h2>` sections with a table:

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

Inline SVG, where a picture shows the mechanism better than text: a flow with decisions, a state machine, table relations, a sequence between actors, a timeline. Zero is fine for a small diff; a full page about a subsystem usually wants two to five.

    <figure><div class="scroll"><svg viewBox="0 0 800 H" role="img" aria-label="one sentence">…</svg></div><figcaption>…</figcaption></figure>

- Width is always 800. Box classes: `box bx-blue|bx-teal|bx-gold|bx-rust|bx-gray|bx-none`. Text classes: `t` bold title, `s` small muted, `m` mono, `lab` edge label, `mid`/`end` anchors, `r`/`bk`/`tl` colours. Arrows: `<path class="arw" marker-end="url(#a)" d="…"/>`, also `arw-r` with `url(#ar)`, `arw-t` with `url(#at)`, `arw-g` with `url(#ag)`. The markers are already on the page.
- Use colours consistently and say what they mean in the caption when it is not obvious.
- Work out the geometry before writing it. A CJK character is about 13px wide (14px in `.t`); Latin and mono characters about 7px. Text fits inside its box with 10px to spare. Arrows start and end on box edges and do not cross boxes. Labels do not sit on a line or on another label. Everything stays inside the viewBox.

Other building blocks from the shell: `<div class="tbl"><table>…</table></div>` for tables, `<p class="note">` for a side note.

## Before you finish

Reread the fragment against the code, claim by claim, and fix what the code does not show. Recheck each diagram's coordinates for overlap. Run the builder until it prints OK and every warning is accounted for.
