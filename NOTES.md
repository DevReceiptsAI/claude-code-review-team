# NOTES: failures, dead ends, fixes

Format: what happened, then a one-line why. Add every error as it happens; these become the "what broke" segment.

## Build log
_No failures recorded yet. Entries are added as they occur._

## Design caveats (say these on camera)
- **Same author, same bias.** I wrote the planted bugs and the reviewer prompts. The subagent prompts include general advice (compare code to its docstring, check for a whitelist before flagging injection) that happens to suit the planted bugs and decoys. A real team would not know its bugs in advance, so the team arm may look better than it would in the wild.
- **Toy repo.** About 300 lines, 10 bugs. Results say little about large codebases.
- **Small sample.** A few runs per arm. Report medians and the min-max range, not a single number.
- **Hook test is a pressure scenario.** The prompt tells Claude to commit anyway and calls a always-failing test "flaky". An ordinary session might obey the CLAUDE.md rule every time.
- **Cost is an estimate.** `total_cost_usd` is the CLI's estimate at API rates. On a plan login nothing is billed.
- **Unmatched findings.** A reviewer may find a real bug that was not planted. Those are judged by hand in `eval/manual_verdicts.json`, otherwise they count as false alarms in the strict column.

## Decisions made while building
- The `CLAUDE.md` commit rule lives in `eval/fixtures/commit-rule.md` and is copied in only for the "rule" arm of the hook test, so the review arms are identical apart from `.claude/`.
- All demo-app tests pass as shipped (so the review arms get no hint from a red suite). The hook test adds its own failing test in a throwaway repo.
- The answer key is outside `demo-app/`, and review runs use a temp copy, so the key is not even on the reviewers' path. `settings.json` also denies reading `../eval/**` for interactive use on camera.
- Hook regex catches `git commit` and chained forms like `git add -A && git commit`. It does not catch `git -C dir commit`. Known gap, mention it if relevant.
- Demo-app + tests total 301 lines, one over the "about 300" target. Left as is.

## To verify in the pilot (not yet confirmed against the real CLI)
- [ ] `claude -p ... --output-format json` field names match what `score.py` reads (`result`, `usage`, `total_cost_usd`, `duration_ms`, `num_turns`, `is_error`). Check with `jq 'keys'`.
- [ ] The review skill is invoked from a plain-language prompt in headless mode (slash-style invocation may not work with `-p`).
- [ ] Subagents are actually dispatched, and `--allowedTools ... Agent` is the right tool name.
- [ ] `--setting-sources project,local` still loads `.claude/skills`, `.claude/agents` and the hook.
- [ ] In the hook test's "rule" arm, `CLAUDE.md` in the project is actually loaded.
- [ ] `--max-budget-usd` behaves sensibly on a plan login.
- [ ] How much of the plan allowance one baseline run and one team run use (`/usage`).

## Video build log (draft cut, 12 Nov)
- Decoy legend text ran off the right edge of the frame. Why: label was too wide for the 14.2-unit frame; shortened it.
- Three arrowheads piled up at the "merged findings" box. Why: all three arrows aimed at one point; now each aims at a different height on the box edge.
- "a script, not a judgment" overlapped the DevReceipts footer in the rule-vs-hook slide. Why: content sat too low; moved the flow up.
- Draft cut has NO measured results. The results segment is a silent slate that says TODO: measure.
- Voice: Kokoro (kokoro-onnx 0.6.1, voice af_heart), free and local. I could not listen to it, so voice quality is unchecked; six samples are in the draft folder for you to choose.
- Captions (.srt) split each segment's text by sentence, timed proportionally to length. Timings are approximate, not word-aligned.
- Audio normalised to -14 LUFS with ffmpeg loudnorm (a common YouTube target; not verified against YouTube docs).

## Video draft v2 (12 Nov): added intro and explanations
- v1 was too short (77 s) and skipped the basics. Why: I scoped it as a design recap, not a video a newcomer can follow. v2 adds the hook, intro, and plain explanations of skills, subagents and hooks, plus one planted bug and one decoy shown as real code (3.5 min).
- Intro bullets overflowed the terminal box and covered the caption. Why: panel was too short for its content; made it taller.
- Subagent panel text ran past its border, and "exit 0/2" labels sat on top of arrows. Why: text wider than the panel, labels placed on the arrow path; shortened text and moved labels.
- Narration is now synthesised one sentence at a time, so each visual appears when its sentence is spoken and the captions are sentence-accurate.
- Still no measured results. Results, what broke, lessons and CTA segments are TODO until the pilot and full run.

