"""Model comparison study: probe every chat model on the API for tool calling, then aggregate results.

Usage:
  python -m eval.model_study probe          # list models, probe tool calling, write eval/results/model_probe.json
  python -m eval.model_study aggregate      # read eval/results/<system>/<dataset>/, write eval/results/study_models.json

The probe sends two requests per chat model, both at temperature 0 with no reasoning setting (the same call the
agent makes): a tiny one with one toy tool, and the real first DataSage turn (system prompt V3, the 13 tool
schemas, profile and sample rows of one held-out table). A model passes when the real turn returns at least one
tool call whose name is a DataSage tool and whose arguments parse as JSON.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

# Family members the model list names only under a family id (reasoning effort picks the member).
FAMILY_MEMBERS = ["qwen3-30b-a3b-instruct-2507", "qwen3-30b-a3b-thinking-2507", "qwen3-235b-a22b-instruct-2507",
                  "qwen3-235b-a22b-thinking-2507", "olmo3-32b-instruct", "olmo3-32b-think", "olmo3-7b-instruct",
                  "olmo3-7b-think", "qwen3-vl-32b-instruct", "qwen3-vl-32b-thinking"]

TOY_TOOL = [{"type": "function", "function": {
    "name": "get_total", "description": "Add two numbers and return the total.",
    "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                   "required": ["a", "b"]}}}]


def _call(client, model: str, messages: list[dict], tools: list[dict]) -> dict:
    start = time.time()
    try:
        response = client.chat.completions.create(model=model, messages=messages, tools=tools, tool_choice="auto",
                                                  temperature=0, timeout=240)
    except Exception as err:
        return {"ok": False, "error": f"{type(err).__name__}: {str(err)[:300]}", "seconds": round(time.time() - start, 1)}
    message = response.choices[0].message
    calls = []
    for c in message.tool_calls or []:
        try:
            args = json.loads(c.function.arguments or "{}")
            parsed = isinstance(args, dict)
        except json.JSONDecodeError:
            args, parsed = c.function.arguments, False
        calls.append({"name": c.function.name, "args_parse": parsed, "args": str(args)[:200]})
    usage = response.usage
    return {"ok": True, "calls": calls, "content": (message.content or "")[:300],
            "finish_reason": response.choices[0].finish_reason, "seconds": round(time.time() - start, 1),
            "prompt_tokens": usage.prompt_tokens if usage else None,
            "completion_tokens": usage.completion_tokens if usage else None}


def probe_one(client, model: str) -> dict:
    from datasage.agent import SYSTEM_PROMPT_V3, _first_message
    from datasage.session import Session, load_rules, load_table
    from datasage.tools import ALL_TOOLS, TOOL_SCHEMAS
    from eval.scoring import all_bundles

    toy = _call(client, model, [{"role": "user", "content": "What is 17 plus 25? Use the get_total tool."}], TOY_TOOL)
    bundle = all_bundles("sales-heldout")[0]
    task = bundle.tasks[0]
    session = Session(load_table(bundle.messy_path), source=str(bundle.messy_path), request=task["question"],
                      rules=load_rules(bundle.rules_path))
    real = _call(client, model, [{"role": "system", "content": SYSTEM_PROMPT_V3},
                                 {"role": "user", "content": _first_message(session)}], TOOL_SCHEMAS)
    toy_pass = toy["ok"] and any(c["name"] == "get_total" and c["args_parse"] for c in toy["calls"])
    real_pass = real["ok"] and any(c["name"] in ALL_TOOLS and c["args_parse"] for c in real["calls"])
    if real_pass:
        verdict = "tool calling works"
    elif not real["ok"]:
        verdict = "API error: " + real["error"][:160]
    elif real["calls"]:
        verdict = "tool calls returned but invalid (unknown tool or arguments not JSON)"
    else:
        verdict = "no tool calls (answered in text)"
    return {"model": model, "toy_pass": toy_pass, "real_pass": real_pass, "verdict": verdict, "toy": toy, "real": real}


def probe(workers: int) -> None:
    from datasage.agent import make_client

    client = make_client()
    listed = [m.model_dump() for m in client.models.list().data]
    chat = [m for m in listed if m.get("mode") == "chat"]
    others = [{"model": m["id"], "mode": m.get("mode")} for m in listed if m.get("mode") != "chat"]
    names = [m["id"] for m in chat if not m.get("family")] + FAMILY_MEMBERS
    meta = {m["id"]: {k: m.get(k) for k in ("context_window", "supports_function_calling", "reasoning", "family",
                                              "description", "quantization")} for m in chat}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(lambda n: probe_one(client, n), names))
    for row in rows:
        row["listed"] = meta.get(row["model"])
        print(f"{row['model']:34s} toy={row['toy_pass']!s:5s} real={row['real_pass']!s:5s} {row['verdict']}", flush=True)
    out = {"listed_models": len(listed), "chat_models": [m["id"] for m in chat], "not_chat": others, "probes": rows}
    (RESULTS / "model_probe.json").write_text(json.dumps(out, indent=2, default=str))


# ---------------------------------------------------------------- aggregation

HELDOUT_TEST = ["sales-heldout", "penguins-heldout", "sales-test", "penguins-test"]
DEV = ["sales", "penguins"]


def _load(system: str, dataset: str) -> list[dict]:
    folder = RESULTS / system / dataset
    return [json.loads(p.read_text()) for p in sorted(folder.glob("*.json"))] if folder.exists() else []


def bootstrap_ci(values: list[int], reps: int = 10000, seed: int = 598) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    n = len(values)
    means = sorted(sum(rng.choice(values) for _ in range(n)) / n for _ in range(reps))
    return means[int(0.025 * reps)], means[int(0.975 * reps) - 1]


def _p90(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round(0.9 * (len(ordered) - 1))))]


def aggregate_rows(rows: list[dict]) -> dict:
    n = len(rows)
    correct = [int(r["analysis_correct"]) for r in rows]
    tp, fp, fn = (sum(r[k] for r in rows) for k in ("detect_tp", "detect_fp", "detect_fn"))
    cleaned = [r for r in rows if r.get("cleaned_available")]
    planted = sum(r["planted"] for r in cleaned)
    calls = sum(r["tool_calls"] for r in rows)
    errors = sum(r["tool_errors"] for r in rows)
    lo, hi = bootstrap_ci(correct)
    stops: dict[str, int] = {}
    for r in rows:
        key = r["stop_reason"].split(":")[0]
        stops[key] = stops.get(key, 0) + 1
    return {
        "tasks": n, "correct": sum(correct), "accuracy": sum(correct) / n, "ci95": [lo, hi],
        "completion": sum(r["completed"] for r in rows) / n,
        "detect_precision": tp / (tp + fp) if tp + fp else 0.0, "detect_recall": tp / (tp + fn) if tp + fn else 0.0,
        "errors_handled": sum(r["corrections"] for r in cleaned) / planted if planted else 0.0,
        "damaged_cells_rows": sum(r["damaged_rows"] + r["damaged_cells"] for r in rows),
        "tool_calls": calls, "tool_errors": errors,
        "tool_error_rate": errors / calls if calls else None,
        "recovered_errors": sum(r["recovered_errors"] for r in rows),
        "approvals_median": statistics.median(r["approvals_asked"] for r in rows) if calls else None,
        "tool_calls_median": statistics.median(r["tool_calls"] for r in rows) if calls else None,
        "seconds_median": statistics.median(r["seconds"] for r in rows), "seconds_p90": _p90([r["seconds"] for r in rows]),
        "tokens_median": statistics.median(r["tokens"] for r in rows),
        "stop_reasons": stops,
    }


def trace_stats(system: str, datasets: list[str]) -> dict:
    """Behaviour read from the agent traces: error kinds, loops, nudges, and the failure causes of wrong tasks
    (eval.failures.diagnose, the same classifier used in Milestones 2 and 3)."""
    from eval.failures import diagnose

    error_kinds: dict[str, int] = {}
    causes: dict[str, int] = {}
    loops = nudges = tasks_with_errors = 0
    wrong = tasks = looked_outside = excluded = 0
    for dataset in datasets:
        folder = RESULTS / system / dataset
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.json")):
            result = json.loads(path.read_text())
            trace_path = folder / "traces" / f"{result['task_id']}.jsonl"
            trace = [json.loads(line) for line in trace_path.read_text().splitlines()] if trace_path.exists() else []
            tools = [e for e in trace if e.get("event") == "tool"]
            tasks += 1
            table = result["task_id"].rsplit("_", 1)[0]
            spec = next(t["spec"] for t in json.loads((ROOT / "datasets" / dataset / table / "tasks.json").read_text())
                        if t["task_id"] == result["task_id"])
            used = set(spec.get("group_by") or []) | {spec.get("metric")} | {f["column"] for f in spec.get("filters") or []}
            looked_outside += any(e["name"].startswith("check_") and isinstance(e["args"], dict)
                                  and e["args"].get("column") not in (None, *used) for e in tools)
            excluded += any(e["name"] == "exclude_rows" and e["ok"] and isinstance(e["output"], dict)
                            and e["output"].get("applied") for e in tools)
            nudges += sum(e.get("event") == "nudge" for e in trace)
            bad = [e for e in tools if not e["ok"]]
            tasks_with_errors += bool(bad)
            for e in bad:
                out = e["output"] if isinstance(e["output"], dict) else {}
                text = str(out.get("error", ""))
                kind = ("invalid arguments (schema or JSON)" if text.startswith("invalid arguments") else
                        "unknown tool name" if text.startswith("unknown tool") else
                        "fix rolled back by validator" if "validation" in out else
                        "finish before analyze" if e["name"] == "finish" else
                        f"{e['name']} raised (bad column, value or expression)")
                error_kinds[kind] = error_kinds.get(kind, 0) + 1
            run = 0
            for e in tools:  # three or more failed calls in a row = an error loop
                run = run + 1 if not e["ok"] else 0
                if run == 3:
                    loops += 1
            if not result["analysis_correct"]:
                wrong += 1
                planted = json.loads((ROOT / "datasets" / dataset / table / "planted.json").read_text())["errors"]
                for reason in diagnose(result, trace, planted):
                    if reason.startswith("stopped early: "):
                        reason = "stopped early: " + reason[len("stopped early: "):].split(":")[0]
                    causes[reason] = causes.get(reason, 0) + 1
    return {"wrong_tasks": wrong, "failure_causes": dict(sorted(causes.items(), key=lambda kv: -kv[1])),
            "tool_error_kinds": error_kinds, "error_loops": loops, "nudges": nudges,
            "tasks_with_tool_errors": tasks_with_errors,
            "tasks_checking_a_column_the_question_does_not_use": looked_outside / tasks if tasks else None,
            "tasks_with_an_applied_exclude_rows": excluded / tasks if tasks else None}


def study_systems() -> list[tuple[str, str, str, str]]:
    """(short name, model id, agent system, single-call system) for every model in the study."""
    from datasage.agent import SMALL_MODEL
    from eval.run_eval import MODEL_SYSTEMS

    rows = [(s, m, f"datasage-m3-{s}", f"b2-{s}") for s, m in MODEL_SYSTEMS.items()]
    return rows + [("qwen3-30b-original", SMALL_MODEL, "datasage-m3", "b2-qwen3-30b")]


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float:
    rx, ry = _ranks(xs), _ranks(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    return cov / (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5


def summary(models: dict) -> dict:
    """Cross-model facts used in docs/final/findings_models.md: the accuracy/latency and accuracy/token Pareto
    fronts, and how accuracy relates to looking beyond the question's columns (models with under 5% tool errors)."""
    rows = [(s, e["agent"]["heldout_test"], e["agent"]["behaviour"]) for s, e in models.items()
            if e["agent"]["heldout_test"] and e["agent"]["heldout_test"]["tasks"] == 80 and not s.endswith("-original")]

    def front(key: str) -> list[str]:
        keep = []
        for s, a, _ in rows:
            dominated = any(b["accuracy"] >= a["accuracy"] and b[key] <= a[key]
                            and (b["accuracy"] > a["accuracy"] or b[key] < a[key]) for _, b, _ in rows)
            if not dominated:
                keep.append(s)
        return sorted(keep, key=lambda s: models[s]["agent"]["heldout_test"][key])

    clean = [(a, b) for _, a, b in rows if (a["tool_error_rate"] or 0) < 0.05]
    return {
        "models_with_80_tasks": len(rows),
        "pareto_accuracy_vs_median_seconds": front("seconds_median"),
        "pareto_accuracy_vs_median_tokens": front("tokens_median"),
        "spearman_accuracy_vs_checking_outside_question_columns": {
            "models": len(clean),
            "rho": spearman([a["accuracy"] for a, _ in clean],
                            [b["tasks_checking_a_column_the_question_does_not_use"] for _, b in clean])},
        "spearman_accuracy_vs_median_seconds": spearman([a["accuracy"] for _, a, _ in rows],
                                                        [a["seconds_median"] for _, a, _ in rows]),
    }


