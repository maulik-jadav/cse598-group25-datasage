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
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .runner import Run

ROOT = Path(__file__).resolve().parents[2]
STATIC = Path(__file__).resolve().parent / "static"
OUT = ROOT / "outputs" / "web"
SAMPLE = {"input": ROOT / "baseline" / "examples" / "messy_sales.csv", "rules": ROOT / "examples" / "messy_sales_rules.json",
          "question": "What was total revenue by category?"}
MAX_UPLOAD = 20 * 1024 * 1024
FILES = {"cleaned.csv": "text/csv", "report.md": "text/markdown", "replay.py": "text/x-python",
         "trace.jsonl": "application/json"}
RUNS: dict[str, Run] = {}
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
            return self._json({"question": SAMPLE["question"], "input": SAMPLE["input"].name, "rules": SAMPLE["rules"].name})
        if len(parts) == 4 and parts[:2] == ["api", "runs"] and parts[3] == "events":
            run = self._run(parts[2])
            return self._events(run, int(parse_qs(url.query).get("from", ["0"])[0])) if run else self._error(404, "no such run")
        if len(parts) == 5 and parts[:2] == ["api", "runs"] and parts[3] == "files":
            run, name = self._run(parts[2]), parts[4]
            if not run or name not in FILES or not (run.out_dir / name).exists():
                return self._error(404, "file not ready")
            data = (run.out_dir / name).read_bytes()
            return self._send(200, data, FILES[name], {"Content-Disposition": f'attachment; filename="{name}"'})
        self._error(404, "not found")

    def do_POST(self):  # noqa: N802
        parts = [p for p in urlparse(self.path).path.split("/") if p]
        try:
            body = self._body()
        except (ValueError, json.JSONDecodeError) as err:
            return self._error(400, str(err))
        if parts == ["api", "runs"]:
            return self._start(body)
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

    def _start(self, body: dict) -> None:
        question = str(body.get("question") or "").strip()
        if not question:
            return self._error(400, "type a question")
        run_id = uuid.uuid4().hex[:10]
        folder = OUT / run_id
        folder.mkdir(parents=True, exist_ok=True)
        if body.get("sample"):
            input_path, rules_path = SAMPLE["input"], SAMPLE["rules"]
        else:
            name = Path(str(body.get("file_name") or "")).name
            suffix = Path(name).suffix.lower()
            if suffix not in (".csv", ".xlsx"):
                return self._error(400, "upload a .csv or .xlsx file")
            try:
                data = base64.b64decode(body.get("file_b64") or "", validate=True)
            except (binascii.Error, ValueError):
                return self._error(400, "could not read the file")
            if not data or len(data) > MAX_UPLOAD:
                return self._error(400, "the file is empty or larger than 20 MB")
            input_path = folder / ("input" + suffix)
            input_path.write_bytes(data)
            rules_path = None
            if body.get("rules_text"):
                try:
                    json.loads(body["rules_text"])
                except json.JSONDecodeError:
                    return self._error(400, "the rules file is not valid JSON")
                rules_path = folder / "rules.json"
                rules_path.write_text(body["rules_text"])
        for old in RUNS.values():  # one live run at a time; an older one stops asking for approvals
            if not old.done:
                old.cancel()
        run = Run(input_path, question, rules_path, folder, MODEL)
        RUNS[run_id] = run
        run.start()
        self._json({"run_id": run_id})

    def _events(self, run: Run, start: int) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
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
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.daemon_threads = True
    print(f"DataSage is running at http://{args.host}:{args.port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
