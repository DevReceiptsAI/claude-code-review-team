# Asset: "Claude Code Review Team" starter pack

The one thing that comes out of this video for viewers to take away.

## What it is
A ready-to-copy `.claude/` setup plus the eval kit that measured it:
- `skills/review/SKILL.md`: the review checklist that starts three subagents and merges their findings
- `agents/`: bug-hunter, security-reviewer, test-reviewer (read-only tools, Sonnet)
- `hooks/block-commit.sh` + `settings.json`: blocks `git commit` while tests fail (exit code 2)
- The eval kit: `bugs.json` answer-key format, `score.py`, `run_eval.sh`, `hook_test.sh`, so people can test their own setup the same way

## Who it is for
Anyone using Claude Code who wants a working starting point and a fair way to check whether their own skills, subagents or hooks are worth it.

## How people use it (README steps)
1. Copy the `.claude/` folder into your project.
2. Run the tests so the hook has something to enforce.
3. Ask Claude to "use the review skill to review this repo".
4. To measure a setup of your own: plant bugs, write the answer key, run `make eval`.

## What it is NOT
- Not a guarantee that a team beats a plain prompt. The video shows the numbers on this one app. `TODO: measure`
- Not tuned for large codebases.

## How to offer it
- **Free, in exchange for an email,** to start a list. Do not sell on day one to a tiny audience.
- **Later paid versions:** a bigger CLAUDE.md pack, more hooks (secrets scanner, test gate), a ready-made eval for other tasks. Price only after you see what people ask for.
- Keep the repo MIT-licensed so the free part stays free; sell the extras and the time-saving, not the basics.

## To do before publishing
- [ ] Put your name in LICENSE
- [ ] Strip the demo-app bugs from what viewers copy, or clearly label the demo app as "for testing only"
- [ ] Add the verified results to README
- [ ] Decide the free signup place (check its terms and pricing)
