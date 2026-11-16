"""Scale, variance and ablation study of the final system (datasage-m3).

Reads the per-task result files only and writes eval/results/study_scale_ablations.json plus Markdown
tables on stdout. Nothing here calls the model.

Usage: python -m eval.study
Inputs:
  eval/results/<system>/<dataset>/            b0, b1, b2, datasage-m3 (run 0) and the ablations
  eval/results/repeats/rep<N>/datasage-m3/    independent repeat runs of datasage-m3
"""

from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path

from datasage.analyze import answers_match, run_analysis
from datasage.fixes import FIXES
from datasage.session import load_table
from datasage.values import comparable, is_missing
from eval.failures import diagnose
from eval.stats import bootstrap_ci, discordant, holm, mcnemar_exact, paired_bootstrap
from eval.scoring import id_key
from eval.summarize import LABELS, aggregate

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPEATS = RESULTS / "repeats"
OUT = RESULTS / "study_scale_ablations.json"

SPLITS = {
    "held-out": ["sales-heldout", "penguins-heldout"],
    "test": ["sales-test", "penguins-test"],
    "s303": ["sales-s303", "penguins-s303"],
    "s404": ["sales-s404", "penguins-s404"],
    "s505": ["sales-s505", "penguins-s505"],
}
POOLS = {"all five splits": list(SPLITS), "held-out + test": ["held-out", "test"], "new splits": ["s303", "s404", "s505"]}
FINAL = "datasage-m3"
BASELINES = ["b0", "b1", "b2"]
ABLATIONS = ["datasage-m3-nocoverage", "datasage-m3-novalidator", "datasage-m3-nomerge", "datasage-m3-compact",
             "datasage-m3-reject"]
N_BOOT = 10000


def load(root: Path, system: str, dataset: str) -> dict[str, dict]:
    folder = root / system / dataset
    if not folder.exists():
        return {}
    return {p.stem: json.loads(p.read_text()) for p in sorted(folder.glob("*.json"))}


def table_of(dataset: str, task_id: str) -> str:
    return f"{dataset}/{task_id.rsplit('_', 1)[0]}"


def keys_for(splits: list[str]) -> list[tuple[str, str]]:
    """(dataset, task_id) for every question of the given splits, from the benchmark task files."""
    out = []
    for split in splits:
        for dataset in SPLITS[split]:
            for folder in sorted((ROOT / "datasets" / dataset).iterdir()):
                if folder.is_dir():
                    out += [(dataset, t["task_id"]) for t in json.loads((folder / "tasks.json").read_text())]
    return out


def runs_of_final() -> dict[str, Path]:
    runs = {"run0": RESULTS}
    if REPEATS.exists():
        runs.update({p.name: p for p in sorted(REPEATS.iterdir()) if (p / FINAL).exists()})
    return runs


def results_for(root: Path, system: str, keys: list[tuple[str, str]]) -> dict[tuple[str, str], dict]:
    cache: dict[str, dict] = {}
    out = {}
    for dataset, task_id in keys:
        if dataset not in cache:
            cache[dataset] = load(root, system, dataset)
        if task_id in cache[dataset]:
            out[(dataset, task_id)] = cache[dataset][task_id]
    return out


def acc_with_ci(rows: dict[tuple[str, str], dict], seed: int = 0) -> dict:
    keys = sorted(rows)
    values = [float(rows[k]["analysis_correct"]) for k in keys]
    lo, hi = bootstrap_ci(values, groups=[table_of(*k) for k in keys], n_boot=N_BOOT, seed=seed)
    return {"n": len(values), "correct": int(sum(values)), "accuracy": sum(values) / len(values), "ci95": [lo, hi]}