def aggregate() -> None:
    probe_file = RESULTS / "model_probe.json"
    probe_data = json.loads(probe_file.read_text()) if probe_file.exists() else None
    out = {"note": "heldout_test pools sales-heldout, penguins-heldout, sales-test and penguins-test (80 tasks); "
                   "ci95 is a 10,000-sample bootstrap of the per-task accuracy; seconds and tokens are per task.",
           "probe": probe_data, "models": {}}
    for short, model, agent_system, single_system in study_systems():
        entry = {"model": model, "agent_system": agent_system, "single_call_system": single_system}
        for label, system in (("agent", agent_system), ("single_call", single_system)):
            per = {d: aggregate_rows(_load(system, d)) for d in HELDOUT_TEST + DEV if _load(system, d)}
            pooled = [r for d in HELDOUT_TEST for r in _load(system, d)]
            dev = [r for d in DEV for r in _load(system, d)]
            entry[label] = {"heldout_test": aggregate_rows(pooled) if pooled else None,
                            "dev": aggregate_rows(dev) if dev else None, "per_dataset": per}
        entry["agent"]["behaviour"] = trace_stats(agent_system, HELDOUT_TEST)
        a, b = entry["agent"]["heldout_test"], entry["single_call"]["heldout_test"]
        if a and b and a["tasks"] == b["tasks"]:
            entry["agent_minus_single_call"] = a["accuracy"] - b["accuracy"]
        out["models"][short] = entry
    out["summary"] = summary(out["models"])
    (RESULTS / "study_models.json").write_text(json.dumps(out, indent=2, default=str))
    for short, e in out["models"].items():
        a, b = e["agent"]["heldout_test"], e["single_call"]["heldout_test"]
        agent = f"{a['correct']}/{a['tasks']} ({100 * a['accuracy']:.1f}%)" if a else "-"
        single = f"{b['correct']}/{b['tasks']}" if b else "-"
        print(f"{short:22s} agent {agent:16s} single call {single}")


