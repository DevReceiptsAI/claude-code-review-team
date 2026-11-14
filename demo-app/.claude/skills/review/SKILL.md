---
name: review
description: Review this repository for bugs, security issues, performance problems and weak tests by sending the code to three specialist subagents, then return one merged findings list. Use when asked to review the code.
---

# Code review team

Review the Python code in `app/` and `tests/`.

1. Start the three subagents **in parallel**, each with the same instruction: "Review the whole repository (`app/` and `tests/`) from your specialty and report findings."
   - `bug-hunter`: logic errors and performance problems
   - `security-reviewer`: security problems
   - `test-reviewer`: weak, misleading or missing tests
2. Collect their findings. Merge duplicates (same file and line, or the same issue described twice).
3. Drop anything you cannot point to a specific line for. Drop style opinions.
4. Output the final list, one finding per line, in exactly this format:

   `FINDING: path/to/file.py:LINE | category | severity | one-sentence description`

   - `category`: logic, security, performance or tests
   - `severity`: high, medium or low
   - `LINE` is a single line number, the line where the problem is.

Do not edit any files. Do not run any commands.
