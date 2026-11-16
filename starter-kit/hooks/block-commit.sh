#!/bin/bash
# Claude Code PreToolUse hook (matcher: Bash): block `git commit` while your tests fail.
# Exit code 2 = block, and the stderr text is shown to Claude. Exit code 1 would NOT block.
#
# 1. Set your test command below (or export TEST_CMD): e.g. "npm test --silent", "go test ./...", "pytest -q".
# 2. Needs `jq` (brew install jq / apt install jq).
# Differences from the hook measured in the video (demo-app/.claude/hooks/block-commit.sh): this one also matches
# `git -C dir commit`, `/usr/bin/git commit` and `bash -c "git commit"`, runs any test command, and fails closed
# (blocks with a message) if jq is missing or the project folder cannot be entered. Checked by tests/test_smoke.py,
# NOT by the Claude runs in the video. Known limits: a hook only stops the model; it can be removed by anyone who can
# edit .claude/settings.json; unusual spellings (aliases, scripts that run git inside) can still slip through.
TEST_CMD="${TEST_CMD:-python3 -m pytest -q}"

if ! command -v jq >/dev/null 2>&1; then
  echo "block-commit.sh needs jq (brew install jq). Blocking so the check is not silently skipped." >&2
  exit 2
fi

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')

# `git` followed, in the same command segment (no ; & |), by the word `commit`.
# Side effect: `git log --grep commit` also triggers the test run (it only blocks if tests fail).
if printf '%s' "$cmd" | grep -Eq "(^|[^[:alnum:]_-])git[^;&|]*[[:space:]]commit([[:space:]]|\$|[\"'])"; then
  cd "${CLAUDE_PROJECT_DIR:-.}" || { echo "block-commit.sh: cannot enter project dir; blocking." >&2; exit 2; }
  if ! output=$(bash -c "$TEST_CMD" 2>&1); then
    {
      echo "Commit blocked by hook: the test suite is failing."
      echo "Fix the tests first. Last lines of test output:"
      printf '%s\n' "$output" | tail -n 8
    } >&2
    exit 2
  fi
fi
exit 0
