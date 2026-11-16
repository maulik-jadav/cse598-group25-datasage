# DataSage final system: scale, variance and ablation study

This report checks how solid the headline result of the final system (`datasage-m3`, 92.5% on held-out and on
test, 40 questions each) really is. We tripled the benchmark, ran the final system four times, switched off
each of its mechanisms one at a time, and tested every difference on paired questions.

Every number below is read from the result files. The aggregates are saved in
`eval/results/study_scale_ablations.json` and are rebuilt by `python -m eval.study`. Per-task results and
traces are under `eval/results/<system>/<dataset>/` and `eval/results/repeats/rep<N>/datasage-m3/<dataset>/`.

## 1. Setup

**Benchmark.** We made three new splits with `eval/generate.py`, exactly as the earlier splits were made
(`--tables 10`, new seeds 303, 404 and 505, `--split s303` and so on). Each split has 10 sales tables and 10
penguin tables, two questions per table, so 40 questions per split. Together with the existing held-out
(seed 101) and test (seed 202) splits this gives **5 splits and 200 questions**. The dev split (seed 7) is left
out because it was used to build the system.

**Systems.**

| Name | What it is |
|---|---|
| B0 | Stakeholder's rule-based script, no cleaning |
| B1 | Fixed cleaning script, no model |
| B2 | One call to the 235B model that writes cleaning code, run once |
| `datasage-m3` | Final system: 30B planner, approval gate (oracle approver), validator, coverage check before analyze, merge rule in the prompt, full memory |
| `datasage-m3-nocoverage` | Final system with `coverage=False`. This turns off the check before analyze, and also the allowed-label hint in the label check and the "stop checking" warning, since one flag controls all three |
| `datasage-m3-novalidator` | Final system without the validator |
| `datasage-m3-nomerge` | Final system with the earlier prompt (`SYSTEM_PROMPT_V2`), which lacks the merge rule |
| `datasage-m3-compact` | Final system with compact memory (existing system, not run on these splits before) |
| `datasage-m3-reject` | Final system where every medium or high risk fix is rejected (no approvals at all) |

**Runs.** `datasage-m3` ran four independent times on all 200 questions: run 0 (the stored Milestone 3 results
for held-out and test, fresh results for the new splits) and three fresh repeats (rep1 to rep3). Each ablation
and each baseline ran once on all 200 questions. In this study we added 1,840 model-backed task runs (680 of
the final system, 1,000 of the ablations, 120 of B2) plus 240 runs of B0 and B1, with no API errors left in the
final files (runs that hit connection errors after a laptop crash were deleted and re-run).

**Statistics.** Confidence intervals (CI) are 95% percentile bootstrap intervals with 10,000 resamples. We
resample whole tables, not single questions, because the two questions about one table share the same errors
and tend to succeed or fail together. Paired comparisons use the same 200 questions for both systems: McNemar's
exact test on the questions where only one of the two is right, a paired bootstrap CI of the difference, and a
Holm correction for the eight comparisons. The helpers are in `eval/stats.py` (tested in `tests/test_stats.py`).

**Caveat on time.** Seconds per question were measured while other studies were using the same API, so they
are about twice the 15 s seen at Milestone 3 and they differ between systems partly because the load changed
during the day. Treat seconds as rough; tool calls and tokens do not depend on load.

## 2. Does the headline hold on more data?

Accuracy of each system on each split (run 0 for `datasage-m3`), with the 95% CI:

| System | held-out | test | s303 | s404 | s505 | all 200 |
|---|---:|---:|---:|---:|---:|---:|
| B0 stakeholder script | 2.5% (0.0 to 7.5) | 5.0% (0.0 to 12.5) | 2.5% (0.0 to 7.5) | 7.5% (0.0 to 15.0) | 12.5% (2.5 to 22.5) | 6.0% (3.0 to 9.5) |
| B1 fixed script | 35.0% (20.0 to 50.0) | 45.0% (27.5 to 62.5) | 55.0% (37.5 to 72.5) | 50.0% (32.5 to 67.5) | 60.0% (42.5 to 75.0) | 49.0% (41.0 to 57.0) |
| B2 single LLM call | 60.0% (42.5 to 77.5) | 47.5% (32.4 to 62.5) | 42.5% (25.0 to 62.5) | 25.0% (10.0 to 42.5) | 57.5% (37.5 to 75.0) | 46.5% (38.5 to 54.5) |
| **DataSage final** | 92.5% (80.0 to 100.0) | 92.5% (85.0 to 100.0) | 97.5% (92.5 to 100.0) | 97.5% (92.5 to 100.0) | 97.5% (92.5 to 100.0) | **95.5% (92.0 to 98.5)** |

