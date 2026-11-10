# general-use-skills
Personal skills I use daily.

> **Heads up: this repo changes frequently.** These skills reflect my personal habits and workflows, and AI models keep improving. Skills may be modified, added, or retired at any time as my usage evolves and as models make some of them unnecessary.

## Skills

- **[intent-review](skills/intent-review/SKILL.md)** — Prepares code, a diff or a pull request for *your own* review. Instead of handing you a list of findings, it writes intent pages: every part is explained as problem / method / why, with the real source (exact line numbers, changed lines marked) in a dark code pane beside the text, and one button per topic jumps the pane to that topic's lines. It states behaviour and documented reasons but never judges, so you read the code and decide what is wrong. A bundled script ([build_page.py](skills/intent-review/scripts/build_page.py)) validates the fragments and builds the final HTML page. For pages about a database, a second script ([er_diagram.py](skills/intent-review/scripts/er_diagram.py)) draws one ER diagram of all the tables: key columns in the page, and every column with its type when you open it over the whole window. Use `/code-review` instead when you want the bugs found for you.
