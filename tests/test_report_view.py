"""Tests for app/report_view.py (no model calls, no streamlit needed)."""

import shutil
from pathlib import Path

from app.report_view import RunView, load_run

RUN_OK = Path(__file__).parent / "fixtures" / "report_view" / "run_ok"


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
