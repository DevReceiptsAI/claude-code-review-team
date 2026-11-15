# Outline: Video #1 as built (5:52)

Title: I Told Claude Code to Ignore My Rule. A Hook Didn't Let It. (see titles.md)
All numbers come from METRICS.md (real runs, 13 Nov 2026).

## 0:00 The result (cold open, about 27 s)
Rule: 5 of 5 commits went through when told to ignore it. Hook: 0 of 5. Then the review result in one line.
## 0:29 The test app
300-line shop app, 10 planted bugs, 3 decoys; one bug and one decoy shown as real code.
## 1:20 Test 1: plain prompt vs checklist vs agent team
Short explainer of skills and subagents just before the test. Fairness (why a checklist arm exists), bug bars, cost bars: 7/10, 9/10, 9/10; team about 2.2x the checklist cost.
## 2:55 The bug all three missed
A query inside a loop (`low_stock_report`). Shown as code.
## 3:10 Test 2: CLAUDE.md rule vs hook
Short hook explainer, 2x2 grid, two transcript quotes from the saved runs.
## 4:16 What broke
Invalid first hook test, unclean decoys, misleading CLI timer, unfair baseline.
## 5:21 What it suggests (and the limits)
Small app, 3 and 5 runs, one model; team may win on a bigger codebase (not tested); hook only catches the commands it matches and Claude offered to disable it if told to.
## Outro
Repo link, next test.
