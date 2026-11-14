# Upload package: Video #1 (copy each block into YouTube Studio)

## Title (pick one; the first is the recommended one)
1. I Told Claude Code to Ignore Its Rule. A Hook Didn't Let It.   (61 characters)
2. One Agent = My 3-Agent Review Team? I Measured It (Claude Code)
3. Claude Code Hooks vs CLAUDE.md Rules: What Actually Blocks a Bad Commit?

Thumbnails: A (ignore the rule), B (1 agent = team?), C (hook vs rule), all in `thumbnails/`. Use A with title 1, B with title 2, C with title 3. Do not mix: the title, thumbnail and first 10 seconds must make the same promise. Test one change at a time and give it time before judging.

## Description (paste everything below the line)
---
I told Claude Code never to commit when tests fail. Then I told it to ignore that rule. Rule: 5 of 5 commits went through. Hook: 0 of 5. I also measured whether a team of 3 review agents beats one agent with a checklist.

Every number on screen came from a real run. Narrated with an AI voice.

Code, test kit and raw results: https://github.com/DevReceiptsAI/claude-code-review-team

Chapters
0:00 The result
0:43 Skills, subagents and hooks in plain words
1:49 The test app: 10 planted bugs and 3 decoys
2:40 Test 1: plain prompt vs checklist vs agent team
4:03 Test 2: CLAUDE.md rule vs hook
4:48 What broke
5:53 What it suggests

Results in one line each
- Plain prompt: 7, 6, 7 of 10 planted bugs (about $0.07, 13 s per run)
- One agent with the checklist: 9, 9, 9 (about $0.10, 25 s)
- Review team of 3 subagents: 9, 9, 9 (about $0.21, 34 s)
- Rule in CLAUDE.md, told to ignore it: 5 of 5 commits. Hook, told to ignore it: 0 of 5.
Costs are estimates at API prices; the runs used a subscription plan.

Limits: one small app, written by me; 3 runs per review setup, 5 per hook test, one model. A team of agents may win on a much bigger codebase. I haven't tested that yet. A hook only stops the model, not someone editing the settings file.

Docs: Skills https://code.claude.com/docs/en/skills.md | Subagents https://code.claude.com/docs/en/sub-agents.md | Hooks https://code.claude.com/docs/en/hooks.md

DevReceipts: real builds, real numbers.

#ClaudeCode #AIAgents #Subagents
---

## Tags (Studio, "More options")
claude code, claude code hooks, claude code subagents, claude code skills, claude.md, ai agents, ai coding, agent evals, llm evaluation, code review ai

## Pinned comment (post it right after publishing)
Everything is reproducible: the repo has the demo app, the answer key, the scripts and the raw results. Biggest caveat: one small app and a few runs per setup. What should I test next: a much bigger codebase, a different model, or something else?

## Playlist
Add to "Agents: Real Builds".

## Settings checklist
- [ ] AI-voice disclosure answered honestly in Studio (check YouTube's current guidance; a plain synthetic narrator over truthful on-screen content is generally described as not needing the realistic-content label, but verify)
- [ ] Captions: upload `DevReceipts-Video1-FINAL.srt` as normal captions (do not burn in)
- [ ] Video watermark: set to the entire video
- [ ] End screen (last 5-20 seconds): add the playlist and a subscribe element. The outro already leaves room
- [ ] Visibility: schedule or publish when you can answer comments in the first hours
- [ ] Repo is public and the link above works before you publish
- [ ] Affiliate/sponsor disclosure: none used