def system_metrics(rows: dict[tuple[str, str], dict]) -> dict:
    tasks = list(rows.values())
    agg = aggregate(tasks)
    out = {"n": len(tasks), **acc_with_ci(rows),
           "completion": agg["completion"], "errors_handled": agg["correction_accuracy"],
           "damage_cells_rows": agg["damaged_cells_rows"], "tasks_with_damage": agg["tasks_with_damage"],
           "detect_precision": agg["detect_precision"], "detect_recall": agg["detect_recall"],
           "tool_calls_mean": statistics.mean(t["tool_calls"] for t in tasks),
           "tool_calls_median": statistics.median(t["tool_calls"] for t in tasks),
           "tool_call_success": agg["tool_call_success"],
           "approvals_median": agg["approvals_median"],
           "seconds_median": agg["latency_median_s"], "seconds_mean": statistics.mean(t["seconds"] for t in tasks),
           "tokens_median": agg["tokens_median"], "tokens_mean": statistics.mean(t["tokens"] for t in tasks),
           "stop_reasons": dict(Counter(t["stop_reason"] for t in tasks).most_common())}
    refusals = [t.get("extra", {}).get("coverage_refusals") for t in tasks]
    if any(r is not None for r in refusals):
        out["coverage_refusals_mean"] = statistics.mean(r or 0 for r in refusals)
    return out


def scale_section(keys_by_split: dict[str, list]) -> dict:
    out: dict = {}
    for system in BASELINES + [FINAL]:
        per = {}
        for split, keys in keys_by_split.items():
            rows = results_for(RESULTS, system, keys)
            if len(rows) == len(keys):
                per[split] = acc_with_ci(rows)
        for pool, members in POOLS.items():
            keys = [k for m in members for k in keys_by_split[m]]
            rows = results_for(RESULTS, system, keys)
            if len(rows) == len(keys):
                per[f"pooled: {pool}"] = acc_with_ci(rows)
        out[system] = per
    return out


def variance_section(keys_by_split: dict[str, list], runs: dict[str, Path]) -> dict:
    out: dict = {}
    groups = {**{s: [s] for s in SPLITS}, **{f"pooled: {p}": m for p, m in POOLS.items()}}
    for name, members in groups.items():
        keys = [k for m in members for k in keys_by_split[m]]
        per_run = {}
        for run, root in runs.items():
            rows = results_for(root, FINAL, keys)
            if len(rows) == len(keys):
                per_run[run] = rows
        if not per_run:
            continue
        accs = {run: sum(r["analysis_correct"] for r in rows.values()) / len(keys) for run, rows in per_run.items()}
        mean_per_q = [statistics.mean(per_run[run][k]["analysis_correct"] for run in per_run) for k in keys]
        lo, hi = bootstrap_ci(mean_per_q, groups=[table_of(*k) for k in keys], n_boot=N_BOOT)
        always_right = sum(m == 1 for m in mean_per_q)
        always_wrong = sum(m == 0 for m in mean_per_q)
        out[name] = {"n_questions": len(keys), "runs": len(per_run), "accuracy_by_run": accs,
                     "mean": statistics.mean(accs.values()), "min": min(accs.values()), "max": max(accs.values()),
                     "sd": statistics.stdev(accs.values()) if len(accs) > 1 else 0.0,
                     "ci95_mean_over_runs": [lo, hi],
                     "questions_right_every_run": always_right, "questions_wrong_every_run": always_wrong,
                     "questions_flipping": len(keys) - always_right - always_wrong}
    return out


def ablation_section(keys: list[tuple[str, str]], keys_by_split: dict[str, list]) -> dict:
    out = {}
    for system in [FINAL] + ABLATIONS + BASELINES:
        rows = results_for(RESULTS, system, keys)
        if len(rows) != len(keys):
            out[system] = {"missing": len(keys) - len(rows)}
            continue
        metrics = system_metrics(rows)
        metrics["accuracy_by_split"] = {s: sum(rows[k]["analysis_correct"] for k in ks) / len(ks)
                                        for s, ks in keys_by_split.items()}
        out[system] = metrics
    return out


