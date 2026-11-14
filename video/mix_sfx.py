#!/usr/bin/env python3
"""Synthesise a few soft sound effects and mix them under the narration.

Usage (from video/):  .venv/bin/python mix_sfx.py
Reads:  build/narration.wav, build/sfx.json (cue times written by scenes.py)
Writes: build/narration_sfx.wav   (narration + effects)

Effects are generated locally (no downloads, no licences): pop, whoosh, ping. They are kept quiet on purpose.
I could not listen to them while building this. Check by ear; lower GAIN or skip them with the narration-only file.
"""
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import lfilter

HERE = Path(__file__).resolve().parent
SR = 24000
GAIN = {"pop": 0.10, "whoosh": 0.09, "ping": 0.08}   # peak amplitude; narration peaks are roughly 0.5-0.9


def pop():
    n = int(0.14 * SR)
    t = np.arange(n) / SR
    freq = 520 * np.exp(-t * 6) + 260
    phase = 2 * np.pi * np.cumsum(freq) / SR
    env = np.exp(-t * 32) * np.minimum(1, t / 0.003)
    return (np.sin(phase) * env).astype(np.float32)


def whoosh():
    n = int(0.5 * SR)
    rng = np.random.default_rng(3)
    noise = rng.standard_normal(n)
    b = np.array([0.18])
    a = np.array([1, -0.82])        # one-pole low-pass: soft "shh", no harsh highs
    x = lfilter(b, a, noise)
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t) ** 2
    return (x * env).astype(np.float32)


def ping():
    n = int(0.28 * SR)
    t = np.arange(n) / SR
    env = np.exp(-t * 14) * np.minimum(1, t / 0.004)
    return ((np.sin(2 * np.pi * 1320 * t) + 0.4 * np.sin(2 * np.pi * 1980 * t)) * env).astype(np.float32)


def main():
    audio, sr = sf.read(HERE / "build" / "narration.wav", dtype="float32")
    assert sr == SR, sr
    cues = json.loads((HERE / "build" / "sfx.json").read_text())
    sounds = {}
    for name, fn in (("pop", pop), ("whoosh", whoosh), ("ping", ping)):
        s = fn()
        sounds[name] = s / (np.max(np.abs(s)) + 1e-9) * GAIN[name]
    mix = audio.copy()
    placed = 0
    for t, kind in cues:
        s = sounds[kind]
        i = int(t * SR)
        if i + len(s) <= len(mix):
            mix[i:i + len(s)] += s
            placed += 1
    peak = float(np.max(np.abs(mix)))
    if peak > 0.98:
        mix *= 0.98 / peak
    sf.write(HERE / "build" / "narration_sfx.wav", mix, SR)
    print(f"placed {placed}/{len(cues)} effects, narration peak {np.max(np.abs(audio)):.2f}, mix peak {np.max(np.abs(mix)):.2f}")


if __name__ == "__main__":
    main()
