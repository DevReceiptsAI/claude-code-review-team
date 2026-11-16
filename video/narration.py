#!/usr/bin/env python3
"""Generate the narration with Kokoro (free, local) and write exact sentence timings.

Usage (from video/):  .venv/bin/python narration.py [voice]      default voice: af_heart
Outputs: build/narration.wav, build/timings.json, build/captions.srt

Final cut v2 (5:52). Every number spoken comes from METRICS.md (real runs).
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
SPEED = 1.05
SENT_GAP = 0.28   # pause between sentences inside a segment
GAP = 0.7         # silence after each segment (the animation fades out during this)
LEAD = 0.4

# (id, [sentences] or None for a silent slate, silent duration in seconds)
SEGMENTS = [
    ("cold_open", [
        "I told Claude Code: never commit when tests fail. Then I told it to ignore that rule.",
        "Five tries. Five commits.",
        "Then I swapped the rule for a short hook script. Same prompt. Zero commits.",
        "I'll show you the hook, and how to test your own rules in five minutes.",
    ], None),
    ("logo", None, 1.2),
    ("setup", [
        "To measure a reviewer, you need to know the right answers.",
        "So I wrote a small shop app, about three hundred lines of Python, and planted ten bugs.",
        "Three logic. Three security. Two performance. Two weak tests.",
        "Plus three decoys.",
    ], None),
    ("bug", [
        "Here's one planted logic bug.",
        "Orders of a hundred dollars or more get a discount.",
        "But the code checks greater than, not greater than or equal.",
        "So exactly a hundred dollars gets nothing.",
        "All tests pass, because none check that amount.",
    ], None),
    ("decoy", [
        "Now a decoy.",
        "This line builds a query from a variable, which usually means a security hole.",
        "But the table name is checked against an approved list first, so it's safe.",
        "Flagging it is a false alarm.",
    ], None),
    ("tools1", [
        "Test 1 uses two Claude Code tools.",
        "A skill is a text file of instructions, a checklist.",
        "A subagent is a helper with one job and read-only tools. My team has three.",
    ], None),
    ("arms", [
        "Now Test 1. Three reviewers, same app, three runs each.",
        "A: a plain prompt. Review this code.",
        "B: one agent with the same checklist, no subagents.",
        "C: the full team. The skill, and three subagents.",
        "B tells us whether a team helps, or whether it's just better instructions.",
    ], None),
    ("fair", [
        "To keep it fair: same model, same effort, same code, a fresh copy every run.",
        "Scoring is automatic, by file and line.",
        "Anything else is listed in the repo for review.",
        "I record bugs caught, real time, and estimated cost.",
    ], None),
    ("res_bugs", [
        "Bugs caught, out of ten.",
        "The plain prompt found seven, six, and seven.",
        "The checklist agent found nine, nine, nine. The team found nine, nine, nine.",
        "The plain prompt never flagged a weak test, because nobody asked it to look. That's most of the gap.",
        "And all three missed the same bug.",
    ], None),
    ("res_cost", [
        "Now the price. These are estimates at API prices. The runs themselves used a subscription plan.",
        "The plain prompt cost about seven cents, and took thirteen seconds.",
        "The checklist agent: about ten cents, twenty-five seconds.",
        "The team: twenty-one cents, thirty-four seconds. About twice the cost of the checklist, for the same bugs.",
        "On my small app, in three runs: same bugs, less than half the cost.",
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
    ("hookdemo", [
        "Here's the hook, running for real.",
        "A failing test, and a commit attempt.",
        "The script runs the tests, prints the failure, and exits with code two. That blocks the commit.",
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
        "That isn't a flaw in the model. Following an explicit instruction is reasonable. But it means a rule in a text file is a default, and a hook is a check that runs outside the model.",
    ], None),
    ("replay", [
        "Here are the real transcripts.",
        "With the rule: it committed, and said it skipped the tests, as I asked.",
        "With the hook: the same prompt, blocked.",
        "And the hook ran even in headless mode. All ten attempts went through it.",
        "One more thing. In these runs Claude had no edit access, and it offered to turn the hook off if I said so.",
    ], None),
    ("broke", [
        "Now, what broke.",
        "My first hook test was invalid. A permission mismatch meant Claude couldn't run the tests, so it refused for the wrong reason. I fixed it and reran.",
        "My decoys weren't clean. Reviewers flagged real problems I hadn't planted.",
        "Many extra findings were real flaws in my own app. The password salt was the username. Tokens never expired.",
        "The tool's timer said the team took ten seconds. The real time was thirty. It skips the subagents.",
        "And my first baseline was unfair. It never mentioned tests, so I added the checklist agent.",
    ], None),
    ("limits", [
        "What this doesn't prove.",
        "It's one small app, three hundred lines, with my bugs and my prompts.",
        "Three runs per review setup, five per hook test, one model.",
        "A team of agents may well win on a much bigger codebase. I haven't tested that yet.",
        "The hook blocked ten out of ten here. But it only catches the commands it matches, and anyone who edits the settings can remove it.",
        "So a hook turns a quiet waiver into a stop that needs a human decision. It does not stop a human.",
    ], None),
    ("kit", [
        "Here's what to copy.",
        "A starter kit is in the repo: the hook script, the settings entry, and the review checklist.",
        "And a five-minute recipe to test your own rule. Break one test, tell Claude to ignore the rule, and count the commits.",
    ], None),
    ("lessons", [
        "So what does this suggest?",
        "One: write the checklist first. Add subagents only if one agent can't hold your code. Measure both.",
        "Two: if a rule must never break, put it in a hook, not a sentence.",
        "Three: when you test an AI setup, expect your own test to be wrong. Mine was, four times.",
    ], None),
    ("outro", [
        "The starter kit and all the raw results are linked in the description, so you can run this on your own project.",
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

    # Captions: at most 2 lines of about 42 characters; longer sentences are split into several cues, timed by length.
    import textwrap
    cues = []
    for a, b, text in srt:
        lines = textwrap.wrap(text, 42)
        chunks = [lines[i:i + 2] for i in range(0, len(lines), 2)]
        total = sum(len(c) for c in lines) or 1
        cur = a
        for ch in chunks:
            share = sum(len(x) for x in ch) / total
            end = min(b, cur + (b - a) * share)
            cues.append((cur, end, "\n".join(ch)))
            cur = end
    (BUILD / "captions.srt").write_text(
        "\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{s}\n" for i, (a, b, s) in enumerate(cues, 1))
    )
    (BUILD / "timings.json").write_text(json.dumps({"voice": VOICE, "total": round(t, 3), "segments": timings}, indent=2))
    print(f"voice={VOICE} total={t:.1f}s ({t/60:.1f} min)")
    for x in timings:
        print(f"  {x['id']:13s} start {x['start']:6.1f}  dur {x['dur']:5.1f}  sentences {len(x['sentences'])}")


if __name__ == "__main__":
    main()
