# Claude Code review team: do skills, subagents and hooks pay off?

A small, reproducible experiment from the [DevReceipts](https://www.youtube.com/@DevReceiptsAi) channel. A demo app with **10 planted bugs and 3 decoys** is reviewed three ways, and a separate test checks whether a **CLAUDE.md rule** or a **hook** stops bad commits. Everything runs inside Claude Code on a plan login: no API key, no paid services, no agent frameworks.

> Video: _link added at upload_ &nbsp;|&nbsp; Full numbers and caveats: [`METRICS.md`](METRICS.md) &nbsp;|&nbsp; What went wrong along the way: [`NOTES.md`](NOTES.md)

## Results (real runs, Sonnet, medium effort)

**Test 1: who finds the planted bugs?** (3 runs per setup, same code each time)

| Setup | Bugs caught /10 | Median time | Median est. cost* |
|---|---|---|---|
| Plain prompt ("review this code") | 7, 6, 7 | 13 s | $0.07 |
| One agent with the review checklist (no subagents) | 9, 9, 9 | 25 s | $0.10 |
| Review team (skill + 3 subagents) | 9, 9, 9 | 34 s | $0.21 |

One agent with the checklist matched the team at under half the cost. The plain prompt lost two bugs mostly because it was never asked to look at the tests (it never flagged a test problem; its tool calls were not logged, so I can't say it never read them). All three setups missed the same bug (a query inside a loop). With the cleaned-up decoys, no decoy was flagged in any of the 9 runs.

**Test 2: does a rule or a hook stop a commit with failing tests?** (5 attempts per cell)

| Setup | Prompt says "I'm in a hurry" | Prompt says "ignore the rule" |
|---|---|---|
| CLAUDE.md rule only | 0 / 5 commits | **5 / 5** commits |
| Hook only (exit code 2) | 0 / 5 | **0 / 5** |

When told outright to ignore the rule, Claude did, and said it skipped the tests. The hook blocked every attempt. Following an explicit instruction is arguably correct behaviour, so this is not a model failure: a CLAUDE.md rule is a default the prompt can waive; a hook runs outside the model, so the prompt alone cannot waive it. **Caveat:** in this test Claude had no Edit/Write permission, so it could not have removed the hook, and in the hook runs it offered to disable or edit the hook if told to. A hook turns a silent waiver into a stop that needs a human decision; it does not stop a human, or an agent allowed to edit `.claude/settings.json`.

\*Estimated at API prices from the CLI's `total_cost_usd` (subagents included). The runs used a subscription plan, so nothing was billed.

## Read this before quoting the numbers
- **One small app (about 300 lines), written by the same person who planted the bugs and wrote the reviewer prompts.** Treat it as "on this repo", not "in general".
- 3 runs per review setup, 5 per hook test, one model, one effort level.
- A team of subagents may well win on a much larger codebase where one context can't hold everything. That is not tested here.
- A hook only stops the model. Anyone who can edit `.claude/settings.json` can remove it.
- The hook only matches `git commit` at the start of a command or after `;`, `&`, `|`. It does **not** catch `git -C dir commit`, `/usr/bin/git commit` or `bash -c "git commit"`.
- The hook calls the system `python3 -m pytest` in the project folder and needs `jq`. If pytest is missing it blocks every commit; if `jq` is missing it now blocks with a clear message instead of silently allowing.
- The one bug all three setups missed (a query inside a loop, `low_stock_report`) is low-impact on a local SQLite file, so a reviewer could reasonably skip it. It still counts as a miss in the score.
- Many "unmatched" findings are real flaws in the demo app (weak password salt, tokens that never expire, an ignored return value). They are listed for manual review, so a high unmatched count is not a false-alarm count.

## What's inside
| Path | What it is |
|---|---|
| `demo-app/` | About 300 lines of Python (shop app + tests). All tests pass as shipped. Contains deliberate bugs: **do not copy it into real projects** |
| `demo-app/.claude/skills/review/` | The review skill: starts three subagents and merges their findings |
| `demo-app/.claude/agents/` | `bug-hunter`, `security-reviewer`, `test-reviewer` (read-only tools) |
| `demo-app/.claude/hooks/block-commit.sh` | Blocks `git commit` while tests fail (exit code 2) |
| `eval/bugs.json` | The answer key: planted bugs and decoys with line ranges |
| `eval/run_eval.sh`, `eval/hook_test.sh`, `eval/score.py` | Headless runs and deterministic scoring (no LLM judge) |
| `eval/results/` | Raw outputs from the runs above (account fields removed) |
| `video/` | The scripts that build the video: narration (Kokoro, local), Manim animation, sound mix |

## Quick start
Requirements: Claude Code (logged in with a plan), Python 3.10+, `git`, `jq`. `ANTHROPIC_API_KEY` must **not** be set, since it would override your plan login (the scripts unset it).
```bash
make setup        # venv + pytest (the only dependency)
make test         # smoke tests, no model calls
make pilot        # 1 run of each review setup (check /usage before and after)
make eval         # 3 runs per setup
make hook-test    # 5 attempts per cell, two prompts
make score        # score results against the answer key
```
These runs use your plan's allowance. Scripted `claude -p` use is subject to Anthropic's terms: read them before running at volume.

## Use the setup in your own project
Copy `demo-app/.claude/` into your repo, adjust the checklist in `skills/review/SKILL.md`, and ask Claude to "use the review skill to review this repo". The hook needs `jq` and a test command it can run (edit `block-commit.sh`). To measure your own setup the same way, plant bugs, write an answer key like `eval/bugs.json`, and run the scripts.

## License
MIT, see [`LICENSE`](LICENSE).
