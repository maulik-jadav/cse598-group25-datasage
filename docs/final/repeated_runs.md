# Repeated runs on the hard split

`datasage-m3` (Qwen3-30B, with the grouping fix in `datasage/analyze.py`) was run on `sales-hard` and
`penguins-hard`, 20 questions each. One run with the fix was already stored in
`eval/results/fix_groupby/`. Two more were run on the current code, into `eval/results/hard_rep3/` and
`eval/results/hard_rep4/`. Accuracy and seconds below are read from the per-task JSON files. A question
counts as right when `analysis_correct` is true. Seconds per question is the mean of the `seconds` field
over the 40 questions in that run.

```bash
python -m eval.run_eval --system datasage-m3 --dataset sales-hard --results eval/results/hard_rep3 --workers 6
python -m eval.run_eval --system datasage-m3 --dataset penguins-hard --results eval/results/hard_rep3 --workers 6
python -m eval.run_eval --system datasage-m3 --dataset sales-hard --results eval/results/hard_rep4 --workers 6
python -m eval.run_eval --system datasage-m3 --dataset penguins-hard --results eval/results/hard_rep4 --workers 6
```

| Run | Folder | Correct | Accuracy | Mean seconds |
|---|---|---:|---:|---:|
| fix (already stored) | `eval/results/fix_groupby/` | 40/40 | 100% | 28.3 |
| repeat 3 | `eval/results/hard_rep3/` | 40/40 | 100% | 25.9 |
| repeat 4 | `eval/results/hard_rep4/` | 40/40 | 100% | 24.5 |

Over these three runs the accuracy mean is 100% and the range is 100% to 100%. The mean of the
seconds-per-question figures is 26.3, and the range is 24.5 to 28.3.

Two earlier runs, from before the grouping fix, are separate. The first scored 90.0%
(`eval/results/datasage-m3/`) and the second 87.5% (`eval/results/repeat2/`). Those misses were the
filter-grouping errors described in `docs/final/findings_hard.md`.

On the standard splits, `docs/final/findings_scale_and_ablations.md` reports 95.5% of 200 questions
(95% interval 92.0 to 98.5), with four runs between 94.0% and 96.0%. The hard split with the fix is
higher than that and did not move across these three runs. The standard-split runs still have misses
on rows that break a rule in a column the question does not use.
