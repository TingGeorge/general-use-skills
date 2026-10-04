---
name: learn
description: Crash-course exam tutor. Reads the teacher's materials (slides, PDFs) and past exam papers, then uses 3b1b style to build one complete, detailed, easy-to-read visual and interactive HTML study guide that gets a beginner a high score on the coming exam — color-coded chapters, lesson cards, diagrams, interactive demos, LaTeX math, Cursor-style code, mock quizzes and a cheat sheet. English text with Traditional Chinese notes on hard concepts.
disable-model-invocation: true
---

# Learn

Build **one self-contained HTML study guide** that a beginner can use to score high on a specific exam, fast.
The reader is a visual learner: long walls of text are a burden. Show it with color, diagrams and things to click; keep prose short.

**The goal, in the user's words:** "Using 3b1b style to build a complete, detailed and easy to read and understand website guide for a beginner to get high score in the exam." Every rule below serves that sentence.

## 3b1b style = how to teach (always on)

Teach the way 3Blue1Brown explains math: the reader should *see* why a result is true before reading the proof.

- **Intuition first.** Each lesson opens with the picture or everyday analogy (insertion sort = sorting playing cards in your hand; binary search = every question throws away half), then the formal definition, then the derivation, then the exam answer.
- **One visual idea per concept.** Find the single picture that makes it obvious: the recursion tree whose levels each cost $n$, $c\cdot g(n)$ overtaking $f(n)$ after $n_0$, the median line splitting the points into A and B.
- **Let the reader move it.** Sliders, step buttons and clickable nodes, with the numbers on screen updating live (counters, sums, $n_0$). Let them break things: e.g. drag $c$ below the leading coefficient and watch $n_0$ disappear.
- **Show the result before you prove it.** Show the data first (e.g. enumerate every permutation and see that the average is $H_n-1$), then derive why.
- **Derive in small steps.** No skipped algebra. Every line follows visibly from the one before; say in a few words which trick each step uses ("subtract (2) from (1)", "telescoping", "arithmetic series").

**Complete** means every in-scope topic in the slides is covered, every derivation is written out in full, and every recurring past-exam question has a ready-to-copy answer. **Detailed** means best, worst and average case where the slides give them, plus each one's derivation. **Easy to read** means short paragraphs with one idea each, plain words, and a hard term explained the first time it appears.

The *look* stays the template's (or the user's style override). Use the dark Manim look only if the user asks for 3b1b's *visuals*: near-black canvas with blue `#58C4DD`, yellow `#FFE066`, green `#83C167` and red `#FC6255` as meaning colors.

Start from [`assets/template.html`](assets/template.html) — it already holds the whole look (CSS, KaTeX, layout script, code highlighter, plot helper).
[`references/example-algorithms-quiz1.html`](references/example-algorithms-quiz1.html) is a finished guide (Algorithms Quiz 1, Ch1–2-2) — copy its demos, derivations, answer templates and in-page self-check instead of reinventing them. It differs from the default in two ways: its main text is Traditional Chinese (that session asked for it), and it has its own flat CSS rather than the template's chapter banners. Take the patterns from it, and take the language and layout from this file and the template.

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
- Long tool output can get compressed or truncated. Write the markdown to a file, strip blank and image lines (`grep -v -E '^\s*$|^!\[|^<!--'`), then read it in line ranges (`sed -n '1,300p'`) until you have seen every slide.

### 2. Analyze the past exams

Read every exam image/PDF. Produce:

- A **question-type table**: for each recurring slot (Q①, Q②…) what was asked each year and what to prepare.
- **Mistakes seen on graded papers** (red marks, partial scores): wrong answer → why → correct answer. These become trap boxes.
- Which topics appear every year → mark those lessons with ★ and a `Quiz 113`-style `tag hot`.

### 3. Verify the math before writing it

Every formula, closed form, example and worked table must be checked by computer (brute force over all permutations, exhaustive search, recompute the example). Never ship an unverified derivation; say in the page what was checked ("verified by exhaustive search").

Put the checks **inside the page**: a self-check script at the end that calls the demos' own functions and compares them to every number the text teaches (e.g. the slide's inversion table, the first quick-sort pass, $X_n = H_n - 1$ for small $n$, the knapsack optimum, D&C result = brute force on random inputs). Log failures with `console.error` and show a footer badge "✔ self-check: N passed". Then the demos and the text cannot drift apart.

When a demo implements the slide pseudocode, make it reproduce the slide's worked trace exactly. Literal pseudocode often needs extra guards (e.g. the textbook quick-sort partition needs `i < j` checks inside the inner loops, or the trace for `3 6 1 4 5 2` breaks).

### 4. Build the page from the template

Copy `assets/template.html` to the output folder, fill every `{{…}}`, replace the EXAMPLE blocks with real content, delete what is unused.

Never overwrite or read existing files in the output folder unless the user says to. If `<exam>.html` already exists, choose a new name (e.g. `quiz1-guide.html`).

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

**Style override:** if the user names a style ("3b1b style") or pastes a style reference, it replaces the template's look. Map its tokens onto the template's CSS variables (canvas, surfaces, ink, fonts, radii, button shapes), and recolor the JS palette used by canvas/SVG demos too. Obey its color restrictions. Example: in the ElevenLabs reference, violet/orange appear only inside demos (the compared item, the pivot, the A/B halves) and never in text; emphasis becomes ink weight 500, and category tags become a neutral pill with a small colored dot. Don't add decorations that look clickable but do nothing (e.g. a play button on a hero sphere).

**Style rules** (default, already in the template — keep them unless overridden):

- Warm eggshell / taupe base, Inter, whisper-weight (300) headings, pill buttons, 20–24 px radii, hairline borders.
- Color is for meaning: chapter colors for regions, green/amber/red for exam-answer/key/trap, green→red for complexity. No decorative gradients beyond the hero sphere.
- Mobile: the template already scrolls wide math/tables inside their boxes and stacks grids.

### 5. Mock quizzes and cheat sheet

- 2 mock quizzes in the real exam format (same number of questions, same point weights, same wording style), answers inside `<details>`.
- A quick true/false set drawn from the traps.
- Cheat sheet: one complexity table, one classification table, the key formulas.

### 6. Hand off

Before handing off, load the page once and confirm the self-check badge passes and the KaTeX math rendered with no raw `$…$` left. Browser tools may block `file://`: serve the output folder with `python3 -m http.server <port>`, and stop the server when done.

Tell the user the file path, what each chapter contains, the list of demos/diagrams, what was verified by computer, and anything uncertain (e.g. formulas reconstructed from slide images). The user reviews the UI themselves and will report anything to change — do not run a screenshot/fix loop unless asked.
