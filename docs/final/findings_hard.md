# DataSage on harder data: the hard split and a model comparison

This note reports what happened when we ran DataSage and the baselines on a new, harder benchmark split.
Every number below comes from the per-task result files under `eval/results/<system>/<dataset>/`, from
`eval/results/summary.md` (written by `python -m eval.summarize`), or from `eval/results/hard_analysis.json`
(written by `python -m eval.analyze_hard`, which reads the same result files). Failure reasons come from
`python -m eval.failures --system <system> --dataset <dataset>` and from the traces in
`eval/results/<system>/<dataset>/traces/`.

## 1. Why a hard split

On the held-out and test splits the default agent (`datasage-m3`, Qwen3-30B) answers 92.5% of questions
correctly with no damaged cells. Those tables are small (41 to 72 rows) with a handful of planted errors
(88 to 108 per split of 10 tables). Three things that real files have were never tested:

1. **More rows breaking a rule than a check lists.** Checks show at most 10 row ids. With 30 bad rows, an
   agent that only knows `exclude_rows` cannot remove them all. This is the case `exclude_where` was added for.
2. **Problems the question does not need.** In a real file there are problems everywhere. A good agent
   fixes what the question depends on and does not get lost in the rest.
3. **Messier values.** Several kinds of problem in one column, numbers like `$ 1,400.00`, misspellings close
   to two allowed labels, and questions with filters.

## 2. What the hard split contains

`eval/generate_hard.py` builds `sales-hard` and `penguins-hard` (seed 303), 10 tables and 20 questions each,
in the same file format as the other splits, so `eval/scoring.py`, the approval oracle and `eval/run_eval.py`
work unchanged. A second seed (`sales-hard2`, `penguins-hard2`, seed 404) was built the same way to check
that the results are not specific to one draw. The regular generator `eval/generate.py` was not changed.

| | sales-hard | penguins-hard | held-out (both) | test (both) |
|---|---:|---:|---:|---:|
| Rows per table | 364 to 1,935 (median 1,255) | 343 to 1,070 (median 804) | 43 to 72 | 41 to 71 |
| Planted errors (10 tables) | 682 | 613 | 196 | 180 |
| Rows that must be excluded | 129 | 121 | | |
| Tables with more than 10 rule-breaking rows in one column | 4 | 5 | | |
| Errors in columns neither question uses (distractors) | 141 | 149 | | |
| Columns with two or more problem kinds | 28 | 38 | | |
| Questions with a filter | 14 of 20 | 8 of 20 | | |

How each requirement is built:

- **Bigger tables.** Sales tables have 300 to 2,000 rows from a larger catalog (six categories, six regions,
  prices up to $2,400). Penguin tables have 300 to 1,200 rows, resampled from the real Palmer Penguins data
  with small jitter that stays inside the rules' ranges.
- **Mass rule breaks.** In most tables with a numeric question, 12 to 40 rows break a range rule in the
  metric: negative or zero quantities, negative prices, body mass in milligrams (x1000) or kilograms (/1000),
  negative or x10 flipper and bill lengths. Two kinds are mixed in one column, so a check on negatives alone
  misses the zeros or the kilograms.
- **Several problem kinds in one column.** Label columns get case, space and spelling variants together;
  metric columns get text numbers and rule breaks together.
- **Distractors.** Errors in columns neither question uses (invalid dates, label variants, text numbers,
  wrong Revenue, missing labels). Their correct handling never removes a row, so they do not change the
  reference answer (a test checks this), but they count as planted errors in "errors handled" and detection.
  The one planned exception: in a Revenue table the rule breaks are negative quantities, which also make
  Revenue negative, so they show up in the question's metric.
- **Text numbers** such as `$2,400.00`, `$ 1,150.00`, `2,400`, `4,250.0`.
- **Misspellings close to two allowed labels**, for example `Northest` (close to Northeast and North) or
  `fmale` (close to female and male). The closest allowed label is always the right one. There are 33 of
  these in the first seed.
- **Filtered questions**, for example "What is the highest unit price in each category in the East region?".
  Both questions of a table share their metric, so a row that must be excluded matters for both.

`tests/test_generate_hard.py` checks that the generator is deterministic for a seed, that the regular
generator's output is unchanged, that reference answers are computed on the clean table with each planted
error's correct handling, that a perfect cleaning scores full marks with the unchanged scorer, and that every
feature above is present.

