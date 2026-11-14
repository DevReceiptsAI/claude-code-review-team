"""DevReceipts Video #1 (FINAL CUT): "I told Claude Code to ignore its rule. A hook didn't let it."

Render:  manim -qm scenes.py ArchitectureScene            (quick check, 720p)
         manim -r 2560,1440 scenes.py ArchitectureScene   (final, 1440p)
Needs build/timings.json from narration.py. Writes build/sfx.json (cue times for mix_sfx.py).
Style follows CLAUDE.md: 16:9, background #0f172a, palette cyan/indigo/teal/violet/yellow/green, 2D primitives only.

Every number in RESULTS comes from METRICS.md (full eval, 13 Nov 2026). Do not edit them by hand.
"""
import json
from pathlib import Path

import numpy as np
from manim import *
from manim.utils.rate_functions import ease_in_out_sine, ease_out_back

BG = "#0f172a"
CYAN, INDIGO, TEAL, VIOLET, YELLOW, GREEN = "#22d3ee", "#6366f1", "#14b8a6", "#8b5cf6", "#facc15", "#4ade80"
PANEL, LIGHT, MUTED, BAR = "#1e293b", "#e2e8f0", "#94a3b8", "#334155"
MONO, SANS = "Menlo", "Helvetica Neue"

# Source: METRICS.md, full eval 13 Nov 2026. Bugs caught per run (3 runs), median est. cost USD, median wall-clock s,
# and commits that landed out of 5 attempts for the hook test.
RESULTS = {
    "bugs": {"plain": [7, 6, 7], "checklist": [9, 9, 9], "team": [9, 9, 9]},
    "cost": {"plain": 0.068, "checklist": 0.095, "team": 0.209},
    "wall": {"plain": 12.9, "checklist": 24.6, "team": 34.0},
    "commits": {("rule", "hurry"): 0, ("hook", "hurry"): 0, ("rule", "override"): 5, ("hook", "override"): 0},
}

HERE = Path(__file__).parent
TIMINGS = {s["id"]: s for s in json.loads((HERE / "build" / "timings.json").read_text())["segments"]}
TOTAL = TIMINGS["outro"]["end"] + 0.5

CHAPTERS = {"hook": 1, "brand": 1, "preview": 1, "intro": 1,
            "skill": 2, "subagent": 2, "hookdef": 2, "judgment": 2,
            "setup": 3, "bug": 3, "decoy": 3,
            "arms": 4, "fair": 4, "res_bugs": 4, "res_cost": 4,
            "hook_vs_rule": 5, "res_hook": 5,
            "broke": 6, "limits": 6, "lessons": 6, "outro": 6}
CHAPTER_NAMES = {1: "INTRO", 2: "THE BASICS", 3: "THE TEST APP", 4: "TEST 1: REVIEWERS", 5: "TEST 2: RULE VS HOOK", 6: "WRAP-UP"}
N_CHAPTERS = 6
BAR_W = 12.4


class ArchitectureScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.sfx_log = []
        self.persist = []
        self.build_backdrop()
        self.build_progress()
        self.footer = Text("DevReceipts", font=MONO, font_size=22, weight=BOLD,
                           t2c={"Receipts": CYAN}).to_corner(DR, buff=0.35)
        self.add(self.footer)
        self.persist.append(self.footer)
        self.wait(TIMINGS["hook"]["start"])
        steps = [("hook", self.step_hook), ("brand", self.step_brand), ("preview", self.step_preview),
                 ("intro", self.step_intro), ("skill", self.step_skill), ("subagent", self.step_subagent),
                 ("hookdef", self.step_hookdef), ("judgment", self.step_judgment), ("setup", self.step_setup),
                 ("bug", self.step_bug), ("decoy", self.step_decoy), ("arms", self.step_arms),
                 ("fair", self.step_fair), ("res_bugs", self.step_res_bugs), ("res_cost", self.step_res_cost),
                 ("hook_vs_rule", self.step_hook_vs_rule), ("res_hook", self.step_res_hook),
                 ("broke", self.step_broke), ("limits", self.step_limits), ("lessons", self.step_lessons),
                 ("outro", self.step_outro)]
        for seg_id, step in steps:
            self.set_chapter(CHAPTERS[seg_id])
            step()
            self.hold_until(TIMINGS[seg_id]["end"] + 0.1)
            if seg_id != "outro":
                self.clear_stage()
        self.hold_until(TIMINGS["outro"]["end"] + 0.5)
        (HERE / "build" / "sfx.json").write_text(json.dumps(self.sfx_log))

    # ---- backdrop, progress bar, chapter label ---------------------------------------
    def build_backdrop(self):
        rng = np.random.default_rng(7)
        glows = VGroup()
        for cx, cy, col in ((-6.5, 3.5, CYAN), (6.5, -3.5, INDIGO)):
            for r, op in ((4.6, 0.025), (3.5, 0.03), (2.5, 0.035), (1.5, 0.04)):
                glows.add(Circle(radius=r, stroke_width=0, fill_color=col, fill_opacity=op).move_to([cx, cy, 0]))
        n = 38
        dots = VGroup(*[Dot(point=[rng.uniform(-7.2, 7.2), rng.uniform(-4.2, 4.2), 0], radius=rng.uniform(0.02, 0.05),
                            color=CYAN).set_opacity(rng.uniform(0.12, 0.3)) for _ in range(n)])
        speeds = rng.uniform(0.08, 0.22, n)

        def drift(group, dt):
            for d, v in zip(group, speeds):
                d.shift(UP * v * dt)
                if d.get_y() > 4.3:
                    d.set_y(-4.3)

        dots.add_updater(drift)
        self.add(glows, dots)
        self.persist += [glows, dots]

    def build_progress(self):
        track = Rectangle(width=BAR_W, height=0.05, stroke_width=0, fill_color=MUTED, fill_opacity=0.25).move_to(UP * 3.88)
        fill = Rectangle(width=0.02, height=0.05, stroke_width=0, fill_color=CYAN, fill_opacity=1)

        def grow(m):
            w = max(0.02, BAR_W * min(1.0, self.renderer.time / TOTAL))
            m.stretch_to_fit_width(w)
            m.move_to(track.get_left() + RIGHT * w / 2)

        fill.add_updater(grow)
        ticks = VGroup(*[Rectangle(width=0.025, height=0.14, stroke_width=0, fill_color=MUTED, fill_opacity=0.6)
                         .move_to(track.get_left() + RIGHT * BAR_W * TIMINGS[k]["start"] / TOTAL)
                         for k in ("skill", "setup", "arms", "hook_vs_rule", "broke")])
        self.chapter_idx = 0
        self.chapter_mob = Text("", font=MONO, font_size=18, color=MUTED)
        self.add(track, ticks, fill, self.chapter_mob)
        self.persist += [track, ticks, fill, self.chapter_mob]

    def set_chapter(self, idx):
        if idx == self.chapter_idx:
            return
        self.chapter_idx = idx
        new = Text(f"{idx}/{N_CHAPTERS}  {CHAPTER_NAMES[idx]}", font=MONO, font_size=18, color=MUTED)
        new.move_to(np.array([-BAR_W / 2, 3.55, 0]), aligned_edge=LEFT)
        self.chapter_mob.become(new)

    # ---- helpers -------------------------------------------------------
    def hold_until(self, t):
        remaining = t - self.renderer.time
        if remaining > 0:
            self.wait(remaining)

    def at(self, seg, i, frac=0.0):
        """Wait until sentence i of a segment starts (plus a fraction of its length)."""
        s = TIMINGS[seg]["sentences"][i]
        self.hold_until(s["start"] + frac * (s["end"] - s["start"]))

    def sfx(self, kind):
        self.sfx_log.append([round(float(self.renderer.time), 3), kind])

    def clear_stage(self):
        stage = [m for m in self.mobjects if m not in self.persist]
        if not stage:
            return
        self.sfx("whoosh")
        wipe = Rectangle(width=0.18, height=8.4, stroke_width=0, fill_color=CYAN, fill_opacity=0.35).move_to(LEFT * 7.6)
        self.add(wipe)
        self.play(*[m.animate.shift(LEFT * 0.7).set_opacity(0) for m in stage],
                  wipe.animate.move_to(RIGHT * 7.6), run_time=0.5)
        self.remove(wipe, *stage)

    def box(self, label, w, h, color, fs=24, fill=PANEL, font=MONO):
        rect = RoundedRectangle(corner_radius=0.14, width=w, height=h, stroke_color=color, stroke_width=3,
                                fill_color=fill, fill_opacity=1)
        txt = Text(label, font=font, font_size=fs, color=LIGHT, line_spacing=0.8)
        if txt.width > w - 0.3:
            txt.scale_to_fit_width(w - 0.3)
        return VGroup(rect, txt)

    def arrow(self, a, b, color=MUTED, buff=0.1):
        return Arrow(a, b, buff=buff, color=color, stroke_width=4, max_tip_length_to_length_ratio=0.25)

    def head(self, text, color):
        return Text(text, font=SANS, font_size=50, weight=BOLD, color=color).move_to(UP * 3.1)

    def code_line(self, text, x_left, y, color=LIGHT, fs=24):
        return Text(text, font=MONO, font_size=fs, color=color).move_to(np.array([x_left, y, 0]), aligned_edge=LEFT)

    def pop(self, m):
        return GrowFromCenter(m, rate_func=ease_out_back)

    def pop_in(self, *mobs, run_time=0.55, lag=0.12):
        self.sfx("pop")
        self.play(LaggedStart(*[self.pop(m) for m in mobs], lag_ratio=lag), run_time=run_time)

    def packet(self, color=CYAN):
        return VGroup(Circle(radius=0.26, stroke_width=0, fill_color=color, fill_opacity=0.25),
                      Dot(radius=0.1, color=color))

    def fire(self, color, start, end, run_time=0.8):
        """A glowing packet that travels from start to end and fades out."""
        pkt = self.packet(color).move_to(start)
        self.add(pkt)
        return Succession(MoveAlongPath(pkt, Line(start, end), rate_func=ease_in_out_sine, run_time=run_time),
                          FadeOut(pkt, run_time=0.2))

    def flash(self, point, color, radius=0.7):
        self.sfx("ping")
        return Flash(np.array(point), color=color, flash_radius=radius, line_length=0.25, num_lines=10, run_time=0.6)

    # ---- 1. hook: a receipt prints the result ---------------------------------------------------
    def step_hook(self):
        self.at("hook", 0)
        W, H, TOP = 6.4, 5.8, 2.75
        INK, SOFT = "#0f172a", "#475569"
        paper = Rectangle(width=W, height=H, stroke_width=0, fill_color="#f1f5f9", fill_opacity=1)
        paper.move_to(np.array([0, TOP - H / 2, 0]))
        teeth = VGroup(*[Square(side_length=0.2, stroke_width=0, fill_color=BG, fill_opacity=1).rotate(PI / 4)
                         .move_to(np.array([-W / 2 + 0.15 + i * 0.29, TOP - H, 0])) for i in range(22)])
        slot = RoundedRectangle(corner_radius=0.1, width=7.2, height=0.3, stroke_width=0, fill_color="#0b1224",
                                fill_opacity=1).move_to(np.array([0, TOP + 0.05, 0]))
        glow = Rectangle(width=6.8, height=0.04, stroke_width=0, fill_color=CYAN, fill_opacity=0.9).move_to(
            np.array([0, TOP - 0.1, 0]))
        self.sfx("pop")
        self.play(FadeIn(slot), FadeIn(glow), run_time=0.3)
        self.add(paper, teeth, slot, glow)
        self.play(GrowFromEdge(paper, UP), FadeIn(teeth), run_time=0.9)
        self.add(slot, glow)

        def line(text, y, fs=20, color=INK, weight=NORMAL, t2c=None, center=False):
            t = Text(text, font=MONO, font_size=fs, color=color, weight=weight, t2c=t2c or {})
            return t.move_to(np.array([0, y, 0])) if center else t.move_to(np.array([-W / 2 + 0.45, y, 0]), aligned_edge=LEFT)

        header = line("DEVRECEIPTS", 2.1, 30, INK, BOLD, center=True)
        sub = line("failing test  /  5 tries each", 1.62, 17, SOFT, center=True)
        sep1 = line("- - - - - - - - - - - - - - - - - -", 1.25, 18, "#94a3b8", center=True)
        self.play(AddTextLetterByLetter(header, time_per_char=0.03), run_time=0.4)
        self.play(FadeIn(sub), FadeIn(sep1), run_time=0.4)
        self.at("hook", 1)
        l1 = line("CLAUDE.md rule + \"ignore it\"", 0.72, 21)
        l1b = line("commits through:  5 / 5", 0.22, 25, INK, BOLD, {"5 / 5": "#b45309"})
        self.play(AddTextLetterByLetter(l1, time_per_char=0.02), run_time=0.7)
        self.sfx("pop")
        self.play(AddTextLetterByLetter(l1b, time_per_char=0.03), run_time=0.7)
        self.at("hook", 2)
        l2 = line("hook + \"ignore it\"", -0.45, 21)
        l2b = line("commits through:  0 / 5", -0.95, 25, INK, BOLD, {"0 / 5": "#047857"})
        sep2 = line("- - - - - - - - - - - - - - - - - -", -1.4, 18, "#94a3b8", center=True)
        self.play(AddTextLetterByLetter(l2, time_per_char=0.02), run_time=0.5)
        self.sfx("pop")
        self.play(AddTextLetterByLetter(l2b, time_per_char=0.03), FadeIn(sep2), run_time=0.7)
        t1 = line("rule = a default", -1.85, 24, INK, BOLD, center=True)
        t2 = line("hook = enforcement", -2.3, 24, "#0e7490", BOLD, center=True)
        self.play(FadeIn(t1, shift=UP * 0.1), FadeIn(t2, shift=UP * 0.1), run_time=0.6)

    # ---- 2. brand card + promise ----------------------------------------------------------------------
    def step_brand(self):
        self.at("brand", 0)
        brand = Text("DevReceipts", font=MONO, font_size=84, weight=BOLD, t2c={"Receipts": CYAN}).shift(UP * 0.7)
        tag = Text("Real builds. Real numbers.", font=MONO, font_size=30, color=MUTED).next_to(brand, DOWN, buff=0.35)
        self.sfx("pop")
        self.play(Write(brand), run_time=1.0)
        self.play(FadeIn(tag), run_time=0.5)
        self.at("brand", 1)
        note = Text("every number here came from a real run", font=MONO, font_size=28, color=CYAN).shift(DOWN * 1.6)
        self.play(FadeIn(note, shift=UP * 0.2), run_time=0.7)

    # ---- 3. preview -----------------------------------------------------------------------------------------
    def step_preview(self):
        self.at("preview", 0)
        c1 = self.box("TEST 1\nreview agents:\nteam vs prompt", 4.2, 2.6, CYAN, fs=24).move_to(LEFT * 4.5 + UP * 0.2)
        c2 = self.box("TEST 2\nrule vs hook:\nwho blocks commits", 4.2, 2.6, VIOLET, fs=24).move_to(UP * 0.2)
        c3 = self.box("AND\nwhat broke\nalong the way", 4.2, 2.6, YELLOW, fs=24).move_to(RIGHT * 4.5 + UP * 0.2)
        self.pop_in(c1, run_time=0.6)
        self.at("preview", 1)
        self.pop_in(c2, run_time=0.6)
        self.at("preview", 2)
        self.pop_in(c3, run_time=0.6)
        self.play(Indicate(c3, color=YELLOW, scale_factor=1.06), run_time=0.8)

    # ---- 4. what Claude Code is ----------------------------------------------------------------------------------
    def step_intro(self):
        self.at("intro", 0)
        term = RoundedRectangle(corner_radius=0.2, width=9.4, height=3.9, stroke_color=INDIGO, stroke_width=3,
                                fill_color=PANEL, fill_opacity=1).shift(UP * 0.9)
        lights = VGroup(*[Dot(radius=0.07, color=c) for c in (CYAN, YELLOW, GREEN)]).arrange(RIGHT, buff=0.15)
        lights.move_to(term.get_corner(UL) + RIGHT * 0.6 + DOWN * 0.35)
        prompt = Text("> review this repo", font=MONO, font_size=30, color=CYAN)
        prompt.move_to(term.get_corner(UL) + RIGHT * 0.6 + DOWN * 0.95, aligned_edge=LEFT)
        cap = Text("Claude Code: an AI assistant in your terminal", font=MONO, font_size=24,
                   color=MUTED).next_to(term, DOWN, buff=0.2)
        self.sfx("pop")
        self.play(self.pop(term), FadeIn(lights), FadeIn(cap), run_time=0.7)
        self.play(AddTextLetterByLetter(prompt, time_per_char=0.04))
        self.at("intro", 1)
        items = VGroup(*[VGroup(Dot(radius=0.08, color=GREEN), Text(t, font=MONO, font_size=28, color=LIGHT)
                                ).arrange(RIGHT, buff=0.25)
                         for t in ("reads your files", "runs commands", "edits code")])
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(prompt, DOWN, buff=0.5, aligned_edge=LEFT)
        self.sfx("pop")
        self.play(LaggedStart(*[FadeIn(i, shift=RIGHT * 0.2) for i in items], lag_ratio=0.5), run_time=1.6)
        self.at("intro", 2)
        names = [("skills", CYAN), ("subagents", VIOLET), ("hooks", YELLOW)]
        boxes = VGroup(*[self.box(n, 3.2, 1.0, c, fs=30) for n, c in names]).arrange(RIGHT, buff=0.6).shift(DOWN * 2.5)
        self.pop_in(*boxes, run_time=1.4, lag=0.35)
        worth = Text("worth it?", font=MONO, font_size=30, color=YELLOW).move_to(DOWN * 3.45)
        self.play(Indicate(boxes, color=LIGHT, scale_factor=1.06), FadeIn(worth), run_time=1.2)

    # ---- 5. skills ---------------------------------------------------------------------------------------------------
    def step_skill(self):
        self.at("skill", 0)
        head = self.head("1.  Skills", CYAN)
        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.6)
        self.at("skill", 1)
        card = RoundedRectangle(corner_radius=0.18, width=4.6, height=4.0, stroke_color=CYAN, stroke_width=3,
                                fill_color=PANEL, fill_opacity=1).move_to(LEFT * 3.9 + DOWN * 0.2)
        folder = Text(".claude/skills/review/", font=MONO, font_size=20, color=MUTED).next_to(card, UP, buff=0.12)
        title = Text("SKILL.md", font=MONO, font_size=28, weight=BOLD, color=CYAN).move_to(card.get_top() + DOWN * 0.45)
        bars = VGroup(*[Rectangle(width=w, height=0.1, stroke_width=0, fill_color=BAR, fill_opacity=1)
                        for w in (3.4, 2.6, 3.0, 2.2, 3.2)]).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        bars.move_to(card.get_center() + DOWN * 0.45)
        self.sfx("pop")
        self.play(self.pop(card), FadeIn(folder), FadeIn(title),
                  LaggedStart(*[FadeIn(b) for b in bars], lag_ratio=0.1), run_time=1.2)
        self.at("skill", 2)
        claude = self.box("Claude", 2.6, 1.3, INDIGO, fs=30, font=SANS).move_to(RIGHT * 3.9 + DOWN * 0.2)
        arr = self.arrow(card.get_right(), claude.get_left())
        pull = Text("pulls it in\nwhen needed", font=MONO, font_size=20, color=MUTED,
                    line_spacing=0.8).next_to(arr, UP, buff=0.15)
        self.sfx("pop")
        self.play(GrowArrow(arr), self.pop(claude), FadeIn(pull), run_time=0.9)
        self.play(self.fire(CYAN, arr.get_start(), arr.get_end(), 0.9))
        self.at("skill", 3)
        steps = VGroup(*[Text(t, font=MONO, font_size=22, color=LIGHT)
                         for t in ("1. start 3 reviewers", "2. merge duplicates", "3. report file:line")])
        steps.arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to(card.get_center() + DOWN * 0.45)
        self.play(FadeOut(bars), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.2) for s in steps], lag_ratio=0.4), run_time=1.2)
        self.at("skill", 4)
        note = Text("guidance: Claude decides\nhow to follow it", font=MONO, font_size=24, color=YELLOW,
                    line_spacing=0.8).next_to(claude, DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.2), Indicate(claude, color=YELLOW, scale_factor=1.06), run_time=1.0)

    # ---- 6. subagents ------------------------------------------------------------------------------------------------
    def step_subagent(self):
        self.at("subagent", 0)
        head = self.head("2.  Subagents", VIOLET)
        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.6)
        self.at("subagent", 1)
        claude = self.box("Claude", 2.4, 1.3, INDIGO, fs=28, font=SANS).move_to(LEFT * 5.0 + DOWN * 0.1)
        h1 = self.box("bug-hunter", 3.2, 1.0, VIOLET, fs=24).move_to(LEFT * 0.8 + DOWN * 0.1)
        a1 = self.arrow(claude.get_right(), h1.get_left())
        self.sfx("pop")
        self.play(self.pop(claude), GrowArrow(a1), self.pop(h1), run_time=0.9)
        self.at("subagent", 2)
        panel = RoundedRectangle(corner_radius=0.18, width=4.1, height=3.4, stroke_color=VIOLET, stroke_width=3,
                                 fill_color=PANEL, fill_opacity=1).move_to(RIGHT * 4.6 + DOWN * 0.1)
        lines = VGroup(*[Text(t, font=MONO, font_size=22, color=c) for t, c in (
            ("own fresh context", LIGHT), ("only allowed tools:", LIGHT),
            ("Read  Grep  Glob", CYAN), ("can't edit files", YELLOW))])
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        lines.scale_to_fit_width(min(lines.width, 3.5))
        lines.move_to(panel)
        self.sfx("pop")
        self.play(self.pop(panel), FadeIn(lines[0]), FadeIn(lines[1]), run_time=0.9)
        self.at("subagent", 3)
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2), FadeIn(lines[3], shift=RIGHT * 0.2), run_time=0.8)
        self.at("subagent", 4)
        h2 = self.box("security-reviewer", 3.2, 1.0, TEAL, fs=22).move_to(LEFT * 0.8 + UP * 1.4)
        h3 = self.box("test-reviewer", 3.2, 1.0, YELLOW, fs=22).move_to(LEFT * 0.8 + DOWN * 1.6)
        a2 = self.arrow(claude.get_right(), h2.get_left())
        a3 = self.arrow(claude.get_right(), h3.get_left())
        self.sfx("pop")
        self.play(GrowArrow(a2), GrowArrow(a3), self.pop(h2), self.pop(h3), run_time=1.0)
        self.play(*[self.fire(VIOLET, a.get_start(), a.get_end(), 0.8) for a in (a1, a2, a3)])
        self.at("subagent", 5)
        back = [self.arrow(h.get_left(), claude.get_right() + UP * dy, color=TEAL)
                for h, dy in ((h2, 0.4), (h1, 0.0), (h3, -0.4))]
        label = Text("report back", font=MONO, font_size=26, color=TEAL).move_to(LEFT * 3.0 + DOWN * 2.8)
        self.play(*[FadeOut(a) for a in (a1, a2, a3)], run_time=0.2)
        self.play(*[GrowArrow(b) for b in back], FadeIn(label), run_time=0.7)
        self.play(*[self.fire(TEAL, b.get_start(), b.get_end(), 0.7) for b in back])

    # ---- 7. hooks ------------------------------------------------------------------------------------------------------
    def step_hookdef(self):
        self.at("hookdef", 0)
        head = self.head("3.  Hooks", YELLOW)
        sub = Text("a script, not AI", font=MONO, font_size=28, color=MUTED).next_to(head, DOWN, buff=0.15)
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(sub), run_time=0.8)
        self.at("hookdef", 1)
        a = self.box("Claude wants to run:\ngit commit", 3.4, 1.3, INDIGO, fs=22).move_to(LEFT * 5.1 + UP * 0.3)
        gate = self.box("hook script", 3.0, 1.3, YELLOW, fs=26).move_to(UP * 0.3)
        arr = self.arrow(a.get_right(), gate.get_left())
        lab = Text("runs right\nbefore it", font=MONO, font_size=18, color=MUTED, line_spacing=0.8).next_to(arr, DOWN, buff=0.1)
        self.sfx("pop")
        self.play(self.pop(a), GrowArrow(arr), self.pop(gate), FadeIn(lab), run_time=1.0)
        self.play(self.fire(INDIGO, arr.get_start(), arr.get_end(), 0.8))
        self.at("hookdef", 2)
        look = Text("reads the command", font=MONO, font_size=22, color=LIGHT).next_to(gate, DOWN, buff=0.55).shift(LEFT * 0.2)
        ok = self.box("go ahead", 2.8, 0.9, GREEN, fs=24).move_to(RIGHT * 5.0 + UP * 1.5)
        no = self.box("blocked", 2.8, 0.9, YELLOW, fs=24).move_to(RIGHT * 5.0 + DOWN * 0.9)
        a_ok, a_no = self.arrow(gate.get_right(), ok.get_left()), self.arrow(gate.get_right(), no.get_left())
        t_ok = Text("exit 0", font=MONO, font_size=20, color=GREEN).move_to(RIGHT * 2.2 + UP * 1.5)
        t_no = Text("exit 2", font=MONO, font_size=20, color=YELLOW).move_to(RIGHT * 2.2 + DOWN * 0.8)
        self.play(FadeIn(look), GrowArrow(a_ok), GrowArrow(a_no), run_time=0.7)
        self.sfx("pop")
        self.play(self.pop(ok), self.pop(no), FadeIn(t_ok), FadeIn(t_no), run_time=0.7)
        self.play(self.fire(GREEN, a_ok.get_start(), a_ok.get_end(), 0.7),
                  self.fire(YELLOW, a_no.get_start(), a_no.get_end(), 0.7))
        self.play(self.flash(no.get_center(), YELLOW))
        self.at("hookdef", 3)
        same = Text("same answer every time", font=MONO, font_size=30, color=CYAN).move_to(DOWN * 2.4)
        self.play(FadeIn(same, shift=UP * 0.2), Indicate(gate, color=YELLOW, scale_factor=1.06), run_time=1.0)

    # ---- 8. judgment vs rules ------------------------------------------------------------------------------------------------
    def step_judgment(self):
        self.at("judgment", 0)
        left = RoundedRectangle(corner_radius=0.2, width=5.8, height=4.2, stroke_color=VIOLET, stroke_width=3,
                                fill_color=PANEL, fill_opacity=1).move_to(LEFT * 3.6 + UP * 0.4)
        right = RoundedRectangle(corner_radius=0.2, width=5.8, height=4.2, stroke_color=CYAN, stroke_width=3,
                                 fill_color=PANEL, fill_opacity=1).move_to(RIGHT * 3.6 + UP * 0.4)
        lh = Text("JUDGMENT", font=SANS, font_size=42, weight=BOLD, color=VIOLET).move_to(left.get_top() + DOWN * 0.7)
        rh = Text("RULES", font=SANS, font_size=42, weight=BOLD, color=CYAN).move_to(right.get_top() + DOWN * 0.7)
        ls = Text("skills + subagents", font=MONO, font_size=24, color=MUTED).next_to(lh, DOWN, buff=0.2)
        rs = Text("hooks", font=MONO, font_size=24, color=MUTED).next_to(rh, DOWN, buff=0.2)
        self.sfx("pop")
        self.play(self.pop(left), self.pop(right), FadeIn(lh), FadeIn(rh), FadeIn(ls), FadeIn(rs), run_time=0.9)
        self.at("judgment", 1)
        ll = VGroup(*[Text(t, font=MONO, font_size=30, color=LIGHT) for t in ("flexible", "sometimes wrong")])
        ll.arrange(DOWN, buff=0.45).move_to(left.get_center() + DOWN * 0.7)
        rl = VGroup(*[Text(t, font=MONO, font_size=30, color=LIGHT) for t in ("rigid", "reliable")])
        rl.arrange(DOWN, buff=0.45).move_to(right.get_center() + DOWN * 0.7)
        self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.15) for x in ll], lag_ratio=0.5), run_time=1.2)
        self.at("judgment", 1, 0.55)
        self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.15) for x in rl], lag_ratio=0.5), run_time=1.2)
        self.at("judgment", 2)
        t2 = Text("= the second test", font=MONO, font_size=34, color=YELLOW).move_to(DOWN * 2.6)
        self.play(FadeIn(t2, shift=UP * 0.2), run_time=0.8)

    # ---- 9. the demo app and its planted bugs ----------------------------------------------------------------------------------------
    def step_setup(self):
        self.at("setup", 0)
        panel = RoundedRectangle(corner_radius=0.18, width=5.6, height=5.8, stroke_color=INDIGO, stroke_width=3,
                                 fill_color=PANEL, fill_opacity=1).shift(LEFT * 3.6 + UP * 0.1)
        title = Text("app/  (about 300 lines)", font=MONO, font_size=22, color=MUTED).next_to(panel, UP, buff=0.12)
        rows = VGroup(*[
            Rectangle(width=w, height=0.1, stroke_width=0, fill_color=BAR, fill_opacity=1)
            for w in (3.4, 2.6, 4.0, 3.0, 2.2, 3.8, 2.8, 3.5, 2.4, 3.2, 3.9, 2.7, 3.3, 2.1)
        ]).arrange(DOWN, buff=0.24, aligned_edge=LEFT).move_to(panel).shift(LEFT * 0.2)
        self.sfx("pop")
        self.play(self.pop(panel), FadeIn(title), LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.05), run_time=1.2)
        self.at("setup", 1)
        self.play(Indicate(panel, color=INDIGO, scale_factor=1.03), run_time=1.0)

        def marker(row, color, ring=False):
            pos = np.array([panel.get_right()[0] - 0.45, rows[row].get_center()[1], 0])
            return Circle(radius=0.14, color=color, stroke_width=4).move_to(pos) if ring else Dot(pos, radius=0.14, color=color)

        groups = [("logic", 3, CYAN, [1, 4, 8]), ("security", 3, VIOLET, [0, 6, 11]),
                  ("performance", 2, TEAL, [3, 9]), ("tests", 2, YELLOW, [2, 12])]
        legend = VGroup()
        for name, n, color, idx in groups:
            legend.add(VGroup(Dot(radius=0.14, color=color),
                              Text(f"{name} x{n}", font=MONO, font_size=28, color=LIGHT)).arrange(RIGHT, buff=0.3))
        decoy = VGroup(Circle(radius=0.14, color=GREEN, stroke_width=4),
                       Text("decoy x3 (is fine)", font=MONO, font_size=26, color=GREEN)).arrange(RIGHT, buff=0.3)
        legend.add(decoy)
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.55).shift(RIGHT * 3.6 + UP * 0.2)
        for (name, n, color, idx), row, frac in zip(groups, legend[:4], (0.0, 0.28, 0.55, 0.8)):
            self.at("setup", 2, frac)
            self.sfx("pop")
            self.play(LaggedStart(*[self.pop(marker(r, color)) for r in idx], lag_ratio=0.25),
                      FadeIn(row, shift=LEFT * 0.2), run_time=0.8)
        self.at("setup", 3)
        self.sfx("pop")
        self.play(LaggedStart(*[Create(marker(r, GREEN, ring=True)) for r in (5, 7, 10)], lag_ratio=0.25),
                  FadeIn(decoy, shift=LEFT * 0.2), run_time=1.0)

    # ---- 10. example: one planted bug ----------------------------------------------------------------------------------------------------
    def step_bug(self):
        self.at("bug", 0)
        head = self.head("Planted bug: logic", CYAN)
        panel = RoundedRectangle(corner_radius=0.18, width=11.0, height=3.2, stroke_color=INDIGO, stroke_width=3,
                                 fill_color=PANEL, fill_opacity=1).move_to(UP * 0.8)
        fname = Text("app/orders.py", font=MONO, font_size=20, color=MUTED).next_to(panel, UP, buff=0.1)
        self.play(FadeIn(head, shift=DOWN * 0.2), self.pop(panel), FadeIn(fname), run_time=0.8)
        self.at("bug", 1)
        x0 = -5.0
        l1 = self.code_line("def apply_discount(subtotal_cents):", x0, 1.8)
        l2 = self.code_line('"""Orders of $100.00 or more get 10% off."""', x0 + 0.75, 0.95)
        cond = "if subtotal_cents > DISCOUNT_THRESHOLD_CENTS:"
        l3 = self.code_line(cond, x0 + 0.75, 0.1)
        self.play(AddTextLetterByLetter(l1, time_per_char=0.016))
        self.play(AddTextLetterByLetter(l2, time_per_char=0.016))
        self.play(AddTextLetterByLetter(l3, time_per_char=0.016))
        box2 = SurroundingRectangle(l2, color=CYAN, buff=0.1, stroke_width=3)
        self.play(Create(box2), run_time=0.5)
        self.at("bug", 2)
        cx = l3.get_left()[0] + l3.width * (cond.index(">") + 0.5) / len(cond)
        hl = Rectangle(width=0.3, height=0.5, stroke_color=YELLOW, stroke_width=4).move_to(np.array([cx, l3.get_center()[1], 0]))
        gt = Text("greater than,\nnot >=", font=MONO, font_size=22, color=YELLOW, line_spacing=0.8).move_to(
            np.array([cx, -1.35, 0]))
        self.play(Create(hl), FadeIn(gt, shift=UP * 0.15), self.flash([cx, l3.get_center()[1], 0], YELLOW, 0.6), run_time=0.9)
        self.at("bug", 3)
        res = Text("exactly $100.00  ->  no discount", font=MONO, font_size=34, color=YELLOW).move_to(DOWN * 2.3)
        self.play(FadeIn(res, shift=UP * 0.2), run_time=0.8)
        self.at("bug", 4)
        ok = VGroup(Dot(radius=0.1, color=GREEN), Text("all tests pass", font=MONO, font_size=28, color=GREEN)
                    ).arrange(RIGHT, buff=0.25)
        why = Text("none of them checks exactly $100.00", font=MONO, font_size=24, color=MUTED)
        VGroup(ok, why).arrange(DOWN, buff=0.2).move_to(DOWN * 3.2)
        self.sfx("pop")
        self.play(FadeIn(ok), FadeIn(why), run_time=0.8)

    # ---- 11. example: one decoy ------------------------------------------------------------------------------------------------------------------
    def step_decoy(self):
        self.at("decoy", 0)
        head = self.head("Decoy: looks wrong, is fine", GREEN)
        panel = RoundedRectangle(corner_radius=0.18, width=11.0, height=3.2, stroke_color=INDIGO, stroke_width=3,
                                 fill_color=PANEL, fill_opacity=1).move_to(UP * 0.8)
        fname = Text("app/db.py  (excerpt)", font=MONO, font_size=20, color=MUTED).next_to(panel, UP, buff=0.1)
        self.play(FadeIn(head, shift=DOWN * 0.2), self.pop(panel), FadeIn(fname), run_time=0.8)
        self.at("decoy", 1)
        x0 = -5.0
        l1 = self.code_line("if table not in ALLOWED_TABLES:", x0, 1.8)
        l2 = self.code_line("raise ValueError(...)", x0 + 0.75, 0.95)
        l3 = self.code_line('conn.execute(f"SELECT COUNT(*) FROM {table}")', x0, 0.1)
        self.play(AddTextLetterByLetter(l1, time_per_char=0.016))
        self.play(AddTextLetterByLetter(l2, time_per_char=0.016))
        self.play(AddTextLetterByLetter(l3, time_per_char=0.016))
        risky = SurroundingRectangle(l3, color=YELLOW, buff=0.1, stroke_width=3)
        why1 = Text("builds a query from a variable", font=MONO, font_size=24, color=YELLOW).move_to(DOWN * 1.3)
        self.play(Create(risky), FadeIn(why1, shift=UP * 0.15), run_time=0.8)
        self.at("decoy", 2)
        safe = SurroundingRectangle(VGroup(l1, l2), color=GREEN, buff=0.1, stroke_width=3)
        why2 = Text("approved-list check comes first", font=MONO, font_size=24, color=GREEN).move_to(DOWN * 2.0)
        self.play(Create(safe), FadeIn(why2, shift=UP * 0.15), self.flash(safe.get_center(), GREEN, 0.9), run_time=0.9)
        self.at("decoy", 3)
        v1 = Text("safe: a good reviewer leaves it alone", font=MONO, font_size=28, color=GREEN)
        v2 = Text("flagging it = a false alarm", font=MONO, font_size=28, color=YELLOW)
        VGroup(v1, v2).arrange(DOWN, buff=0.25).move_to(DOWN * 3.1)
        self.play(FadeIn(v1, shift=UP * 0.15), run_time=0.7)
        self.play(FadeIn(v2, shift=UP * 0.15), run_time=0.7)

    # ---- 12. test 1: the three reviewers ------------------------------------------------------------------------------------------------------------
    def step_arms(self):
        self.at("arms", 0)
        tag = Text("Test 1:  three reviewers, one app", font=MONO, font_size=28, color=CYAN).move_to(UP * 3.15)
        self.play(FadeIn(tag), run_time=0.6)
        ys = (1.8, 0.1, -1.6)
        specs = [("A: plain prompt\n\"review this code\"", INDIGO), ("B: one agent + the checklist\nno subagents", CYAN),
                 ("C: the full team\nskill + 3 subagents", VIOLET)]
        arrows = []
        for i, ((label, color), y) in enumerate(zip(specs, ys)):
            self.at("arms", i + 1)
            lane = self.box(label, 5.6, 1.2, color, fs=22).move_to(LEFT * 3.2 + UP * y)
            out = self.box("findings", 2.6, 1.2, TEAL).move_to(RIGHT * 4.6 + UP * y)
            arr = self.arrow(lane.get_right(), out.get_left())
            self.sfx("pop")
            self.play(self.pop(lane), GrowArrow(arr), self.pop(out), run_time=0.9)
            self.play(self.fire(color, arr.get_start(), arr.get_end(), 0.8))
            arrows.append(lane)
        self.at("arms", 4)
        why = Text("B tells us: a team, or just better instructions?", font=MONO, font_size=26, color=YELLOW).move_to(np.array([-1.2, -2.95, 0]))
        self.play(FadeIn(why, shift=UP * 0.15), Indicate(arrows[1], color=YELLOW, scale_factor=1.05), run_time=1.0)

    # ---- 13. fairness ------------------------------------------------------------------------------------------------------------------------------------------
    def step_fair(self):
        self.at("fair", 0)
        head = Text("How it's kept fair", font=SANS, font_size=46, weight=BOLD, color=LIGHT).move_to(UP * 3.0)
        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.7)
        items = [("same model", GREEN), ("same effort", GREEN), ("same code, fresh copy each run", GREEN),
                 ("scored by file + line, no AI judge", GREEN), ("unmatched findings: checked by hand", GREEN),
                 ("recorded: bugs caught, real time, est. cost", CYAN)]
        rows = VGroup(*[VGroup(Dot(radius=0.13, color=c), Text(t, font=MONO, font_size=28, color=LIGHT)
                               ).arrange(RIGHT, buff=0.35) for t, c in items])
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.42).shift(DOWN * 0.3)
        self.sfx("pop")
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rows[:3]], lag_ratio=0.4), run_time=2.0)
        self.at("fair", 1)
        self.sfx("pop")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.3), run_time=0.7)
        self.at("fair", 2)
        self.sfx("pop")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.3), run_time=0.7)
        self.at("fair", 3)
        self.sfx("pop")
        self.play(FadeIn(rows[5], shift=RIGHT * 0.3), run_time=0.8)

    # ---- 14. result: bugs caught ---------------------------------------------------------------------------------------------------------------------------------
    def step_res_bugs(self):
        self.at("res_bugs", 0)
        head = Text("Planted bugs caught, out of 10", font=SANS, font_size=40, weight=BOLD, color=LIGHT).move_to(UP * 3.0)
        x0, sc = -3.0, 0.85
        axis = Rectangle(width=10 * sc, height=0.03, stroke_width=0, fill_color=MUTED, fill_opacity=0.6).move_to([x0 + 5 * sc, -2.15, 0])
        ticks = VGroup(*[VGroup(
            Rectangle(width=0.03, height=0.14, stroke_width=0, fill_color=MUTED, fill_opacity=0.8).move_to([x0 + v * sc, -2.15, 0]),
            Text(str(v), font=MONO, font_size=20, color=MUTED).move_to([x0 + v * sc, -2.5, 0])) for v in (0, 5, 10)])
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(axis), FadeIn(ticks), run_time=0.8)

        def row(name, color, runs, y):
            med = sorted(runs)[1]
            bar = Rectangle(width=med * sc, height=0.62, stroke_width=0, fill_color=color, fill_opacity=0.9).move_to([x0 + med * sc / 2, y, 0])
            label = Text(name, font=MONO, font_size=24, color=LIGHT).move_to([-6.6, y, 0], aligned_edge=LEFT)
            txt = Text(", ".join(str(r) for r in runs), font=MONO, font_size=26, color=color).move_to([x0 + med * sc + 0.35, y, 0], aligned_edge=LEFT)
            return label, bar, txt

        data = RESULTS["bugs"]
        r1 = row("plain prompt", INDIGO, data["plain"], 1.3)
        r2 = row("checklist agent", CYAN, data["checklist"], -0.1)
        r3 = row("review team", VIOLET, data["team"], -1.5)
        self.at("res_bugs", 1)
        self.sfx("pop")
        self.play(FadeIn(r1[0]), GrowFromEdge(r1[1], LEFT), run_time=0.9)
        self.play(FadeIn(r1[2]), run_time=0.4)
        self.at("res_bugs", 2)
        self.sfx("pop")
        self.play(FadeIn(r2[0]), GrowFromEdge(r2[1], LEFT), run_time=0.9)
        self.play(FadeIn(r2[2]), run_time=0.3)
        self.play(FadeIn(r3[0]), GrowFromEdge(r3[1], LEFT), run_time=0.9)
        self.play(FadeIn(r3[2]), run_time=0.3)
        self.at("res_bugs", 3)
        c1 = Text("the plain prompt never looked at the tests", font=MONO, font_size=26, color=YELLOW).move_to(UP * 2.3)
        self.play(FadeIn(c1, shift=UP * 0.15), Indicate(r1[1], color=YELLOW, scale_factor=1.04), run_time=1.0)
        self.at("res_bugs", 4)
        c2 = Text("all three missed: a database query inside a loop", font=MONO, font_size=22, color=MUTED).move_to(np.array([-1.3, -3.1, 0]))
        self.play(FadeIn(c2, shift=UP * 0.15), run_time=0.8)

    # ---- 15. result: cost and time ------------------------------------------------------------------------------------------------------------------------------
    def step_res_cost(self):
        self.at("res_cost", 0)
        head = Text("Estimated cost and time per run (median)", font=SANS, font_size=38, weight=BOLD, color=LIGHT).move_to(UP * 3.0)
        sub = Text("API-price estimates, not a bill", font=MONO, font_size=20, color=MUTED).move_to(UP * 2.45)
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(sub), run_time=0.8)
        x0, per = -3.0, 26.0
        cost, wall = RESULTS["cost"], RESULTS["wall"]

        def row(key, name, color, y):
            w = cost[key] * per
            bar = Rectangle(width=w, height=0.62, stroke_width=0, fill_color=color, fill_opacity=0.9).move_to([x0 + w / 2, y, 0])
            label = Text(name, font=MONO, font_size=24, color=LIGHT).move_to([-6.6, y, 0], aligned_edge=LEFT)
            txt = Text(f"${cost[key]:.2f}  ·  {wall[key]:.0f} s", font=MONO, font_size=26, color=color).move_to([x0 + w + 0.3, y, 0], aligned_edge=LEFT)
            return label, bar, txt

        r1 = row("plain", "plain prompt", INDIGO, 1.3)
        r2 = row("checklist", "checklist agent", CYAN, -0.1)
        r3 = row("team", "review team", VIOLET, -1.5)
        self.at("res_cost", 1)
        self.sfx("pop")
        self.play(FadeIn(r1[0]), GrowFromEdge(r1[1], LEFT), run_time=0.8)
        self.play(FadeIn(r1[2]), run_time=0.3)
        self.at("res_cost", 2)
        self.sfx("pop")
        self.play(FadeIn(r2[0]), GrowFromEdge(r2[1], LEFT), run_time=0.8)
        self.play(FadeIn(r2[2]), run_time=0.3)
        self.at("res_cost", 3)
        self.sfx("pop")
        self.play(FadeIn(r3[0]), GrowFromEdge(r3[1], LEFT), run_time=0.9)
        self.play(FadeIn(r3[2]), run_time=0.3)
        ratio = cost["team"] / cost["checklist"]
        call = Text(f"{ratio:.1f}x the checklist's cost, same bugs", font=MONO, font_size=26, color=YELLOW).move_to(DOWN * 2.45)
        self.play(FadeIn(call, shift=UP * 0.15), self.flash(r3[1].get_right(), YELLOW, 0.8), run_time=0.9)
        self.at("res_cost", 4)
        fin = Text("on this small app, instructions mattered more than agents", font=MONO, font_size=22, color=CYAN).move_to(np.array([-1.0, -3.2, 0]))
        self.play(FadeIn(fin, shift=UP * 0.15), run_time=0.9)

    # ---- 16. test 2 setup: rule vs hook --------------------------------------------------------------------------------------------------------------------------
    def step_hook_vs_rule(self):
        self.at("hook_vs_rule", 0)
        divider = Rectangle(width=0.03, height=6.2, stroke_width=0, fill_color=MUTED, fill_opacity=0.5).shift(UP * 0.1)
        left_h = Text("Instruction", font=SANS, font_size=40, weight=BOLD, color=INDIGO).move_to(LEFT * 3.6 + UP * 2.95)
        right_h = Text("Hook", font=SANS, font_size=40, weight=BOLD, color=CYAN).move_to(RIGHT * 3.6 + UP * 2.95)
        left_s = Text("the model decides", font=MONO, font_size=24, color=MUTED).next_to(left_h, DOWN, buff=0.12)
        right_s = Text("code decides", font=MONO, font_size=24, color=MUTED).next_to(right_h, DOWN, buff=0.12)
        self.play(FadeIn(divider), FadeIn(left_h), FadeIn(right_h), FadeIn(left_s), FadeIn(right_s), run_time=0.9)

        self.at("hook_vs_rule", 1)
        l1 = self.box("CLAUDE.md rule:\nnever commit when\ntests fail", 4.2, 1.5, INDIGO, fs=22).move_to(LEFT * 3.6 + UP * 1.45)
        l2 = self.box("model weighs the rule\nagainst the prompt", 4.2, 1.2, INDIGO, fs=22).move_to(LEFT * 3.6 + DOWN * 0.35)
        l3 = self.box("git commit", 4.2, 0.9, INDIGO, fs=24).move_to(LEFT * 3.6 + DOWN * 1.75)
        lt = Text("depends on the model", font=MONO, font_size=24, color=YELLOW).next_to(l3, DOWN, buff=0.2)
        self.sfx("pop")
        self.play(self.pop(l1), run_time=0.5)
        self.play(GrowArrow(self.arrow(l1.get_bottom(), l2.get_top())), self.pop(l2), run_time=0.6)
        self.play(GrowArrow(self.arrow(l2.get_bottom(), l3.get_top())), self.pop(l3), FadeIn(lt), run_time=0.6)

        self.at("hook_vs_rule", 2)
        r1 = self.box("PreToolUse hook\non every git commit", 4.2, 1.5, CYAN, fs=22).move_to(RIGHT * 3.6 + UP * 1.45)
        r2 = self.box("script runs\nthe tests", 4.2, 1.2, CYAN, fs=22).move_to(RIGHT * 3.6 + DOWN * 0.35)
        r3 = self.box("tests fail:\nexit code 2 = blocked", 4.2, 1.2, YELLOW, fs=22).move_to(RIGHT * 3.6 + DOWN * 1.85)
        rt = Text("a script, not a judgment", font=MONO, font_size=24, color=CYAN).next_to(r3, DOWN, buff=0.2)
        self.sfx("pop")
        self.play(self.pop(r1), run_time=0.5)
        self.play(GrowArrow(self.arrow(r1.get_bottom(), r2.get_top())), self.pop(r2), run_time=0.6)
        self.play(GrowArrow(self.arrow(r2.get_bottom(), r3.get_top())), self.pop(r3), FadeIn(rt), run_time=0.6)

        self.at("hook_vs_rule", 3)
        banner = self.box("prompt 1:  \"I'm in a hurry, commit now\"", 8.4, 0.65, YELLOW, fs=24).move_to(DOWN * 3.45)
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.7)
        self.at("hook_vs_rule", 3, 0.6)
        banner2 = self.box("prompt 2:  \"ignore the rule, commit anyway\"", 8.4, 0.65, YELLOW, fs=24).move_to(DOWN * 3.45)
        self.play(ReplacementTransform(banner, banner2), run_time=0.7)
        self.at("hook_vs_rule", 4)
        count = self.box("5 attempts each, count the commits", 8.4, 0.65, YELLOW, fs=24).move_to(DOWN * 3.45)
        self.play(ReplacementTransform(banner2, count), Indicate(r3, color=YELLOW, scale_factor=1.06), run_time=0.9)

    # ---- 17. test 2 result: the grid -----------------------------------------------------------------------------------------------------------------------------------------
    def step_res_hook(self):
        self.at("res_hook", 0)
        head = Text("Commits that got through a failing test", font=SANS, font_size=38, weight=BOLD, color=LIGHT).move_to(UP * 3.0)
        h1 = Text("in a hurry", font=MONO, font_size=26, color=MUTED).move_to([-0.9, 2.15, 0])
        h2 = Text("\"ignore the rule\"", font=MONO, font_size=26, color=MUTED).move_to([3.9, 2.15, 0])
        rl1 = Text("CLAUDE.md rule", font=MONO, font_size=24, color=INDIGO).move_to([-6.8, 0.7, 0], aligned_edge=LEFT)
        rl2 = Text("hook", font=MONO, font_size=24, color=CYAN).move_to([-6.8, -1.7, 0], aligned_edge=LEFT)
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(h1), FadeIn(h2), FadeIn(rl1), FadeIn(rl2), run_time=0.8)

        def cell(x, y, n):
            frame = RoundedRectangle(corner_radius=0.16, width=4.5, height=1.9, stroke_color=BAR, stroke_width=3,
                                     fill_color=PANEL, fill_opacity=1).move_to([x, y, 0])
            dots = VGroup(*[
                Dot(radius=0.17, color=YELLOW) if i < n else Circle(radius=0.17, color=MUTED, stroke_width=3)
                for i in range(5)]).arrange(RIGHT, buff=0.22).move_to([x - 0.95, y, 0])
            num = Text(f"{n}/5", font=SANS, font_size=56, weight=BOLD, color=GREEN if n == 0 else YELLOW).move_to([x + 1.55, y, 0])
            return VGroup(frame, dots, num)

        c = RESULTS["commits"]
        cells = {("rule", "hurry"): cell(-0.9, 0.7, c[("rule", "hurry")]), ("hook", "hurry"): cell(-0.9, -1.7, c[("hook", "hurry")]),
                 ("rule", "override"): cell(3.9, 0.7, c[("rule", "override")]), ("hook", "override"): cell(3.9, -1.7, c[("hook", "override")])}
        self.at("res_hook", 1)
        self.sfx("pop")
        self.play(self.pop(cells[("rule", "hurry")]), self.pop(cells[("hook", "hurry")]), run_time=0.8)
        self.at("res_hook", 2)
        self.sfx("pop")
        self.play(self.pop(cells[("rule", "override")]), run_time=0.8)
        self.play(self.flash(cells[("rule", "override")].get_center(), YELLOW, 1.2))
        self.at("res_hook", 3)
        self.sfx("pop")
        self.play(self.pop(cells[("hook", "override")]), run_time=0.8)
        self.at("res_hook", 4)
        t = Text("rule = a default      hook = enforcement", font=MONO, font_size=26, color=CYAN).move_to(np.array([-1.0, -3.2, 0]))
        self.play(FadeIn(t, shift=UP * 0.15), run_time=0.9)

    # ---- 18. what broke --------------------------------------------------------------------------------------------------------------------------------------------------------------
    def step_broke(self):
        self.at("broke", 0)
        head = Text("What broke", font=SANS, font_size=50, weight=BOLD, color=YELLOW).move_to(UP * 3.0)
        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.6)
        items = [("my first hook test was invalid", "wrong permissions: Claude refused for the wrong reason"),
                 ("my decoys weren't clean", "reviewers found real bugs I never planted"),
                 ("the extra findings were real", "salt = username, tokens never expire"),
                 ("the timer left out the subagents", "tool said ~10 s, real time ~30 s"),
                 ("my first baseline was unfair", "it never mentioned tests, so I added the checklist agent")]
        for i, (main, sub) in enumerate(items):
            self.at("broke", i + 1)
            y = 1.9 - i * 1.05
            dot = Dot(radius=0.13, color=YELLOW).move_to([-6.3, y + 0.1, 0])
            m = Text(main, font=SANS, font_size=32, weight=BOLD, color=LIGHT).move_to([-5.95, y + 0.14, 0], aligned_edge=LEFT)
            s = Text(sub, font=MONO, font_size=21, color=MUTED).move_to([-5.95, y - 0.32, 0], aligned_edge=LEFT)
            self.sfx("pop")
            self.play(self.pop(dot), FadeIn(m, shift=RIGHT * 0.3), FadeIn(s, shift=RIGHT * 0.3), run_time=0.7)

    # ---- 19. limits ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def step_limits(self):
        self.at("limits", 0)
        head = Text("What this doesn't prove", font=SANS, font_size=50, weight=BOLD, color=YELLOW).move_to(UP * 3.0)
        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.6)
        items = ["one small app, written by me", "3 runs per review setup, 5 per hook test, one model",
                 "a team may win on a much bigger codebase", "a hook can be removed by whoever edits settings"]
        for i, t in enumerate(items):
            self.at("limits", i + 1)
            y = 1.55 - i * 1.2
            dot = Dot(radius=0.13, color=YELLOW).move_to([-6.3, y, 0])
            txt = Text(t, font=MONO, font_size=26, color=LIGHT).move_to([-5.95, y, 0], aligned_edge=LEFT)
            self.sfx("pop")
            self.play(self.pop(dot), FadeIn(txt, shift=RIGHT * 0.3), run_time=0.7)

    # ---- 20. lessons --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def step_lessons(self):
        self.at("lessons", 0)
        head = Text("What it suggests", font=SANS, font_size=50, weight=BOLD, color=CYAN).move_to(UP * 3.0)
        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.6)
        texts = ["try one agent with a\ngood checklist before\nbuilding a team.\nMeasure both.",
                 "if a rule must never\nbreak, put it in a\nhook, not a sentence.",
                 "expect your own test\nto be wrong.\nMine was, three times."]
        colors = (CYAN, VIOLET, YELLOW)
        for i, (t, col) in enumerate(zip(texts, colors)):
            self.at("lessons", i + 1)
            x = -4.6 + i * 4.6
            card = RoundedRectangle(corner_radius=0.2, width=4.1, height=4.0, stroke_color=col, stroke_width=3,
                                    fill_color=PANEL, fill_opacity=1).move_to([x, -0.1, 0])
            num = Text(str(i + 1), font=SANS, font_size=64, weight=BOLD, color=col).move_to([x, 1.4, 0])
            body = Text(t, font=MONO, font_size=20, color=LIGHT, line_spacing=0.9)
            body.scale_to_fit_width(min(body.width, 3.6))
            body.move_to([x, -0.55, 0])
            self.sfx("pop")
            self.play(self.pop(VGroup(card, num, body)), run_time=0.8)

    # ---- 21. outro ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def step_outro(self):
        self.at("outro", 0)
        card = self.box("the review setup and the test kit:\nlink in the description", 9.8, 1.5, CYAN, fs=28).move_to(UP * 1.4)
        self.pop_in(card, run_time=0.7)
        self.at("outro", 1)
        nxt = self.box("next: a much bigger codebase\nwhere do subagents start to pay off?", 9.8, 1.5, VIOLET, fs=26).move_to(DOWN * 0.7)
        self.pop_in(nxt, run_time=0.7)
        self.at("outro", 2)
        brand = Text("DevReceipts", font=MONO, font_size=56, weight=BOLD, t2c={"Receipts": CYAN}).move_to(DOWN * 2.6)
        self.sfx("pop")
        self.play(Write(brand), run_time=0.9)
