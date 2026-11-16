# CSE 598 Group 25: DataSage

Capstone project for CSE 598 Agentic AI (Arizona State University, Fall 2026).

DataSage is an agent that takes a messy CSV or Excel file and a question about it, finds data-quality problems, fixes or flags them (asking the user before any risky change), and then answers the question on the cleaned data with a report of every change it made.

**Stakeholder:** Vyshanth Buddani ([@VB914](https://github.com/VB914)). Original proposal and baseline: https://github.com/VB914/DataSage

## Team (Group 25)

| Name | GitHub |
|---|---|
| Shrey Bishnoi | [@shrey-Bish](https://github.com/shrey-Bish) |
| Ritik Agarwal | [@ritwiz06](https://github.com/ritwiz06) |
| Arsha Jindal | [@Arshajindal](https://github.com/Arshajindal) |
| Maulik Jadav | [@maulik-jadav](https://github.com/maulik-jadav) |
| Vatsal Nirmal | [@vatsal-prog](https://github.com/vatsal-prog) |

Team tasks, setup and how to open a pull request: [docs/TEAM_HANDOFF.md](docs/TEAM_HANDOFF.md).

## Repository layout

```text
app/web/      the browser app (python -m app.web.server)
datasage/     the agent: session state, profiler, checks, fixes, approval gate, validator,
              analysis, tool schemas and dispatcher, agent loop, report and replay script
baselines/    B0 (stakeholder baseline wrapper), B1 (fixed cleaning script), B2 (single model call),
              and the DataSage runner used by the evaluation
baseline/     the stakeholder's rule-based baseline, copied unchanged from VB914/DataSage (commit 4b1df80)
eval/         benchmark generator, scoring, approval oracle, evaluation runner, results
  sources/    public source data (Palmer Penguins, CC0) and its license note
  datasets/   generated tables: messy.csv, clean.csv, reference.csv, planted.json, rules.json, tasks.json
  results/    one JSON per task per system, traces, and summary.md / summary.csv
examples/     rules file for the stakeholder's messy_sales.csv, and a 1,208-row demo table with its generator
tests/        unit tests for the deterministic parts (no model calls)
docs/         milestone reports; docs/milestone2/demo/ holds the recorded demo run
```

## Setup

Python 3.11 or newer is required (pandas 3 does not support older versions).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # then put your ASU RC LLM key in .env
python -m pytest -q tests
```

The tests also run on GitHub for every pull request (`.github/workflows/tests.yml`); they need no API key.

The agent calls an OpenAI-compatible endpoint. We use ASU Research Computing
(`RC_LLM_BASE_URL=https://openai.rc.asu.edu/v1`) with `qwen3-30b-a3b-instruct-2507` (the default since
Milestone 3, about 15 s per question) and `qwen3-235b-a22b-instruct-2507` (pass `--model` to use it).
`.env` is ignored by git.

## Run DataSage

```bash
python -m datasage --input baseline/examples/messy_sales.csv \
  --rules examples/messy_sales_rules.json \
  --request "What was total revenue by category?"
```

Input files: CSV (the separator `,` `;` tab or `|` and the encoding UTF-8, Windows-1252 or Latin-1 are
detected) or Excel `.xlsx` (`--sheet NAME` picks a sheet; default the first). The replay script reads the
file the same way.

By default each medium or high risk fix is shown at the terminal and needs `y` to be applied. Other
modes: `--approve auto`, `--approve reject`, and `--approve tools --allow drop_duplicates,parse_dates`
(approve only those fix types, used for the recorded demo). Outputs go to `outputs/run/`:
`report.md`, `cleaned.csv` (the original file is never changed), `replay.py` (plain pandas), and
`trace.jsonl` (every tool call).

## Run DataSage in the browser

```bash
python -m app.web.server          # then open http://127.0.0.1:8501
```

Drop a CSV or Excel file (and optionally a JSON rules file), type a question and press Run, or pick one
of the two samples: Vyshanth's 8-row `messy_sales.csv`, or `examples/large_sales.csv` (1,208 rows, about 50
planted problems; rebuild it with `python examples/make_large_sales.py`). Both use
`examples/messy_sales_rules.json` and the question "What was total revenue by category?".

- **Ask me or Auto.** Next to Run: *Ask me* (default) stops at every risky fix; *Auto* applies every fix
  without asking, shows each one briefly, and still logs it as approved automatically.
- **Three tabs.** *Table* is the live run on one screen; *Answer* opens by itself when the run ends; *Data
  health* shows what the run found and did.
- **Live table.** The first 40 rows show at once; any row with a problem, anywhere in the file, slides in
  as the agent finds it. Problem cells are amber, fixed cells green, removed rows fold away, and rejected
  fixes stay marked as caveats.
- **Approvals on the row.** Each risky fix opens a card under the affected row, saying what it will do and
  showing the exact rows: removed rows in full, or each changed cell as old → new. Click a row number to
  jump to it. Keep or Apply decides it.
- **Answer.** The result counts up, with every change and who approved it, and the four output files,
  each with a line on what it is for (cleaned table, report, replay script, step log).
- **Data health.** After the run: rows before and after, every problem found by column (fixed, kept as a
  caveat, or not needed for the question), and the answer before cleaning next to the answer after.

With Docker instead: `docker build -t datasage .` then `docker run --rm -p 8501:8501 --env-file .env datasage`.

Two more pages: **Results** (`/results`, linked in the header) is the evaluation dashboard: accuracy per
system and split, accuracy against speed, detection, damage, the Milestone 2 to 3 progression, ablations
and the remaining failure causes, all read from `eval/results/`. **Column profile** (`/profile?run=<id>`,
linked under "Your files" after a run) compares every column before and after cleaning.

It needs the same `.env` key as the command line and nothing else (standard library only). Uploads and
outputs go to `outputs/web/<run id>/`. Options: `--port`, `--model`, `--host` (default 127.0.0.1, so only
your machine can open it). An approval left unanswered for 10 minutes, or a run replaced by a new one,
counts as rejected.

## Reproduce the evaluation

```bash
python -m eval.generate --tables 10 --seed 7          # dev split: 20 sales + 20 penguin tasks
python -m eval.generate --tables 10 --seed 101 --split heldout   # held-out split (sales-heldout, penguins-heldout)
python -m eval.generate --tables 10 --seed 202 --split test      # test split made for Milestone 3 (sales-test, penguins-test)
python -m eval.run_eval --system b0 --dataset sales   # repeat for each system and dataset
python -m eval.run_eval --system datasage --dataset penguins --workers 4
python -m eval.run_eval --system datasage-reject --dataset sales --limit 10   # Table 8 ablations: first 10 tasks;
python -m eval.run_eval --system datasage-novalidator --dataset sales --limit 10   # repeat both for penguins
python -m eval.summarize                              # writes eval/results/summary.md
python -m eval.failures --system datasage             # likely cause of each wrong task, from its trace
```

Table 3 (rows, tasks and planted errors) is counted from the generated files: rows in each table's
`messy.csv`, tasks in `tasks.json`, and planted errors in the `errors` list of `planted.json`, under
`eval/datasets/<dataset>/`. Table 8's ordinary 235B rows are the same first 10 task files from
`eval/results/datasage/`, not the 20-task averages in `summary.md`.

Systems: `b0`, `b1`, `b2`, `datasage`, `datasage-small`, `datasage-reject`, `datasage-novalidator`, and the
Milestone 2 fix variants `datasage-fix`, `datasage-small-fix`, `datasage-small-fix-strict` (exclusion rule in the
prompt; `-strict` also uses a stricter approval oracle). Milestone 3: `datasage-m3` is the default agent (30B,
coverage check before `analyze`, spelling merges into the rules' allowed labels); `datasage-m3-compact` is the
same with compact memory, and `datasage-m3-large` uses the 235B model. Datasets: `sales`, `penguins`,
`sales-heldout`, `penguins-heldout`, `sales-test`, `penguins-test`. Results are cached per task, so an
interrupted run can be restarted.

## Run the stakeholder baseline on its own

```bash
cd baseline
python run_baseline.py --input examples/messy_sales.csv --analysis revenue_by_category
python smoke_test.py
```

## Team workflow

- Commit under your own GitHub account. Individual grades use commit and pull request authorship.
- Work on a branch and open a pull request into `main`. Ask one teammate to review before merging.
- Never commit API keys. Put them in a local `.env` file, which git already ignores.
- Keep any stakeholder data that is not public out of this repository.
