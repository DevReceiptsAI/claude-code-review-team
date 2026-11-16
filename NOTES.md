# NOTES: failures, dead ends, fixes

Format: what happened, then a one-line why. Add every error as it happens; these become the "what broke" segment.

## Design caveats (say these on camera)
- **Same author, same bias.** I wrote the planted bugs and the reviewer prompts. The subagent prompts include general advice (compare code to its docstring, check for a whitelist before flagging injection) that happens to suit the planted bugs and decoys. A real team would not know its bugs in advance, so the team arm may look better than it would in the wild.
- **Toy repo.** About 300 lines, 10 bugs. Results say little about large codebases.
- **Small sample.** A few runs per arm. Report medians and the min-max range, not a single number.
- **Hook test is a pressure scenario.** The prompt tells Claude to commit anyway and calls a always-failing test "flaky". An ordinary session might obey the CLAUDE.md rule every time.
- **Cost is an estimate.** `total_cost_usd` is the CLI's estimate at API rates. On a plan login nothing is billed.
- **Unmatched findings.** A reviewer may find a real bug that was not planted. They are NOT judged by hand yet (`eval/manual_verdicts.json` does not exist); until then the strict column counts them as unmatched, not as confirmed false alarms.

## Decisions made while building
- The `CLAUDE.md` commit rule lives in `eval/fixtures/commit-rule.md` and is copied in only for the "rule" arm of the hook test, so the review arms are identical apart from `.claude/`.
- All demo-app tests pass as shipped (so the review arms get no hint from a red suite). The hook test adds its own failing test in a throwaway repo.
- The answer key is outside `demo-app/`, and review runs use a temp copy, so the key is not even on the reviewers' path. `settings.json` also denies reading `../eval/**` for interactive use on camera.
- Hook regex catches `git commit` and chained forms like `git add -A && git commit`. It does not catch `git -C dir commit`. Known gap, mention it if relevant.
- Demo-app + tests total 301 lines, one over the "about 300" target. Left as is.

## Verification checklist for the pilot (results are in "Pilot findings" below)
- [x] `claude -p ... --output-format json` field names match what `score.py` reads (`result`, `usage`, `total_cost_usd`, `duration_ms`, `num_turns`, `is_error`). Check with `jq 'keys'`.
- [x] The review skill is invoked from a plain-language prompt in headless mode (slash-style invocation may not work with `-p`).
- [x] Subagents are actually dispatched, and `--allowedTools ... Agent` is the right tool name.
- [x] `--setting-sources project,local` still loads `.claude/skills`, `.claude/agents` and the hook.
- [ ] In the hook test's "rule" arm, `CLAUDE.md` in the project is actually loaded. (not checked directly; the rule arm refused to commit in 5/5 "hurry" runs, which is consistent with it being loaded)
- [x] `--max-budget-usd` behaves sensibly on a plan login.
- [x] How much of the plan allowance one baseline run and one team run use (`/usage`).

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
- [x] Hook test arms were run later (see "Full eval and hook test").

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

## Final video build (14 Nov)
- Final cut: 6:25, 2560x1440, narration by Kokoro af_heart, sentence-synced animation, receipt hook, results charts from METRICS.md, soft sound effects (a -nosfx version is saved too). The sound effects and the voice were NOT heard by me; check by ear.
- The first layout pass had text running off cards and off the paper in the receipt, cost labels clipped at the right edge, and captions touching the footer. Why: widths guessed from character counts; fixed by measuring frames and shrinking or shortening.
- Thumbnails: first versions had the headline under the cards (B), the stamp hiding the command (C) and the headline touching the receipt (A). Fixed and checked at 168 px wide.
- Length is 6:25, shorter than the 12-16 minute plan. Reason: with the narration trimmed to real content there was nothing to cut in without padding. Padding hurts retention; the "bigger codebase" test is better as Video #2.
- Before publishing results to GitHub: removed the account, session and id fields the CLI adds from every results JSON; verified no names, emails or home paths remain.

