#!/usr/bin/env python3
"""Generate the narration with Kokoro (free, local) and write exact sentence timings.

Usage (from video/):  .venv/bin/python narration.py [voice]      default voice: af_heart
Outputs: build/narration.wav, build/timings.json, build/captions.srt

DRAFT CUT v2: intro, the basics (skill / subagent / hook), the test design. It states NO measured
result. The results segment is a silent slate until the real runs exist.
Each sentence is synthesised separately, so animations can be timed to the exact sentence.
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
BUILD.mkdir(exist_ok=True)
VOICE = sys.argv[1] if len(sys.argv) > 1 else "af_heart"
SPEED = 1.0
SENT_GAP = 0.28   # pause between sentences inside a segment
GAP = 0.7         # silence after each segment (the animation fades out during this)
LEAD = 0.4

# (id, [sentences] or None for a silent slate, silent duration in seconds)
SEGMENTS = [
    ("cold_open", [
        "This test fails. My rule says: never commit when tests fail.",
        "So I told Claude Code to ignore the rule.",
        "Five tries. Five commits.",
        "Then I added a short hook script. Same prompt. Zero commits.",
        "But the real surprise was a different test.",
        "A team of three AI reviewers against one agent with a checklist. Same score. The team cost twice as much.",
        "And all three missed the same bug, every run. I'll show you which one.",
    ], None),
    ("logo", None, 1.2),
    ("setup", [
        "To measure a reviewer, you need to know the right answers.",
        "So I wrote a small shop app, about three hundred lines of Python, and planted ten bugs in it.",
        "Three logic bugs. Three security bugs. Two performance bugs. And two weak tests.",
        "And three decoys, which I'll explain in a second.",
    ], None),
    ("bug", [
        "Here's one of the logic bugs.",
        "The discount is for orders of a hundred dollars or more.",
        "But the code checks greater than, not greater than or equal.",
        "So an order of exactly a hundred dollars gets no discount.",
        "The tests all pass, because none of them check that exact amount.",
    ], None),
    ("decoy", [
        "Now a decoy.",
        "This line builds a database query from a variable. That usually means a security hole.",
        "But the code checks the table name against an approved list first, so it's safe.",
        "A good reviewer leaves it alone. If it flags this, that's a false alarm.",
    ], None),
    ("tools1", [
        "Test 1 uses two of Claude Code's tools.",
        "A skill is a text file of instructions, a checklist Claude can pull in.",
        "A subagent is a helper with one job, and read-only tools. My team has three.",
    ], None),
    ("arms", [
        "Now Test 1. Three reviewers, same app, same model, three runs each.",
        "A: a plain prompt. Review this code.",
        "B: one agent with the same checklist as the skill, but no subagents.",
        "C: the full team. The skill, and three subagents.",
        "B is there for a reason. It tells us whether a team helps, or whether it's just better instructions.",
    ], None),
    ("fair", [
        "To keep it fair: same model, same effort, same code, a fresh copy every run.",
        "Scoring is automatic. A finding counts if it lands on a planted line.",
        "Anything else, I check by hand.",
        "I record bugs caught, real elapsed time, and estimated cost.",
    ], None),
    ("res_bugs", [
        "Bugs caught, out of ten.",
        "The plain prompt found seven, six, and seven.",
        "The checklist agent found nine, nine, nine. The team found nine, nine, nine.",
        "The plain prompt never looked at the tests, because nobody asked it to. That's most of the gap.",
        "And all three missed the same bug.",
    ], None),
    ("res_cost", [
        "Now the price. These are estimates at API prices. The runs themselves used a subscription plan.",
        "The plain prompt cost about seven cents, and took thirteen seconds.",
        "The checklist agent: about ten cents, twenty-five seconds.",
        "The team: twenty-one cents, thirty-four seconds. About twice the cost of the checklist, for the same bugs.",
        "On my small app, in three runs, the instructions mattered more than the number of agents.",
    ], None),
    ("miss", [
        "Now, the bug all three missed.",
        "It's in a function that checks stock. For every item, it asks the database a separate question.",
        "A database query inside a loop. It works, so nothing looks wrong. All nine runs walked right past it.",
    ], None),
    ("hookexp", [
        "Test 2 uses a hook.",
        "A hook is a script that runs before Claude runs a command.",
        "Mine runs the tests before any git commit, and blocks the commit if they fail.",
    ], None),
    ("hook_vs_rule", [
        "Test 2 is about enforcement.",
        "In one setup, a rule in claude dot M D says: never commit when tests fail.",
        "In the other, the hook blocks the commit if the tests fail.",
        "Then I try two prompts. First, I'm in a hurry. Then, I say outright: ignore the rule.",
        "Five attempts each.",
    ], None),
    ("res_hook", [
        "Here's what happened.",
        "When I only said I was in a hurry, the rule held. Zero out of five commits.",
        "When I told Claude to ignore the rule, it did. Five out of five.",
        "The hook blocked all ten attempts. Even when I said to override it.",
        "That isn't a flaw in the model. Following an explicit instruction is reasonable. But it means a rule in a text file is a default, and a hook is enforcement.",
    ], None),
    ("replay", [
        "Here are the real transcripts.",
        "With the rule: it committed, and said it skipped the tests, as I asked.",
        "With the hook: the same prompt, blocked.",
        "And the hook ran even in headless mode. All ten attempts went through it.",
    ], None),
    ("broke", [
        "Now, what broke.",
        "My first hook test was wrong. Claude couldn't run the tests because of a permission mismatch, so it refused to commit for the wrong reason. I fixed it and ran it again.",
        "My decoys weren't clean. The reviewers flagged real problems I hadn't planted, like negative prices printing wrong.",
        "Many of the extra findings were real flaws in my own demo app. The password salt was the username. Tokens never expired.",
        "The tool's own timer said the team took about ten seconds. The real time was about thirty. It leaves out the subagents.",
        "And my first comparison was unfair. The plain prompt never mentioned tests. That's why there's a checklist agent.",
    ], None),
    ("limits", [
        "What this doesn't prove.",
        "It's one small app, three hundred lines, with my bugs and my prompts.",
        "Three runs per review setup, five per hook test, one model.",
        "A team of agents may well win on a much bigger codebase. I haven't tested that yet.",
        "The hook blocked ten out of ten here. But it only catches the commands it matches, and anyone who edits the settings can remove it.",
    ], None),
    ("lessons", [
        "So what does this suggest?",
        "One: before you build an agent team, try one agent with a good checklist. Measure both.",
        "Two: if a rule must never break, put it in a hook, not a sentence.",
        "Three: when you test an AI setup, expect your own test to be wrong. Mine was, four times.",
    ], None),
    ("outro", [
        "The review setup and the test kit are in the description, so you can run this on your own project.",
        "Next, I'll test a much bigger codebase, to see where subagents start to pay off.",
        "DevReceipts. Real builds, real numbers.",
    ], None),
]


def main():
    kokoro = Kokoro(str(HERE / "models/kokoro-v1.0.onnx"), str(HERE / "models/voices-v1.0.bin"))
    sr = 24000
    track = [np.zeros(int(LEAD * sr), dtype=np.float32)]
    t = LEAD
    timings, srt = [], []
    for seg_id, sentences, silent in SEGMENTS:
        seg_start = t
        sents_t = []
        if sentences:
            for i, text in enumerate(sentences):
                samples, rate = kokoro.create(text, voice=VOICE, speed=SPEED, lang="en-us")
                assert rate == sr, rate
                samples = samples.astype(np.float32)
                d = len(samples) / sr
                sents_t.append({"start": round(t, 3), "end": round(t + d, 3), "text": text})
                srt.append((t, t + d, text))
                track.append(samples)
                t += d
                if i < len(sentences) - 1:
                    track.append(np.zeros(int(SENT_GAP * sr), dtype=np.float32))
                    t += SENT_GAP
        else:
            track.append(np.zeros(int(silent * sr), dtype=np.float32))
            t += silent
        timings.append({"id": seg_id, "start": round(seg_start, 3), "end": round(t, 3),
                        "dur": round(t - seg_start, 3), "sentences": sents_t})
        track.append(np.zeros(int(GAP * sr), dtype=np.float32))
        t += GAP
    sf.write(BUILD / "narration.wav", np.concatenate(track), sr)

    def ts(x):
        h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

    (BUILD / "captions.srt").write_text(
        "\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{s}\n" for i, (a, b, s) in enumerate(srt, 1))
    )
    (BUILD / "timings.json").write_text(json.dumps({"voice": VOICE, "total": round(t, 3), "segments": timings}, indent=2))
    print(f"voice={VOICE} total={t:.1f}s ({t/60:.1f} min)")
    for x in timings:
        print(f"  {x['id']:13s} start {x['start']:6.1f}  dur {x['dur']:5.1f}  sentences {len(x['sentences'])}")


if __name__ == "__main__":
    main()
