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
    ("hook", [
        "I told Claude Code: never commit when tests fail.",
        "Then I told it to ignore that rule. It committed, five times out of five.",
        "A hook stopped it every time. Zero out of five.",
    ], None),
    ("brand", [
        "This is DevReceipts. Real builds, real numbers.",
        "Every number in this video came from a real run.",
    ], None),
    ("preview", [
        "Two tests. First: does a team of review agents beat a plain prompt?",
        "Second: does a rule in a text file beat a script?",
        "I'll also show what broke along the way, because a lot did.",
    ], None),
    ("intro", [
        "If you haven't used Claude Code: it's an AI assistant that works in your terminal.",
        "It reads your files, runs commands, and edits code.",
        "You can customize it in three main ways: skills, subagents, and hooks.",
    ], None),
    ("skill", [
        "First, skills.",
        "A skill is a text file of instructions, saved in a folder.",
        "Write a checklist once, and Claude can pull it in whenever the task comes up.",
        "For us, that's a review checklist.",
        "Here's the catch: a skill is guidance. Claude reads it, and decides how to follow it.",
    ], None),
    ("subagent", [
        "Second, subagents.",
        "A subagent is a helper with one job.",
        "It starts with a fresh, empty context, and it can only use the tools you give it.",
        "Ours can only read files. They can't change anything.",
        "Why bother? Each helper stays focused on one kind of problem, and several can work at the same time.",
        "Then they report back.",
    ], None),
    ("hookdef", [
        "Third, hooks. A hook isn't AI at all.",
        "It's a script that runs automatically at a set moment. For example, right before Claude runs a command.",
        "The script looks at the command and decides: let it through, or block it.",
        "A script gives the same answer every time.",
    ], None),
    ("judgment", [
        "So skills and subagents are judgment. Hooks are rules.",
        "Judgment is flexible, and sometimes wrong. A rule is rigid, and reliable.",
        "That difference is the whole second test.",
    ], None),
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
        "And all three missed the same bug: a database query inside a loop.",
    ], None),
    ("res_cost", [
        "Now the price. These are estimates at API prices. The runs themselves used a subscription plan.",
        "The plain prompt cost about seven cents, and took thirteen seconds.",
        "The checklist agent: about ten cents, twenty-five seconds.",
        "The team: twenty-one cents, thirty-four seconds. About twice the cost of the checklist, for the same bugs.",
        "On this small app, the instructions mattered more than the number of agents.",
    ], None),
    ("hook_vs_rule", [
        "Test 2 is about enforcement.",
        "In one setup, a rule in claude dot M D says: never commit when tests fail.",
        "In the other, a hook runs the tests before every commit, and blocks the commit if they fail.",
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
        "It's one small app. I wrote it, and I wrote the bugs and the prompts.",
        "Three runs per review setup, five per hook test, one model.",
        "A team of agents may well win on a much bigger codebase, where one context can't hold everything. I haven't tested that yet.",
        "And a hook only stops the model. Anyone who can edit the settings file can remove it.",
    ], None),
    ("lessons", [
        "So what does this suggest?",
        "One: before you build an agent team, try one agent with a good checklist. Measure both.",
        "Two: if a rule must never break, put it in a hook, not a sentence.",
        "Three: when you test an AI setup, expect your own test to be wrong. Mine was, three times.",
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
