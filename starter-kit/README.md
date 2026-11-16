# Starter kit: a commit hook that holds, a review checklist, and a way to test your own rules

From the [DevReceipts](https://www.youtube.com/@DevReceiptsAi) video "I Told Claude Code to Ignore My Rule. A Hook Didn't Let It."

| File | What it does |
|---|---|
| `hooks/block-commit.sh` | PreToolUse hook: runs your tests before any `git commit` and blocks the commit (exit code 2) if they fail |
| `settings.snippet.json` | the `.claude/settings.json` entry that turns the hook on |
| `skills/review/SKILL.md` | the review checklist (also works as one agent without subagents: in the video's test it matched the 3-agent team at under half the cost) |
| `agents/*.md` | bug-hunter, security-reviewer, test-reviewer (read-only), used by the skill |
| `test-your-rule.md` | the 5-minute recipe to test whether your own rule or hook holds |

## Install (3 steps)
1. Copy `hooks/` to `.claude/hooks/` in your project, and `skills/` and `agents/` to `.claude/skills/` and `.claude/agents/` (skip agents if you only want the checklist).
2. Merge `settings.snippet.json` into `.claude/settings.json`. Set `TEST_CMD` in the script (default `python3 -m pytest -q`). Needs `jq`.
3. `chmod +x .claude/hooks/block-commit.sh`, then run the free check in `test-your-rule.md`.

## Rule of thumb from the video's test (one small app, 3 runs per setup; not a law)
Write the checklist first. Add subagents only if one context cannot hold your code. If a rule must never be broken, put it in a hook, not a sentence.

## Honest limits
The hook only stops the model, not a person, and anyone who can edit `.claude/settings.json` can remove it. This version of the hook was checked with `tests/test_smoke.py` (no model calls); the video's Claude runs used the simpler `demo-app/.claude/hooks/block-commit.sh`.
MIT licensed, no warranty.
