# Vatsal's worklog

## Purpose

A log of what I change in this repository, for teammates. Newest entry last.

## Log

### 2026-11-21: repeated runs on the hard split (V1)

Ran `datasage-m3` on `sales-hard` and `penguins-hard` twice more, on the current code (the grouping
fix is already in `datasage/analyze.py`). Results are in `eval/results/hard_rep3/` and
`eval/results/hard_rep4/`. Together with the stored run in `eval/results/fix_groupby/`, all three
runs scored 40/40. The write-up, including the commands, is `docs/final/repeated_runs.md`.

No code changes. The result files come from `eval/run_eval.py`.

### 2026-11-21: two real inspection files (V2)

Added a Chicago food-inspection extract and a New York restaurant-inspection extract under
`eval/real/`, with rules, three questions each, and answers counted by hand before the runs.
Ran the default agent with `--approve auto`. Three of six answers matched. The misses are in
`docs/final/real_files.md`: dates parsed to missing, violation rows counted as separate inspections,
and three Dunkin' rows dropped because longitude was 0.

No change under `datasage/`.
