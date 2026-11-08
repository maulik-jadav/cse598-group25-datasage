"""Preview page: open an existing DataSage run folder in the browser, read only.

From the repository root (needs streamlit; no API key):
    streamlit run app/preview_report.py                                # the Milestone 2 demo run
    streamlit run app/preview_report.py -- --run outputs/run           # any other run folder
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# `streamlit run app/preview_report.py` puts the script's own folder (app/) on sys.path, not the
# repository root, so `import app.report_view` would fail. Add the root (the folder above app/) first.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.report_view import render_report  # noqa: E402

DEFAULT_RUN = REPO_ROOT / "docs" / "milestone2" / "demo"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview a DataSage run folder (read only).")
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN,
                        help="run folder with report.md, cleaned.csv, replay.py, trace.jsonl (default: the Milestone 2 demo)")
    # parse_known_args: ignore any arguments meant for streamlit itself instead of exiting.
    args, _unknown = parser.parse_known_args(argv)
    return args


def main(argv: list[str] | None = None) -> None:
    import streamlit as st

    args = parse_args(argv)
    st.set_page_config(page_title="DataSage run preview", layout="wide")
    st.title("DataSage run preview")
    render_report(args.run)


if __name__ == "__main__":  # streamlit runs this file as __main__
    main()
