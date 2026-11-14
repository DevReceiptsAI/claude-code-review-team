#!/bin/bash
# PreToolUse hook for the Bash tool.
# Runs the test suite whenever Claude tries `git commit` and blocks the commit
# (exit code 2) if the tests fail. Any other command passes straight through.
# Note: exit code 1 would NOT block, only exit code 2 does.

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')

# Matches `git commit` at the start of the command or after ; & |
# so `git add . && git commit -m x` is caught too.
if printf '%s' "$cmd" | grep -Eq '(^|[;&|])[[:space:]]*git[[:space:]]+commit'; then
  cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
  if ! output=$(python3 -m pytest -q 2>&1); then
    {
      echo "Commit blocked by hook: the test suite is failing."
      echo "Fix the tests first. Last lines of pytest output:"
      printf '%s\n' "$output" | tail -n 8
    } >&2
    exit 2
  fi
fi
exit 0