## 3. Results on the hard split

Systems: B1 (fixed cleaning script), B2 (one call to the 235B model that writes pandas code), and DataSage M3
with three planner models and the same prompt, tools, coverage check and oracle approver:
`datasage-m3` (Qwen3-30B-A3B, the default), `datasage-m3-large` (Qwen3-235B-A22B) and the new
`datasage-m3-gptoss` (gpt-oss-120b, a different model family; picked from the API's model list because it
supports tool calls and sits between the two Qwen models in size). All runs are full: 40 questions per system.

Both datasets together (40 questions per system):

| System | Correct | Accuracy | Damage | Detect P | Detect R | Errors handled | Median s | Median tokens | Total s | Total tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B1 fixed script | 4 | 10.0% | 0 | 0.88 | 0.86 | 72.6% | 0.0 | 0 | 1.9 | 0 |
| B2 single LLM call (235B) | 22 | 55.0% | 637 | 0.90 | 0.71 | 75.5% | 43.9 | 3,048 | 2,657 | 121,767 |
| DataSage M3 (30B, default) | 36 | 90.0% | 0 | 0.97 | 0.81 | 92.0% | 42.6 | 98,654 | 1,665 | 3,902,641 |
| DataSage M3 (235B) | 39 | 97.5% | 0 | 0.93 | 0.85 | 96.1% | 169.4 | 97,567 | 7,961 | 4,051,320 |
| DataSage M3 (gpt-oss-120b) | 36 | 90.0% | 0 | 0.95 | 0.60 | 80.9% | 59.7 | 74,101 | 2,647 | 3,254,596 |

Per dataset (from `summary.md`):

| System | sales-hard correct | penguins-hard correct | sales-hard handled | penguins-hard handled | Tool-call OK (sales / penguins) |
|---|---:|---:|---:|---:|---:|
| B1 | 20% | 0% | 79% | 66% | n/a |
| B2 | 45% | 65% | 73% | 78% | n/a |
| DataSage M3 (30B) | 80% | 100% | 89% | 95% | 100% / 100% |
| DataSage M3 (235B) | 95% | 100% | 94% | 99% | 100% / 100% |
| DataSage M3 (gpt-oss-120b) | 80% | 100% | 81% | 81% | 82% / 89% |

Errors handled, split into errors the question depends on and distractors (planted errors handled out of
planted, both datasets; the cleaned table is rebuilt by replaying each run's logged changes, and the rebuilt
table scores exactly like the run did for every task):

| System | Question errors | Distractors |
|---|---:|---:|
| B1 | 1,248 / 1,750 (71.3%) | 632 / 840 (75.2%) |
| DataSage M3 (30B) | 1,750 / 1,750 (100%) | 634 / 840 (75.5%) |
| DataSage M3 (235B) | 1,750 / 1,750 (100%) | 739 / 840 (88.0%) |
| DataSage M3 (gpt-oss-120b) | 1,723 / 1,750 (98.5%) | 373 / 840 (44.4%) |

Note on this table: a text number is scored as handled if its value reads the same as the clean number, even
when the column was never converted, so text-number errors count as handled for every system. What matters
for the answer is that the metric column is converted, because `analyze` refuses a text metric.

The main result: **both Qwen planners handled every one of the 1,750 errors that the questions depend on, with
zero damaged cells, on tables 10 to 40 times larger than before.** The lost answers are not cleaning failures
(section 5).

## 4. How each system degrades from held-out and test to hard

Accuracy (40 questions per split; held-out and test are the existing results):

| System | Held-out | Test | Hard (seed 303) | Hard2 (seed 404) |
|---|---:|---:|---:|---:|
| B1 fixed script | 35.0% | 45.0% | 10.0% | 7.5% |
| B2 single LLM call | 60.0% | 47.5% | 55.0% | not run |
| DataSage M3 (30B) | 92.5% | 92.5% | 90.0% | 85.0% |
| DataSage M3 (235B) | not run | not run | 97.5% | 97.5% |
| DataSage M3 (gpt-oss-120b) | not run | not run | 90.0% | 100.0% |

The 235B and gpt-oss M3 systems have no held-out or test runs in this branch (another study runs every model
on the standard splits), so their drop cannot be read from this table.

What changed for the default agent (`datasage-m3`), held-out and test versus hard:

