"""Tests for the analysis pages (/results and /profile) and their APIs. No model calls."""

import csv
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from app.web import analysis, server
from app.web.runner import Run

SUMMARY = Path(analysis.RESULTS) / "summary.csv"


def _serve(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "OUT", tmp_path)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def _get(url):
    try:
        with urllib.request.urlopen(url) as res:
            return res.status, res.headers["Content-Type"], res.read()
    except urllib.error.HTTPError as err:
        return err.code, err.headers["Content-Type"], err.read()


@pytest.fixture(scope="module")
def results():
    return analysis.results()


def test_results_api_has_every_system_and_split_in_summary_csv(results):
    with open(SUMMARY, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert {s["id"] for s in results["splits"]} == {r["dataset"] for r in rows}
    assert [s["id"] for s in results["splits"]][:6] == ["sales", "penguins", "sales-heldout", "penguins-heldout",
                                                        "sales-test", "penguins-test"]
    assert set(results["order"]) == {r["system"] for r in rows}
    for r in rows:  # every per-split number is the one in summary.csv
        got = results["per_split"][r["dataset"]][r["system"]]
        assert got["analysis_accuracy"] == pytest.approx(float(r["analysis_accuracy"]))
        assert got["latency_median_s"] == pytest.approx(float(r["latency_median_s"]))
        assert got["tasks"] == int(r["tasks"])
    assert results["final"] == "datasage-m3" and results["systems"]["datasage-m3"]["kind"] == "final"
    assert {results["systems"][b]["kind"] for b in ("b0", "b1", "b2")} == {"baseline"}
    assert all(results["systems"][s]["label"] != s for s in results["order"])  # plain names, not ids


def test_pooled_groups_match_the_per_split_numbers(results):
    all_six = next(g for g in results["groups"] if g["id"] == "all")
    final = all_six["systems"]["datasage-m3"]
    per = [results["per_split"][s]["datasage-m3"] for s in all_six["splits"]]
    assert final["tasks"] == sum(p["tasks"] for p in per)
    assert final["analysis_accuracy"] == pytest.approx(sum(p["analysis_accuracy"] * p["tasks"] for p in per) / final["tasks"])
    assert final["wrong"] == round(final["tasks"] * (1 - final["analysis_accuracy"]))
    assert "datasage" not in all_six["systems"]  # Milestone 2 never ran on the test split
    assert results["progression"] == ["datasage", "datasage-fix", "datasage-small-fix", "datasage-m3"]


def test_ablation_compares_the_same_tasks(results):
    abl = results["ablation"]
    assert abl["splits"] == ["sales", "penguins"]
    for split in abl["splits"]:
        tasks = {s: m["tasks"] for s, m in abl["by_split"][split].items()}
        assert set(tasks) == {"datasage", "datasage-novalidator", "datasage-reject"} and len(set(tasks.values())) == 1
        assert abl["by_split"][split]["datasage-reject"]["analysis_accuracy"] == pytest.approx(
            results["per_split"][split]["datasage-reject"]["analysis_accuracy"])
    assert results["failures"]["datasage-m3"]["counts"]


def _fake_run(tmp_path):
    folder = tmp_path / "abc123def0"
    folder.mkdir()
    source = folder / "input.csv"
    source.write_text("id,Category,Revenue,Date\n1,Toys,10,2026-01-02\n2,toys,\"1,200\",2026-01-03\n"
                      "2,toys,\"1,200\",2026-01-03\n3,Games,n/a,not-a-date\n")
    (folder / "cleaned.csv").write_text("row,id,Category,Revenue,Date\n0,1,Toys,10,2026-01-02\n1,2,Toys,1200,2026-01-03\n"
                                        "3,3,Games,15,\n")
    run = Run(source, "total revenue by category", None, folder, None)
    run.done = True
    return run


def test_profile_compares_input_with_cleaned_csv(tmp_path):
    run = _fake_run(tmp_path)
    status, body = analysis.run_profile(run.id, {run.id: run}, tmp_path)
    assert status == 200
    assert (body["rows_before"], body["rows_after"], body["rows_removed"]) == (4, 3, 1)
    assert body["removed_ids"] == [2] and body["input"] == "input.csv"
    cols = {c["name"]: c for c in body["columns"]}
    assert "row" not in cols and list(cols) == ["id", "Category", "Revenue", "Date"]
    cat = cols["Category"]
    assert cat["before"]["distinct"] == 3 and cat["after"]["distinct"] == 2 and cat["change"]["edited"] == 1
    rev = cols["Revenue"]
    assert rev["before"]["type"] == "mostly numbers" and rev["after"]["type"] == "number"
    assert rev["change"] == {"filled": 1, "blanked": 0, "edited": 1, "cells_changed": 2, "type_changed": True,
                             "added": False, "dropped": False}
    assert rev["before"]["missing"] == 1 and rev["after"]["missing_pct"] == 0
    assert sum(rev["after"]["hist"]["counts"]) == 3 and rev["after"]["hist"]["edges"][0] == rev["before"]["hist"]["edges"][0]
    assert cols["Date"]["change"]["blanked"] == 1 and cols["Date"]["after"]["type"] == "date"
    assert cols["id"]["change"]["cells_changed"] == 0


def test_profile_api_and_pages_are_served(tmp_path, monkeypatch):
    run = _fake_run(tmp_path)
    monkeypatch.setitem(server.RUNS, run.id, run)
    httpd, base = _serve(tmp_path, monkeypatch)
    try:
        status, ctype, body = _get(f"{base}/api/runs/{run.id}/profile")
        assert status == 200 and "json" in ctype and json.loads(body)["rows_after"] == 3
        assert _get(f"{base}/api/runs/nope/profile")[0] == 404
        run.done = False
        assert _get(f"{base}/api/runs/{run.id}/profile")[0] == 409
        status, ctype, body = _get(f"{base}/api/results")
        assert status == 200 and json.loads(body)["final"] == "datasage-m3"
        for page, script in (("/results", b"/static/results.js"), ("/profile?run=x", b"/static/profile.js")):
            status, ctype, body = _get(base + page)
            assert status == 200 and ctype.startswith("text/html") and script in body
        for asset in ("results.js", "profile.js", "viz.js", "analysis.css"):
            assert _get(f"{base}/static/{asset}")[0] == 200
        status, _, body = _get(base + "/")
        assert b'href="/results"' in body
    finally:
        httpd.shutdown()


def test_saved_run_is_found_from_its_report(tmp_path):
    run = _fake_run(tmp_path)
    (run.out_dir / "report.md").write_text(f"# DataSage report\n\n- Input: `{run.input_path}`\n- Question: total revenue\n")
    status, body = analysis.run_profile(run.id, {}, tmp_path)
    assert status == 200 and body["question"] == "total revenue"
    assert analysis.saved_run(tmp_path, "../etc") is None
    (run.out_dir / "report.md").write_text("# DataSage report\n\n- Input: `/etc/hosts`\n")
    assert analysis.run_profile(run.id, {}, tmp_path)[0] == 404
