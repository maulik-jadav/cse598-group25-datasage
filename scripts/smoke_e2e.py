"""End-to-end smoke test of DataSage with the real model (needs the .env key; takes a few minutes).

    python scripts/smoke_e2e.py

Starts the browser app's server in this process, then drives it the way the page does: every page and
asset, every sample in Auto mode (in parallel, as different browsers), Ask mode with Keep / Apply,
uploads (semicolon + Windows-1252 CSV, a two-sheet Excel file, several stacked files, bad files), Stop,
downloads, the file viewer, the column profile, and replay.py reproducing cleaned.csv. Then the command
line with several inputs and with an Excel sheet. Answers are checked against an independent pandas
calculation. Prints PASS / FAIL per check and exits non-zero on any failure.
"""

from __future__ import annotations

import base64
import difflib
import io
import json
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http.server import ThreadingHTTPServer
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.web import server  # noqa: E402
from datasage.analyze import answers_match  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []
LOCK = threading.Lock()


def check(name: str, ok: bool, detail: str = "") -> bool:
    with LOCK:
        RESULTS.append((name, bool(ok), detail))
        print(f"{'PASS' if ok else 'FAIL'}  {name}{'  ' + detail if detail and not ok else ''}", flush=True)
    return bool(ok)


# ---------- expected answers, computed without DataSage ----------
def expected_sales(frames: dict[str, pd.DataFrame], by: str = "Category") -> dict:
    """Every fix approved: drop exact duplicates, merge labels into the allowed ones, drop Quantity < 1,
    Revenue = Quantity * Price. `frames` maps source file name -> raw text frame."""
    parts = []
    for name, df in frames.items():
        df = df.copy()
        df["source_file"] = name
        parts.append(df)
    df = pd.concat(parts, ignore_index=True)
    df = df[~df.drop(columns="source_file").duplicated()] if len(frames) > 1 else df.drop_duplicates()
    allowed = ["Electronics", "Accessories"]
    df["Category"] = [difflib.get_close_matches(str(v).strip().title(), allowed, 1, 0.6)[0] for v in df["Category"]]
    q, p = pd.to_numeric(df["Quantity"]), pd.to_numeric(df["Price"])
    keep = q >= 1
    return {k: float(v) for k, v in (q[keep] * p[keep]).groupby(df.loc[keep, by]).sum().items()}


# From examples/make_demo_files.py (it prints these): the answers when every fix is approved.
HR = {"Engineering": 130027.03, "Sales": 82280.22, "Finance": 100993.24, "Operations": 62343.37, "Marketing": 88243.24}
INVENTORY = {"Phoenix": 1156928.05, "Tempe": 936441.6, "Mesa": 844651.2, "Tucson": 1286821.7}