def table() -> None:
    """Print the comparison table (Markdown) from study_models.json, best agent accuracy first."""
    data = json.loads((RESULTS / "study_models.json").read_text())["models"]

    def pct(x):
        return "n/a" if x is None else f"{100 * x:.1f}"

    rows = []
    for short, e in data.items():
        a, b = e["agent"]["heldout_test"], e["single_call"]["heldout_test"]
        if not a:
            continue
        rows.append((a["accuracy"], short, e, a, b))
    print("| Model | n | Agent correct | 95% CI | Single call | Gain | Done | Detect P/R | Errors handled | Damage "
          "| Tool errors | Recovered | Approvals | Median s | p90 s | Median tokens |")
    print("|---|---:|---:|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for acc, short, e, a, b in sorted(rows, key=lambda r: (-r[0], r[3]["seconds_median"])):
        single = f"{pct(b['accuracy'])}% ({b['correct']}/{b['tasks']})" if b else "n/a"
        gain = e.get("agent_minus_single_call")
        terr = f"{a['tool_errors']}/{a['tool_calls']} ({pct(a['tool_error_rate'])}%)"
        name = e["model"] + (" (original M3 run)" if short.endswith("-original") else "")
        print(f"| {name} | {a['tasks']} | {pct(acc)}% ({a['correct']}) | {pct(a['ci95'][0])}-{pct(a['ci95'][1])} "
              f"| {single} | {'n/a' if gain is None else f'{100 * gain:+.1f}'} | {pct(a['completion'])}% "
              f"| {a['detect_precision']:.2f}/{a['detect_recall']:.2f} | {pct(a['errors_handled'])}% "
              f"| {a['damaged_cells_rows']} | {terr} | {a['recovered_errors']} | {a['approvals_median']} "
              f"| {a['seconds_median']:.0f} | {a['seconds_p90']:.0f} | {a['tokens_median']:,.0f} |")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["probe", "aggregate", "table"])
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    {"probe": lambda: probe(args.workers), "aggregate": aggregate, "table": table}[args.command]()


if __name__ == "__main__":
    main()
