"""Runs DataSage in a worker thread for the browser app and turns its progress into events.

The agent loop itself is unchanged: `run_agent` gets a `BrowserApprover` (it waits for a click in the
page) and an `on_event` callback (it turns each tool call into an event with the table's current state).
"""

from __future__ import annotations

import math
import threading
import time
import uuid
from pathlib import Path

import pandas as pd

from datasage.agent import run_agent
from datasage.approval import Approver
from datasage.report import write_outputs
from datasage.session import load_table

MAX_ROWS = 200          # rows shown in the page
APPROVAL_TIMEOUT = 600  # seconds; an unanswered approval (page closed) counts as rejected

LABELS = {
    "lookup_rules": "Reading the rules",
    "profile_dataset": "Profiling the table",
    "check_duplicates": "Looking for duplicate rows",
    "check_missing": "Looking for blanks in {column}",
    "check_label_variants": "Checking labels in {column}",
    "check_dates": "Checking dates in {column}",
    "check_numeric": "Checking numbers in {column}",
    "check_out_of_range": "Checking the range of {column}",
    "check_cross_column": "Checking {column} against its formula",
    "trim_whitespace": "Trimming spaces in {column}",
    "normalize_labels": "Merging labels in {column}",
    "drop_duplicates": "Removing duplicate rows",
    "parse_dates": "Reading dates in {column}",
    "cast_numeric": "Turning text into numbers in {column}",
    "exclude_rows": "Dropping rows that break a rule",
    "recompute_column": "Recomputing {column}",
    "set_missing": "Blanking unreadable values in {column}",
    "fill_missing": "Filling blanks in {column}",
    "analyze": "Computing the answer",
    "finish": "Writing the report",
}
QUESTIONS = {
    "drop_duplicates": "Remove the duplicate rows?",
    "exclude_rows": "Drop these rows from the analysis?",
    "normalize_labels": "Merge these labels in {column}?",
    "parse_dates": "Convert the dates in {column}?",
    "set_missing": "Blank the unreadable values in {column}?",
    "fill_missing": "Fill the blanks in {column}?",
    "cast_numeric": "Turn the text in {column} into numbers?",
    "recompute_column": "Recompute {column} from its formula?",
    "trim_whitespace": "Trim the spaces in {column}?",
}


def label(tool: str, args: dict) -> str:
    return LABELS.get(tool, tool).format(column=args.get("column", "a column"))


def _same(a, b) -> bool:
    if _blank(a) and _blank(b):
        return True
    if _blank(a) or _blank(b):
        return False
    try:
        return float(a) == float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)


def _blank(v) -> bool:
    return v is None or v is pd.NA or (isinstance(v, float) and math.isnan(v)) or (not isinstance(v, str) and pd.isna(v))


def _text(v) -> str:
    if _blank(v):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def table_state(session) -> dict:
    """Per shown row: removed or not, and per cell its current text and state.

    States: "" (plain), "flag" (a check found a problem that is still open), "fixed" (a fix changed it),
    "kept" (a fix for it was rejected, so it stays as a caveat). A row can be "removed", "flag" or "kept".
    """
    original, current = session.original, session.current
    shown = list(original.index[:MAX_ROWS])
    flagged: dict[int, set] = {}
    for (kind, column), issue in session.issues.items():
        for r in issue.get("rows", []):
            flagged.setdefault(int(r), set()).add(column)
    kept: dict[int, set] = {}
    for rej in session.rejected:
        args = rej["args"]
        rows = args.get("rows") or []
        if rej["tool"] in ("exclude_rows", "drop_duplicates"):
            for r in rows or [r for r, cols in flagged.items() if "*" in cols]:
                kept.setdefault(int(r), set()).add("*")
        else:
            col = args.get("column")
            for r, cols in flagged.items():
                if col in cols and (not rows or r in rows):
                    kept.setdefault(r, set()).add(col)
    rows_out = {}
    for r in shown:
        r = int(r)
        removed = r not in current.index
        cells = {}
        for col in original.columns:
            before = original.at[r, col]
            now = before if removed else current.at[r, col]
            state = ""
            if not removed and not _same(before, now):
                state = "fixed"
            elif col in kept.get(r, ()) or ("*" in kept.get(r, ()) and col in flagged.get(r, ())):
                state = "kept"
            elif col in flagged.get(r, ()):
                state = "flag"
            cells[str(col)] = {"text": _text(now), "state": state}
        row_state = "removed" if removed else "kept" if "*" in kept.get(r, ()) else "flag" if "*" in flagged.get(r, ()) else ""
        rows_out[r] = {"state": row_state, "cells": cells}
    return {"rows": rows_out, "version": session.version}