def read_text(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


# ---------- HTTP helpers ----------
class Client:
    def __init__(self, base: str):
        self.base = base

    def get(self, path: str) -> tuple[int, bytes]:
        try:
            with urllib.request.urlopen(self.base + path, timeout=60) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def post(self, path: str, body: dict) -> tuple[int, dict]:
        req = urllib.request.Request(self.base + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)

    def run(self, body: dict, answers=None, stop_after_steps: int | None = None, timeout: int = 600) -> dict:
        """Start a run and follow its events; answers(ev) -> True/False for Ask-mode approvals."""
        status, out = self.post("/api/runs", body)
        if status != 200:
            return {"error": out, "status": status, "events": [], "done": {}}
        rid, events, steps = out["run_id"], [], 0
        t0 = time.time()
        with urllib.request.urlopen(f"{self.base}/api/runs/{rid}/events", timeout=timeout) as stream:
            for raw in stream:
                line = raw.decode().rstrip("\n")
                if not line.startswith("data: "):
                    continue
                ev = json.loads(line[6:])
                events.append(ev)
                if ev["type"] == "step":
                    steps += 1
                    if stop_after_steps and steps == stop_after_steps:
                        self.post(f"/api/runs/{rid}/cancel", {})
                if ev["type"] == "approval" and not ev.get("auto") and answers:
                    self.post(f"/api/runs/{rid}/approve", {"id": ev["id"], "answer": answers(ev)})
                if ev["type"] in ("done", "error"):
                    break
        return {"run_id": rid, "events": events, "done": events[-1] if events else {}, "seconds": time.time() - t0}


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


# ---------- checks ----------
def pages(c: Client) -> None:
    for path in ["/", "/results", "/profile", "/view", "/static/app.js", "/static/app.css", "/static/results.js",
                 "/static/profile.js", "/static/view.js", "/static/view.css", "/static/viz.js", "/static/analysis.css"]:
        status, body = c.get(path)
        check(f"page {path}", status == 200 and len(body) > 100, f"status {status}")
    status, body = c.get("/api/results")
    check("results API", status == 200 and b"datasage-m3" in body, f"status {status}")
    for size in ["small", "large", "monthly", "hr", "inventory"]:
        status, body = c.get(f"/api/sample?size={size}")
        check(f"sample info {size}", status == 200 and b"question" in body)


def finished_run(name: str, c: Client, r: dict, expected: dict, auto: bool) -> None:
    done = r.get("done", {})
    if not check(f"{name}: finished", done.get("type") == "done" and done.get("finished"),
                 f"{done.get('stop_reason') or r.get('error')}"):
        return
    check(f"{name}: answer correct", answers_match(done.get("answer"), expected), f"got {done.get('answer')} want {expected}")
    asks = [e for e in r["events"] if e["type"] == "approval"]
    if auto:
        check(f"{name}: every approval automatic", all(e.get("auto") for e in asks), f"{len(asks)} approvals")
        check(f"{name}: change log says how", all(ch.get("how") in ("approved automatically", "safe, applied without asking")
                                                  for ch in done["changes"] if ch["applied"]))
    for f in done.get("files", []):
        status, body = c.get(f"/api/runs/{r['run_id']}/files/{f}")
        check(f"{name}: download {f}", status == 200 and len(body) > 0)
    status, body = c.get(f"/view?run={r['run_id']}&file=report.md")
    check(f"{name}: file viewer page", status == 200 and b"view.js" in body)
    status, body = c.get(f"/api/runs/{r['run_id']}/profile")
    check(f"{name}: column profile", status == 200 and b"columns" in body, f"status {status}")
    check(f"{name}: data health", done.get("health", {}).get("rows_before") is not None)


def replay_matches(name: str, run_id: str) -> None:
    out = server.OUT / run_id
    ns: dict = {}
    try:
        exec(compile((out / "replay.py").read_text(), str(out / "replay.py"), "exec"), ns)
    except Exception as err:  # noqa: BLE001
        check(f"{name}: replay.py runs", False, f"{type(err).__name__}: {err}")
        return
    df = ns["df"].reset_index(drop=True)
    replayed = df.astype(object).where(df.notna(), "").astype(str)  # blanks as "" like cleaned.csv
    cleaned = pd.read_csv(out / "cleaned.csv", dtype=str, keep_default_na=False).drop(columns="row")
    norm = lambda s: s.str.replace(r"\.0$", "", regex=True)  # noqa: E731  (1800 vs 1800.0)
    same = replayed.shape == cleaned.shape and all(norm(replayed[c]).tolist() == norm(cleaned[c]).tolist() for c in cleaned.columns)
    check(f"{name}: replay.py reproduces cleaned.csv", same, f"replayed {replayed.shape} cleaned {cleaned.shape}")


def cli_answer(stdout: str):
    line = next((ln for ln in stdout.splitlines() if ln.startswith("answer:")), "")
    return eval(line[len("answer:"):]) if line and "None" not in line else None  # noqa: S307 (our own output)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="datasage-smoke-"))
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    c = Client(f"http://127.0.0.1:{httpd.server_address[1]}")
    print(f"server on {c.base}; scratch {tmp}", flush=True)
    pages(c)

    small = read_text(ROOT / "baseline/examples/messy_sales.csv")
    large = read_text(ROOT / "examples/large_sales.csv")
    monthly = {f"orders_2026-{m}.csv": read_text(ROOT / f"examples/demo/monthly/orders_2026-{m}.csv") for m in ("07", "08", "09")}
    rules_text = (ROOT / "examples/messy_sales_rules.json").read_text()
    q_sales = "What was total revenue by category?"
    q_monthly = "What was total revenue in each monthly file?"

    # 1. all samples in Auto mode, at the same time, as five different browsers
    samples = {
        "small": (q_sales, expected_sales({"s": small})),
        "large": (q_sales, expected_sales({"l": large})),
        "monthly": (q_monthly, expected_sales(monthly, by="source_file")),
        "hr": ("What is the average salary by department?", HR),
        "inventory": ("What is the total stock value by warehouse?", INVENTORY),
    }
    with ThreadPoolExecutor(5) as pool:
        futures = {k: pool.submit(c.run, {"sample": k, "question": q, "client_id": f"browser-{k}", "approve": "auto"})
                   for k, (q, _) in samples.items()}
        runs = {k: f.result() for k, f in futures.items()}
    for k, r in runs.items():
        finished_run(f"auto {k}", c, r, samples[k][1], auto=True)
        if r.get("run_id"):
            replay_matches(f"auto {k}", r["run_id"])

    # 2. Ask mode: apply the safe kinds of fix, keep the row drops and blanks
    r = c.run({"sample": "small", "question": q_sales, "client_id": "ask", "approve": "ask"},
              answers=lambda ev: ev["tool"] in ("drop_duplicates", "normalize_labels", "cast_numeric", "recompute_column"))
    asks = [e for e in r["events"] if e["type"] == "approval"]
    check("ask: approvals waited for the page", bool(asks) and not any(e.get("auto") for e in asks))
    check("ask: approval cards carry row evidence", all(e.get("examples", {}).get("rows") is not None for e in asks))
    kept = r["done"].get("answer")
    check("ask: Keep leaves the -1 row in (Electronics 2,185)", answers_match(kept, {"Electronics": 2185.0, "Accessories": 830.0}),
          f"got {kept}")
    check("ask: rejected fixes listed as caveats", any(not ch["applied"] for ch in r["done"].get("changes", [])))

    # 3. uploads: semicolon + Windows-1252 CSV, two-sheet Excel, stacked files, bad files
    semi = small.to_csv(index=False, sep=";").replace("Monitor", "Monitör").encode("cp1252")
    r = c.run({"question": q_sales, "file_name": "semi.csv", "file_b64": b64(semi), "client_id": "u1", "approve": "auto",
               "rules_text": rules_text})
    finished_run("upload ; cp1252 csv", c, r, expected_sales({"s": small}), auto=True)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf) as w:
        pd.DataFrame({"note": ["cover sheet"]}).to_excel(w, sheet_name="Read me", index=False)
        small.to_excel(w, sheet_name="Orders", index=False)
    status, info = c.post("/api/inspect", {"file_name": "book.xlsx", "file_b64": b64(buf.getvalue())})
    check("inspect lists Excel sheets", status == 200 and info.get("sheets") == ["Read me", "Orders"], str(info))
    r = c.run({"question": q_sales, "file_name": "book.xlsx", "file_b64": b64(buf.getvalue()), "sheet": "Orders",
               "client_id": "u2", "approve": "auto", "rules_text": rules_text})
    finished_run("upload xlsx, sheet Orders", c, r, expected_sales({"s": small}), auto=True)
    files = [{"file_name": n, "file_b64": b64(df.to_csv(index=False).encode())} for n, df in monthly.items()]
    r = c.run({"question": q_monthly, "files": files, "client_id": "u3", "approve": "auto", "rules_text": rules_text})
    finished_run("upload 3 stacked files", c, r, expected_sales(monthly, by="source_file"), auto=True)
    status, out = c.post("/api/runs", {"question": "q", "files": [files[0], {"file_name": "x.csv", "file_b64": b64(b"A,B\n1,2\n")}]})
    check("stacking refuses different columns", status == 400 and "same columns" in out.get("error", ""), str(out))
    status, out = c.post("/api/runs", {"question": "q", "file_name": "x.txt", "file_b64": b64(b"hello")})
    check("refuses a .txt upload", status == 400)
    status, out = c.post("/api/runs", {"question": "q", "file_name": "x.csv", "file_b64": "not base64!!"})
    check("refuses broken base64", status == 400)

    # 4. Stop during a run
    r = c.run({"sample": "large", "question": q_sales, "client_id": "stop", "approve": "ask"},
              answers=lambda ev: True, stop_after_steps=2)
    check("stop ends the run quickly", r["done"].get("stop_reason") == "cancelled" and r["seconds"] < 60,
          f"{r['done'].get('stop_reason')} after {r['seconds']:.1f}s")

    # 5. command line: several inputs, and an Excel sheet
    rules = str(ROOT / "examples/messy_sales_rules.json")
    paths = [str(ROOT / f"examples/demo/monthly/orders_2026-{m}.csv") for m in ("07", "08", "09")]
    cli = subprocess.run([sys.executable, "-m", "datasage", "--input", *paths, "--rules", rules, "--approve", "auto",
                          "--request", q_monthly, "--out", str(tmp / "cli_multi")], cwd=ROOT, capture_output=True, text=True, timeout=600)
    check("CLI: several inputs stacked and answered",
          cli.returncode == 0 and answers_match(cli_answer(cli.stdout), expected_sales(monthly, by="source_file")), cli.stderr[-300:])
    xlsx = tmp / "book.xlsx"
    xlsx.write_bytes(buf.getvalue())
    cli = subprocess.run([sys.executable, "-m", "datasage", "--input", str(xlsx), "--sheet", "Orders", "--rules", rules,
                          "--approve", "auto", "--request", q_sales, "--out", str(tmp / "cli_xlsx")],
                         cwd=ROOT, capture_output=True, text=True, timeout=600)
    check("CLI: Excel sheet", cli.returncode == 0 and answers_match(cli_answer(cli.stdout), expected_sales({"s": small})), cli.stderr[-300:])
    ns: dict = {}
    try:
        exec((tmp / "cli_xlsx" / "replay.py").read_text(), ns)
        check("CLI: replay.py reads the Excel sheet", len(ns["df"]) == len(pd.read_csv(tmp / "cli_xlsx" / "cleaned.csv")))
    except Exception as err:  # noqa: BLE001
        check("CLI: replay.py reads the Excel sheet", False, f"{type(err).__name__}: {err}")

    httpd.shutdown()
    failed = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(failed)} passed, {len(failed)} failed")
    for name, _, detail in failed:
        print(f"  FAIL {name}: {detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
