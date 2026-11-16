"""Numbers for docs/final/findings_hard.md, read from the per-task result files of the hard split.

For DataSage systems the cleaned table is rebuilt by replaying the logged changes (each change's tool and
arguments) on the messy file, which gives the same table the run ended with. That lets us split "errors
handled" into errors in the columns the question uses and distractors, and by error type.

Usage: python -m eval.analyze_hard [--datasets sales-hard penguins-hard]   (writes eval/results/hard_analysis.json)
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

from baselines.systems import b1_clean
from datasage import fixes
from datasage.analyze import answers_match
from datasage.session import load_table
from eval.generate_hard import question_columns
from eval.scoring import id_key, load_bundle
from eval.summarize import aggregate, load
from datasage.values import comparable, is_missing

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SYSTEMS = ["b1", "b2", "datasage-m3", "datasage-m3-large", "datasage-m3-gptoss"]


def replay(bundle, changes: list[dict]):
    df = load_table(bundle.messy_path)
    for c in changes:
        args = {k: v for k, v in c["args"].items() if k != "reason"}
        df = fixes.FIXES[c["tool"]](df, **args).df
    return df


def handled(df, planted: list[dict], id_col: str) -> list[bool]:
    got: dict[str, list[dict]] = {}
    for _, row in df.iterrows():
        got.setdefault(id_key(row[id_col]), []).append(row.to_dict())
    out = []
    for p in planted:
        rows = got.get(p["id"], [])
        res = p["resolution"]
        if res == "drop_copy":
            ok = len(rows) == 1
        elif res == "exclude":
            ok = len(rows) == 0
        elif res == "restore":
            ok = bool(rows) and comparable(rows[0].get(p["column"])) == comparable(p["clean_value"])
        else:
            ok = bool(rows) and is_missing(rows[0].get(p["column"]))
        out.append(ok)
    return out


def correct_if_filter_key_dropped(r: dict, spec: dict) -> bool:
    """True if the answer only differs by also grouping on a filtered column ("Accessories | West" for "Accessories")."""
    if r["analysis_correct"] or not r.get("answer"):
        return bool(r["analysis_correct"])
    values = {str(f["value"]) for f in spec.get("filters", [])}
    if not values:
        return False
    fixed = {}
    for key, value in r["answer"].items():
        parts = [part for part in str(key).split(" | ") if part not in values]
        fixed[" | ".join(parts) or "all"] = value
    return len(fixed) == len(r["answer"]) and answers_match(fixed, r["reference_answer"])


def category(p: dict, used: set[str]) -> str:
    if p["column"] == "*":
        return "question"
    if p["column"] in used or p["resolution"] == "exclude":  # excluded rows always change the answer
        return "question"
    return "distractor"


def analyze(system: str, dataset: str) -> dict | None:
    folder = RESULTS / system / dataset
    rows = [json.loads(p.read_text()) for p in sorted(folder.glob("*.json"))] if folder.exists() else []
    if not rows:
        return None
    by_cat = defaultdict(lambda: [0, 0])
    by_type = defaultdict(lambda: [0, 0])
    stop = Counter()
    tools_used = Counter()
    mass_tasks = mass_ok = mass_where = mass_where_ok = replay_mismatch = 0
    per_task = []
    for r in rows:
        stop[r["stop_reason"]] += 1
        table = r["task_id"].rsplit("_", 1)[0]
        bundle = load_bundle(ROOT / "datasets" / dataset / table)
        task = next(t for t in bundle.tasks if t["task_id"] == r["task_id"])
        used = question_columns(task["spec"])
        changes = r.get("extra", {}).get("changes")
        if system == "b1":
            changes = []  # B1 has no change log; its cleaning is a fixed function, rebuilt below
        for c in changes or []:
            tools_used[c["tool"]] += 1
        excl = Counter(p["column"] for p in bundle.planted if p["resolution"] == "exclude")
        mass_cols = [c for c, n in excl.items() if n > 10]
        info = {"task_id": r["task_id"], "correct": r["analysis_correct"], "mass_columns": mass_cols,
                "correct_if_filter_key_dropped": correct_if_filter_key_dropped(r, task["spec"])}
        if changes is not None:
            df = b1_clean(pd.read_csv(bundle.messy_path))[0] if system == "b1" else replay(bundle, changes)
            flags = handled(df, bundle.planted, bundle.id_col)
            replay_mismatch += sum(flags) != r["corrections"]  # the rebuilt table must score like the run did
            for p, ok in zip(bundle.planted, flags):
                cat = category(p, used)
                by_cat[cat][0] += ok
                by_cat[cat][1] += 1
                key = p["type"] + (" (distractor)" if cat == "distractor" else "")
                by_type[key][0] += ok
                by_type[key][1] += 1
            if mass_cols:
                mass_tasks += 1
                where = [c for c in changes if c["tool"] == "exclude_where"]
                ex_flags = [ok for p, ok in zip(bundle.planted, flags) if p["resolution"] == "exclude"]
                all_out = all(ex_flags)
                mass_ok += all_out
                mass_where += bool(where)
                mass_where_ok += bool(where) and all_out
                info.update(exclude_where=bool(where), excluded_all=all_out,
                            excluded=f"{sum(ex_flags)}/{len(ex_flags)}")
        per_task.append(info)
    secs = [r["seconds"] for r in rows]
    toks = [r["tokens"] for r in rows]
    out = {
        "tasks": len(rows),
        "correct": sum(r["analysis_correct"] for r in rows),
        "correct_if_filter_key_dropped": None,  # filled below
        "seconds_median": statistics.median(secs), "seconds_mean": round(statistics.mean(secs), 1),
        "seconds_total": round(sum(secs), 1),
        "tokens_median": statistics.median(toks), "tokens_total": sum(toks),
        "tool_calls_median": statistics.median(r["tool_calls"] for r in rows),
        "approvals_median": statistics.median(r["approvals_asked"] for r in rows),
        "stop_reasons": dict(stop),
        "fix_tools_applied": dict(tools_used),
    }
    if by_cat:
        out["replay_mismatches"] = replay_mismatch
        out["handled_by_category"] = {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_cat.items())}
        out["handled_by_type"] = {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_type.items())}
        out["mass_rule_break_tasks"] = {"tasks": mass_tasks, "used_exclude_where": mass_where,
                                        "all_rule_breaking_rows_excluded": mass_ok,
                                        "exclude_where_and_all_excluded": mass_where_ok}
    out["correct_if_filter_key_dropped"] = sum(t["correct_if_filter_key_dropped"] for t in per_task)
    out["per_task"] = per_task
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", nargs="+", default=["sales-hard", "penguins-hard"])
    args = parser.parse_args()
    report = {}
    for dataset in args.datasets:
        for system in SYSTEMS:
            found = analyze(system, dataset)
            if found:
                report.setdefault(dataset, {})[system] = found
                brief = {k: v for k, v in found.items() if k != "per_task"}
                print(dataset, system, json.dumps(brief))
    # Pooled over sales + penguins of the same split (and over the standard held-out and test splits, to compare).
    pools = {"hard": ["sales-hard", "penguins-hard"], "hard2": ["sales-hard2", "penguins-hard2"],
             "heldout": ["sales-heldout", "penguins-heldout"], "test": ["sales-test", "penguins-test"]}
    for name, datasets in pools.items():
        for system in SYSTEMS:
            rows = [r for d in datasets for r in load(system, d)]
            if rows:
                agg = aggregate(rows)
                agg["correct"] = sum(r["analysis_correct"] for r in rows)
                agg["seconds_total"] = round(sum(r["seconds"] for r in rows), 1)
                agg["tokens_total"] = sum(r["tokens"] for r in rows)
                report.setdefault("pooled", {}).setdefault(name, {})[system] = agg
                print("pooled", name, system, json.dumps(agg))
    (RESULTS / "hard_analysis.json").write_text(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
