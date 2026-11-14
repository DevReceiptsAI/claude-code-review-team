#!/bin/bash
# Headless review eval. Uses your Claude Code plan login: NO API key, nothing billed.
#
#   eval/run_eval.sh pilot        1 baseline run + 1 team run (do this first)
#   eval/run_eval.sh full [N]     N runs of each arm, default 3
#
# Arms (same model, same effort, same code; only difference is the .claude/ folder):
#   baseline: plain "review this code" prompt, demo-app copied WITHOUT .claude/
#   checklist: one agent given the skill's checklist inline, no subagents
#   team:     "use the review skill" prompt, demo-app copied WITH .claude/ (skill + 3 subagents)
#
# Check /usage before and after and write the numbers in METRICS.md.
set -euo pipefail

# An API key in the environment would override your plan login and bill you.
unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
if [ -f "$ROOT/.env" ]; then set -a; . "$ROOT/.env"; set +a; fi
MODEL="${MODEL:-sonnet}"
EFFORT="${EFFORT:-medium}"
MAX_BUDGET_USD="${MAX_BUDGET_USD:-3}"   # runaway guard per run (estimated cost, not billing)

MODE="${1:-}"
N=1
if [ "$MODE" = "full" ]; then N="${2:-3}"; elif [ "$MODE" != "pilot" ]; then
  echo "usage: $0 pilot | full [N]" >&2; exit 1
fi
command -v claude >/dev/null || { echo "claude CLI not found" >&2; exit 1; }

FORMAT_RULE='Report each issue on its own line as: FINDING: path/to/file.py:LINE | short description'
mkdir -p "$HERE/results"

run_one() {
  local arm="$1" n="$2" out work prompt
  out="$HERE/results/${arm}-run${n}.json"
  if [ -e "$out" ] && [ "${FORCE:-0}" != "1" ]; then
    echo "skip: $out exists (set FORCE=1 to overwrite)"; return 0
  fi
  work="$(mktemp -d)"
  cp -R "$ROOT/demo-app" "$work/demo-app"
  find "$work" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
  rm -rf "$work/demo-app/.pytest_cache"
  tools="Read Grep Glob Agent"
  if [ "$arm" = "baseline" ]; then
    rm -rf "$work/demo-app/.claude"
    prompt="Review this code for problems. $FORMAT_RULE"
  elif [ "$arm" = "checklist" ]; then
    # one agent, the same checklist as the skill, but NO subagents (Agent tool not allowed)
    rm -rf "$work/demo-app/.claude"
    tools="Read Grep Glob"
    prompt="Review the Python code in app/ and tests/ for: (1) logic errors and performance problems, (2) security problems, (3) weak, misleading or missing tests. Report only issues you can tie to a specific line. Skip style opinions. $FORMAT_RULE"
  else
    prompt="Use the review skill to review this repo. $FORMAT_RULE"
  fi
  echo "running $arm run $n ..."
  local t0 t1
  t0=$(perl -MTime::HiRes=time -e 'printf "%.2f", time')
  ( cd "$work/demo-app" && claude -p "$prompt" \
      --model "$MODEL" --effort "$EFFORT" \
      --output-format json --no-session-persistence \
      --setting-sources project,local \
      --max-budget-usd "$MAX_BUDGET_USD" \
      --allowedTools $tools ) > "$out" 2> "${out%.json}.err" \
    || echo "  run exited non-zero, see ${out%.json}.err"
  t1=$(perl -MTime::HiRes=time -e 'printf "%.2f", time')
  perl -e "printf '%.1f', $t1 - $t0" > "${out%.json}.wall"   # real wall-clock seconds for the claude call
  rm -rf "$work"
}

ARMS="${ARMS:-baseline checklist team}"   # e.g. ARMS=baseline to run only one arm
for n in $(seq 1 "$N"); do
  for arm in $ARMS; do
    run_one "$arm" "$n"
  done
done

echo "done. Score with: python3 eval/score.py"
