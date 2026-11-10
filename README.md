# general-use-skills
Personal skills I use daily.

## Skills

- **[intent-review](skills/intent-review/SKILL.md)** — Prepares code, a diff or a pull request for *your own* review. Instead of handing you a list of findings, it writes intent pages: every part is explained as problem / method / why, with the real source (exact line numbers, changed lines marked) in a dark code pane beside the text, and one button per topic jumps the pane to that topic's lines. It states behaviour and documented reasons but never judges, so you read the code and decide what is wrong. A bundled script ([build_page.py](skills/intent-review/scripts/build_page.py)) validates the fragments and builds the final HTML page. Use `/code-review` instead when you want the bugs found for you.