On the 120 new questions alone the final system scores 97.5% (94.2 to 100.0), against 55.0% for B1 and 41.7%
for B2. So the result was not a lucky draw of 80 questions: on 2.5 times as much fresh data it holds, and the
interval on all 200 questions is narrow enough (about 92% to 98.5%) to say the final system answers well over
nine questions in ten on this kind of table.

The baselines move a lot from split to split (B2 goes from 25% to 60%), which shows why 40 questions was too
few to rank systems that are close. The final system is the steadiest of the four.

## 3. Run-to-run variance of the final system

The model runs at temperature 0, but the API is not fully deterministic, so we ran the final system four times.

| Split | Questions | Runs | Mean | Min | Max | SD (points) | 95% CI of the mean | Right every run | Wrong every run | Flips |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| held-out | 40 | 4 | 91.3% | 87.5% | 92.5% | 2.5 | 79.4 to 99.4 | 35 | 3 | 2 |
| test | 40 | 4 | 93.8% | 92.5% | 95.0% | 1.4 | 86.2 to 100.0 | 37 | 2 | 1 |
| s303 | 40 | 4 | 96.9% | 95.0% | 97.5% | 1.3 | 91.2 to 100.0 | 38 | 1 | 1 |
| s404 | 40 | 4 | 95.6% | 92.5% | 97.5% | 2.4 | 89.4 to 100.0 | 37 | 1 | 2 |
| s505 | 40 | 4 | 98.1% | 97.5% | 100.0% | 1.3 | 94.4 to 100.0 | 39 | 0 | 1 |
| held-out + test | 80 | 4 | 92.5% | 90.0% | 93.8% | 1.8 | 85.6 to 97.8 | 72 | 5 | 3 |
| new splits | 120 | 4 | 96.9% | 95.8% | 97.5% | 0.8 | 94.0 to 99.2 | 114 | 2 | 4 |
| **all 200** | 200 | 4 | **95.1%** | 94.0% | 96.0% | 0.9 | **91.9 to 97.8** | 186 | 7 | 7 |

The CI here is built from each question's average over the four runs, again resampling whole tables.

In plain words: the earlier 92.5% on held-out and on test is confirmed (four-run means of 91.3% and 93.8%;
together exactly 92.5%). A single 40-question run can move by up to 5 points (held-out ranged from 87.5% to
92.5%), but over all 200 questions the four runs stay within 94.0% to 96.0%. Of 200 questions, 186 are right
in every run, 7 are wrong in every run and only 7 change between runs. Most of the remaining error is
systematic, not noise, which is good news: it can be fixed (Section 6).

## 4. Ablations: which mechanisms matter

All on the same 200 questions, one run each:

| System | Accuracy (95% CI) | Errors handled | Damage | Tool calls (mean) | Tokens (median) | Seconds (median) | Finished |
|---|---:|---:|---:|---:|---:|---:|---:|
| DataSage final | 95.5% (92.0 to 98.5) | 93.0% | 0 | 12.4 | 61,680 | 27.0 | 100% |
| no coverage check | 91.5% (87.5 to 95.0) | 91.6% | 0 | 12.3 | 60,195 | 28.6 | 100% |
| no validator | 96.5% (94.0 to 99.0) | 93.2% | 0 | 12.7 | 61,918 | 30.1 | 100% |
| no merge rule in prompt | 97.0% (94.5 to 99.0) | 92.0% | 0 | 12.3 | 60,414 | 33.9 | 100% |
| compact memory | 86.0% (81.0 to 90.5) | 86.6% | 0 | 16.5 | 77,047 | 37.8 | 95% |
| every risky fix rejected | 12.0% (7.0 to 17.5) | 42.8% | 0 | 14.0 | 72,280 | 34.7 | 99.5% |
| B2 single LLM call | 46.5% (38.5 to 54.5) | 78.5% | 119 | n/a | 2,460 | 29.0 | 95% |

