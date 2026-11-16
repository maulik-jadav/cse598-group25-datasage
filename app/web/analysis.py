"""Data for the two analysis pages: the evaluation dashboard (/results) and a run's data profile (/profile).

Every number on /results is read from eval/results: summary.csv for each split, and the per-task JSON
files for the pooled views, the ablation comparison and the wrong-answer counts. Nothing is typed in by hand.
"""

from __future__ import annotations

import csv
import json
import math
import re
from datetime import date
from pathlib import Path

import pandas as pd

from datasage.session import load_table
from datasage.values import iso_date, loose_number, plain_number
from eval.summarize import ORDER, aggregate, load

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "eval" / "results"

SPLITS = [
    ("sales", "Sales", "dev"), ("penguins", "Penguins", "dev"),
    ("sales-heldout", "Sales", "held-out"), ("penguins-heldout", "Penguins", "held-out"),
    ("sales-test", "Sales", "test"), ("penguins-test", "Penguins", "test"),
    # scale-up splits (seeds 303, 404, 505), see docs/final/findings_scale_and_ablations.md
    ("sales-s303", "Sales", "seed 303"), ("penguins-s303", "Penguins", "seed 303"),
    ("sales-s404", "Sales", "seed 404"), ("penguins-s404", "Penguins", "seed 404"),
    ("sales-s505", "Sales", "seed 505"), ("penguins-s505", "Penguins", "seed 505"),
]
GROUPS = [
    ("devheld", "Dev + held-out", ["sales", "penguins", "sales-heldout", "penguins-heldout"]),
    ("test", "Test", ["sales-test", "penguins-test"]),
    ("all", "All six", [s[0] for s in SPLITS[:6]]),
]
# Plain names for the page. kind: baseline, datasage (earlier versions), final, ablation.
SYSTEMS = {
    "b0": ("Stakeholder script", "Baseline B0: the stakeholder's rule-based checks, no cleaning", "baseline"),
    "b1": ("Fixed cleaning script", "Baseline B1: the same fixes on every table, no model", "baseline"),
    "b2": ("Single LLM call", "Baseline B2: one model call returns cleaning code, run once with no checks", "baseline"),
    "datasage": ("Milestone 2, 235B", "DataSage at Milestone 2 with the large model", "datasage"),
    "datasage-small": ("Milestone 2, 30B", "DataSage at Milestone 2 with the small model", "datasage"),
    "datasage-fix": ("+ exclusion rule, 235B", "Milestone 2 plus the rule to drop rows that break a rule", "datasage"),
    "datasage-small-fix": ("+ exclusion rule, 30B", "The same rule with the small model", "datasage"),
    "datasage-small-fix-strict": ("+ rule, strict approver, 30B", "The 30B rule version with a stricter approval oracle", "datasage"),
    "datasage-m3": ("DataSage final, 30B", "Milestone 3: coverage check before answering, spelling merges into allowed labels", "final"),
    "datasage-m3-compact": ("Final, compact memory", "Milestone 3 with compact memory", "datasage"),
    "datasage-m3-large": ("Final, 235B", "Milestone 3 with the large model", "datasage"),
    "datasage-m3-auto": ("Final, Auto mode", "The final 30B agent with every risky fix approved, like the browser's Auto mode", "ablation"),
    "datasage-reject": ("Every risky fix rejected", "The 235B agent when the person says no to every risky fix", "ablation"),
    "datasage-novalidator": ("No validator", "The 235B agent without the validator that checks each fix and rolls back a bad one", "ablation"),
    "datasage-m3-nocoverage": ("Final, no coverage check", "The final agent without the coverage check before analyze", "ablation"),
    "datasage-m3-novalidator": ("Final, no validator", "The final agent without the validator", "ablation"),
    "datasage-m3-nomerge": ("Final, no merge rule", "The final agent with the prompt that lacks the spelling-merge rule", "ablation"),
    "datasage-m3-reject": ("Final, every risky fix rejected", "The final agent when the person says no to every risky fix", "ablation"),
}
PROGRESSION = ["datasage", "datasage-fix", "datasage-small-fix", "datasage-m3"]
ABLATION = ["datasage", "datasage-novalidator", "datasage-reject"]
FINAL = "datasage-m3"
NUMERIC = ["analysis_accuracy", "completion", "detect_precision", "detect_recall", "correction_accuracy",
           "damaged_cells_rows", "tool_call_success", "recovery", "approvals_median", "latency_median_s",
           "tokens_median", "tasks"]