## Video draft v3 (12 Nov): motion pass
- Research (creator blogs, mostly vendor content; weak evidence): skip long branded intros, show mechanisms not decoration, use easing and soft sound, keep captions plain. See channel/video-playbook.md section 8.
- Added: ease-out-back pops, data packets along arrows, typed code, flash emphasis, drifting background, chapter progress bar, wipe transitions, kinetic hook line, soft sound effects (separate file, mix_sfx.py).
- Chapter label ("4/5 THE TWO TESTS") touched the "Test 1" tag and the "Instruction" heading. Why: both sat at the same height near the top-left; moved the tag and headings down.
- Sound effects are synthesised locally (pop, whoosh, ping) at low gain. I could NOT listen to them, so they are unchecked. A version without them is saved as -nosfx.
- No music added. If you add one: YouTube Audio Library, 10-20 dB under the voice, check the licence.
- Render time: about 2 minutes at 1440p. The background and progress bar are animated every frame, so this is slower than v2.

## Pilot findings (12 Nov, real run)
Confirmed against the real CLI:
- [x] JSON fields match what score.py reads: result, usage, total_cost_usd, duration_ms, num_turns, is_error, subtype (plus modelUsage, subagent_stats).
- [x] The review skill is triggered by a plain-language prompt in headless mode, and all 3 subagents ran (subagent_stats: bug-hunter, security-reviewer, test-reviewer, 0 failed).
- [x] `--allowedTools ... Agent` is the right tool name, and `--setting-sources project,local` still loads the project skill and agents.
- [x] `--max-budget-usd 1.5` was accepted on a plan login; nothing hit the cap.
- [ ] Hook test arms not run yet. CLAUDE.md loading in the "rule" arm still unconfirmed.

Problems found (these are the "what broke" segment):
- **The decoys are not clean.** The reviewers flagged D2 (`format_price`, negative cents prints "$-2.50") and D3 (`count_by_status` reads `order["status"]` but the orders table has no status column). Both are real problems I did not intend. Why: I wrote realistic code and assumed my decoys were flawless; they were only "fine for the intended use". Decoy hits are therefore not reliable false alarms. Fix before the full run: replace D2 and D3 with truly correct code, or remove them and say so.
- **Many "unmatched" findings are real.** Examples both arms raised: the PBKDF2 salt is the username, the token never expires, `place_order` ignores `reserve`'s result, the tests miss real paths. Why: the demo app has real flaws I did not plant. Counting every unmatched finding as a false alarm unfairly punishes the team (11 unmatched vs 5). The manual review (eval/manual_verdicts.json) matters more than the strict column.
- **`duration_ms` is misleading for the team arm.** It reported 10.5 s while real elapsed time was about 31 s. Why: it does not include subagent time. Fix: wall-clock is now recorded per run.
- **Unfair baseline.** The plain prompt ("Review this code for problems") never mentions tests, so T1 and T2 were never in scope. The team has a test-reviewer. Proposed fix: add a third arm "checklist": one agent, no subagents, given the same checklist text as the skill (including tests). That separates "better instructions" from "a team".
- The prompts told both arms to use the same output format, and both followed it.

Open question for the video: if the checklist-only arm matches the team at a lower cost, the honest headline is "you may not need subagents".

## Full eval and hook test (13 Nov)
- **The first hook test was invalid.** The rule arm showed 5/5 "blocked", but Claude never reached the commit step. Why: my allowlist had `python3 -m pytest` while Claude ran `python -m pytest`, which was denied in headless mode; unable to run the tests, it refused to commit under the CLAUDE.md rule. That result said nothing about the rule holding under pressure. Fix: allow every spelling, rerun, and archive the invalid run in eval/results/hook-v1/.
- Added a second prompt, "explicit override", because "in a hurry" never actually told Claude to ignore the rule. With it the contrast between a rule and a hook shows up clearly (rule 5/5 landed, hook 0/5).
- Two "hurry / rule" runs had a compound command with a subshell, `ls && (python -m pytest ...)`, denied by the allowlist; Claude re-ran the tests another way and still saw the failure. Minor, but it shows allowlist patterns do not match every shape of command.
- In the hook arm each run records one "permission denial": that is the hook blocking the commit, not a permission problem.
- Review eval: with the cleaned decoys, 0 decoys were flagged in 9 runs. All three arms always missed P1 (a query inside a loop). The checklist arm matched the team's 9/10 at less than half the cost.
- Everything above is one small demo app, written by me, 3 runs per review arm and 5 per hook cell.