"Errors handled" is the share of planted errors left in the correct state in the cleaned table. "Damage" counts
clean cells changed or clean rows removed. "Finished" is the share of runs that ended with an answer (for B2:
code that ran).

### Paired comparison with the final system (same 200 questions)

| Other system | Final | Other | Difference (95% CI) | Only final right | Only other right | McNemar p | Holm p | Difference vs final's 4-run mean (95% CI) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 stakeholder script | 95.5% | 6.0% | +89.5 (85.0 to 93.5) | 179 | 0 | 2.6e-54 | 2.1e-53 | +89.1 (84.9 to 93.0) |
| B1 fixed script | 95.5% | 49.0% | +46.5 (38.5 to 54.0) | 93 | 0 | 2e-28 | 1e-27 | +46.1 (38.4 to 53.6) |
| B2 single LLM call | 95.5% | 46.5% | +49.0 (40.5 to 57.5) | 98 | 0 | 6.3e-30 | 3.8e-29 | +48.6 (40.4 to 57.0) |
| no coverage check | 95.5% | 91.5% | +4.0 (0.5 to 7.5) | 11 | 3 | 0.057 | 0.17 | +3.6 (0.2 to 7.1) |
| no validator | 95.5% | 96.5% | -1.0 (-3.0 to 1.0) | 1 | 3 | 0.62 | 0.62 | -1.4 (-3.2 to 0.2) |
| no merge rule in prompt | 95.5% | 97.0% | -1.5 (-3.5 to 0.0) | 0 | 3 | 0.25 | 0.5 | -1.9 (-3.9 to -0.1) |
| compact memory | 95.5% | 86.0% | +9.5 (5.5 to 14.0) | 19 | 0 | 3.8e-06 | 1.5e-05 | +9.1 (5.2 to 13.4) |
| every risky fix rejected | 95.5% | 12.0% | +83.5 (78.0 to 89.0) | 167 | 0 | 1.1e-50 | 7.5e-50 | +83.1 (77.2 to 88.6) |

A positive difference means the final system is better. The last column compares each system with the final
system's average over its four runs, which removes the luck of any single run.

### What this means, mechanism by mechanism

- **Approvals (the human in the loop) matter most: 83.5 points.** With every risky fix rejected the agent
  still finds the problems (detection recall 0.89) and never damages data, but it may only apply low-risk
  fixes, so it gets 12% right. Dropping duplicates, excluding rule-breaking rows and merging misspellings all
  need a yes. The design is safe when people say no, but the accuracy comes from people saying yes.
- **Against the baselines: 46 to 90 points, and never worse on any question.** On all 200 questions there is
  not one question that B0, B1 or B2 gets right and the final system gets wrong. B2 also damaged clean data in
  8% of its tasks (119 cells or rows); no DataSage variant damaged anything.
- **Full memory beats compact memory by 9.5 points (p < 0.001).** Compact memory was meant to save tokens but
  does the opposite here: it uses 33% more tool calls (16.5 against 12.4) and 25% more tokens (median 77,047
  against 61,680), because the agent forgets what it already did and re-checks. Ten runs hit the 30-call budget
  before finishing. Full memory, the current default, is the right choice.
- **The coverage check helps, by about 4 points.** Without it the agent got 11 questions wrong that the final
  system got right, and only 3 the other way. The paired bootstrap interval (0.5 to 7.5 points) and the 4-run
  comparison (0.2 to 7.1) both exclude zero, but the exact McNemar test gives p = 0.057 (0.17 after the Holm
  correction). Read it as a real but modest gain that this sample cannot fully confirm. The check refused
  analyze in 15 of the final system's 200 runs. The ablation's own failures were rule-breaking rows left in
  (11 cases), duplicates left in (4) and misspellings left in (2), which is exactly what the check looks for.
- **The validator made no measurable difference** (-1.0 points, p = 0.62). In the 200 runs of the final
  system the validator never rolled back a fix, so on these tables the fix tools never produced a change it
  had to stop. It is a safety net for tables we do not have here, not a source of accuracy.
