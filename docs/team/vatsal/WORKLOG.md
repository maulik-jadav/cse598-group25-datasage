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
