"""Report view: read a finished DataSage run folder and show it.

A run folder is what `python -m datasage ... --out DIR` writes (datasage/report.py, write_outputs):
report.md, cleaned.csv, replay.py and trace.jsonl. The loader only reads; it never changes the folder.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# Files offered for download, in display order. recipe.json comes from the recipes work (item 7).
RUN_FILES = ("cleaned.csv", "replay.py", "trace.jsonl", "recipe.json")

# Headers of the Changes table as markdown_report() in datasage/report.py writes them, mapped to our keys.
CHANGE_KEYS = {"version": "version", "fix": "fix", "risk": "risk", "approval": "approval",
               "what changed": "what_changed", "reason": "reason"}
# Column labels for the change-log table on the page (the report's own header names).
CHANGE_LABELS = {key: header.capitalize() for header, key in CHANGE_KEYS.items()}
_MIME = {".csv": "text/csv", ".py": "text/x-python", ".jsonl": "application/jsonl", ".json": "application/json"}

_HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")
_SEPARATOR = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?$")
_CELL_SPLIT = re.compile(r"(?<!\\)\|")  # a pipe that is not escaped as \|


@dataclass
class RunView:
    run_dir: Path
    report_md: str | None  # text of report.md, None if the file is missing or unreadable
    changes: list[dict]  # one dict per change-log row: version, fix, risk, approval, what_changed, reason
    files: dict[str, Path]  # whichever of RUN_FILES exist


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:  # missing file, a folder with that name, no permission
        return None


def _cells(line: str) -> list[str]:
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|") and not inner.endswith("\\|"):
        inner = inner[:-1]
    return [cell.strip().replace("\\|", "|") for cell in _CELL_SPLIT.split(inner)]


def parse_change_log(report_md: str) -> list[dict]:
    """Read the table under the "Changes" heading into one dict per row.

    Rejected fixes are kept: report.py writes them with Version "-" and Approval "rejected". report.py
    does not escape "|" inside a reason, so extra cells in a row are joined back into the last column.
    Returns [] when there is no Changes section or its table has no rows.
    """
    lines = (report_md or "").splitlines()
    start = None
    for i, line in enumerate(lines):
        heading = _HEADING.match(line.strip())
        if heading and heading.group(1).strip().lower() == "changes":
            start = i + 1
            break
    if start is None:
        return []

    headers: list[str] | None = None
    rows: list[dict] = []
    for line in lines[start:]:
        text = line.strip()
        if _HEADING.match(text):
            break  # the next section starts
        if not text.startswith("|"):
            if headers is not None and text:
                break  # text after the table
            continue  # blank lines before the table
        if headers is None:
            headers = [CHANGE_KEYS.get(cell.lower(), cell.lower()) for cell in _cells(text)]
            continue
        if _SEPARATOR.match(text):
            continue
        cells = _cells(text)
        if len(cells) > len(headers):
            cells = cells[:len(headers) - 1] + [" | ".join(cells[len(headers) - 1:])]
        cells += [""] * (len(headers) - len(cells))
        found = dict(zip(headers, cells))
        rows.append({key: found.get(key, "") for key in CHANGE_KEYS.values()})
    return rows


def load_run(run_dir: Path) -> RunView:
    """Load a run folder. Missing pieces give None or are left out; this never raises for a bad folder."""
    run_dir = Path(run_dir)
    report_md = _read_text(run_dir / "report.md")
    changes = parse_change_log(report_md) if report_md else []
    files = {name: run_dir / name for name in RUN_FILES if (run_dir / name).is_file()}
    return RunView(run_dir=run_dir, report_md=report_md, changes=changes, files=files)


def render_report(run_dir: Path) -> None:
    """Show a run folder in Streamlit: report.md, the change log as a table, and one download per file.

    Streamlit is imported here and nowhere else, so load_run and parse_change_log (and their tests) work
    without it. The page that calls this sets st.set_page_config. Nothing is written to the run folder.
    """
    import pandas as pd
    import streamlit as st

    view = load_run(run_dir)
    st.caption(f"Run folder: {view.run_dir}")

    if view.report_md is None:
        st.warning(f"No report.md in {view.run_dir}.")
    else:
        st.markdown(view.report_md)  # HTML in the report stays escaped (unsafe_allow_html is off)

    st.subheader("Change log")
    if view.changes:
        table = pd.DataFrame(view.changes, columns=list(CHANGE_LABELS)).rename(columns=CHANGE_LABELS)
        st.dataframe(table, hide_index=True)
    else:
        st.info("No changes were recorded for this run.")

    st.subheader("Files")
    if not view.files:
        st.info("No output files in this folder.")
    for name, path in view.files.items():
        try:
            data = path.read_bytes()
        except OSError as err:
            st.warning(f"Could not read {name}: {err}")
            continue
        st.download_button(f"Download {name}", data=data, file_name=name,
                           mime=_MIME.get(path.suffix, "text/plain"), key=f"download:{view.run_dir}:{name}")