- **The merge rule in the prompt is not needed any more** (-1.5 points, p = 0.25, and no question where only
  the final system was right). The agent still merged labels without the rule (233 applied merges against 243),
  because the label check itself returns a `suggested_fix` mapping and the coverage check tells the agent to
  use it. The code now does the work the prompt sentence was written for.

## 5. Why the final system is still wrong

We rebuilt the cleaned table of each wrong run from its change log (`eval/study.py`, `root_causes`) and
checked which planted errors that could change the answer were not handled. The rebuild reproduces the
reported answer in 1,792 of 1,794 agent runs that gave an answer; the two exceptions are runs where the agent
added an extra filter to its analyze call, and the script labels that case separately.

Over 4 runs x 200 questions there are 39 wrong task-runs:

| Root cause | Wrong task-runs |
|---|---:|
| A row that breaks a range rule on a column the question does not use was not excluded | 36 |
| A Revenue that breaks the formula (cross-column error) was not restored | 1 |
| A row that breaks a range rule on a question column was not excluded | 1 |
| The analyze call asked a different question (added a filter on sex) | 1 |

All 36 of the main cause are penguin tables where `body_mass_g` was planted 1,000 times too large, and the
question does not use body mass (for example "How many penguins were measured on each island?" or "What is the
average flipper length for each species?"). The benchmark's reference removes those rows, so every count and
average they fall into is off. The coverage check only covers the columns the question uses, so it never asks
for the body mass range check, and the agent usually does not run it on its own. On the 23 questions with such
a row the final system is right in 56 of 92 runs (61%); on the other 177 questions it is right in 705 of 708
runs (99.6%). Negative flipper lengths and quantities, the same kind of problem, are handled much more often
(338 of 360 runs right on exposed questions) because the agent checks those columns more readily.

The 7 questions wrong in every run all have this cause. `eval/failures.py` gives a noisier picture (for example
"never ran a check for missing", which does not matter because missing values are meant to stay missing); its
labels are kept in the JSON file for reference.

Failure causes of the ablations, from the same rebuild: without the coverage check, duplicates and misspellings
start to slip through too; with compact memory, 10 runs ran out of tool calls and 5 left a formula error in
Revenue; with every fix rejected, the commonest causes are duplicates left in (106) and negative rows left in
(85 on other columns, 20 on question columns).

## 6. Recommendations

1. **Extend the coverage check to row-level rules on every column.** Before analyze, run the range check on
   every column that has a `min` or `max` rule, not only the question's columns, and ask to exclude rows that
   break one. This targets 36 of the 39 remaining wrong task-runs (about 4.5 points of accuracy) at the cost of
   one or two extra checks per run. It is a code change, so it needs a fresh evaluation run to confirm.
2. **Keep full memory as the default and drop compact memory.** It is 9.5 points worse and uses more tokens,
   the opposite of its purpose.
3. **Report results on all 200 questions with intervals, not on 40.** Single 40-question runs of the same
   system moved by up to 5 points and baselines moved by up to 35 points between splits; the pooled number with
   its interval (95.5%, 92.0 to 98.5; 95.1% over four runs) is the one to quote.
4. **Keep the validator and the merge rule, but do not credit them for accuracy.** Neither changed accuracy
   here. The validator is cheap insurance for unusual tables; the merge rule could be removed from the prompt
   without loss, which shortens the prompt.
5. **Make the "no approvals" case clearer to users.** When the person rejects every risky fix the agent stays
   safe but only gets 12% right. The report should say plainly that the answer still contains the rejected
   problems and how much they move it (for example by also showing the answer with the fixes applied).

## 7. How to reproduce

```bash
python -m eval.generate --tables 10 --seed 303 --split s303   # and 404, 505
python -m eval.run_eval --system datasage-m3 --dataset sales-s303 --workers 12
python -m eval.run_eval --system datasage-m3 --dataset sales-test --workers 12 --results eval/results/repeats/rep1
python -m eval.run_eval --system datasage-m3-nocoverage --dataset sales-s303 --workers 12   # each ablation
python -m eval.study      # writes eval/results/study_scale_ablations.json and prints the tables
python -m eval.summarize  # adds the new splits and systems to summary.md
```
