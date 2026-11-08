"""Report view: read a finished DataSage run folder and show it.

A run folder is what `python -m datasage ... --out DIR` writes (datasage/report.py, write_outputs):
report.md, cleaned.csv, replay.py and trace.jsonl. The loader only reads; it never changes the folder.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Files offered for download, in display order. recipe.json comes from the recipes work (item 7).
RUN_FILES = ("cleaned.csv", "replay.py", "trace.jsonl", "recipe.json")


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


def load_run(run_dir: Path) -> RunView:
    """Load a run folder. Missing pieces give None or are left out; this never raises for a bad folder."""
    run_dir = Path(run_dir)
    report_md = _read_text(run_dir / "report.md")
    files = {name: run_dir / name for name in RUN_FILES if (run_dir / name).is_file()}
    return RunView(run_dir=run_dir, report_md=report_md, changes=[], files=files)
