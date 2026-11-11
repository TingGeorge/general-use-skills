---
name: intent-review
description: Prepare code, a diff or a pull request for the user's own review as intent pages. Each page explains every part as problem / method / why with the real source beside it in a dark code pane (changed lines marked for diffs), and gives no findings, so the user reads and judges the code themselves and asks questions as they go. Use this whenever the user wants to review, read through, walk through or understand code, a module, a branch, a diff, a commit range or a PR themselves, says things like "help me review this PR", "I want to review what the agents wrote", "make review pages", "intent review", or asks for the review style with the code sidebar. Do not use it when the user wants you to find the bugs for them (that is /code-review).
---

# Intent review

The user reviews the code. You prepare the reading material and then answer their questions.

A normal review hands the user a list of findings, and they end up reviewing the list. Here they get pages that say, for each part of the code, what problem it solves, how, and why it was done that way, with the full source files in a pane beside the text. One button per topic moves the pane to that topic's lines. The user reads, compares the stated intent with the code, and decides what is wrong. This is slower for them and that is the point: they come out knowing the code.

So the two rules that shape everything:

- **The pages state behaviour and documented reasons. They do not judge, advise or list problems.**
- **Every claim on a page comes from code or documents you actually read, with exact line numbers.** The user will check them against the pane, and one wrong line number costs their trust in the rest.

## 1. Pin down what is being reviewed

Work out the target and never change the user's checkout to read it.

| The user points at | Sources come from | Compare against |
|---|---|---|
| a folder, module or feature | `HEAD` (or the working tree if it has uncommitted work they mean) | nothing: a plain page |
| uncommitted changes | the working tree (no `--rev`) | `--base HEAD` |
| a branch | `--rev <tip>` | `--base $(git merge-base <main> <tip>)` |
| commits A to B, both included | `--rev B` | `--base A~1` |
| a PR | `gh pr view N --json title,body,baseRefName,headRefOid,commits,files`, then `git fetch origin pull/N/head`; `--rev <headRefOid>` | `--base $(git merge-base origin/<baseRefName> <headRefOid>)` |

If the target is unclear (which branch, since when), ask before reading a lot of code. In zsh write `git show "${REV}:path"` with the braces; `$REV:a...` is read as a modifier and breaks the path.

Then find the written intent, because the "why" on a page may only come from written sources: specs and PRDs, ADRs or design docs, the PR description, commit messages (`git log base..rev`), linked issues, code comments. Note the language the project's documents are written in; the pages use that language.

## 2. Plan the pages and show the plan

One page holds 3 to 6 topics and the files they need. A small diff or PR is one page. A subsystem or a large PR is several pages, split by purpose (for a PR: by intent of the change; for a codebase: by the parts of the system), so that each page can be read in one sitting.

When there is more than one page, show the user the list first: page title, what it covers, the main files, and the order to read them in. Start writing after they agree. For a single page, say in one line what it will cover and go on.

Pages are files in the repository so the user can keep them. Use the folder the project already has for such pages; if there is none, create `docs/code_review/` and name it in the hand-over, with no need to wait for an answer. File names: `Topic_Name.html` for plain pages, `PR_123_Topic.html` or `Diff_<base>_<rev>_Topic.html` for changes, where base and rev are the short hashes from `git rev-parse --short`. Do not commit them unless asked.

## 3. Write each page

Read `references/writing.md` first; it has the fragment layout, the content rules and the diagram markup. Then, per page:

1. Read the code of the page completely, the tests that exercise it, and the documents found in step 1.
2. Choose the topics from how the code is organised around purposes.
3. Write the fragment to a scratch file (not into the repo). A page about code starts with a function map, and a page about a database schema with an ER diagram; both are drawn by scripts in this skill (see `references/writing.md`).
4. Build it:

       python3 -I <skill>/scripts/build_page.py <fragment> --out <repo>/<folder>/<Page>.html --repo <repo> [--rev REV] [--base BASE] --lang <zh-TW|en>

   `--lang` sets the pane's button labels; use `zh-TW` for a Traditional Chinese project and `en` otherwise. The builder fails on broken structure, bad line ranges, and (with `--base`) changed files that are neither embedded nor listed as skipped. It warns about changed lines no topic points at. Fix and rerun until it prints OK and every warning is either covered by a topic or listed in the page's "other changes" table.

With several pages, write them in parallel with subagents, one page each. A subagent starts with nothing, so its brief needs: the target (repo, rev, base), the page's title and scope, the other pages' titles (so it knows what is out of scope), where the specs and decisions are, the path to `references/writing.md` and the example fragment, the exact build command, and an instruction to write only its fragment and page file. Follow the user's own preferences for subagent models if they have any.

## 4. Check before the user sees it

The user will hold every sentence against the code, so check the pages the same way first.

- **Claims.** Reread each page against the code, claim by claim. A single small page you can reread yourself. For several pages, or a page with more than a few topics, have a fresh subagent do it, since the writer tends to read what they meant and not what they wrote: give it the page's fragment and the repo, ask it to verify every line reference and every statement about behaviour and every "why" against its cited source, and to report only what is wrong. Fix what it finds and rebuild.
- **Rendering.** Open one page in a browser. Check that a topic button moves the pane to the right lines, that a `file:line` ref works, that diagrams have no overlapping text, and on a diff page that added and removed lines are marked. The shell is the same for every page, so one page is enough for the pane; diagrams differ per page, so look at each page's figures.

## 5. Hand over

Show each page the way this environment shows artifacts (publish it as a private artifact, or follow the user's own rule for where artifacts go). When a page is rebuilt later, update the same artifact so its link stays the same.

Tell the user, briefly: the pages and their reading order, what each covers, every place where a reason was not documented, and anything you could not determine. Do not add your opinion of the code.

## 6. While the user reviews

The user reads and asks, in chat or in comments on the page. Your part:

- Answer what they ask, simply and from the code, with `file:line`. If the answer needs a concept they may not know, explain it in a few words.
- Do not volunteer findings, and do not hint. If they ask you directly whether something is a bug or what you think, answer honestly and completely: the rule is about not leading, not about hiding.
- When they find a real problem, it is theirs: note it the way they want (a list, an issue, a PR comment) in their words. Fix code only when they ask.
- When the code changes, or they point out a page is wrong or unclear, fix the fragment, rebuild, and update the same artifact.

## Files in this skill

- `scripts/build_page.py`: checks a fragment and builds the page. `--selfcheck` runs its own test.
- `scripts/fn_map.py`: a small library for the function map each code page starts with (files, functions, calls); it refuses crossing lines and arrows not backed by a line of code (see "Function map" in `references/writing.md`). `--selfcheck` runs its own test.
- `scripts/er_diagram.py`: draws the ER diagram for a page about a database schema from a JSON spec (see "ER diagram" in `references/writing.md`). `--selfcheck` runs its own test.
- `assets/shell.html`: styles, the code pane (dark, wrap toggle, adjustable width, diff marks), the open-in-window button for `figure.zoom`, and its script. Highlighting follows the file extension. Change the look here, then rebuild pages.
- `references/writing.md`: how to write a fragment. Read before writing; give its path to page-writing subagents.
- `references/example_fragment.html`: a finished fragment to copy structure and diagram markup from.
