#!/usr/bin/env python3
"""Cut 3 vertical Shorts (1080x1920) from the final video: the 16:9 picture is centred on a navy canvas,
with a hook line above and burned-in captions below (most Shorts are watched muted).
Usage (from video/):  .venv/bin/python build_shorts.py [final-mp4]   -> out/shorts/*.mp4
Needs build/timings.json and the final mp4 (default out/DevReceipts-Video1-FINAL-v3.mp4). No model or API calls."""
import json, subprocess, sys, textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "out" / "DevReceipts-Video1-FINAL-v3.mp4"
OUT = HERE / "out" / "shorts"
OUT.mkdir(parents=True, exist_ok=True)
SEGS = {s["id"]: s for s in json.loads((HERE / "build" / "timings.json").read_text())["segments"]}
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

# (file name, segment id, first sentence index, last sentence index, hook line, small line)
CLIPS = [
    ("short1-ignore-the-rule", "cold_open", 0, 2, "I told Claude Code|to ignore my rule", "5 of 5 commits, then a hook gave 0"),
    ("short2-rule-vs-hook", "res_hook", 0, 4, "CLAUDE.md rule|vs hook", "same prompt, 5 tries each"),
    ("short3-bug-all-missed", "miss", 0, 2, "The bug 3 AI reviewers|all missed", "9 runs out of 9"),
]


def ts(x):
    return f"{int(x//3600):02d}:{int(x%3600//60):02d}:{x%60:06.3f}".replace(".", ",")


for name, seg, i0, i1, hook, small in CLIPS:
    sents = SEGS[seg]["sentences"][i0:i1 + 1]
    t0, t1 = max(0.0, sents[0]["start"] - 0.2), sents[-1]["end"] + 0.5
    cues = []
    for s in sents:
        lines = textwrap.wrap(s["text"], 26)
        chunks = [lines[i:i + 2] for i in range(0, len(lines), 2)]
        total = sum(len(l) for l in lines) or 1
        cur = s["start"] - t0
        for ch in chunks:
            end = cur + (s["end"] - s["start"]) * sum(len(l) for l in ch) / total
            cues.append((cur, end, "\n".join(ch)))
            cur = end
    # captions: drawtext per line (this ffmpeg's subtitles filter rendered nothing), text read from small files
    tdir = OUT / "txt"
    tdir.mkdir(exist_ok=True)
    caps = []
    for n, (a_, b_, t) in enumerate(cues):
        for j, line in enumerate(t.split("\n")):
            f = tdir / f"{name}-{n}-{j}.txt"
            f.write_text(line)
            caps.append(f"drawtext=fontfile='{FONT}':textfile='{f}':fontcolor=white:fontsize=66:borderw=5:bordercolor=0x0f172a:"
                        f"x=(w-text_w)/2:y={1330 + j * 90}:enable='between(t,{a_:.3f},{b_:.3f})'")
    dt = lambda t, size, color, y: (f"drawtext=fontfile='{FONT}':text='{t}':fontcolor={color}:fontsize={size}:"
                                    f"x=(w-text_w)/2:y={y}")
    h1, h2 = hook.split("|")
    vf = (f"[0:v]scale=1080:-2[v];color=c=0x0f172a:s=1080x1920:d={t1 - t0:.2f}[bg];[bg][v]overlay=0:(H-h)/2-60[m];"
          f"[m]{dt(h1, 84, 'white', 230)},{dt(h2, 84, 'white', 330)},{dt(small, 44, '0x22d3ee', 480)},"
          f"{dt('DevReceipts', 40, '0x94a3b8', 1800)},{','.join(caps)}[out]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", str(SRC),
           "-filter_complex", vf, "-map", "[out]", "-map", "0:a", "-c:v", "libx264", "-crf", "18", "-preset", "slow",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(OUT / f"{name}.mp4")]
    subprocess.run(cmd, check=True)
    print(f"{name}: {t1 - t0:.1f}s")