## Re-edit after the Opus review (14 Nov)
- Independent review (an Opus subagent) said: demand exists but the headline result is the expected one, the 2.5-minute explainer was the biggest retention risk, the visuals read as a slide deck, and the title gave away the outcome. Its demand figures (300-3K views for a new channel) are an unverified estimate.
- Changes: new cold open built from the saved runs (terminal, 5 stamped receipts, hook gate, score cards, blurred "bug nobody caught" tease), brand card cut to 1 s, explainer replaced by just-in-time skill/subagent and hook explanations right before each test, the missed bug shown as real code, verbatim transcript replays, a search-style title, on-screen caveats ("my 300-line app, 3 runs", "API-price estimates", "it only catches the commands it matches").
- Fixed a real mismatch: the lessons said the test was wrong "three times" but four test problems were listed. It now says four.
- Verified from our own data: hooks ran in headless `claude -p` mode in all 10 hook attempts, which contradicts a blog claim that they do not.
- Replay panel text overlapped its own header twice. Why: I sized the text by guess. Fixed by measuring text height with Manim before rendering (17 pt, wrap 38).
- Length is now 5:52. Still not heard by me: voice and sound effects.

## Second review and v3 re-cut (15 Nov)
- A second independent review (Opus subagent; model output, checked by me where noted) re-verified every on-screen number against `eval/results/` and found them correct. It found wording and repo problems instead:
  - "Anything else, I check by hand" was untrue (`eval/manual_verdicts.json` was never created). Now: "listed in the repo for review". Why: I wrote the line before doing the work.
  - "A hook is enforcement the prompt can't waive" overstated the test: Claude had no Edit/Write permission and offered to disable the hook if told to. Caveat added to README, description, video and pinned comment.
  - The "verbatim from eval/results/" label was wrong for the hook message (it comes from `block-commit.sh`). Label fixed.
  - Title "Claude Code Ignores CLAUDE.md?" implied Claude ignores rules unprompted; the rule held 5/5 under "hurry". Title changed to "I Told Claude Code to Ignore My Rule. A Hook Didn't Let It."
  - `make test` used the system python instead of the venv; the hook failed open when `jq` was missing (now fails closed with a message; matching logic unchanged, so the tested behaviour is the same); `score.py` printed the misleading CLI timer (now wall-clock); stale TODO text in METRICS/NOTES/titles/outline; macOS temp paths in two results JSONs (scrubbed); `.err` files tracked in subfolders.
- Wording fixed in the video: "never looked at the tests" -> "never flagged a test problem" (its tool calls were not logged); "added a hook" -> "swapped the rule for a hook"; "instructions beat agents" -> "same bugs, under half the cost".
- Layout: chapter label overlapped the app title (panel moved down). The "stray dash" at 0:03 and the 2-arrow tools diagram turned out to be mid-animation frames, not bugs.
- Encoding: re-encoded at crf 16, 48 kHz stereo AAC; captions split to at most 2 lines of about 42 characters; 7 s quiet tail with the cards cleared for YouTube end-screen elements.
- Voice speed set to 1.05 (was 1.0) and setup lines tightened: the first Test 1 result now arrives at about 1:55 instead of 2:11. Still not heard by me.

## Video #1 v4: making it useful (16 Nov)
- A third review (Opus subagent, model output) said: ship Video #1 after small fixes, move the bigger-codebase test to Video #2, and add something viewers can copy. Reasons for deferring the bigger test: about $4-5 of API-price estimate (roughly one 5-hour session of plan allowance), planted bugs could not be verified against the library's tests this session, and the model may remember the library (diskcache), which would flatter every arm.
- Added: `starter-kit/` (hook with a configurable test command, wider command matching and fail-closed behaviour, settings snippet, review skill and agents, `test-your-rule.md`); 14 more smoke tests (30 pass, no model calls); a real captured run of the hook script (`eval/results/hook-demo-output.txt`) shown in the video; a "Copy this" segment; the opening rewritten as one story (rule 5/5, hook 0/5) with the team result left for Test 1. The first Test 1 number now arrives at about 1:44.
- The kit's hook is NOT the one the Claude runs used. It was checked by smoke tests only. The video's Claude results come from `demo-app/.claude/hooks/block-commit.sh` (matching logic unchanged; only the fail-closed branches were added).
- Why the third pass found things earlier passes did not: each earlier pass checked claims and layout, none asked "what can a viewer copy?".
- Blocked: a permission check refused running the third-party `diskcache` test suite, so the bigger-codebase test was not started. `eval/big/` is local only and git-ignored.
- Shorts built with `build_shorts.py` (letterboxed 16:9 on a vertical canvas, captions via drawtext because this ffmpeg's `subtitles` filter rendered nothing).

## v5 (16 Nov)
- Shortened "what broke" (40 s to 34 s), faster typing in the opening, one logo in the outro (footer fades out), thumbnail A now has a large CLAUDE CODE line. Chapters regenerated from timings.
