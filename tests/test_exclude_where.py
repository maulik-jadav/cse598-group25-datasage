"""exclude_where: a range rule applied to every row, so fixes are not limited to the 10 row ids a check lists."""

import json

import pandas as pd

from datasage import fixes
from datasage.approval import AutoApprover
from datasage.session import Session
from datasage.tools import Dispatcher

RULES = {"Qty": {"min": 1}, "Category": {"allowed": ["A", "B"]}}


def _session(n_bad=25):
    qty = [2] * 60 + [-1] * n_bad
    df = pd.DataFrame({"Id": range(len(qty)), "Category": (["A", "B"] * 50)[: len(qty)], "Qty": qty,
                       "Rev": [q * 10 for q in qty]})
    return Session(df, source="t.csv", request="units by category", rules=RULES)


def _call(d, name, **args):
    return d.call(name, json.dumps(args))


def test_check_says_when_more_rows_break_a_rule_than_it_lists():
    d = Dispatcher(_session(), AutoApprover())
    out, ok = _call(d, "check_out_of_range", column="Qty", minimum=1)
    assert ok and out["count"] == 25 and len(out["rows"]) == 10 and "exclude_where" in out["rows_listed_note"]
    out, _ = _call(d, "check_out_of_range", column="Category", minimum=None)  # nothing found: no note
    assert "rows_listed_note" not in out


def test_exclude_where_removes_every_rule_breaking_row_and_passes_validation():
    d = Dispatcher(_session(), AutoApprover())
    out, ok = _call(d, "exclude_where", column="Qty", minimum=1, reason="Qty must be at least 1")
    assert ok and out["applied"] and out["validation"]["ok"], out
    assert len(d.session.current) == 60 and (d.session.current["Qty"] >= 1).all()
    assert d.session.changes[-1].rows_removed == list(range(60, 85))


def test_exclude_where_lets_analyze_through_the_coverage_check():
    d = Dispatcher(_session(), AutoApprover(), coverage=True)
    _call(d, "exclude_where", column="Qty", minimum=1, reason="rule")
    out, ok = _call(d, "analyze", group_by=["Category"], metric="Qty", agg="sum")
    assert ok and out["result"] == {"A": 60.0, "B": 60.0}


def test_exclude_where_replay_code_matches():
    df = _session(5).current
    result = fixes.exclude_where(df, "Qty", minimum=1)
    ns = {"pd": pd, "df": df.copy()}
    exec(result.code, ns)
    assert ns["df"].index.tolist() == result.df.index.tolist()
    assert result.summary == "excluded 5 row(s) where Qty is below 1"


def test_extra_arguments_are_dropped_not_fatal():
    d = Dispatcher(_session(), AutoApprover())
    out, ok = _call(d, "check_out_of_range", column="Qty", minimum=1, reason="the model added this")
    assert ok and out["count"] == 25 and "reason" in out["ignored_arguments"]


def test_the_same_failing_call_twice_gets_a_plain_instruction():
    d = Dispatcher(_session(), AutoApprover())
    first, ok1 = _call(d, "check_out_of_range", column="Nope", minimum=1)
    second, ok2 = _call(d, "check_out_of_range", column="Nope", minimum=1)
    assert not ok1 and not ok2 and "repeat_failure" not in first and "Do not send it again" in second["repeat_failure"]


def test_coverage_requires_the_metric_formula_check():
    df = pd.DataFrame({"Id": [1, 2, 3], "Cat": ["A", "B", "A"], "Qty": [1, 2, 3], "Price": [10, 10, 10], "Rev": [10, 20, 300]})
    s = Session(df, source="t.csv", request="q", rules={"Rev": {"formula": "Rev = Qty * Price"}})
    d = Dispatcher(s, AutoApprover(), coverage=True)
    needed = d.required_checks({"group_by": ["Cat"], "metric": "Rev", "agg": "sum", "filters": []})
    assert ("check_cross_column", {"column": "Rev", "expression": "Qty * Price"}) in needed
    out, ok = _call(d, "analyze", group_by=["Cat"], metric="Rev", agg="sum")
    assert out.get("analyze_refused") and any(f["check"] == "check_cross_column" for f in out["open_findings"])
    _call(d, "recompute_column", column="Rev", expression="Qty * Price", rows=[2], reason="formula")
    out, ok = _call(d, "analyze", group_by=["Cat"], metric="Rev", agg="sum")
    assert out["result"] == {"A": 40.0, "B": 20.0}


def test_replay_of_a_recompute_on_a_text_column(tmp_path):
    from datasage.agent import RunResult
    from datasage.report import replay_script
    from datasage.session import load_table
    f = tmp_path / "t.csv"
    f.write_text('Qty,Price,Rev\n2,10,"1,200"\n3,10,30\n')
    s = Session(load_table(f), source=str(f), request="q", rules={})
    d = Dispatcher(s, AutoApprover())
    out, ok = _call(d, "recompute_column", column="Rev", expression="Qty * Price", rows=[0], reason="formula")
    assert ok and out["applied"], out
    script = replay_script(RunResult(session=s, model="m", finished=True, stop_reason="finish", final_summary=""))
    ns = {}
    exec(script, ns)
    assert ns["df"]["Rev"].tolist() == s.current["Rev"].tolist() == [20.0, 30.0]


def test_replay_of_a_recompute_on_a_whole_number_column(tmp_path):
    from datasage.agent import RunResult
    from datasage.report import replay_script
    from datasage.session import load_table
    f = tmp_path / "t.csv"
    f.write_text("Qty,Price,Rev\n2,10,999\n3,10,30\n")
    s = Session(load_table(f), source=str(f), request="q", rules={})
    _call(Dispatcher(s, AutoApprover()), "recompute_column", column="Rev", expression="Qty * Price", rows=[0], reason="f")
    ns = {}
    exec(replay_script(RunResult(session=s, model="m", finished=True, stop_reason="finish", final_summary="")), ns)
    assert ns["df"]["Rev"].tolist() == [20, 30]
