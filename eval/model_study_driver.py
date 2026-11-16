"""Run every unfinished (system, dataset) pair of the model study from ONE local process.

Usage:
  python -m eval.model_study_driver agent 48 6   # 48 pairs at once, 6 tasks each: high API concurrency, one process
  python -m eval.model_study_driver b2 4 6
  python -m eval.model_study_driver clean        # delete results that ended in a client-side connection error

Threads, not processes: the study ran on a laptop with 8 GB of memory, and one process per pair crashed it.
B2 runs each generated script in a subprocess; here a lock lets only one such subprocess exist at a time.
`clean` logs every deleted result to eval/results/model_study_reruns.json, so the re-run is on record.
"""

from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
DATASETS = ["sales-heldout", "penguins-heldout", "sales-test", "penguins-test"]
OTHER_STUDIES = ("datasage-m3-large", "datasage-m3-compact", "datasage-m3-auto")


def clean() -> None:
    log_path = RESULTS / "model_study_reruns.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else {
        "note": "Tasks re-run because the first attempt ended with a client-side connection error (the laptop running "
                "the study crashed and lost its network), not a model error. Each listed result was deleted and the "
                "task was run again with the same command.", "removed": []}
    removed = 0
    for path in sorted(glob.glob(str(RESULTS / "datasage-m3-*/*/*.json")) + glob.glob(str(RESULTS / "b2-*/*/*.json"))):
        p = Path(path)
        system = p.parent.parent.name
        if system in OTHER_STUDIES:
            continue
        result = json.loads(p.read_text())
        text = f"{result['stop_reason']} {result.get('note', '')}"
        if result["stop_reason"].startswith("api_error") and "Connection error" in text:
            log["removed"].append({"system": system, "dataset": p.parent.name, "task_id": p.stem,
                                   "reason": text.strip()[:120], "at": time.strftime("%Y-%m-%d %H:%M")})
            p.unlink()
            trace = p.parent / "traces" / f"{p.stem}.jsonl"
            if trace.exists():
                trace.unlink()
            removed += 1
    log_path.write_text(json.dumps(log, indent=1))
    print(f"removed {removed}; {len(log['removed'])} logged in total")


def drive(kind: str, parallel: int, workers: int) -> None:
    os.environ.setdefault("DATASAGE_MAX_RETRIES", "10")
    from eval.run_eval import MODEL_SYSTEMS, run

    if kind == "b2":  # at most one generated-code subprocess at a time
        lock, original = threading.Lock(), subprocess.run

        def one_at_a_time(*args, **kwargs):
            with lock:
                return original(*args, **kwargs)
        subprocess.run = one_at_a_time
    prefix = "datasage-m3-" if kind == "agent" else "b2-"
    jobs = [(prefix + short, d) for d in DATASETS for short in MODEL_SYSTEMS
            if len(list((RESULTS / (prefix + short) / d).glob("*.json"))) < 20]
    print(f"{len(jobs)} jobs", flush=True)

    def one(job):
        system, dataset = job
        start = time.time()
        try:
            run(system, dataset, workers, None, RESULTS)
        except Exception:
            traceback.print_exc()
        print(f"JOB DONE {system} {dataset} in {time.time() - start:.0f}s", flush=True)

    with ThreadPoolExecutor(max_workers=parallel) as pool:
        list(pool.map(one, jobs))
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "clean":
        clean()
    else:
        drive(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
