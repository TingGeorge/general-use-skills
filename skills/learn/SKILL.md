---
name: learn
description: Crash-course exam tutor. Reads the teacher's materials (slides, PDFs) and past exam papers, then builds one visual, interactive HTML study guide that gets a beginner a high score on the coming exam — color-coded chapters, lesson cards, diagrams, interactive demos, LaTeX math, Cursor-style code, mock quizzes and a cheat sheet. English text with Traditional Chinese notes on hard concepts.
disable-model-invocation: true
---

# Learn

Build **one self-contained HTML study guide** that a beginner can use to score high on a specific exam, fast.
The reader is a visual learner: long walls of text are a burden. Show it with color, diagrams and things to click; keep prose short.

Start from [`assets/template.html`](assets/template.html) — it already holds the whole look (CSS, KaTeX, layout script, code highlighter, plot helper).
[`references/example-algorithms-quiz1.html`](references/example-algorithms-quiz1.html) is a finished guide built with this skill — copy patterns from it (demos, figures, derivations) instead of reinventing them.

## Inputs to confirm

From the user's message, pin down — ask only if missing:

- **Materials folder** (slides / PDFs) and **exam scope** (e.g. "up to chapter 2-2").
- **Past exams folder** (photos or PDFs of old papers).
- **Output folder** (e.g. `tutorials/`). File name: `<exam>.html`, e.g. `quiz1.html`, `midterm.html`.

## Steps

### 1. Read every in-scope material

- `.pptx` / `.docx` / `.pdf` → `markitdown <file>` (or the pdf skill).
- Old `.ppt` → `soffice --headless --convert-to pptx` into a temp dir first, then `markitdown`.
- Slide formulas are often images and get lost in conversion: rebuild them from the slide's surrounding steps and notes.
- Read only what is in scope. Note out-of-scope topics for the footer.

### 2. Analyze the past exams

Read every exam image/PDF. Produce:

- A **question-type table**: for each recurring slot (Q①, Q②…) what was asked each year and what to prepare.
- **Mistakes seen on graded papers** (red marks, partial scores): wrong answer → why → correct answer. These become trap boxes.
- Which topics appear every year → mark those lessons with ★ and a `Quiz 113`-style `tag hot`.

### 3. Verify the math before writing it

Every formula, closed form, example and worked table must be checked by computer (a short Python script: brute force over all permutations, exhaustive search, recompute the example). Never ship an unverified derivation; say in the page what was checked ("verified by exhaustive search").

### 4. Build the page from the template

Copy `assets/template.html` to the output folder, fill every `{{…}}`, replace the EXAMPLE blocks with real content, delete what is unused.

**Structure** (flat inside `<main>`; the layout script groups it):

- `h2` = chapter → becomes a colored banner with chips linking to its lessons. Attributes: `data-ch` (`intro | ch1 | ch21 | ch22 | rev`, add more colors in CSS), `data-kicker` ("Chapter 1"), optional `data-intro` (label for the card before the first h3).
- `h3` with an `id` = lesson → becomes a white card with a colored top bar and number pill. The sidebar `<b data-ch>` groups must match.
- Order: Start (how to use + roadmap + past-exam analysis) → one chapter per scope unit → Final review (traps grid, mock quizzes, cheat sheet).

**Every lesson** gets, as fitting:

- A `tldr` one-liner with colored complexity pills (`cx-fast` / `cx-mid` / `cx-slow` / `cx-x`).
- Short English explanation; key terms bold.
- A `zh-note` (繁體中文, 1–2 sentences) on every concept that is hard for a beginner: the intuition, the trick, the easy-to-confuse distinction. Not a translation of everything.
- The derivation in display math, split into `aligned` lines short enough to fit without scrolling.
- `box good` "What to write on the exam (N points)": the shortest complete answer.
- `box trap` for known mistakes, `box key` for the one idea to remember.

**Visuals — add one wherever a picture or a click explains faster than text:**

- Interactive demos (`.demo`, tinted with the chapter color): step-through of an algorithm with counters, sliders that move a curve (`linePlot` helper), "click a node/point" diagrams, pick-items puzzles, histograms computed over all cases, best-vs-worst side-by-side. Each demo has a one-line `demo-hint` and a `verdict` line that states the takeaway from live data (never hard-code a claim the data can contradict).
- Static SVG figures (`figure.fig`, picture left, one-sentence caption right) for definitions: graphs, trees, polygons, balance diagrams.
- Classification as colored lanes; roadmap cards; traps as a numbered card grid; cheat-sheet cells auto-colored by complexity.
- Clickable SVG parts get `tabindex="0" role="button" aria-label` (keyboard support is built in).

**Text and code conventions:**

- Language: **English main text**, Traditional Chinese only in `zh-note` (and the `中文說明` legend). Follow the user if they ask for another mix.
- Math: LaTeX via KaTeX — `$…$` inline, `$$…$$` in `<div class="math">`. Use `\lt \gt` instead of raw `<` `>`; never `&&` annotation columns that push lines wide — put notes in a `p.sub` under the block.
- Code: `<pre class="code" data-file="name.pseudo">` → Cursor-style dark editor with colors and line numbers. Edit the `KW` set for the course's keywords. Comments with `//`, aligned, short.
- Plain traces / ASCII sketches stay in a light `<pre>`.

**Style rules** (already in the template — keep them):

- Warm eggshell / taupe base, Inter, whisper-weight (300) headings, pill buttons, 20–24 px radii, hairline borders.
- Color is for meaning: chapter colors for regions, green/amber/red for exam-answer/key/trap, green→red for complexity. No decorative gradients beyond the hero sphere.
- Mobile: the template already scrolls wide math/tables inside their boxes and stacks grids.

### 5. Mock quizzes and cheat sheet

- 2 mock quizzes in the real exam format (same number of questions, same point weights, same wording style), answers inside `<details>`.
- A quick true/false set drawn from the traps.
- Cheat sheet: one complexity table, one classification table, the key formulas.

### 6. Hand off

Tell the user the file path, what each chapter contains, the list of demos/diagrams, what was verified by computer, and anything uncertain (e.g. formulas reconstructed from slide images). The user reviews the UI themselves and will report anything to change — do not run a screenshot/fix loop unless asked.
