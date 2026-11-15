#!/usr/bin/env python3
"""Score review runs against the answer key.

Usage:
    python3 eval/score.py                      # scores eval/results/{baseline,team}-run*.json
    python3 eval/score.py path/to/run.json ... # score specific files

Each run file is the JSON printed by `claude -p ... --output-format json`.
Findings are lines containing `FINDING: path/to/file.py:LINE ...`.

Scoring rules (deterministic, no LLM judge):
  - A finding catches a planted bug if the file matches and the line is inside
    the bug's range (+/- tolerance from bugs.json). Each bug counts once.
  - Otherwise, if it lands on a decoy, it is a decoy hit (a false alarm).
  - Otherwise it is "unmatched": a human must decide if it is a real bug that
    was not planted or a false alarm. Put verdicts in eval/manual_verdicts.json:
        {"team-run1.json|app/auth.py:40": "real_bug" | "false_alarm"}
    Unmatched findings with no verdict are counted as false alarms in the
    "strict" column and listed for review.
"""
import json
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEY_PATH = HERE / "bugs.json"
VERDICTS_PATH = HERE / "manual_verdicts.json"
RESULTS_DIR = HERE / "results"

FINDING_RE = re.compile(r"FINDING:\s*`?([\w./\\-]+?\.py):(\d+)(?:-\d+)?`?(.*)")


def load_key(path=KEY_PATH):
    return json.loads(Path(path).read_text())


def parse_findings(text):
    """Return a list of (file, line, rest_of_line) from FINDING: lines."""
    found = []
    for raw in (text or "").splitlines():
        m = FINDING_RE.search(raw.replace("**", ""))
        if m:
            path = m.group(1).replace("\\", "/").lstrip("./")
            found.append((path, int(m.group(2)), m.group(3).strip(" |`")))
    return found


def _same_file(a, b):
    return a == b or a.endswith("/" + b) or b.endswith("/" + a)


def _in_range(item, path, line, tol):
    return _same_file(path, item["file"]) and item["start"] - tol <= line <= item["end"] + tol


def score_findings(findings, key):
    tol = key.get("tolerance_lines", 2)
    caught, decoy_hits, unmatched, duplicates = set(), [], [], 0
    seen = set()
    for path, line, rest in findings:
        if (path, line) in seen:
            duplicates += 1
            continue
        seen.add((path, line))
        bug = next((b for b in key["bugs"] if _in_range(b, path, line, tol)), None)
        if bug:
            if bug["id"] in caught:
                duplicates += 1
            caught.add(bug["id"])
            continue
        decoy = next((d for d in key["decoys"] if _in_range(d, path, line, tol)), None)
        if decoy:
            decoy_hits.append(f"{decoy['id']} {path}:{line}")
            continue
        unmatched.append({"loc": f"{path}:{line}", "text": rest})
    return {
        "caught": sorted(caught),
        "decoy_hits": decoy_hits,
        "unmatched": unmatched,
        "duplicates": duplicates,
        "total_findings": len(findings),
    }


def score_text(text, key=None):
    return score_findings(parse_findings(text), key or load_key())


def run_stats(data):
    usage = data.get("usage") or {}
    tokens = sum(
        usage.get(k, 0) or 0
        for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    )
    return {
        "duration_s": round((data.get("duration_ms") or 0) / 1000, 1),
        "cost_usd_est": data.get("total_cost_usd"),
        "turns": data.get("num_turns"),
        "tokens_main_thread": tokens,
        "output_tokens": usage.get("output_tokens"),
        "is_error": data.get("is_error"),
        "subtype": data.get("subtype"),
    }


def score_file(path, key, verdicts):
    data = json.loads(Path(path).read_text())
    res = score_findings(parse_findings(data.get("result", "")), key)
    res.update(run_stats(data))
    res["file"] = Path(path).name
    wall = Path(path).with_suffix(".wall")
    res["wall_s"] = float(wall.read_text()) if wall.exists() else None
    verdict_of = lambda u: verdicts.get(f"{res['file']}|{u['loc']}")  # noqa: E731
    res["unmatched_real"] = [u for u in res["unmatched"] if verdict_of(u) == "real_bug"]
    confirmed_false = sum(1 for u in res["unmatched"] if verdict_of(u) == "false_alarm")
    # strict: every decoy hit and every unmatched finding counts as a false alarm
    res["false_alarms_strict"] = len(res["decoy_hits"]) + len(res["unmatched"])
    # reviewed: only decoy hits and unmatched findings a human confirmed as false
    res["false_alarms_reviewed"] = len(res["decoy_hits"]) + confirmed_false
    res["awaiting_review"] = sum(1 for u in res["unmatched"] if verdict_of(u) is None)
    return res


def fmt(v):
    return "n/a" if v is None else (f"{v:.4f}" if isinstance(v, float) else str(v))


def main(argv):
    key = load_key()
    verdicts = json.loads(VERDICTS_PATH.read_text()) if VERDICTS_PATH.exists() else {}
    files = [Path(a) for a in argv] or sorted(RESULTS_DIR.glob("baseline-run*.json")) + sorted(
        RESULTS_DIR.glob("checklist-run*.json")) + sorted(RESULTS_DIR.glob("team-run*.json"))
    if not files:
        print("No result files found in eval/results/. Run eval/run_eval.sh first.")
        return 1
    rows = [score_file(f, key, verdicts) for f in files]
    print("| run | caught /10 | decoy hits | unmatched | wall s | cli duration s | est. cost USD | turns | main-thread tokens | error |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(
            f"| {r['file']} | {len(r['caught'])} | {len(r['decoy_hits'])} | {len(r['unmatched'])} "
            f"| {fmt(r['wall_s'])} | {r['duration_s']} | {fmt(r['cost_usd_est'])} | {fmt(r['turns'])} | {r['tokens_main_thread']} "
            f"| {r['subtype'] if r['is_error'] else ''} |"
        )
    print()
    for arm in ("baseline", "checklist", "team"):
        arm_rows = [r for r in rows if r["file"].startswith(arm)]
        if arm_rows:
            caught = [len(r["caught"]) for r in arm_rows]
            print(
                f"{arm}: runs={len(arm_rows)} median caught={statistics.median(caught)}/10 "
                f"(min {min(caught)}, max {max(caught)}), "
                f"median wall-clock={statistics.median(r['wall_s'] if r['wall_s'] is not None else r['duration_s'] for r in arm_rows)}s "
                f"(CLI duration omits subagent time)"
            )
    print("\nMissed bugs per run:")
    all_ids = [b["id"] for b in key["bugs"]]
    for r in rows:
        print(f"  {r['file']}: {', '.join(i for i in all_ids if i not in r['caught']) or 'none'}")
    print("\nUnmatched findings (decide: real_bug or false_alarm, record in eval/manual_verdicts.json):")
    any_unmatched = False
    for r in rows:
        for u in r["unmatched"]:
            any_unmatched = True
            print(f"  {r['file']}|{u['loc']}  {u['text'][:100]}")
    if not any_unmatched:
        print("  none")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