def paired_section(keys: list[tuple[str, str]], runs: dict[str, Path]) -> list[dict]:
    final = results_for(RESULTS, FINAL, keys)
    reps = {run: results_for(root, FINAL, keys) for run, root in runs.items()}
    reps = {run: rows for run, rows in reps.items() if len(rows) == len(keys)}
    out = []
    for other in BASELINES + ABLATIONS:
        rows = results_for(RESULTS, other, keys)
        common = [k for k in keys if k in rows and k in final]
        if not common:
            continue
        a = [bool(final[k]["analysis_correct"]) for k in common]
        b = [bool(rows[k]["analysis_correct"]) for k in common]
        groups = [table_of(*k) for k in common]
        only_final, only_other = discordant(a, b)
        boot = paired_bootstrap(a, b, groups=groups, n_boot=N_BOOT)
        entry = {"system": other, "n": len(common), "final_accuracy": sum(a) / len(a), "other_accuracy": sum(b) / len(b),
                 "only_final_right": only_final, "only_other_right": only_other,
                 "mcnemar_p": mcnemar_exact(only_final, only_other),
                 "diff": boot["diff"], "diff_ci95": list(boot["ci"])}
        if len(reps) > 1 and all(k in rows for k in keys):
            mean_final = [statistics.mean(reps[r][k]["analysis_correct"] for r in reps) for k in keys]
            other_all = [float(rows[k]["analysis_correct"]) for k in keys]
            boot_all = paired_bootstrap(mean_final, other_all, groups=[table_of(*k) for k in keys], n_boot=N_BOOT)
            entry.update(diff_vs_mean_of_runs=boot_all["diff"], diff_vs_mean_of_runs_ci95=list(boot_all["ci"]),
                         runs_averaged=len(reps))
        out.append(entry)
    for entry, adj in zip(out, holm([e["mcnemar_p"] for e in out])):
        entry["mcnemar_p_holm"] = adj
    return out


def question_columns(spec: dict) -> set[str]:
    cols = {g.split(":")[0] for g in spec["group_by"]} | {f["column"] for f in spec.get("filters") or []}
    return cols | ({spec["metric"]} if spec.get("metric") else set())


def replay_cleaned(dataset: str, task_id: str, result: dict):
    """Rebuild the cleaned table of an agent run by applying its logged changes to the messy file."""
    changes = (result.get("extra") or {}).get("changes")
    if changes is None:
        return None
    df = load_table(ROOT / "datasets" / dataset / task_id.rsplit("_", 1)[0] / "messy.csv")
    for change in changes:
        df = FIXES[change["tool"]](df, **{k: v for k, v in change["args"].items() if k != "reason"}).df
    return df


def handled(planted: dict, rows: list[dict]) -> bool:
    """Whether one planted error was handled correctly, by the same rule as eval.scoring.score."""
    res = planted["resolution"]
    if res == "drop_copy":
        return len(rows) == 1
    if res == "exclude":
        return len(rows) == 0
    if res == "restore":
        return bool(rows) and comparable(rows[0].get(planted["column"])) == comparable(planted["clean_value"])
    return bool(rows) and is_missing(rows[0].get(planted["column"]))


def same_question(spec: dict, args: dict) -> bool:
    """Whether an analyze call asks the benchmark question (a count may name any metric column)."""
    filters = lambda fs: sorted((f["column"], str(f["value"])) for f in fs or [])  # noqa: E731
    return (list(args.get("group_by") or []) == list(spec["group_by"]) and args.get("agg") == spec["agg"]
            and (spec["agg"] == "count" or args.get("metric") == spec["metric"])
            and filters(args.get("filters")) == filters(spec.get("filters")))