| | Held-out | Test | Hard | Hard2 |
|---|---:|---:|---:|---:|
| Accuracy | 92.5% | 92.5% | 90.0% | 85.0% |
| Errors handled | 90.3% | 91.7% | 92.0% | 93.0% |
| Damage | 0 | 0 | 0 | 0 |
| Median tokens per question | 61,059 | 59,249 | 98,654 | 94,006 |
| Median approvals per question | 2 | 2 | 5 | 5 |
| Median seconds per question | 17.1 | 15.6 | 42.6 | 19.6 |

- **B1 collapses** (35-45% to 10%). It merges only case and space variants (it handled 481 of 769 label
  variants in question columns), has no notion of the rules' ranges (0 of 190 out-of-range values handled:
  zero quantities, milligram and kilogram masses, x10 lengths) and never checks Revenue against
  Quantity x Price (0 of 66 wrong Revenue values handled).
- **B2 holds its accuracy but damages tables.** It is at 55% (between its held-out 60% and test 47.5%), but
  4 of its 40 runs crashed on values like `$ 1400.00` (`could not convert string to float`), a `.lower()` on a
  number and a syntax error, and its cleaning removed or changed 637 rows and cells that should have been kept
  (416 cells in `penguinshard_03_q1` and 176 rows in `penguinshard_09_q1`, both of which still got the right
  answer).
- **DataSage barely moves on accuracy and not at all on damage.** The cost is in effort: 61% to 67% more
  tokens, and the user is asked about 5 risky fixes per question instead of 2 (185 approvals over 40
  questions for the 30B model). Latency is noisy because the API was shared with other runs at the same time
  (the same agent took a median 42.6 s on hard and 19.6 s on hard2); tokens are the steadier cost measure.

## 5. Failure analysis: every wrong datasage-m3 and datasage-m3-large answer

There are 4 wrong answers for `datasage-m3` and 1 for `datasage-m3-large` on the hard split. **All five have
one cause: the agent grouped by the filter column as well as the requested column.** The data was cleaned
correctly in all five (no damage, every question error handled), and every number in the answer equals the
reference; only the answer keys differ, for example `"Accessories | East": 50.0` where the reference has
`"Accessories": 50.0`. The scorer compares keys exactly, so these count as wrong.

| Task | System | Question | Evidence from the result and trace | Errors handled |
|---|---|---|---|---:|
| saleshard_02_q0 | 30B | highest unit price in each category in the East region | last `analyze`: `group_by [Category, Region]`, filter Region = East | 59 / 63 |
| saleshard_04_q0 | 30B | average revenue per order in each category for the West region | answer keys `Accessories \| West`, ... | 50 / 59 |
| saleshard_06_q0 | 30B | highest unit price in each category in the East region | answer keys `Accessories \| East`, ...; `exclude_where` had removed all 21 negative prices | 71 / 80 |
| saleshard_08_q0 | 30B | average revenue per order in each category for the West region | answer keys `Accessories \| West`, ... | 59 / 65 |
| saleshard_09_q0 | 235B | units sold in each category in the South region | last `analyze`: `group_by [Category, Region]`, filter Region = South; `exclude_where` had removed all 23 bad quantities | 64 / 64 |

The missing "errors handled" in these rows are distractors (invalid dates and label variants in columns the
question does not use), which the prompt allows the agent to leave alone.

Evidence that this is one specific weakness and not general difficulty:

