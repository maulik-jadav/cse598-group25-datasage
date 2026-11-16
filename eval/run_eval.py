"""Run systems over the benchmark and save one JSON result per task (resumable).

Usage:
  python -m eval.run_eval --system datasage --dataset sales --workers 4
  python -m eval.run_eval --system b2 --dataset penguins
Systems: b0, b1, b2, datasage, datasage-small, datasage-reject, datasage-novalidator,
         datasage-fix, datasage-fix-strict, datasage-small-fix, datasage-small-fix-strict,
         datasage-m3 (small model, the default agent), datasage-m3-compact, datasage-m3-large,
         datasage-m3-auto (datasage-m3 with every risky fix approved, like the browser's Auto mode),
         and the ablations of datasage-m3: datasage-m3-nocoverage, datasage-m3-novalidator,
         datasage-m3-nomerge (prompt without the merge rule), datasage-m3-reject (every risky fix rejected)
Datasets: sales, penguins (dev), sales-heldout, penguins-heldout, sales-test, penguins-test (seed 202),
          sales-hard, penguins-hard, sales-hard2, penguins-hard2 (eval/generate_hard.py; extra system datasage-m3-gptoss),
          and sales-s303, penguins-s303, sales-s404, penguins-s404, sales-s505, penguins-s505
"""

from __future__ import annotations

import argparse
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from baselines import systems
from datasage.agent import SMALL_MODEL, make_client
from eval.scoring import SystemOutput, all_bundles, score

ROOT = Path(__file__).resolve().parent

SYSTEMS = {
    "b0": lambda b, t, c, trace: systems.run_b0(b, t),
    "b1": lambda b, t, c, trace: systems.run_b1(b, t),
    "b2": lambda b, t, c, trace: systems.run_b2(b, t, client=c),
    "datasage": lambda b, t, c, trace: systems.run_datasage(b, t, client=c, trace_path=trace),
    "datasage-small": lambda b, t, c, trace: systems.run_datasage(b, t, model=SMALL_MODEL, client=c, trace_path=trace),
    "datasage-reject": lambda b, t, c, trace: systems.run_datasage(b, t, approver="reject", client=c, trace_path=trace),
    "datasage-novalidator": lambda b, t, c, trace: systems.run_datasage(b, t, use_validator=False, client=c, trace_path=trace),
    # Milestone 2 failure-analysis fix: exclusion rule in the prompt, with the normal or the strict oracle.
    "datasage-fix": lambda b, t, c, trace: systems.run_datasage(b, t, prompt_fix=True, client=c, trace_path=trace),
    "datasage-fix-strict": lambda b, t, c, trace: systems.run_datasage(b, t, prompt_fix=True, approver="oracle-strict",
                                                                     client=c, trace_path=trace),
    "datasage-small-fix": lambda b, t, c, trace: systems.run_datasage(b, t, model=SMALL_MODEL, prompt_fix=True,
                                                                    client=c, trace_path=trace),
    "datasage-small-fix-strict": lambda b, t, c, trace: systems.run_datasage(b, t, model=SMALL_MODEL, prompt_fix=True,
                                                                           approver="oracle-strict", client=c, trace_path=trace),
    # Milestone 3 (Section 6, items 1 and 2): compact memory, coverage check, spelling merges.
    "datasage-m3": lambda b, t, c, trace: systems.run_datasage(b, t, model=SMALL_MODEL, m3=True, client=c, trace_path=trace),
    "datasage-m3-compact": lambda b, t, c, trace: systems.run_datasage(b, t, model=SMALL_MODEL, m3=True, memory="compact",
                                                                     client=c, trace_path=trace),
    "datasage-m3-large": lambda b, t, c, trace: systems.run_datasage(b, t, m3=True, client=c, trace_path=trace),
}

# Hard split study: one extra planner model of a different family (same DataSage M3 setup as datasage-m3).
EXTRA_MODEL = "gpt-oss-120b"
SYSTEMS["datasage-m3-gptoss"] = lambda b, t, c, trace: systems.run_datasage(b, t, model=EXTRA_MODEL, m3=True, client=c,
                                                                           trace_path=trace)

# The browser app's Auto mode: the same agent as datasage-m3, but every risky fix is approved without a check.
SYSTEMS["datasage-m3-auto"] = lambda b, t, c, trace: systems.run_datasage(b, t, model=SMALL_MODEL, m3=True, approver="auto",
                                                                          client=c, trace_path=trace)

# Ablations of the final system (datasage-m3): each switches off one mechanism and keeps the rest.
_M3 = dict(model=SMALL_MODEL, m3=True)
SYSTEMS.update({
    "datasage-m3-nocoverage": lambda b, t, c, trace: systems.run_datasage(b, t, coverage=False, client=c, trace_path=trace, **_M3),
    "datasage-m3-novalidator": lambda b, t, c, trace: systems.run_datasage(b, t, use_validator=False, client=c,
                                                                         trace_path=trace, **_M3),
    "datasage-m3-nomerge": lambda b, t, c, trace: systems.run_datasage(b, t, prompt="v2", client=c, trace_path=trace, **_M3),
    "datasage-m3-reject": lambda b, t, c, trace: systems.run_datasage(b, t, approver="reject", client=c, trace_path=trace, **_M3),
})

DATASETS = ["sales", "penguins", "sales-heldout", "penguins-heldout", "sales-test", "penguins-test",
            # scale-up splits made with the same generator and new seeds (303, 404, 505)
            "sales-s303", "penguins-s303", "sales-s404", "penguins-s404", "sales-s505", "penguins-s505",
            # hard split (eval/generate_hard.py): bigger tables, mass rule breaks, distractors; hard2 is a second seed
            "sales-hard", "penguins-hard", "sales-hard2", "penguins-hard2"]

