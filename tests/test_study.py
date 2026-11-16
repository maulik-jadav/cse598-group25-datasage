"""Tests for the failure-analysis helpers of eval/study.py. They read the committed benchmark and
result files; no model calls."""

import json
from pathlib import Path

from datasage.analyze import answers_match, run_analysis
from eval import study

RESULT = Path(study.RESULTS / "datasage-m3" / "sales-test" / "salest_00_q0.json")


def test_question_columns():
    spec = {"group_by": ["Date:month", "Region"], "metric": "Revenue", "agg": "sum",
            "filters": [{"column": "Category", "value": "Electronics"}]}
    assert study.question_columns(spec) == {"Date", "Region", "Revenue", "Category"}
    assert study.question_columns({"group_by": ["island"], "metric": None, "agg": "count"}) == {"island"}


def test_handled_follows_the_scoring_rules():
    assert study.handled({"resolution": "exclude"}, [])
    assert not study.handled({"resolution": "exclude"}, [{"x": 1}])
    assert study.handled({"resolution": "drop_copy"}, [{"x": 1}])
    assert not study.handled({"resolution": "drop_copy"}, [{"x": 1}, {"x": 1}])
    restore = {"resolution": "restore", "column": "Price", "clean_value": 12.0}
    assert study.handled(restore, [{"Price": 12}])
    assert not study.handled(restore, [{"Price": 120}])
    assert study.handled({"resolution": "set_missing", "column": "Date"}, [{"Date": None}])


def test_answer_diff_uses_the_scoring_tolerance():
    ref = {"A": 100.0, "B": 10.0}
    assert study.answer_diff({"answer": None, "reference_answer": ref}) == "no answer"
    assert "values equal" in study.answer_diff({"answer": {"A": 100.2, "B": 10.0}, "reference_answer": ref})
    text = study.answer_diff({"answer": {"A": 120.0, "C": 1.0}, "reference_answer": ref})
    assert "missing groups ['B']" in text and "extra groups ['C']" in text and "1 of 2" in text


def test_replay_rebuilds_the_logged_answer():
    result = json.loads(RESULT.read_text())
    cleaned = study.replay_cleaned("sales-test", result["task_id"], result)
    tasks = json.loads((study.ROOT / "datasets" / "sales-test" / "salest_00" / "tasks.json").read_text())
    spec = next(t["spec"] for t in tasks if t["task_id"] == result["task_id"])
    answer = run_analysis(cleaned, spec["group_by"], spec["metric"], spec["agg"], spec.get("filters"))["result"]
    assert answers_match(answer, result["answer"])


def test_root_causes_lists_unhandled_errors_when_nothing_was_fixed():
    untouched = {"answer": {"x": 1.0}, "stop_reason": "finish", "extra": {"changes": []}, "damaged_rows": 0, "damaged_cells": 0}
    causes = study.root_causes("penguins-test", "penguinst_00_q1", untouched)
    assert causes == ["label_variant (restore) on a question column not handled",
                      "out_of_range (exclude) on a column the question does not use not handled"]
    # salest_00_q0 asks for mean Price, which is still text when nothing was fixed
    assert study.root_causes("sales-test", "salest_00_q0", untouched) == [
        "the question cannot be answered on the cleaned table: metric column 'Price' is text, not numbers"]
    # the committed run cleaned the table correctly, so a wrong answer could only come from the analyze call
    result = json.loads(RESULT.read_text())
    assert study.root_causes("sales-test", "salest_00_q0", result) == [
        "cleaned table is right; answer differs for another reason"]
    extra_filter = [{"event": "tool", "name": "analyze", "output": {"result": {}},
                     "args": {"group_by": ["Category"], "metric": "Price", "agg": "mean",
                              "filters": [{"column": "Region", "value": "North"}]}}]
    assert study.root_causes("sales-test", "salest_00_q0", result, extra_filter) == [
        "analyze asked a different question (grouping, metric, aggregation or filters)"]


def test_same_question_ignores_the_metric_of_a_count():
    spec = {"group_by": ["island"], "metric": None, "agg": "count"}
    assert study.same_question(spec, {"group_by": ["island"], "metric": "penguin_id", "agg": "count", "filters": []})
    assert not study.same_question(spec, {"group_by": ["species"], "metric": None, "agg": "count"})
    assert study.root_causes("sales-test", "salest_00_q0", {"answer": {"x": 1.0}, "stop_reason": "finish", "extra": {}}) == ["no change log"]
    assert study.root_causes("sales-test", "salest_00_q0", {"answer": {"x": 1.0}, "stop_reason": "tool_budget_exhausted"}) == [
        "did not finish (stopped: tool_budget_exhausted)"]
    assert study.root_causes("sales-test", "salest_00_q0", {"answer": None, "stop_reason": "tool_budget_exhausted"}) == [
        "no answer (stopped: tool_budget_exhausted)"]