def _num(text: str):
    if text in ("", None):
        return None
    value = float(text)
    return int(value) if value.is_integer() and abs(value) > 1 else value


def read_summary(path: Path | None = None) -> list[dict]:
    with open(path or RESULTS / "summary.csv", newline="") as fh:
        return [{"dataset": r["dataset"], "system": r["system"], **{k: _num(r.get(k, "")) for k in NUMERIC}}
                for r in csv.DictReader(fh)]


def _pick(agg: dict) -> dict:
    return {k: agg.get(k) for k in NUMERIC}


def results() -> dict:
    rows = read_summary()
    present = {r["system"] for r in rows}
    order = [s for s in ORDER if s in present] + sorted(present - set(ORDER))
    per_split: dict = {}
    for r in rows:
        per_split.setdefault(r["dataset"], {})[r["system"]] = {k: r[k] for k in NUMERIC}
    splits = [{"id": s, "label": f"{name} {kind}", "table": name, "kind": kind} for s, name, kind in SPLITS if s in per_split]

    groups = []
    for gid, label, members in GROUPS:
        systems = {}
        for system in order:
            if SYSTEMS.get(system, ("", "", ""))[2] == "ablation":
                continue
            if not all(system in per_split.get(s, {}) for s in members):
                continue
            tasks = [t for s in members for t in load(system, s)]
            if tasks:
                agg = _pick(aggregate(tasks))
                agg["wrong"] = sum(not t["analysis_correct"] for t in tasks)
                systems[system] = agg
        groups.append({"id": gid, "label": label, "splits": members, "systems": systems})

    # The ablations ran on the first 10 tasks of sales and penguins; compare with the same tasks of the 235B agent.
    ablation = {"splits": [], "systems": {}, "by_split": {}}
    ids = {}
    for split in ("sales", "penguins"):
        ref = load("datasage-reject", split)
        if ref:
            ablation["splits"].append(split)
            ids[split] = {t["task_id"] for t in ref}
    for system in ABLATION:
        tasks = {s: [t for t in load(system, s) if t["task_id"] in ids[s]] for s in ablation["splits"]}
        if all(tasks.values()) and tasks:
            ablation["systems"][system] = _pick(aggregate([t for s in tasks for t in tasks[s]]))
            for s, rows in tasks.items():
                ablation["by_split"].setdefault(s, {})[system] = _pick(aggregate(rows))

    failures = {}
    for path in sorted(RESULTS.glob("failures_*.json")):
        data = json.loads(path.read_text())
        failures[path.stem.removeprefix("failures_")] = {
            "wrong": len(data.get("tasks", [])), "counts": data.get("counts", []),
            "tasks": [{"id": t[0], "causes": t[1]} for t in data.get("tasks", [])]}

    return {
        "splits": splits, "order": order, "final": FINAL, "progression": [s for s in PROGRESSION if s in present],
        "systems": {s: {"label": SYSTEMS.get(s, (s, s, "datasage"))[0], "about": SYSTEMS.get(s, (s, s, "datasage"))[1],
                        "kind": SYSTEMS.get(s, (s, s, "datasage"))[2]} for s in order},
        "per_split": per_split, "groups": groups, "ablation": ablation, "failures": failures,
    }


# ---- data profile ---------------------------------------------------------------------------------

TOP = 6
BINS = 12
_STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}( 00:00:00)?$")


def _blank(v) -> bool:
    return v is None or (not isinstance(v, (list, dict, str)) and bool(pd.isna(v)))


