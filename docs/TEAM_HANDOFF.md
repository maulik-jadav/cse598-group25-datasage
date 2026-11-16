# Team handoff: final stretch

For: Arsha, Ritik, Maulik and Vatsal. Last updated November 16, 2026.

Milestone 2 is submitted and items 1 and 2 of Section 6 are merged (PR #7). The browser app for the demo
(item 7's page) is in `app/web/`. The rest of the work is split below. Individual grades draw on commit and PR
authorship, so **each task should end in its own merged PR** under your own GitHub account.

## Dates

| Date | What |
|---|---|
| Nov 16 to 20 | Vyshanth rates 10 DataSage reports (ratings week) |
| **Nov 20, 2:00 PM MST, Zoom** | Review with Vyshanth |
| **Nov 23, 2:00 PM (hard)** | Poster PDF due on Canvas (24 × 36 in portrait, `Group25_Poster.pdf`). No printing if late |
| Nov 27 | All code PRs open, so there is time to merge and re-run before the final report |
| **Dec 2, class time** | Poster session in person. Everyone attends |
| TBD (check Canvas) | Final report |

## Where things stand

| What | Where |
|---|---|
| The agent (30B model is now the default) | `datasage/` (`agent.py` loop, `tools.py` dispatcher and coverage check, `checks.py`, `fixes.py`) |
| Baselines B0, B1, B2 | `baselines/systems.py` |
| Benchmark, scoring, runner | `eval/generate.py`, `eval/scoring.py`, `eval/oracle.py`, `eval/run_eval.py` |
| All results | `eval/results/summary.md`; final system is `datasage-m3` |
| Report view (Arsha) and recipe format (Ritik) | `app/report_view.py`, `app/preview_report.py`, `datasage/recipes.py` |
| Item 7 design note | `docs/design/item7_recipes_ui.md` |
| Poster draft (print-ready PDF, source and figures) | `docs/final/poster/` (see its README) |
| Demo run with the 30B default | `docs/final/demo/` (13 s, same answer as the Milestone 2 demo) |
| Browser app (item 7 page) | `app/web/`; run `python -m app.web.server` and open http://127.0.0.1:8501 (README, "Run DataSage in the browser") |

Final system (`datasage-m3`, Qwen3-30B), share of questions answered correctly:

| System | Held-out (40) | Test (40) | Damaged cells | Seconds per question |
|---|---|---|---|---|
| B1 fixed script | 35.0% | 45.0% | 0 | < 1 |
| B2 single model call | 60.0% | 47.5% | 35 | about 32 |
| DataSage 30B (final) | 92.5% | 92.5% | 0 | about 17 |

All 6 remaining misses are rows that break a rule in a column the question doesn't use. Vyshanth chose
to check only the question's columns, so we raise this at the Nov 20 review rather than change it.

## Your tasks

Every task ends in a PR into `main`. Put a short note of what you did in `docs/team/<you>/WORKLOG.md`.

### Arsha

| # | Task | Done when | Due |
|---|---|---|---|
| A1 | **Ratings packet (item 6).** Run DataSage on 10 questions: Vyshanth's two files plus questions from the held-out tables. Send him the 10 `report.md` files and a short form (correct? clear? would you trust it? each 1 to 5, plus a comment). Collect his answers. | His ratings are summarised in `docs/final/ratings.md` (scores and quotes, no copy of his files). | Send Nov 17, collect Nov 20 |
| A2 | **Acceptance test (item 6).** 3 files (Vyshanth's two plus one test-split table), each with questions and expected answers. Pass = at least 90% correct and no valid cell changed. | `docs/final/acceptance_test.md` with the command, each question, expected and actual answer, pass or fail. | Nov 25 |
| A3 | **Poster.** Check every number on the draft against `eval/results/summary.md`, collect team edits, export the PDF at 24 × 36 in and submit it on Canvas. | `Group25_Poster.pdf` submitted and copied to `docs/final/`. | Submit by Nov 22 |

### Ritik

| # | Task | Done when | Due |
|---|---|---|---|
| R1 | **Recipe replay (item 7).** Build a recipe from a run's approved fixes and replay it on a new file without the model, as planned in the design note. | Tests in `tests/test_recipes.py` show a recipe from one table replayed on another table with the same columns. | Nov 25 |
| R2 | **Nov 20 review.** Send Vyshanth an agenda by Nov 19: results, the out-of-question-column misses, ratings, demo plan. Take notes. | `docs/meetings/2026-11-20-review.md`, same format as the Oct 28 notes. | Nov 20 |

### Maulik

| # | Task | Done when | Due |
|---|---|---|---|
| M1 | **Dates (item 3).** Blank unreadable dates and convert clear formats automatically as low risk, logged. Ask only for ambiguous dates such as 03/04/2026. | Tests cover all three cases; the change log shows each conversion. | Nov 24 |
| M2 | **Refund rule (item 3).** Add an `allow_negative_quantities` rules key. When it is set, negative quantities are kept as refunds without asking. | Tests for both settings; the README's rules section mentions the key. | Nov 24 |
| M3 | **No-regression run.** After M1 and M2 merge, re-run `datasage-m3` on held-out and test into a new results folder and compare with the current numbers. | A short write-up in `docs/final/regression_check.md`; any drop explained from the traces. | Nov 27 |

### Vatsal

| # | Task | Done when | Due |
|---|---|---|---|
| V1 | **Repeated runs (item 5).** Run `datasage-m3` 3 times on held-out and test (separate `--results` folders), and report the mean and range of accuracy and seconds per question. | `docs/final/repeated_runs.md` with a table and the commands used. | Nov 24 |
| V2 | **Real messy files (item 4).** Pick 2 public messy CSV files with a license that allows reuse. Write 3 questions, a rules file and the correct answers by hand for each, then run DataSage. | Data, rules and questions in `eval/real/`; results and what went wrong in `docs/final/real_files.md`. | Nov 27 |

### Shrey

Owns the browser app (`app/web/`) and the Demo Day plan (a 3-minute walk-through for the poster session plus a backup screen recording, in `docs/final/demo_script.md`, by Nov 30). Also reviews and merges every PR and assembles the final report. Each of you writes the final-report paragraph for your own tasks.

## Setup (about 5 minutes)

Python 3.11 or newer.

```bash
git clone https://github.com/shrey-Bish/cse598-group25-datasage.git
cd cse598-group25-datasage
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q tests                          # 36 tests, no API key needed
python -m eval.summarize                           # prints the results tables
```

Running DataSage needs an ASU RC model key in a `.env` file (copy `.env.example`). Use your own key. A1,
A2, M3, V1 and V2 need one; check your quota before starting V1, which makes the most calls.

## How to commit and open a PR

Do this once in the repo folder, with the email on **your** GitHub account (otherwise the commits are not
credited to you):

```bash
git config user.name "Your Name"
git config user.email "the-email-on-your-github-account"
```

For each task:

```bash
git checkout main
git pull
git checkout -b yourname/short-topic
# ...make your changes...
git add <the files you changed>
git commit -m "Say what you did, in a full sentence"
git push -u origin yourname/short-topic
```

Then open a pull request into `main` and ask Shrey to review it.

Rules:

- Never commit `.env` or any API key. The repo is public.
- Never commit Vyshanth's two sample files or their outputs. He allowed sending them to the ASU model
  service, not publishing them. Summaries and scores are fine.
- Do not edit files in `eval/results/` by hand. They come from `eval/run_eval.py`.
- Small, clear commits are better than one large one.

Questions about the code: ask Shrey, or open a GitHub issue so the answer stays with the repo.