def root_causes(dataset: str, task_id: str, result: dict, trace: list[dict] | None = None) -> list[str]:
    """Why an answer is wrong. If the cleaned table (rebuilt from the change log) gives the reference answer
    to the benchmark question, the analyze call asked something else. Otherwise: the planted errors that
    could change this answer and were not handled, plus damage to clean data."""
    table = task_id.rsplit("_", 1)[0]
    folder = ROOT / "datasets" / dataset / table
    planted = json.loads((folder / "planted.json").read_text())
    task = next(t for t in json.loads((folder / "tasks.json").read_text()) if t["task_id"] == task_id)
    stop = str(result.get("stop_reason")).split(":")[0]
    if not result.get("answer"):
        return [f"no answer (stopped: {stop})"]
    if stop not in ("finish", "answered_without_finish", "done"):  # an unfinished run is scored wrong
        return [f"did not finish (stopped: {stop})"]
    cleaned = replay_cleaned(dataset, task_id, result)
    if cleaned is None:
        return ["no change log"]
    spec = task["spec"]
    out = []
    calls = [e["args"] for e in trace or [] if e.get("event") == "tool" and e.get("name") == "analyze"
             and isinstance(e.get("output"), dict) and "result" in e["output"]]
    if calls and not same_question(spec, calls[-1]):
        out.append("analyze asked a different question (grouping, metric, aggregation or filters)")
    try:
        right = answers_match(run_analysis(cleaned, spec["group_by"], spec["metric"], spec["agg"],
                                           spec.get("filters"))["result"], task["reference_answer"])
    except ValueError as err:
        return out + [f"the question cannot be answered on the cleaned table: {str(err).split(';')[0]}"]
    if right:
        return out or ["cleaned table is right; answer differs for another reason"]
    cols = question_columns(spec)
    by_id: dict = {}
    for _, row in cleaned.iterrows():
        by_id.setdefault(id_key(row[planted["id_column"]]), []).append(row.to_dict())
    for p in planted["errors"]:
        if p["column"] not in cols and p["column"] != "*" and p["resolution"] != "exclude":
            continue  # cannot change this answer
        if handled(p, by_id.get(p["id"], [])):
            continue
        where = "a question column" if p["column"] in cols else "all rows" if p["column"] == "*" else \
            "a column the question does not use"
        out.append(f"{p['type']} ({p['resolution']}) on {where} not handled")
    if result.get("damaged_rows") or result.get("damaged_cells"):
        out.append("clean rows removed or clean cells changed")
    return sorted(set(out)) or ["every relevant planted error handled, yet the cleaned table gives another answer"]


def answer_diff(result: dict) -> str:
    """Short description of how the answer differs from the reference."""
    got, ref = result.get("answer"), result.get("reference_answer") or {}
    if not got:
        return "no answer"
    missing = sorted(set(ref) - set(got))
    extra = sorted(set(got) - set(ref))
    def differs(a, b) -> bool:  # the same tolerance as datasage.analyze.answers_match
        if a is None or b is None:
            return a != b
        return abs(a - b) > max(0.01, 0.005 * abs(b))

    wrong = sorted(k for k in set(ref) & set(got) if differs(got[k], ref[k]))
    parts = []
    if missing:
        parts.append(f"missing groups {missing}")
    if extra:
        parts.append(f"extra groups {extra}")
    if wrong:
        parts.append(f"{len(wrong)} of {len(ref)} group values differ ({', '.join(wrong[:4])})")
    return "; ".join(parts) or "values equal within tolerance (scored wrong)"


def failure_section(keys: list[tuple[str, str]], runs: dict[str, Path]) -> dict:
    """Why answers were wrong: the trace-based labels of eval.failures, and root causes found by replaying
    each run's change log and checking which planted errors that could change the answer were not handled."""
    def wrong_runs(root: Path, system: str) -> list[dict]:
        out = []
        for (dataset, task_id), result in results_for(root, system, keys).items():
            if result["analysis_correct"]:
                continue
            planted = json.loads((ROOT / "datasets" / dataset / task_id.rsplit("_", 1)[0] / "planted.json").read_text())
            trace_path = root / system / dataset / "traces" / f"{task_id}.jsonl"
            trace = [json.loads(x) for x in trace_path.read_text().splitlines()] if trace_path.exists() else []
            out.append({"question": f"{dataset}/{task_id}", "trace_labels": diagnose(result, trace, planted["errors"]),
                        "root_causes": root_causes(dataset, task_id, result, trace), "answer_diff": answer_diff(result),
                        "stop_reason": result["stop_reason"]})
        return out

    labels: Counter = Counter()
    causes: Counter = Counter()
    by_question: dict = {}
    for run, root in runs.items():
        for w in wrong_runs(root, FINAL):
            labels.update(w["trace_labels"])
            causes.update(w["root_causes"])
            entry = by_question.setdefault(w["question"], {"wrong_in_runs": [], "root_causes": Counter(),
                                                            "answer_diffs": []})
            entry["wrong_in_runs"].append(run)
            entry["root_causes"].update(w["root_causes"])
            entry["answer_diffs"].append(w["answer_diff"])
    ablations = {}
    for system in ABLATIONS:
        wrong = wrong_runs(RESULTS, system)
        ablations[system] = {"wrong": len(wrong),
                             "root_causes": Counter(c for w in wrong for c in w["root_causes"]).most_common(),
                             "trace_labels": Counter(c for w in wrong for c in w["trace_labels"]).most_common()}
    return {
        "final_runs": list(runs),
        "final_wrong_task_runs": sum(len(v["wrong_in_runs"]) for v in by_question.values()),
        "final_root_causes": causes.most_common(),
        "final_trace_labels": labels.most_common(),
        "final_wrong_questions": {k: {"wrong_in_runs": v["wrong_in_runs"], "root_causes": v["root_causes"].most_common(),
                                      "answer_diffs": v["answer_diffs"]}
                                  for k, v in sorted(by_question.items(), key=lambda kv: -len(kv[1]["wrong_in_runs"]))},
        "ablations": ablations,
    }