def _text(v) -> str:
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def _as_date(v) -> date | None:
    if hasattr(v, "date") and not isinstance(v, str):
        try:
            return v.date()
        except (TypeError, ValueError):
            return None
    s = str(v).strip()
    return iso_date(s[:10]) if _STAMP.match(s) else None


def _kind(values: list) -> str:
    if not values:
        return "empty"
    if all(plain_number(v) is not None for v in values):
        return "number"
    if all(_as_date(v) is not None for v in values):
        return "date"
    share = max(sum(loose_number(v) is not None for v in values), sum(_as_date(v) is not None for v in values)) / len(values)
    if share >= 0.6:
        return "mostly numbers" if sum(loose_number(v) is not None for v in values) >= sum(_as_date(v) is not None for v in values) else "mostly dates"
    return "text"


def _scalar(v):
    if isinstance(v, float):
        return v if math.isfinite(v) else None
    return v


def _side(series: pd.Series) -> dict:
    values = [v for v in series.tolist() if not _blank(v)]
    n = len(series)
    kind = _kind(values)
    counts = pd.Series([_text(v) for v in values], dtype=object).value_counts() if values else pd.Series(dtype=int)
    out = {"type": kind, "rows": n, "missing": n - len(values), "missing_pct": (n - len(values)) / n if n else 0.0,
           "distinct": int(len(counts))}
    if kind in ("number", "mostly numbers"):
        nums = [loose_number(v) for v in values]
        odd = [v for v in values if plain_number(v) is None]
        nums = [x for x in nums if x is not None]
        out.update(base="number", min=_scalar(min(nums)), max=_scalar(max(nums)), mean=_scalar(sum(nums) / len(nums)), _nums=nums)
    elif kind in ("date", "mostly dates"):
        days = [d for d in (_as_date(v) for v in values) if d is not None]
        odd = [v for v in values if _as_date(v) is None]
        out.update(base="date", min=min(days).isoformat(), max=max(days).isoformat(), _nums=[d.toordinal() for d in days])
    else:
        out["base"] = "text"
        out["top"] = [[str(k), int(c)] for k, c in counts.head(TOP).items()]
        out["other"] = int(counts.iloc[TOP:].sum()) if len(counts) > TOP else 0
        return out
    if odd:  # values that are not clean numbers or dates yet
        bad = pd.Series([_text(v) for v in odd], dtype=object).value_counts()
        out["unclean"] = {"count": len(odd), "examples": [[str(k), int(c)] for k, c in bad.head(4).items()]}
    return out


def _histogram(sides: list[dict], kind: str) -> None:
    pools = [s["_nums"] for s in sides if s and s.get("_nums") and s["base"] == kind]
    if not pools:
        return
    lo, hi = min(min(p) for p in pools), max(max(p) for p in pools)
    bins = 1 if hi == lo else BINS
    width = (hi - lo) / bins if bins > 1 else 1
    edges = [lo + i * width for i in range(bins + 1)]
    for side in sides:
        if not side or not side.get("_nums") or side["base"] != kind:
            continue
        counts = [0] * bins
        for x in side["_nums"]:
            counts[min(bins - 1, int((x - lo) / width)) if bins > 1 else 0] += 1
        labels = [date.fromordinal(int(round(e))).isoformat() for e in edges] if kind == "date" else edges
        side["hist"] = {"edges": labels, "counts": counts}


def _key(v):
    """How a cell is compared: 640 and 640.0 are the same, but "1,800" and 1800 differ (a fix changed the cell)."""
    if _blank(v):
        return None
    number = plain_number(v)
    if number is not None:
        return ("n", number)
    day = _as_date(v)
    return ("d", day.isoformat()) if day else ("t", str(v))


def _diff(before: pd.Series, after: pd.Series) -> dict:
    common = after.index.intersection(before.index)
    filled = blanked = edited = 0
    for row in common:
        a, b = before.at[row], after.at[row]
        ca, cb = _key(a), _key(b)
        if ca == cb:
            continue
        if ca is None:
            filled += 1
        elif cb is None:
            blanked += 1
        else:
            edited += 1
    return {"filled": filled, "blanked": blanked, "edited": edited, "cells_changed": filled + blanked + edited}


