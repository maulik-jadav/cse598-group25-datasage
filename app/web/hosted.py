"""DataSage on a serverless host (Vercel): the same pages and agent as app/web/server.py.

    uvicorn app.web.hosted:app          # locally, to try the hosted version

A serverless host sends each request to whichever instance is free and keeps nothing between requests, so a
run cannot be split over separate requests as the local server does (start, event stream, approve, download).
Here one WebSocket carries the whole run: the start message with the upload, every event, each approval, and
at the end the output files and the column profile, which the page keeps in the browser for View, Download
and the profile tab. Everything else (pages, samples, the results dashboard, file inspection) needs no state
and is served as plain requests.

Settings (environment variables): RC_LLM_API_KEY and RC_LLM_BASE_URL as for the command line;
DATASAGE_MODEL (default: the agent's default); DATASAGE_RUN_LIMIT, seconds before a run is stopped (default
240, so a run ends inside the host's 300 s limit even with one slow model call left);
DATASAGE_APPROVAL_TIMEOUT, seconds an approval waits for a click (default 120).
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from . import analysis, runner, server

if os.environ.get("VERCEL"):  # only /tmp is writable there
    server.OUT = Path(os.environ.get("DATASAGE_OUT", "/tmp/datasage"))
APPROVAL_TIMEOUT = int(os.environ.get("DATASAGE_APPROVAL_TIMEOUT", "120"))
RUN_LIMIT = int(os.environ.get("DATASAGE_RUN_LIMIT", "240"))
MODEL = os.environ.get("DATASAGE_MODEL") or None
POLL = 0.15  # seconds between checks for new events

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=server.STATIC), name="static")


def _json(data, status: int = 200) -> Response:
    # json.dumps as in server.py (default=str), so both servers send the same bytes
    return Response(json.dumps(data, default=str), status_code=status, media_type="application/json",
                    headers={"Cache-Control": "no-store"})


def _page(name: str) -> FileResponse:
    return FileResponse(server.STATIC / name, headers={"Cache-Control": "no-store"})


@app.get("/", include_in_schema=False)
def index():
    return _page("index.html")


@app.get("/results", include_in_schema=False)
def results_page():
    return _page("results.html")


@app.get("/profile", include_in_schema=False)
def profile_page():
    return _page("profile.html")


@app.get("/view", include_in_schema=False)
def view_page():
    return _page("view.html")


@app.get("/api/config")
def config():
    return _json({"hosted": True, "run_limit": RUN_LIMIT, "approval_timeout": APPROVAL_TIMEOUT})


@app.get("/api/sample")
def sample(size: str = "small"):
    return _json(server.sample_info(size))


@app.get("/api/results")
def results():
    return _json(analysis.results())


@app.post("/api/inspect")
async def inspect(request: Request):
    try:
        body = await request.json()
    except ValueError:
        return _json({"error": "could not read the request"}, 400)
    status, data = await asyncio.to_thread(server.inspect_upload, body)
    return _json(data, status)


@app.get("/api/runs/{run_id}/files/{name}")
def run_file(run_id: str, name: str):
    # The page normally has these from the socket. This only works when the request lands on the same instance.
    run = server.RUNS.get(run_id)
    if not run or name not in server.FILES or not (run.out_dir / name).is_file():
        return _json({"error": "This file is kept in the browser tab that ran it. Open it from that tab."}, 404)
    return Response((run.out_dir / name).read_bytes(), media_type=server.FILES[name],
                    headers={"Content-Disposition": f'attachment; filename="{name}"'})


@app.get("/api/runs/{run_id}/profile")
def run_profile(run_id: str):
    status, body = analysis.run_profile(run_id, server.RUNS, server.OUT)
    if status == 404:
        body = {"error": "The profile is kept in the browser tab that ran it. Open it from that tab."}
    return _json(body, status)


def _outputs(run: runner.Run) -> dict:
    """The output files and the column profile, sent just before the done event."""
    for _ in range(50):  # the worker marks the run done just after it emits the done event
        if run.done:
            break
        time.sleep(0.1)
    files = {}
    for name in server.FILES:
        path = run.out_dir / name
        if path.is_file():
            files[name] = path.read_text(errors="replace")
    status, profile = analysis.run_profile(run.id, server.RUNS, server.OUT)
    return {"type": "files", "run_id": run.id, "files": files, "profile": profile if status == 200 else None}


async def _listen(ws: WebSocket, run: runner.Run) -> None:
    """Approvals and Stop from the page, until it disconnects."""
    try:
        while True:
            msg = await ws.receive_json()
            if not isinstance(msg, dict):
                continue
            if msg.get("type") == "approve":
                run.answer(str(msg.get("id", "")), bool(msg.get("answer")))
            elif msg.get("type") == "cancel":
                run.cancel()
    except (WebSocketDisconnect, ValueError, RuntimeError):
        return


@app.websocket("/api/ws")
async def run_socket(ws: WebSocket):
    await ws.accept()
    try:
        body = await ws.receive_json()
    except (WebSocketDisconnect, ValueError):
        return
    if not isinstance(body, dict):
        body = {}
    run, error = await asyncio.to_thread(server.prepare_run, body, MODEL)
    if error:
        await ws.send_text(json.dumps({"type": "error", "message": error}))
        await ws.close()
        return
    run.approval_timeout = APPROVAL_TIMEOUT
    await ws.send_text(json.dumps({"type": "run", "run_id": run.id, "run_limit": RUN_LIMIT}))
    run.start()
    listener = asyncio.create_task(_listen(ws, run))
    deadline = time.monotonic() + RUN_LIMIT
    sent, cut = 0, False
    try:
        while True:
            with run.cond:
                batch = run.events[sent:]
                finished = run.done
            for event in batch:
                if event.get("type") == "done":
                    await ws.send_text(json.dumps(await asyncio.to_thread(_outputs, run), default=str))
                await ws.send_text(json.dumps(event, default=str))
            sent += len(batch)
            if finished and sent >= len(run.events):
                break
            if listener.done():  # the page closed: stop the agent rather than run on for nobody
                run.cancel()
                return
            if not cut and time.monotonic() > deadline:
                cut = True
                run.cancel()
                await ws.send_text(json.dumps({"type": "notice", "message":
                    f"Stopped after {RUN_LIMIT // 60} minutes, the limit for the hosted app. "
                    "The answer below uses the fixes made so far; run DataSage locally for longer runs."}))
            await asyncio.sleep(POLL)
        await ws.close()
    except (WebSocketDisconnect, RuntimeError):
        run.cancel()
    finally:
        listener.cancel()
        if not run.done:  # however the connection ended (closed page, cancelled task), do not run on for nobody
            run.cancel()