- On the hard split it happens only on questions that group by Category and filter on Region ("in each
  category in the East region", "for the West region"). There are 8 such questions: the 30B model got 4 of
  them wrong, the 235B model 1, gpt-oss-120b none. On hard2, 6 of 9 such questions failed for the 30B model,
  and those 6 are its only wrong answers there. The 235B model's only wrong answer on hard2 is the same
  mistake on a penguin question ("average bill length for each sex on Biscoe island", answered with
  `group_by [island, sex]` and keys like `Biscoe | female`, after it had handled 68 of 68 planted errors).
- Questions filtered the other way ("total revenue by region for Electronics") never failed, and the
  held-out and test splits have no Region filters at all, which is why this never showed before.
- If the filter value is dropped from the answer keys, all of these answers match the reference:
  `correct_if_filter_key_dropped` in `hard_analysis.json` is 40/40 for both Qwen models on hard and on
  hard2.
- `eval/failures.py` did not have a reason for this, so its first run blamed "never ran a check for
  invalid_date" (a distractor). A new reason was added: "grouped by the filter column too (answer keys carry
  the filter value)". It now names this cause for all 5 hard failures and all 7 hard2 failures of the
  two Qwen models.

Neither Qwen model ever triggered the coverage check (0 refusals in 80 runs): both ran every required check on
their own, including the Revenue = Quantity x Price check in all 20 sales questions.

For comparison, the 4 wrong answers of gpt-oss-120b have real cleaning causes:

- `saleshard_04_q0`, `saleshard_08_q1`: it never ran `check_cross_column`, so Revenue values written x10 stayed
  in (Electricals average 17,878.39 instead of 2,767.86; North total 108,135 instead of 52,690). It ran that
  check in only 11 of 20 sales questions; the coverage check does not require it.
- `saleshard_05_q1`: it proposed `exclude_rows` for the 6 rule-breaking rows plus 2 rows whose only problem
  was a missing Region (rows 449 and 635). The oracle rejected the whole fix, the agent did not retry, and
  because the coverage check treats a finding as settled once a fix touching its rows was rejected, `analyze`
  ran with the rule-breaking rows still in (Northeast 998 instead of 1,006).
- `saleshard_08_q0`: its `exclude_rows` mixed 6 rule-breaking rows with 3 rows that only needed Revenue
  recomputed, so it was rejected; it then blanked Quantity on the 6 rows with `set_missing`, which left their
  negative Revenue in the average.

gpt-oss-120b also never called `finish` (all 40 runs ended with an answer but no finish call) and had 85
failed `analyze` calls: 58 sent an extra `"operator"` or `"op"` key inside a filter and 27 sent the filter as
a list such as `["Region", "=", "West"]`. The new tolerant argument handling drops unknown keys only at the top
level, not inside filters, so these calls failed; it recovered from 27% of its errors.

## 6. Was exclude_where used when it was needed?

18 questions (9 tables) have more than 10 rule-breaking rows in one column, which `exclude_rows` cannot cover
from one check's row list.

| System | Used exclude_where | Removed every rule-breaking row |
|---|---:|---:|
| B1 | n/a | 4 / 18 |
| DataSage M3 (30B) | 18 / 18 | 18 / 18 |
| DataSage M3 (235B) | 18 / 18 | 18 / 18 |
| DataSage M3 (gpt-oss-120b) | 17 / 18 | 18 / 18 |

The one gpt-oss case without it (`penguinshard_00_q1`) removed the 15 rows in two `exclude_rows` calls (10,
then the 5 the re-check listed). The 30B model used `exclude_where` in exactly those 18 questions and
`exclude_rows` for small counts (14 times); the 235B model used `exclude_where` for every range rule (32
times). No `exclude_where` was ever rejected by the oracle, and none removed a row that should be kept
(damage 0). On hard2, 24 questions needed it, and all three agents used it in all 24 and removed every
rule-breaking row. One small issue: its change summary joins two bounds with "and" ("excluded 14 row(s)
where bill_length_mm is below 30 and above 60"), where it means "or".

## 7. Cost and latency between models

| | 30B (A3B) | gpt-oss-120b | 235B (A22B) |
|---|---:|---:|---:|
| Accuracy (hard) | 90.0% | 90.0% | 97.5% |
| Accuracy if the filter key is dropped | 100% | 90.0% | 100% |
| Total seconds, 40 questions | 1,665 | 2,647 | 7,961 |
| Seconds per correct answer | 46 | 74 | 204 |
| Total tokens, 40 questions | 3.90 M | 3.25 M | 4.05 M |
| Tokens per correct answer | 108,407 | 90,405 | 103,880 |
| Median tool calls (sales / penguins) | 17 / 15 | 17.5 / 12.5 | 18 / 15 |

- The 235B model gives 3 more correct answers out of 40 but takes 4.8 times as long in total, and every one
  of its tokens runs through about 22B active parameters against about 3B for the 30B model.
- gpt-oss-120b uses the fewest tokens (it checks fewer columns: detection recall 0.60) but is slower than the
  30B model because of failed calls and retries, and its cleaning is the least thorough.
- Token use per question is similar for all three agents (74k to 99k median), because the cost is dominated
  by re-sending the conversation each turn, not by table size: the model sees a profile, never the rows.

## 8. Second seed (hard2)

The second seed (`sales-hard2`, `penguins-hard2`, seed 404: 648 to 1,565 sales rows, 375 to 1,162 penguin
rows, 1,329 planted errors, 12 tables with more than 10 rule-breaking rows in one column) gives the same
picture. B2 was not run on it.

| System | Correct | Accuracy | Damage | Detect P | Detect R | Errors handled | Question errors | Median s | Median tokens | Total s | Total tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B1 fixed script | 3 | 7.5% | 0 | 0.88 | 0.88 | 73.2% | | 0.0 | 0 | 1.8 | 0 |
| DataSage M3 (30B) | 34 | 85.0% | 0 | 0.94 | 0.82 | 93.0% | 1,821 / 1,821 | 19.6 | 94,006 | 773 | 3,764,764 |
| DataSage M3 (235B) | 39 | 97.5% | 0 | 0.92 | 0.83 | 93.7% | 1,821 / 1,821 | 144.8 | 98,343 | 5,868 | 3,928,801 |
| DataSage M3 (gpt-oss-120b) | 40 | 100.0% | 0 | 0.96 | 0.64 | 81.0% | 1,819 / 1,821 | 68.2 | 78,905 | 2,739 | 3,096,773 |

- Every wrong Qwen answer on hard2 is again the filter-grouping mistake (6 for the 30B model, 1 for the 235B
  model); with the filter value dropped from the keys both are at 40/40.
- gpt-oss-120b got every answer right on this seed. Its hard-split failures came from Revenue values written
  x10 and from mixed exclusions, and on this seed those cases did not hit its questions. It still has the
  lowest detection recall (0.64) and handles the fewest distractors, never calls `finish`, and 15% of its
  tool calls failed.

**Repeat run.** `datasage-m3` was run a second time on the hard split (results in
`eval/results/repeat2/datasage-m3/`, kept apart so the main results are not mixed). It got 35 of 40 (87.5%)
against 36 of 40 the first time. 39 of the 40 questions had the same outcome; the one that changed
(`saleshard_07_q1`, "How many orders are there in each category in the East region?") failed for the same
filter-grouping reason, so all 5 wrong answers of the repeat have that one cause. The rest matched the first
run: 1,750 of 1,750 question errors handled, damage 0, every rule-breaking row removed in all 18 questions
that needed it (17 with `exclude_where`, one with `exclude_rows`), 40/40 if the filter key is dropped. The
median time was 20.2 s against 42.6 s in the first run with about the same tokens (100,506 against 98,654),
which confirms that the latency differences come from the shared API's load, not from the agent.

Across all 200 DataSage Qwen runs on hard data (30B: hard, hard repeat, hard2; 235B: hard, hard2) there are 17
wrong answers, and all 17 have the filter-grouping cause.

## 9. Recommendations

1. **Fix the filter-in-group_by mistake in code, not in the prompt.** In `analyze`, if a group-by column is
   also filtered to a single value, drop it from the group-by (and say so in the result). This alone would
   turn all 17 Qwen failures on hard, hard2 and the repeat into correct answers
   (`correct_if_filter_key_dropped`). Add questions filtered on one value of a column that could also be a
   group (Region, island) to the dev split so this stays tested.
2. **Require the formula check in the coverage gate.** When the rules give a formula for a column the question
   uses (Revenue = Quantity x Price), add `check_cross_column` to the required checks. gpt-oss skipped it in 9
   of 20 sales questions and lost 2 answers to it.
3. **Do not let a rejected fix close a finding.** A rejected `exclude_rows` that also contained rows outside
   the finding should not mark the finding as handled; the refusal should ask for a fix limited to the
   finding's rows, or suggest `exclude_where`. This caused 2 of gpt-oss's 4 failures.
4. **Make argument handling tolerant inside filters too.** Accept `{"column", "operator": "=", "value"}` and
   `[column, "=", value]` as an equality filter. That removes 85 failed calls for gpt-oss-120b and makes
   other model families cheaper to use.
5. **Keep the 30B model as the default and keep the hard split as a regression test.** Over both seeds
   gpt-oss-120b got 76 of 80, the 30B model 70 and the 235B model 78, but every 30B and 235B miss had correct
   numbers under the wrong keys, while gpt-oss's 4 misses were wrong numbers that look plausible. The 30B
   model handles more errors than gpt-oss (92.0% against 80.9% on hard) in 63% of its time, and after
   recommendation 1 it would match the 235B model at about a fifth of the time. The approval load (median 5
   per question on large files) is the next thing users will notice; grouping related fixes into one approval
   would help.
