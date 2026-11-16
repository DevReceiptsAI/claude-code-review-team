# Outline: Video #1 as built (about 6:00)

Title: I Told Claude Code to Ignore My Rule. A Hook Didn't Let It. (see titles.md). All numbers come from METRICS.md (real runs, 13 Nov 2026).
Chapter times are generated into `build/chapters.txt` (and `description.md`) after each narration run; do not trust old timestamps.

1. Cold open (~15 s): one story. Told to ignore the rule: 5 of 5 commits. Swapped in a hook: 0 of 5. Promise: the hook and a 5-minute test for your own rules.
2. The test app: 300 lines, 10 planted bugs, 3 decoys; one bug and one decoy as real code.
3. Test 1: plain prompt vs one agent with checklist vs 3-subagent team (skill/subagent explainer just before). 7/10, 9/10, 9/10; team about 2.2x the checklist's cost.
4. The bug all three missed (query in a loop).
5. Test 2: hook explainer, the hook running for real (captured output), rule vs hook grid, two real quotes, the caveat (no edit access; Claude offered to disable the hook).
6. What broke (invalid first hook test, unclean decoys, misleading CLI timer, unfair baseline).
7. Limits, then "Copy this": the starter kit and the 5-minute recipe.
8. Lessons and outro. Next: does a team win on a much bigger codebase? (not tested yet)