# Model comparison study (docs/final/findings_models.md): datasage-m3-<short> is datasage-m3 with only the model
# changed, and b2-<short> is the B2 single call with that model. Models that passed the tool-calling probe in
# eval/model_study.py. datasage-m3-qwen3-30b is datasage-m3 run again alongside the others, so its latency is
# measured under the same load.
MODEL_SYSTEMS = {
    "qwen3-30b": SMALL_MODEL, "qwen3-235b": "qwen3-235b-a22b-instruct-2507", "qwen3-30b-think": "qwen3-30b-a3b-thinking-2507",
    "qwen3-235b-think": "qwen3-235b-a22b-thinking-2507", "qwen3-coder-30b": "qwen3-coder-30b-a3b-instruct",
    "qwen3-coder-next": "qwen3-coder-next", "qwen3-vl-32b": "qwen3-vl-32b-instruct",
    "qwen3-vl-32b-think": "qwen3-vl-32b-thinking", "qwen35-27b": "qwen35-27b", "qwen35-122b": "qwen35-122b-a10b",
    "qwen35-397b": "qwen35-397b-a17b", "qwen36-27b": "qwen36-27b", "qwen36-35b": "qwen36-35b-a3b",
    "qwen38-27b": "qwen38-27b", "qwen-agentworld-35b": "qwen-agentworld-35b-a3b", "hemmingway-1-5": "hemmingway-1-5",
    "olmo3-7b": "olmo3-7b-instruct", "olmo3-7b-think": "olmo3-7b-think", "olmo3-32b": "olmo3-32b-instruct",
    "olmo3-32b-think": "olmo3-32b-think", "gpt-oss-120b": "gpt-oss-120b", "llama4-scout": "llama4-scout-17b",
    "llama4-maverick": "llama4-maverick-17b", "gemma4-31b": "gemma4-31b-it", "granite41-30b": "granite41-30b",
    "devstral2-123b": "devstral2-123b", "mistral-large-4": "mistral-large-4", "glm-5-2": "glm-5-2",
    "glm-5-3": "glm-5-3", "glm-5-3-flash": "glm-5-3-flash", "glm-5-3-spec": "glm-5-3-spec",
    "deepseek-v4-1-flash": "deepseek-v4-1-flash", "kimi-k2-7-code": "kimi-k2-7-code", "minimax-m2-7": "minimax-m2-7",
    "minimax-m3": "minimax-m3", "mimo-v2-6-flash": "mimo-v2-6-flash", "mimo-v2-6-pro": "mimo-v2-6-pro",
    "beam-1-0": "beam-1-0", "inkling-small": "inkling-small", "laguna-s-2-1": "laguna-s-2-1",
    "muse-glimmer-30b": "muse-glimmer-30b", "muse-spark-open": "muse-spark-open", "ornith-1-5-35b": "ornith-1-5-35b-a3b",
}


def _model_systems(short: str, model: str) -> dict:
    return {
        f"datasage-m3-{short}": lambda b, t, c, trace: systems.run_datasage(b, t, model=model, m3=True, client=c,
                                                                           trace_path=trace),
        f"b2-{short}": lambda b, t, c, trace: systems.run_b2(b, t, model=model, client=c),
    }


for _short, _model in MODEL_SYSTEMS.items():
    SYSTEMS.update(_model_systems(_short, _model))


def run(system: str, dataset: str, workers: int, limit: int | None, results_dir: Path, only: set[str] | None = None) -> None:
    out_dir = results_dir / system / dataset
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(b, t) for b in all_bundles(dataset) for t in b.tasks if not only or t["task_id"] in only][:limit]
    client = make_client() if system not in ("b0", "b1") else None

    def one(bundle, task):
        path = out_dir / f"{task['task_id']}.json"
        if path.exists():
            return task["task_id"], "cached"
        trace = out_dir / "traces" / f"{task['task_id']}.jsonl"
        try:
            output = SYSTEMS[system](bundle, task, client, trace)
        except Exception as err:  # a crash counts as an incomplete task, not a pipeline failure
            output = SystemOutput(answer=None, cleaned=None, completed=False, stop_reason="crash",
                                  note=f"{type(err).__name__}: {err}"[:300])
            (out_dir / f"{task['task_id']}.error.txt").write_text(traceback.format_exc())
        result = score(bundle, task, output)
        result.update(system=system, dataset=dataset, question=task["question"], reference_answer=task["reference_answer"],
                      issues_reported=sorted(map(list, output.issues)))
        path.write_text(json.dumps(result, indent=2, default=str))
        return task["task_id"], "ok" if result["analysis_correct"] else f"wrong ({result['stop_reason']})"

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(one, b, t) for b, t in jobs]
        for done, future in enumerate(as_completed(futures), 1):
            task_id, status = future.result()
            print(f"[{system}/{dataset}] {done}/{len(jobs)} {task_id}: {status}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", required=True, choices=list(SYSTEMS))
    parser.add_argument("--dataset", required=True, choices=DATASETS)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--only", default="", help="comma list of task ids to run")
    parser.add_argument("--results", default=str(ROOT / "results"))
    args = parser.parse_args()
    only = {t.strip() for t in args.only.split(",") if t.strip()}
    run(args.system, args.dataset, args.workers, args.limit, Path(args.results), only)


if __name__ == "__main__":
    main()
