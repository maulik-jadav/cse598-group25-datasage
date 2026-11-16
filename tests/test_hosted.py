"""Tests for the hosted app (app/web/hosted.py): pages, and a whole run over one WebSocket. No model calls."""

import base64
import time

import pytest
from fastapi.testclient import TestClient

from app.web import analysis, hosted, runner, server

SAMPLE_CSV = b"Category,Revenue\nA,1\nA,1\nB,2\n"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "OUT", tmp_path)
    monkeypatch.setattr(server, "RUNS", {})
    return TestClient(hosted.app)


def fake_work(self):
    """A run that asks one question and writes one file, instead of calling the model."""
    try:
        self.emit({"type": "start", "question": self.question, "columns": ["Category", "Revenue"], "total_rows": 4, "rows": []})
        approved = runner.BrowserApprover(self).decide("drop_duplicates", {}, "medium", {"rows_removed": [1]})
        (self.out_dir / "cleaned.csv").write_text("row,Category,Revenue\n0,A,1\n2,B,2\n")  # first column: row ids
        self.emit({"type": "done", "approved": approved, "finished": True, "files": ["cleaned.csv"]})
    finally:
        self.done = True
        with self.cond:
            self.cond.notify_all()


def upload(**extra):
    return {"question": "Total revenue by category?", "file_name": "t.csv",
            "file_b64": base64.b64encode(SAMPLE_CSV).decode(), **extra}


def test_pages_and_plain_requests(client):
    for path in ("/", "/results", "/profile", "/view", "/static/app.js"):
        assert client.get(path).status_code == 200, path
    assert client.get("/api/config").json()["hosted"] is True
    assert client.get("/api/sample?size=large").json()["input"] == "large_sales.csv"
    assert client.get("/api/results").status_code == 200
    r = client.post("/api/inspect", json={"file_name": "t.csv", "file_b64": base64.b64encode(SAMPLE_CSV).decode()})
    assert r.status_code == 200 and r.json()["kind"] == "csv"
    assert client.post("/api/inspect", json={"file_name": "t.txt", "file_b64": ""}).status_code == 400


def test_a_whole_run_with_an_approval_over_one_socket(client, monkeypatch):
    monkeypatch.setattr(runner.Run, "_work", fake_work)
    with client.websocket_connect("/api/ws") as ws:
        ws.send_json(upload())
        assert ws.receive_json()["type"] == "run"
        assert ws.receive_json()["type"] == "start"
        ask = ws.receive_json()
        assert ask["type"] == "approval" and ask["auto"] is False
        ws.send_json({"type": "approve", "id": ask["id"], "answer": True})
        assert ws.receive_json() == {**ws_closed(ask["id"]), "seq": 2}
        files = ws.receive_json()
        assert files["type"] == "files" and files["files"]["cleaned.csv"].startswith("row,Category")
        assert files["profile"]["run_id"] == files["run_id"]  # the profile tab gets its data from here
        done = ws.receive_json()
        assert done["type"] == "done" and done["approved"] is True


def ws_closed(approval_id):
    return {"type": "approval_closed", "id": approval_id, "answer": True, "timed_out": False}


def test_a_bad_upload_is_reported_on_the_socket(client):
    with client.websocket_connect("/api/ws") as ws:
        ws.send_json(upload(question=""))
        assert ws.receive_json() == {"type": "error", "message": "type a question"}


def test_the_time_limit_stops_the_run_and_keeps_the_answer(client, monkeypatch):
    monkeypatch.setattr(runner.Run, "_work", fake_work)
    monkeypatch.setattr(hosted, "RUN_LIMIT", 0)
    with client.websocket_connect("/api/ws") as ws:
        ws.send_json(upload())
        seen = [ws.receive_json() for _ in range(6)]  # run, start, approval, notice, approval_closed, files, done
        seen.append(ws.receive_json())
    kinds = [m["type"] for m in seen]
    assert "notice" in kinds and kinds[-1] == "done"
    assert seen[-1]["approved"] is False  # the question that was waiting is refused, not left hanging


def test_closing_the_page_stops_the_run(client, monkeypatch):
    monkeypatch.setattr(runner.Run, "_work", fake_work)
    with client.websocket_connect("/api/ws") as ws:
        ws.send_json(upload())
        run_id = ws.receive_json()["run_id"]
        ws.receive_json(), ws.receive_json()  # start, approval
    run = server.RUNS[run_id]
    for _ in range(50):
        if run.cancelled:
            break
        time.sleep(0.05)
    assert run.cancelled


def test_hosted_runs_wait_less_for_an_approval_and_say_so(client, monkeypatch):
    monkeypatch.setattr(runner.Run, "_work", fake_work)
    with client.websocket_connect("/api/ws") as ws:
        ws.send_json(upload())
        run = server.RUNS[ws.receive_json()["run_id"]]
        assert run.approval_timeout == hosted.APPROVAL_TIMEOUT == 120
        ws.receive_json(), ws.receive_json()
    assert runner.APPROVAL_TIMEOUT == 600  # the local server keeps its 10 minutes
    assert runner._wait_text(600) == "10 minutes" and runner._wait_text(120) == "2 minutes" and runner._wait_text(90) == "90 seconds"
