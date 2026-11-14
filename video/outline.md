# Outline: Video #1 (talking points, not a script)

Working title: "Do Claude Code subagents and hooks actually help? I measured it." (final title waits for the results, see titles.md)
Target length: 12-16 minutes. Cut hard. Judge by the retention graph, not the clock.
Rule: any number below is `TODO: measure` until it comes from METRICS.md.

## 0:00 Hook (under 15 s): result first
The results exist now (see METRICS.md). B and C are both true; the strongest hook is probably C, with B as the second beat.
- **A: the team clearly wins.** Scoreboard slams in: plain prompt X/10, team Y/10. One line on cost.
- **B: flat or the checklist matches the team.** "I built a team of three AI reviewers. One agent with the same checklist found about the same bugs for less." (only if true)
- **C: the hook test is the story (real numbers now).** "I told Claude never to commit with failing tests. Then I told it to ignore that rule." Rule: 5 of 5 commits went through. Hook: 0 of 5.
Visual: receipt prints out the numbers line by line (signature visual).

## 0:15 Brand card (about 4 s)
"DevReceipts. Real builds. Real numbers." No "welcome back", no channel history.

## 0:20 Preview + open loop
What we test, and one honest tease: the part that broke (see "What broke").

## Context (under 60 s)
- What Claude Code is, in one sentence, for a newcomer.
- Skills, subagents, hooks in plain words (already animated in the draft cut, v3).
- Skills/subagents = judgment. Hooks = rules.

## The test app
- Small shop app, ~300 lines, 10 planted bugs in 4 types, 3 decoys.
- Show one real bug (the `>` vs `>=` discount) and one decoy as code.

## Test 1: plain prompt vs checklist vs team
- Three arms. Why three: the checklist arm separates "better instructions" from "a team".
- Same model, same effort, same code, fresh copy each run, 3 runs each.
- Results (3 runs each): plain prompt 7, 6, 7 of 10; checklist 9, 9, 9; team 9, 9, 9. Median cost about $0.07 / $0.10 / $0.21, median time about 13 / 25 / 34 s (API-rate estimates).
- Every arm always missed the query-in-a-loop bug. The plain prompt also never reviewed the tests.
- Headline: the checklist matched the team at under half the cost, so for this task the instructions mattered more than the subagents.

## Test 2: CLAUDE.md rule vs hook
- Failing test + a prompt that says we are in a hurry. 5 attempts per setup.
- Two pressure levels: "hurry" (rule held, 0 of 5 commits) and an explicit "override" (rule gave way, 5 of 5 commits; hook still 0 of 5).
- Say plainly that this is a pressure scenario, that following an explicit override is arguably correct, and that a hook only enforces against the model.

## What broke (real, already logged in NOTES.md)
- My "clean" decoys were not clean: the reviewers flagged real problems I had not planted (negative prices, a missing database column).
- Many "unmatched" findings were real flaws in my own demo app (the salt is the username, tokens never expire).
- The CLI reported 10.5 s for the team run while real elapsed time was about 31 s: it leaves out subagent time.
- The first comparison was unfair: the plain prompt never mentioned tests, so it skipped them. That is why there is a third arm.
- My first hook test was invalid: Claude could not run the tests because of a permission mismatch (`python` vs `python3`), so it refused to commit for the wrong reason. Rerun with fixed permissions and a second, explicit-override prompt.
Each of these changed how the test is scored. Tell it as it happened.

## Lessons (fill from results and your own opinion)
- When to use a skill/subagents, when a plain prompt or checklist is enough. `TODO: your take`
- When a hook is the right tool.
- What I would change next time.

## CTA
- Starter pack (the `.claude/` folder and the eval kit): link in description. `TODO: link`
- Next video tease. `TODO`
- No "like and subscribe" before the first payoff.
