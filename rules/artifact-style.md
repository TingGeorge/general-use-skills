# Artifact and diagram style

How I want any artifact page or diagram made, in every project and for every kind of content
(plans, explanations, reports, reviews, study notes). This rule covers how a page looks and how it is
built. A project's own instructions win when they conflict with this file.

## Pictures first, very little text

- I read pictures first and get lost in long text. Show an idea as a picture whenever it can be one:
  a diagram, chart, table, timeline, or before/after comparison.
- Per topic: one lead sentence, one picture, then a few short rows of text. No long paragraphs.
- Cut text; do not just fold it away.
- Start the page with the overview: what this page is about and where things stand.

## Look

- 3Blue1Brown-like: calm, clean, a few strong colours on a light background.
- Light theme only, even when the device is in dark mode: set `color-scheme: light`, give `body` an
  explicit light background, and add no dark-mode tokens.
- Static: no animation.
- Page text in the language I am using in the conversation (Traditional Chinese when it is Chinese),
  in plain everyday words. Labels inside diagrams are short English.
- Works at phone width with no horizontal page scroll. A wide picture sits in its own scrolling box.
- Pictures at a normal size, not huge: a diagram should fit in one screen without scrolling on a
  laptop. Cap its width instead of letting it stretch to the page width, and keep its minimum width
  small (about 600px) so it does not force a big sideways scroll.
- Not tiny either: pick the cap per picture so the text inside it shows at about the same size as the
  page's body text. A big diagram needs a cap around 700–820px; a small one drawn at 640px may need to
  be shown larger than it was drawn.
- Text must never be squeezed: no fixed narrow widths for labels or table columns.

## Diagrams

- One idea per diagram. Keep it simple enough to read at a glance.
- Avoid crossing arrows. If they would cross, split the idea into two diagrams.
- Leave out detail that is not needed to understand the idea; put it in the text or leave it for later.
- Not too simple either: do not simplify so far that things which really exist disappear.
- To show that some blocks share something (same group, same source, same kind), draw a frame around
  the existing blocks and label it. Add separate boxes or a second diagram for it only when that is
  really necessary; extra boxes make it look like there are more things than there are.
- Leave air: clear gaps between neighbouring boxes and padding around the text inside each box.
- Saved Excalidraw files use these settings: Sloppiness = Architect (the first option,
  `roughness: 0`) and Font family = Code (the `</>` option, `fontFamily: 8`).
- Diagrams drawn inline in the chat use Sloppiness = Architect too, but leave the font at the tool's
  default: asking the inline tool for another font cuts the text off at both ends.
- Explain every part. Each block gets a short note next to or under the diagram: what it is, what it
  does, one example. Where it helps, clicking a block jumps to its note.

## Discussing and saving

- While we are discussing, show pictures inline in the chat when the app can render them, rather than
  in a separate app or a file I have to go and open.
- When something is worth keeping, save it as an HTML page I can read directly.
- A diagram drawn with Excalidraw is also saved as its `.excalidraw` file, in an `excalidraw/` folder
  beside the page. Other kinds of pictures (charts, tables, SVG drawn straight into the page) need no
  separate file.

## How pages are built

- Pages are built by a subagent: Opus, effort medium. Brief it with these rules and the exact content.
- Before handing a page over, open it in a browser and check the whole page. Say plainly what was not
  checked.
