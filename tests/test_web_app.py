"""Tests for the browser app (app/web): table state, the browser approver and the server routes. No model calls."""

import base64
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pandas as pd

from app.web import runner, server
from app.web.runner import BrowserApprover, Run, table_state
from datasage.approval import AutoApprover, RejectApprover
from datasage.session import Session
from datasage.tools import Dispatcher

RULES = {"Category": {"allowed": ["Electronics", "Furniture"]}, "Quantity": {"min": 1}}


def _session():
    df = pd.DataFrame({"Category": ["Electronics", "electronics", "Furniture", "Furniture"], "Quantity": [2, 3, -1, -1]})
    return Session(df, source="t.csv", request="units by category", rules=RULES)


def _call(d, name, **args):
    return d.call(name, json.dumps(args))


def test_table_state_marks_flagged_fixed_and_removed_cells():
    d = Dispatcher(_session(), AutoApprover())
    _call(d, "check_label_variants", column="Category")
    _call(d, "check_out_of_range", column="Quantity", minimum=1)
    state = table_state(d.session)["rows"]
    assert state[1]["cells"]["Category"]["state"] == "flag"
    assert state[2]["cells"]["Quantity"]["state"] == "flag"
    _call(d, "normalize_labels", column="Category", mapping={"electronics": "Electronics"}, reason="case")
    _call(d, "exclude_rows", rows=[2], reason="Quantity below 1")
    state = table_state(d.session)["rows"]
    assert state[1]["cells"]["Category"] == {"text": "Electronics", "state": "fixed"}
    assert state[2]["state"] == "removed"
    assert state[3]["cells"]["Quantity"]["state"] == "flag"  # still open


def test_rejected_row_fix_is_shown_as_kept():
    d = Dispatcher(_session(), RejectApprover())
    _call(d, "check_out_of_range", column="Quantity", minimum=1)
    _call(d, "exclude_rows", rows=[2], reason="Quantity below 1")
    row = table_state(d.session)["rows"][2]
    assert row["state"] == "kept" and row["cells"]["Quantity"]["state"] == "kept"


def test_browser_approver_waits_for_the_page(tmp_path):
    run = Run(Path("x.csv"), "q", None, tmp_path, None)
    approver = BrowserApprover(run)
    answers = []
    worker = threading.Thread(target=lambda: answers.append(
        approver.decide("drop_duplicates", {"reason": "dup"}, "medium", {"summary": "removed 1 row", "rows_removed": [4]})))
    worker.start()
    for _ in range(200):
        asks = [e for e in run.events if e["type"] == "approval"]
        if asks:
            break
        threading.Event().wait(0.01)
    assert asks[0]["title"] == "Remove the duplicate rows?" and asks[0]["rows"] == [4]
    assert run.answer(asks[0]["id"], True)
    worker.join(2)
    assert answers == [True]
    assert run.events[-1] == {"type": "approval_closed", "id": asks[0]["id"], "answer": True, "timed_out": False,
                              "seq": run.events[-1]["seq"]}


def test_cancelled_run_rejects_pending_approvals(tmp_path):
    run = Run(Path("x.csv"), "q", None, tmp_path, None)
    answers = []
    worker = threading.Thread(target=lambda: answers.append(
        BrowserApprover(run).decide("exclude_rows", {"rows": [1]}, "high", {"summary": "excluded 1 row"})))
    worker.start()
    for _ in range(200):
        if run.pending:
            break
        threading.Event().wait(0.01)
    run.cancel()
    worker.join(2)
    assert answers == [False]


def _serve(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "OUT", tmp_path)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def _post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.load(res)
    except urllib.error.HTTPError as err:
        return err.code, json.load(err)


def test_server_serves_the_page_and_checks_input(tmp_path, monkeypatch):
    httpd, base = _serve(tmp_path, monkeypatch)
    try:
        with urllib.request.urlopen(base + "/") as res:
            assert res.status == 200 and b"DataSage" in res.read()
        with urllib.request.urlopen(base + "/static/app.js") as res:
            assert "javascript" in res.headers["Content-Type"]
        assert _post(base + "/api/runs", {"question": ""})[0] == 400
        csv = base64.b64encode(b"a,b\n1,2\n").decode()
        assert _post(base + "/api/runs", {"question": "q", "file_name": "x.txt", "file_b64": csv})[0] == 400
        assert _post(base + "/api/runs", {"question": "q", "file_name": "x.csv", "file_b64": csv,
                                          "rules_text": "{not json"})[0] == 400
        assert _post(base + "/api/runs/nope/approve", {"id": "x", "answer": True})[0] == 404
        try:
            urllib.request.urlopen(base + "/static/../server.py")
            raise AssertionError("path outside static was served")
        except urllib.error.HTTPError as err:
            assert err.code == 404
    finally:
        httpd.shutdown()


