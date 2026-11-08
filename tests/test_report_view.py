"""Tests for app/report_view.py (no model calls, no streamlit needed)."""

import shutil
import subprocess
import sys
import types
from pathlib import Path

import pandas as pd

from app.report_view import CHANGE_KEYS, RunView, load_run, parse_change_log, render_report
from datasage.agent import RunResult
from datasage.report import markdown_report
from datasage.session import Change, Session

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_OK = Path(__file__).parent / "fixtures" / "report_view" / "run_ok"
KEYS = ["version", "fix", "risk", "approval", "what_changed", "reason"]


def test_load_run_reads_report_and_files():
    view = load_run(RUN_OK)
    assert isinstance(view, RunView)
    assert view.run_dir == RUN_OK
    assert view.report_md is not None and view.report_md.startswith("# DataSage report")
    assert set(view.files) == {"cleaned.csv", "replay.py"}  # no trace.jsonl or recipe.json in the fixture
    assert all(path.is_file() for path in view.files.values())


def test_missing_report_gives_none(tmp_path):
    shutil.copy(RUN_OK / "cleaned.csv", tmp_path / "cleaned.csv")
    view = load_run(tmp_path)
    assert view.report_md is None
    assert view.changes == []
    assert list(view.files) == ["cleaned.csv"]


def test_missing_folder_does_not_raise(tmp_path):
    view = load_run(tmp_path / "no_such_run")
    assert view.report_md is None and view.changes == [] and view.files == {}


def test_parse_change_log_reads_three_rows():
    rows = parse_change_log((RUN_OK / "report.md").read_text())
    assert [r["approval"] for r in rows] == ["approved", "auto", "rejected"]
    assert all(list(r) == KEYS for r in rows)
    assert rows[0] == {"version": "v1", "fix": "drop_duplicates", "risk": "medium", "approval": "approved",
                       "what_changed": "removed 1 exact duplicate row(s)", "reason": "Row 3 repeats row 0."}
    assert rows[1]["fix"] == "normalize_labels" and rows[1]["risk"] == "low"


def test_rejected_row_is_kept():
    rejected = parse_change_log((RUN_OK / "report.md").read_text())[2]
    assert rejected["version"] == "-"
    assert rejected["fix"] == "exclude_rows" and rejected["risk"] == "high"
    assert rejected["approval"] == "rejected"
    assert rejected["what_changed"] == "excluded 1 row(s): [2] (not applied)"


def test_no_changes_section_gives_empty_list():
    assert parse_change_log("# DataSage report\n\n## Answer\n\nNo answer was produced.\n") == []
    assert parse_change_log("") == []


def test_load_run_fills_changes():
    assert len(load_run(RUN_OK).changes) == 3


def test_parser_matches_datasage_report_writer():
    # Build a report with the real writer (datasage/report.py) from a synthetic session; no model call.
    session = Session(pd.DataFrame({"Store": ["North", "north", "South"], "Units": [10, 6, -4]}),
                      source="inventory.csv", request="Units per store?")
    session.changes.append(Change(version=1, tool="normalize_labels", args={}, reason="case only", risk="low",
                                  approval="auto", summary="Store: merged 1 label variant(s), 1 cells"))
    session.rejected.append({"tool": "exclude_rows", "risk": "high", "summary": "excluded 1 row(s): [2]",
                             "args": {"reason": "Units < 0 | breaks the rule"}})
    result = RunResult(session=session, model="test", finished=True, stop_reason="finish", final_summary="done")
    rows = parse_change_log(markdown_report(result))
    assert [(r["version"], r["fix"], r["approval"]) for r in rows] == [
        ("v1", "normalize_labels", "auto"), ("-", "exclude_rows", "rejected")]
    assert rows[1]["reason"] == "Units < 0 | breaks the rule"  # a pipe in the reason is not split off
    assert set(CHANGE_KEYS.values()) == set(KEYS)


def test_importing_report_view_does_not_import_streamlit():
    # A fresh interpreter, so streamlit imported by another test cannot hide the problem.
    code = "import sys, app.report_view; print('streamlit' in sys.modules)"
    out = subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "False"


class FakeStreamlit(types.ModuleType):
    """Records every st.<name>(...) call so render_report can be tested without streamlit."""

    def __init__(self):
        super().__init__("streamlit")
        self.calls = []

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *args, **kwargs: self.calls.append((name, args, kwargs))


def test_render_report_shows_report_changes_and_downloads(monkeypatch):
    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    render_report(RUN_OK)
    names = [name for name, _, _ in fake.calls]
    markdown = [args[0] for name, args, _ in fake.calls if name == "markdown"]
    assert markdown == [(RUN_OK / "report.md").read_text()]
    (table,) = [args[0] for name, args, _ in fake.calls if name == "dataframe"]
    assert list(table.columns) == ["Version", "Fix", "Risk", "Approval", "What changed", "Reason"]
    assert len(table) == 3
    downloads = [kwargs["file_name"] for name, _, kwargs in fake.calls if name == "download_button"]
    assert downloads == ["cleaned.csv", "replay.py"]
    assert "warning" not in names


def test_render_report_on_empty_folder_warns(monkeypatch, tmp_path):
    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, "streamlit", fake)
    render_report(tmp_path)
    names = [name for name, _, _ in fake.calls]
    assert "warning" in names and "markdown" not in names and "download_button" not in names
    assert list(tmp_path.iterdir()) == []  # nothing written to the run folder
