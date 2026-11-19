# general-use-agent-settings
Personal skills I use daily.

> **Heads up: this repo changes frequently.** These skills reflect my personal habits and workflows, and AI models keep improving. Skills may be modified, added, or retired at any time as my usage evolves and as models make some of them unnecessary.

## Skills

- **[intent-review](skills/intent-review/SKILL.md)** — Prepares code, a diff or a pull request for *your own* review. Instead of handing you a list of findings, it writes intent pages: every part is explained as problem / method / why, with the real source (exact line numbers, changed lines marked) in a dark code pane beside the text, and one button per topic jumps the pane to that topic's lines. It states behaviour and documented reasons but never judges, so you read the code and decide what is wrong. A bundled script ([build_page.py](skills/intent-review/scripts/build_page.py)) validates the fragments and builds the final HTML page. Each code page starts with a function map (files, functions and the calls between them), drawn with [fn_map.py](skills/intent-review/scripts/fn_map.py), which refuses crossing lines and any arrow not backed by a line of code. For pages about a database, another script ([er_diagram.py](skills/intent-review/scripts/er_diagram.py)) draws one ER diagram of all the tables: key columns in the page, and every column with its type when you open it over the whole window. Use `/code-review` instead when you want the bugs found for you.

## Rules

Global instructions Claude Code loads in every project. To use one, copy it into `~/.claude/rules/`.

- **[ponytail](rules/ponytail.md)** — Lazy senior dev mode: check whether code needs to be written at all, then reach for the standard library, platform features and installed dependencies before writing the minimum that works.
- **[clean-code](rules/clean-code.md)** — How code should read top to bottom: names, function size and order, blank lines, comments, error handling, tests, plus notes for Python, TypeScript, Bun and C/C++.
- **[Karpathy](rules/Karpathy.md)** — Think before coding, keep it simple, change only what the task needs, and define a check that proves the work is done.
- **[Trash_rm](rules/Trash_rm.md)** — Delete files only with the macOS `trash` command after you approve the paths; never `rm`.
- **[artifact-style](rules/artifact-style.md)** — How artifact pages and diagrams look: pictures before text, a calm light theme, no animation, readable at phone width.
