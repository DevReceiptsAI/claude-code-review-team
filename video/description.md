# Upload package: Video #1 (copy each block into YouTube Studio)

## Title (recommended: 1; it is literally what happened and matches thumbnail A)
1. I Told Claude Code to Ignore My Rule. A Hook Didn't Let It.   (main)
2. AI Coding Rules Can Be Ignored. Here's What Actually Works   (wider-audience alternative; true: the rule gave way when told to be ignored)
3. Stop AI From Committing Broken Code (I Tested It 20 Times)   (benefit-first alternative; 20 = the hook-test attempts)
4. I Tested Claude Code Subagents. A Checklist Tied Them.   (pair with thumbnail B; Test 1 angle)

Thumbnails (in `thumbnails/`): A "ignore the rule" (main, matches title 1), D "AI commits broken code" (broader, matches titles 2 and 3), B "1 agent = team?" (title 4), C "hook vs rule" (search-style). Start with A + title 1. In Studio use Test & compare on thumbnails (A vs D); change one thing at a time and wait for enough impressions before judging. A title swap after the first days is allowed but changes what you are measuring. Never let the title and thumbnail make different promises, and never promise more than METRICS.md shows.

## Description (paste everything below the line)
---
Can you trust an AI coding assistant to follow your rules? I told Claude Code never to commit when tests fail, then told it to ignore that rule. With a rule in CLAUDE.md: 5 of 5 commits went through. With a hook script instead: 0 of 5. I also tested whether a team of 3 AI code-review agents beats one agent with a checklist (same bugs found, 2.2x the cost).

I tested Claude Code only. The same split (a rule in a prompt vs a check that runs outside the model) should apply to other AI coding agents, but I haven't tested that. Every number on screen came from a real run. Narrated with an AI voice.

Copy-paste starter kit (hook + review checklist + 5-minute test recipe), code and raw results: https://github.com/DevReceiptsAI/claude-code-review-team

Chapters
0:00 The result
0:18 The test app: 10 planted bugs and 3 decoys
1:00 Test 1: plain prompt vs checklist vs agent team
2:26 The bug all three missed
2:40 Test 2: CLAUDE.md rule vs hook
4:03 What broke
4:38 What this doesn't prove
5:06 Copy this: the starter kit

Results in one line each
- Plain prompt: 7, 6, 7 of 10 planted bugs (about $0.07, 13 s per run)
- One agent with the checklist: 9, 9, 9 (about $0.10, 25 s)
- Review team of 3 subagents: 9, 9, 9 (about $0.21, 34 s)
- Rule in CLAUDE.md, told to ignore it: 5 of 5 commits. Hook (instead of the rule), told to ignore it: 0 of 5.
Costs are estimates at API prices; the runs used a subscription plan.

Limits: one small app (300 lines), written by me; 3 runs per review setup, 5 per hook test, one model. A team of agents may win on a much bigger codebase. I haven't tested that yet. The hook blocked 10 of 10 here, but it only catches the commands it matches, and anyone who can edit the settings can remove it. In this test Claude had no file-edit access, and it offered to disable the hook if I told it to: a hook turns a silent waiver into a stop that needs a human decision. The hook ran in headless (-p) mode in all 10 attempts. The one bug all three reviewers missed (a query in a loop) is low-impact on a local SQLite file.

Docs: Skills https://code.claude.com/docs/en/skills | Subagents https://code.claude.com/docs/en/sub-agents | Hooks https://code.claude.com/docs/en/hooks

DevReceipts: real builds, real numbers.

#ClaudeCode #AICoding #AIAgents
---

## Tags (Studio, "More options")
ai coding assistant, claude code, claude code tutorial, claude code hooks, claude.md, claude code subagents, ai code review, ai agents, ai coding, agent evals

## Pinned comment (post it right after publishing)
Everything is reproducible: the repo has the demo app, the answer key, the scripts and the raw results. Biggest caveat: one small app and a few runs per setup. Next video: does a team of agents win on a much bigger (5,000-line) codebase? What else should I test: a different model, or something else? Fair criticism up front: the rule only gave way when I told it to, and the bug all three missed is low-impact on a local database.

## Playlist
Add to "Agents: Real Builds".

## Settings checklist
- [ ] AI-voice disclosure answered honestly in Studio (check YouTube's current guidance; a plain synthetic narrator over truthful on-screen content is generally described as not needing the realistic-content label, but verify)
- [ ] Captions: upload `DevReceipts-Video1-FINAL-v6.srt` as normal captions (do not burn in)
- [ ] Video watermark: set to the entire video
- [ ] End screen (last 5-20 seconds): add the playlist and a subscribe element. The outro already leaves room
- [ ] Visibility: schedule or publish when you can answer comments in the first hours
- [ ] Repo is public and the link above works before you publish
- [ ] Affiliate/sponsor disclosure: none used
