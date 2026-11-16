"""Stacking several files with the same columns into one table."""

import base64
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pandas as pd
import pytest

from app.web import server
from datasage.session import load_table
from datasage.stack import stack_files


def test_stack_matches_columns_by_name_and_records_the_source(tmp_path):
    (tmp_path / "jul.csv").write_text("Region,Sales\nWest,5\nEast,7\n")
    (tmp_path / "aug.csv").write_bytes("sales ; region \n9;Süd\n".encode("cp1252"))  # other order, ; and Windows-1252
    info = stack_files([tmp_path / "jul.csv", tmp_path / "aug.csv"], tmp_path / "all.csv")
    df = load_table(tmp_path / "all.csv")
    assert info["rows"] == 3 and [f["rows"] for f in info["files"]] == [2, 1]
    assert list(df.columns) == ["source_file", "Region", "Sales"]
    assert df["source_file"].tolist() == ["jul.csv", "jul.csv", "aug.csv"]
    assert df["Sales"].tolist() == [5, 7, 9] and df.loc[2, "Region"] == "Süd"


def test_stack_explains_mismatched_columns(tmp_path):
    (tmp_path / "a.csv").write_text("Region,Sales\nWest,5\n")
    (tmp_path / "b.csv").write_text("Region,Revenue\nWest,5\n")
    with pytest.raises(ValueError, match=r"b.csv: missing Sales; extra Revenue"):
        stack_files([tmp_path / "a.csv", tmp_path / "b.csv"], tmp_path / "all.csv")


def test_stack_needs_at_least_two_files(tmp_path):
    (tmp_path / "a.csv").write_text("A\n1\n")
    with pytest.raises(ValueError):
        stack_files([tmp_path / "a.csv"], tmp_path / "all.csv")


def test_server_stacks_uploaded_files_and_the_monthly_sample(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "OUT", tmp_path)
    monkeypatch.setattr(server, "RUNS", {})
    monkeypatch.setattr(server.Run, "start", lambda self: None)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"

    def post(body):
        req = urllib.request.Request(base + "/api/runs", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)
    b64 = lambda s: base64.b64encode(s.encode()).decode()
    try:
        status, out = post({"question": "q", "files": [{"file_name": "a.csv", "file_b64": b64("X,Y\n1,2\n")},
                                                        {"file_name": "b.csv", "file_b64": b64("Y,X\n3,4\n")}]})
        assert status == 200
        run = server.RUNS[out["run_id"]]
        assert run.sources["rows"] == 2 and list(pd.read_csv(run.input_path).columns) == ["source_file", "X", "Y"]
        status, out = post({"question": "q", "files": [{"file_name": "a.csv", "file_b64": b64("X\n1\n")},
                                                        {"file_name": "b.csv", "file_b64": b64("Z\n1\n")}]})
        assert status == 400 and "same columns" in out["error"]
        status, out = post({"sample": "monthly", "question": "q"})
        run = server.RUNS[out["run_id"]]
        assert status == 200 and run.sources["rows"] == 1208 and len(run.sources["files"]) == 3
    finally:
        httpd.shutdown()