def exposure_section(keys: list[tuple[str, str]], runs: dict[str, Path]) -> dict:
    """Accuracy of datasage-m3 (all runs) on questions whose table has a row to exclude for a rule broken
    on a column the question does not use, against the other questions."""
    out = {}
    for kind in ("out_of_range", "negative"):
        groups: dict = {"exposed": [], "not exposed": []}
        for dataset, task_id in keys:
            folder = ROOT / "datasets" / dataset / task_id.rsplit("_", 1)[0]
            planted = json.loads((folder / "planted.json").read_text())["errors"]
            spec = next(t["spec"] for t in json.loads((folder / "tasks.json").read_text()) if t["task_id"] == task_id)
            cols = question_columns(spec)
            exposed = any(p["type"] == kind and p["column"] not in cols for p in planted)
            groups["exposed" if exposed else "not exposed"].append((dataset, task_id))
        out[kind] = {}
        for name, group in groups.items():
            right = total = 0
            for root in runs.values():
                rows = results_for(root, FINAL, group)
                right += sum(r["analysis_correct"] for r in rows.values())
                total += len(rows)
            out[kind][name] = {"questions": len(group), "task_runs": total, "right": right,
                               "accuracy": right / total if total else None}
    return out


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def ci(pair) -> str:
    return f"{100 * pair[0]:.1f} to {100 * pair[1]:.1f}"