def read_cleaned(path: Path) -> pd.DataFrame:
    """cleaned.csv keeps the source row ids in its first column, named "row"."""
    df = load_table(path)
    first = df.columns[0]
    df.index = pd.Index([int(v) for v in df[first]], name="row")
    df = df.drop(columns=first)
    return df.rename(columns={c: str(c)[:-2] for c in df.columns if str(c).endswith(".1") and str(c)[:-2] == "row"})


def profile(input_path: Path, cleaned_path: Path) -> dict:
    before = load_table(input_path)
    after = read_cleaned(cleaned_path)
    before.columns = [str(c) for c in before.columns]
    after.columns = [str(c) for c in after.columns]
    names = list(before.columns) + [c for c in after.columns if c not in before.columns]
    removed = [int(r) for r in before.index if r not in after.index]
    columns = []
    for name in names:
        b = _side(before[name]) if name in before.columns else None
        a = _side(after[name]) if name in after.columns else None
        for kind in ("number", "date"):
            _histogram([b, a], kind)
        change = _diff(before[name], after[name]) if b and a else {"filled": 0, "blanked": 0, "edited": 0, "cells_changed": 0}
        change["type_changed"] = bool(b and a and b["type"] != a["type"])
        change["added"], change["dropped"] = b is None, a is None
        for side in (b, a):
            if side:
                side.pop("_nums", None)
        columns.append({"name": name, "before": b, "after": a, "change": change})
    missing = lambda df: int(df.isna().sum().sum())  # noqa: E731
    return {
        "rows_before": int(len(before)), "rows_after": int(len(after)), "rows_removed": len(removed),
        "removed_ids": removed[:50], "columns_before": int(len(before.columns)), "columns_after": int(len(after.columns)),
        "cells_changed": int(sum(c["change"]["cells_changed"] for c in columns)),
        "missing_before": missing(before), "missing_after": missing(after), "columns": columns,
    }


_RUN_ID = re.compile(r"^[0-9a-f]{6,32}$")


def saved_run(out_root: Path, run_id: str) -> dict | None:
    """A finished run from an earlier server session: its folder, plus the input and question named in report.md."""
    if not _RUN_ID.match(run_id):
        return None
    folder = out_root / run_id
    report = folder / "report.md"
    if not report.is_file():
        return None
    text = report.read_text(errors="replace")
    found = re.search(r"^- Input: `(.+?)`", text, re.M)
    question = re.search(r"^- Question: (.+)$", text, re.M)
    if not found:
        return None
    path = Path(found.group(1)).resolve()
    if not path.is_file() or not (path.is_relative_to(ROOT) or path.is_relative_to(folder.resolve())):
        return None
    return {"input_path": path, "out_dir": folder, "question": question.group(1).strip() if question else ""}


def run_profile(run_id: str, runs: dict, out_root: Path) -> tuple[int, dict]:
    """(status, body) for GET /api/runs/<id>/profile. Uses the live run if the server still has it."""
    live = runs.get(run_id)
    if live is not None:
        if not live.done:
            return 409, {"error": "the run is still going"}
        found = {"input_path": Path(live.input_path), "out_dir": Path(live.out_dir), "question": live.question}
    else:
        found = saved_run(out_root, run_id)
    if not found:
        return 404, {"error": "no such run"}
    cleaned = found["out_dir"] / "cleaned.csv"
    if not cleaned.is_file():
        return 404, {"error": "this run has no cleaned table"}
    try:
        body = profile(found["input_path"], cleaned)
    except Exception as err:  # shown on the page; the server keeps running
        return 500, {"error": f"could not profile this run: {type(err).__name__}: {err}"}
    body.update(run_id=run_id, question=found["question"], input=found["input_path"].name)
    return 200, body