class BrowserApprover(Approver):
    name = "browser"

    def __init__(self, run: "Run"):
        self.run = run

    def decide(self, tool, args, risk, preview):
        approval_id = uuid.uuid4().hex[:8]
        waiter = threading.Event()
        self.run.pending[approval_id] = {"event": waiter, "answer": False}
        rows = list(preview.get("rows_removed") or args.get("rows") or [])
        self.run.emit({
            "type": "approval", "id": approval_id, "tool": tool, "risk": risk,
            "title": QUESTIONS.get(tool, f"Apply {tool}?").format(column=args.get("column", "this column")),
            "summary": preview.get("summary", ""), "reason": args.get("reason", ""),
            "rows": [int(r) for r in rows][:20], "column": args.get("column"),
        })
        answered = waiter.wait(APPROVAL_TIMEOUT) and not self.run.cancelled
        answer = bool(self.run.pending.pop(approval_id)["answer"]) if answered else False
        self.run.emit({"type": "approval_closed", "id": approval_id, "answer": answer, "timed_out": not answered})
        return answer


class Run:
    def __init__(self, input_path: Path, question: str, rules_path: Path | None, out_dir: Path, model: str | None):
        self.id = out_dir.name
        self.input_path, self.question, self.rules_path, self.out_dir, self.model = input_path, question, rules_path, out_dir, model
        self.events: list[dict] = []
        self.cond = threading.Condition()
        self.pending: dict[str, dict] = {}
        self.cancelled = False
        self.done = False
        self.counts = {"checks": 0, "fixes": 0}

    def emit(self, event: dict) -> None:
        with self.cond:
            event["seq"] = len(self.events)
            self.events.append(event)
            self.cond.notify_all()

    def answer(self, approval_id: str, answer: bool) -> bool:
        item = self.pending.get(approval_id)
        if not item:
            return False
        item["answer"] = answer
        item["event"].set()
        return True

    def cancel(self) -> None:
        self.cancelled = True
        for item in list(self.pending.values()):
            item["event"].set()

    def start(self) -> None:
        threading.Thread(target=self._work, daemon=True).start()

    def _on_event(self, event: dict, session) -> None:
        if event.get("event") != "tool":
            return
        name, args = event["name"], event["args"] if isinstance(event["args"], dict) else {}
        if name.startswith("check_"):
            self.counts["checks"] += 1
        output = event.get("output") or {}
        if output.get("applied"):
            self.counts["fixes"] += 1
        phase = "rules" if name in ("lookup_rules", "profile_dataset") else "check" if name.startswith("check_") \
            else "answer" if name in ("analyze", "finish") else "fix"
        refused = bool(output.get("analyze_refused"))
        self.emit({"type": "step", "tool": name, "label": label(name, args), "phase": phase, "ok": event.get("ok"),
                   "refused": refused, "counts": dict(self.counts), "table": table_state(session)})

    def _work(self) -> None:
        start = time.time()
        try:
            df = load_table(self.input_path)
            self.emit({"type": "start", "question": self.question, "columns": [str(c) for c in df.columns],
                       "total_rows": len(df), "rows": initial_rows(self.input_path)})
            kwargs = {"model": self.model} if self.model else {}
            result = run_agent(self.input_path, self.question, BrowserApprover(self), rules_path=self.rules_path,
                               on_event=self._on_event, **kwargs)
            write_outputs(result, self.out_dir)
            analysis = result.session.analyses[-1] if result.session.analyses else None
            changes = [{"applied": True, "text": f"{c.tool}: {c.summary}", "approval": c.approval}
                       for c in result.session.changes]
            changes += [{"applied": False, "text": f"{r['tool']}: {r['summary']} (rejected, kept as a caveat)",
                         "approval": "rejected"} for r in result.session.rejected]
            self.emit({
                "type": "done", "finished": result.finished, "stop_reason": result.stop_reason,
                "answer": analysis["result"] if analysis else None,
                "analysis": {k: analysis.get(k) for k in ("group_by", "metric", "agg", "rows_used")} if analysis else None,
                "summary": result.final_summary, "changes": changes, "seconds": round(time.time() - start, 1),
                "tool_calls": result.tool_calls, "approvals": result.approvals_asked, "model": result.model,
                "files": ["cleaned.csv", "report.md", "replay.py", "trace.jsonl"], "table": table_state(result.session),
            })
        except Exception as err:  # shown in the page; the server keeps running
            self.emit({"type": "error", "message": f"{type(err).__name__}: {err}"})
        finally:
            self.done = True
            with self.cond:
                self.cond.notify_all()


def initial_rows(path: Path) -> list[dict]:
    df = load_table(path)
    return [{"id": int(r), "cells": {str(c): _text(df.at[r, c]) for c in df.columns}} for r in df.index[:MAX_ROWS]]