def markdown(study: dict) -> str:
    columns = list(SPLITS) + [f"pooled: {p}" for p in POOLS]
    lines = ["## Accuracy per split (run 0), 95% cluster bootstrap CI", "",
             "| System | " + " | ".join(columns) + " |", "|---|" + "---:|" * len(columns)]
    for system, per in study["scale"].items():
        lines.append(f"| {LABELS.get(system, system)} | " + " | ".join(
            f"{pct(per[c]['accuracy'])} ({ci(per[c]['ci95'])})" if c in per else "n/a" for c in columns) + " |")
    lines += ["", "## datasage-m3 across independent runs", "",
              "| Split | n | runs | mean | min | max | SD | 95% CI | right every run | wrong every run | flips |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, v in study["variance"].items():
        lines.append(f"| {name} | {v['n_questions']} | {v['runs']} | {pct(v['mean'])} | {pct(v['min'])} | {pct(v['max'])} | "
                     f"{100 * v['sd']:.1f} | {ci(v['ci95_mean_over_runs'])} | {v['questions_right_every_run']} | "
                     f"{v['questions_wrong_every_run']} | {v['questions_flipping']} |")
    lines += ["", "## Ablations (all five splits, 200 questions)", "",
              "| System | Accuracy (95% CI) | Errors handled | Damage | Tasks w/ damage | Tool calls (mean) | Seconds (med) | Tokens (med) | Completed |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for system, m in study["ablations"].items():
        if "missing" in m:
            lines.append(f"| {LABELS.get(system, system)} | missing {m['missing']} | | | | | | | |")
            continue
        lines.append(f"| {LABELS.get(system, system)} | {pct(m['accuracy'])} ({ci(m['ci95'])}) | {pct(m['errors_handled'])} | "
                     f"{m['damage_cells_rows']} | {pct(m['tasks_with_damage'])} | {m['tool_calls_mean']:.1f} | "
                     f"{m['seconds_median']:.1f} | {m['tokens_median']:,.0f} | {pct(m['completion'])} |")
    lines += ["", "## Paired comparison with datasage-m3 run 0 (same questions)", "",
              "| Other system | n | M3 | Other | Diff (95% CI) | Only M3 right | Only other right | McNemar p | Holm p | Diff vs M3 mean of runs (95% CI) |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for e in study["paired"]:
        extra = f"{100 * e['diff_vs_mean_of_runs']:+.1f} ({ci(e['diff_vs_mean_of_runs_ci95'])})" if "diff_vs_mean_of_runs" in e else ""
        lines.append(f"| {LABELS.get(e['system'], e['system'])} | {e['n']} | {pct(e['final_accuracy'])} | {pct(e['other_accuracy'])} | "
                     f"{100 * e['diff']:+.1f} ({ci(e['diff_ci95'])}) | {e['only_final_right']} | {e['only_other_right']} | "
                     f"{e['mcnemar_p']:.2g} | {e['mcnemar_p_holm']:.2g} | {extra} |")
    f = study["failures"]
    lines += ["", f"## Root causes for datasage-m3 ({f['final_wrong_task_runs']} wrong task-runs over {len(f['final_runs'])} runs)", ""]
    lines += [f"- {n}: {cause}" for cause, n in f["final_root_causes"]]
    lines += ["", "Trace labels from eval/failures.py:", ""]
    lines += [f"- {n}: {cause}" for cause, n in f["final_trace_labels"]]
    lines += ["", "Questions wrong in at least one run:", ""]
    lines += [f"- {q}: wrong in {len(v['wrong_in_runs'])} ({', '.join(v['wrong_in_runs'])}); {v['root_causes']}; "
              f"answer: {v['answer_diffs'][0]}" for q, v in f["final_wrong_questions"].items()]
    lines += ["", "datasage-m3 on questions exposed to a rule-breaking row on a column they do not use (all runs):", ""]
    for kind, groups in study["exposure_to_rule_breaking_rows_on_unused_columns"].items():
        lines += [f"- {kind}, {name}: {g['questions']} questions, {g['right']}/{g['task_runs']} task-runs right"
                  for name, g in groups.items()]
    lines += ["", "Root causes for the ablations:", ""]
    for system, v in f["ablations"].items():
        lines.append(f"- {system} ({v['wrong']} wrong): " + "; ".join(f"{c} x{n}" for c, n in v["root_causes"]))
    return "\n".join(lines)


def build() -> dict:
    keys_by_split = {s: keys_for([s]) for s in SPLITS}
    all_keys = [k for s in SPLITS for k in keys_by_split[s]]
    runs = runs_of_final()
    return {
        "about": "Scale, variance and ablation study of datasage-m3. CIs are 95% percentile bootstrap intervals "
                 f"({N_BOOT} resamples) that resample whole tables (two questions each). McNemar p-values are exact "
                 "and two-sided; Holm adjusts them for the number of comparisons. run0 is eval/results/datasage-m3; "
                 "repN are eval/results/repeats/repN/datasage-m3.",
        "splits": SPLITS, "questions": {s: len(k) for s, k in keys_by_split.items()},
        "scale": scale_section(keys_by_split),
        "variance": variance_section(keys_by_split, runs),
        "ablations": ablation_section(all_keys, keys_by_split),
        "paired": paired_section(all_keys, runs),
        "failures": failure_section(all_keys, runs),
        "exposure_to_rule_breaking_rows_on_unused_columns": exposure_section(all_keys, runs),
    }


def main() -> None:
    study = build()
    OUT.write_text(json.dumps(study, indent=2, default=str))
    print(markdown(study))


if __name__ == "__main__":
    main()