def test_labels_name_the_column():
    assert runner.label("check_dates", {"column": "Date"}) == "Checking dates in Date"
    assert runner.label("unknown_tool", {}) == "unknown_tool"


def test_approval_wording_and_row_previews():
    from app.web.runner import examples, future
    d = Dispatcher(_session(), AutoApprover())
    before = d.session.current
    after = before.drop(index=[2])
    preview = {"summary": "excluded 1 row(s): [2]", "rows_removed": [2], "cells_changed": 0, "before": before, "after": after}
    assert future("exclude_rows", {"rows": [2]}, preview) == "Will drop 1 row from the analysis"
    ex = examples(preview)
    assert ex["kind"] == "remove" and ex["rows"][0]["id"] == 2 and ex["rows"][0]["cells"]["Quantity"] == "-1"
    after = before.copy()
    after.loc[1, "Category"] = "Electronics"
    preview = {"summary": "", "rows_removed": [], "cells_changed": 1, "before": before, "after": after}
    assert future("normalize_labels", {"column": "Category", "mapping": {"electronics": "Electronics"}}, preview) == \
        "Will merge 1 label in Category, changing 1 cell"
    assert examples(preview, "normalize_labels", {"column": "Category"})["rows"] == [
        {"id": 1, "changes": [{"column": "Category", "before": "electronics", "after": "Electronics"}], "inputs": []}]


def test_details_show_the_evidence_for_each_fix_type():
    from app.web.runner import examples
    df = pd.DataFrame({"A": ["x", "y", "x", "y"], "Qty": [1, 2, 1, -2], "Price": [5, 5, 5, 5], "Rev": [5, 10, 5, 99]})
    s = Session(df, source="t.csv", request="q", rules={"Qty": {"min": 1}})
    d = Dispatcher(s, AutoApprover())
    _call(d, "check_out_of_range", column="Qty", minimum=1)
    # duplicates: the copy points at the earlier row it repeats
    dup = examples({"rows_removed": [2], "before": df, "after": df.drop(index=[2])}, "drop_duplicates", {}, s)
    assert dup["kind"] == "duplicates" and dup["rows"][0]["id"] == 2 and dup["rows"][0]["same_as"] == 0
    # dropped rows: the cell that breaks the rule is named
    rem = examples({"rows_removed": [3], "before": df, "after": df.drop(index=[3])}, "exclude_rows", {"rows": [3]}, s)
    assert rem["rows"][0]["problems"] == {"Qty": "values outside the rules"}
    # recompute: the formula's inputs come with the change
    after = df.copy(); after.loc[3, "Rev"] = -10
    rec = examples({"before": df, "after": after}, "recompute_column", {"column": "Rev", "expression": "Qty * Price"}, s)
    assert rec["rows"][0]["changes"] == [{"column": "Rev", "before": "99", "after": "-10"}]
    assert rec["rows"][0]["inputs"] == [{"column": "Qty", "value": "-2"}, {"column": "Price", "value": "5"}]


def test_health_reports_outcomes_and_the_answer_before_cleaning():
    from app.web.runner import health
    d = Dispatcher(_session(), RejectApprover())
    _call(d, "check_label_variants", column="Category")
    _call(d, "check_out_of_range", column="Quantity", minimum=1)
    _call(d, "normalize_labels", column="Category", mapping={"electronics": "Electronics"}, reason="case")  # low risk, applied
    _call(d, "exclude_rows", rows=[2, 3], reason="Quantity below 1")  # rejected
    h = health(d.session, {"group_by": ["Category"], "metric": "Quantity", "agg": "sum", "filters": []})
    status = {(i["type"], i["column"]): i["status"] for i in h["issues"]}
    assert status[("label_variant", "Category")] == "fixed" and status[("out_of_range", "Quantity")] == "kept"
    assert h["rows_before"] == 4 and h["rows_after"] == 4 and h["cells_changed"] == 1
    assert h["raw_answer"]["result"] == {"Electronics": 2.0, "electronics": 3.0, "Furniture": -2.0}
