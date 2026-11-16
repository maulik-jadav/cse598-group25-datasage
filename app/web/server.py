"""DataSage in the browser: python -m app.web.server, then open http://127.0.0.1:8501

Standard library only. The page uploads a CSV or Excel file (plus an optional rules file) and a
question, watches the agent's steps as server-sent events, and answers approvals with a click.
Uploads and outputs go to outputs/web/<run id>/ (ignored by git). Binds to 127.0.0.1 by default.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import mimetypes
import re
import shutil
import tempfile
import time
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from datasage.session import detect_csv, excel_sheets
from datasage.stack import MAX_FILES, stack_files

from . import analysis
from .runner import Run

ROOT = Path(__file__).resolve().parents[2]
STATIC = Path(__file__).resolve().parent / "static"
OUT = ROOT / "outputs" / "web"
SAMPLES = {
    "small": {"input": ROOT / "baseline" / "examples" / "messy_sales.csv", "rules": ROOT / "examples" / "messy_sales_rules.json",
              "question": "What was total revenue by category?"},
    "large": {"input": ROOT / "examples" / "large_sales.csv", "rules": ROOT / "examples" / "messy_sales_rules.json",
              "question": "What was total revenue by category?"},
    "monthly": {"inputs": [ROOT / "examples" / "demo" / "monthly" / f"orders_2026-{m}.csv" for m in ("07", "08", "09")],
                "input": ROOT / "examples" / "demo" / "monthly", "rules": ROOT / "examples" / "messy_sales_rules.json",
                "question": "What was total revenue in each monthly file?"},
    "hr": {"input": ROOT / "examples" / "demo" / "hr_employees.csv", "rules": ROOT / "examples" / "demo" / "hr_rules.json",
           "question": "What is the average salary by department?"},
    "inventory": {"input": ROOT / "examples" / "demo" / "inventory.csv", "rules": ROOT / "examples" / "demo" / "inventory_rules.json",
                  "question": "What is the total stock value by warehouse?"},
}
MAX_UPLOAD = 20 * 1024 * 1024
FILES = {"cleaned.csv": "text/csv", "report.md": "text/markdown", "replay.py": "text/x-python",
         "trace.jsonl": "application/json"}
RUNS: dict[str, Run] = {}
MAX_RUNS = 50              # finished runs kept in memory; older ones are dropped with their folders
OUTPUT_TTL = 24 * 3600     # output folders older than this are deleted
CLIENT_ID = re.compile(r"^[A-Za-z0-9-]{1,64}$")
RUN_ID = re.compile(r"^[0-9a-f]{10}$")
MODEL: str | None = None


class Handler(BaseHTTPRequestHandler):
    server_version = "DataSage"

    def log_message(self, fmt, *args):  # quieter console: only errors
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(fmt, *args)

    # ---- helpers -------------------------------------------------------------------------------
    def _send(self, status: int, body: bytes, ctype: str, extra: dict | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data, status: int = 200) -> None:
        self._send(status, json.dumps(data, default=str).encode(), "application/json")

    def _error(self, status: int, message: str) -> None:
        self._json({"error": message}, status)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_UPLOAD * 1.4:
            raise ValueError("file is larger than 20 MB")
        return json.loads(self.rfile.read(length) or b"{}")

    def _run(self, run_id: str) -> Run | None:
        return RUNS.get(run_id)

    # ---- routes --------------------------------------------------------------------------------
    def do_GET(self):  # noqa: N802
        url = urlparse(self.path)
        parts = [p for p in url.path.split("/") if p]
        if not parts:
            return self._static("index.html")
        if parts[0] == "static" and len(parts) == 2:
            return self._static(parts[1])
        if parts == ["api", "sample"]:
            s = SAMPLES.get(parse_qs(url.query).get("size", ["small"])[0], SAMPLES["small"])
            label = f"{len(s['inputs'])} monthly files" if s.get("inputs") else s["input"].name
            return self._json({"question": s["question"], "input": label, "rules": s["rules"].name})
        if len(parts) == 4 and parts[:2] == ["api", "runs"] and parts[3] == "events":
            run = self._run(parts[2])
            return self._events(run, int(parse_qs(url.query).get("from", ["0"])[0])) if run else self._error(404, "no such run")
        if len(parts) == 5 and parts[:2] == ["api", "runs"] and parts[3] == "files":
            run, name = self._run(parts[2]), parts[4]
            # A run from an earlier server session is no longer in memory, but its folder is still on disk.
            folder = run.out_dir if run else (OUT / parts[2] if RUN_ID.match(parts[2]) else None)
            if not folder or name not in FILES or not (folder / name).exists():
                return self._error(404, "file not ready")
            data = (folder / name).read_bytes()
            return self._send(200, data, FILES[name], {"Content-Disposition": f'attachment; filename="{name}"'})
        if parts in (["results"], ["profile"], ["view"]):  # analysis pages, see app/web/analysis.py
            return self._static(parts[0] + ".html")
        if parts == ["api", "results"]:
            return self._json(analysis.results())
        if len(parts) == 4 and parts[:2] == ["api", "runs"] and parts[3] == "profile":
            status, body = analysis.run_profile(parts[2], RUNS, OUT)
            return self._json(body, status)
        self._error(404, "not found")

    def do_POST(self):  # noqa: N802
        parts = [p for p in urlparse(self.path).path.split("/") if p]
        try:
            body = self._body()
        except (ValueError, json.JSONDecodeError) as err:
            return self._error(400, str(err))
        if parts == ["api", "runs"]:
            return self._start(body)
        if parts == ["api", "inspect"]:
            return self._inspect(body)
        if len(parts) == 4 and parts[:2] == ["api", "runs"]:
            run = self._run(parts[2])
            if not run:
                return self._error(404, "no such run")
            if parts[3] == "approve":
                ok = run.answer(str(body.get("id", "")), bool(body.get("answer")))
                return self._json({"ok": ok}, 200 if ok else 409)
            if parts[3] == "cancel":
                run.cancel()
                return self._json({"ok": True})
        self._error(404, "not found")

    def _static(self, name: str) -> None:
        path = (STATIC / name).resolve()
        if path.parent != STATIC or not path.is_file():
            return self._error(404, "not found")
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self._send(200, path.read_bytes(), ctype + ("; charset=utf-8" if ctype.startswith("text/") or ctype.endswith("javascript") else ""))

    def _decode(self, body: dict) -> tuple[str, bytes]:
        name = Path(str(body.get("file_name") or "")).name
        suffix = Path(name).suffix.lower()
        if suffix not in (".csv", ".xlsx"):
            raise ValueError("upload a .csv or .xlsx file")
        try:
            data = base64.b64decode(body.get("file_b64") or "", validate=True)
        except (binascii.Error, ValueError):
            raise ValueError("could not read the file")
        if not data or len(data) > MAX_UPLOAD:
            raise ValueError("the file is empty or larger than 20 MB")
        return suffix, data

    def _inspect(self, body: dict) -> None:
        """Before a run: the sheets of an Excel file, or the separator and encoding found in a CSV."""
        try:
            suffix, data = self._decode(body)
        except ValueError as err:
            return self._error(400, str(err))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ("inspect" + suffix)
            path.write_bytes(data)
            try:
                if suffix == ".xlsx":
                    return self._json({"kind": "excel", "sheets": excel_sheets(path)})
                return self._json({"kind": "csv", **detect_csv(path)})
            except Exception as err:  # a damaged file: say so instead of failing later
                return self._error(400, f"could not open the file: {type(err).__name__}")

    def _rules(self, body: dict, folder: Path):
        """The uploaded rules file saved in the run folder; None without one, False when it is not valid JSON."""
        if not body.get("rules_text"):
            return None
        try:
            json.loads(body["rules_text"])
        except json.JSONDecodeError:
            return False
        path = folder / "rules.json"
        path.write_text(body["rules_text"])
        return path

    def _start(self, body: dict) -> None:
        question = str(body.get("question") or "").strip()
        if not question:
            return self._error(400, "type a question")
        run_id = uuid.uuid4().hex[:10]
        folder = OUT / run_id
        folder.mkdir(parents=True, exist_ok=True)
        sources = None
        if body.get("sample"):
            s = SAMPLES.get(str(body["sample"]), SAMPLES["small"])
            input_path, rules_path = s["input"], s["rules"]
            if s.get("inputs"):
                input_path = folder / "input.csv"
                sources = stack_files(s["inputs"], input_path)
        elif isinstance(body.get("files"), list) and len(body["files"]) > 1:
            parts = []
            for i, f in enumerate(body["files"][:MAX_FILES]):
                try:
                    suffix, data = self._decode(f)
                except ValueError as err:
                    return self._error(400, f"{Path(str(f.get('file_name') or '')).name or 'a file'}: {err}")
                part = folder / "parts" / f"{i:02d}{suffix}"
                part.parent.mkdir(parents=True, exist_ok=True)
                part.write_bytes(data)
                parts.append((part, Path(str(f.get("file_name") or part.name)).name))
            input_path = folder / "input.csv"
            try:
                sources = stack_files([p for p, _ in parts], input_path, [n for _, n in parts])
            except ValueError as err:
                return self._error(400, str(err))
            rules_path = self._rules(body, folder)
            if rules_path is False:
                return self._error(400, "the rules file is not valid JSON")
        else:
            try:
                suffix, data = self._decode(body)
            except ValueError as err:
                return self._error(400, str(err))
            input_path = folder / ("input" + suffix)
            input_path.write_bytes(data)
            rules_path = self._rules(body, folder)
            if rules_path is False:
                return self._error(400, "the rules file is not valid JSON")
        client = str(body.get("client_id") or "")
        client = client if CLIENT_ID.match(client) else ""
        for old in RUNS.values():  # a new run replaces this browser's earlier run, never someone else's
            if not old.done and client and old.client_id == client:
                old.cancel()
        sheet = body.get("sheet")
        run = Run(input_path, question, rules_path, folder, MODEL, sheet=str(sheet) if sheet not in (None, "") else None,
                  client_id=client, mode=str(body.get("approve") or "ask"))
        run.sources = sources
        RUNS[run_id] = run
        run.start()
        prune()
        self._json({"run_id": run_id})

    def _events(self, run: Run, start: int) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        # The stream has no length, so closing the connection is what tells the client it has ended.
        # ("Connection: keep-alive" would make http.server hold the socket open after the run is done.)
        self.send_header("Connection", "close")
        self.end_headers()
        sent = start
        try:
            while True:
                with run.cond:
                    if sent >= len(run.events) and not run.done:
                        run.cond.wait(timeout=15)
                    batch = run.events[sent:]
                    finished = run.done
                if not batch:
                    if finished:
                        break
                    self.wfile.write(b": ping\n\n")
                for event in batch:
                    self.wfile.write(f"id: {event['seq']}\ndata: {json.dumps(event, default=str)}\n\n".encode())
                sent += len(batch)
                self.wfile.flush()
                if finished and sent >= len(run.events):
                    break
        except (BrokenPipeError, ConnectionResetError):
            pass


def prune(now: float | None = None) -> None:
    """Keep memory and disk bounded: drop the oldest finished runs past MAX_RUNS, and delete old output folders."""
    now = now or time.time()
    finished = [rid for rid, r in RUNS.items() if r.done]
    for rid in finished[: max(0, len(RUNS) - MAX_RUNS)]:
        shutil.rmtree(RUNS.pop(rid).out_dir, ignore_errors=True)
    if OUT.exists():
        live = {r.out_dir.name for r in RUNS.values() if not r.done}
        for folder in OUT.iterdir():
            if folder.is_dir() and folder.name not in live and now - folder.stat().st_mtime > OUTPUT_TTL:
                RUNS.pop(folder.name, None)
                shutil.rmtree(folder, ignore_errors=True)


def main() -> None:
    global MODEL
    parser = argparse.ArgumentParser(description="DataSage browser app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument("--model", help="model name (default: the agent's default, Qwen3-30B)")
    args = parser.parse_args()
    MODEL = args.model
    if not re.match(r"^[\w.\-:]+$", args.host):
        raise SystemExit("bad host")
    prune()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.daemon_threads = True
    print(f"DataSage is running at http://{args.host}:{args.port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
