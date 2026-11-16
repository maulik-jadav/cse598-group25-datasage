"""Stack several files with the same columns (e.g. monthly exports) into one table for a DataSage run.

Each file is read as text the way load_table reads it (separator and encoding detected, Excel sheet by
name or the first one). Columns are matched by name, ignoring case and surrounding spaces, so their order
may differ between files. A `source_file` column, first, records where every row came from, so a question
can be answered across all files or per file. The stacked table is written as one UTF-8 CSV, and the run
then works on that file exactly as on a single upload.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .session import detect_csv

SOURCE = "source_file"
MAX_FILES = 20


def _read_text(path: Path, sheet=None) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        read = detect_csv(path)
        return pd.read_csv(path, dtype=str, keep_default_na=False, sep=read["sep"], encoding=read["encoding"])
    if path.suffix.lower() == ".xlsx":
        return pd.read_excel(path, sheet_name=sheet if sheet is not None else 0, dtype=str, keep_default_na=False)
    raise ValueError(f"{path.name}: unsupported file type; use .csv or .xlsx")


def _key(name) -> str:
    return str(name).strip().lower()


def stack_files(paths: list[Path], out_path: Path, names: list[str] | None = None) -> dict:
    """Stack `paths` into one CSV at `out_path`. Raises ValueError when the files' columns do not match."""
    paths = [Path(p) for p in paths]
    names = names or [p.name for p in paths]
    if not 2 <= len(paths) <= MAX_FILES:
        raise ValueError(f"stack between 2 and {MAX_FILES} files")
    frames = [_read_text(p) for p in paths]
    first = [str(c).strip() for c in frames[0].columns]
    if SOURCE in {_key(c) for c in first}:
        raise ValueError(f"the files already have a '{SOURCE}' column")
    wanted = {_key(c): c for c in first}
    problems = []
    for name, df in zip(names, frames):
        have = {_key(c) for c in df.columns}
        missing = [wanted[k] for k in wanted if k not in have]
        extra = [str(c).strip() for c in df.columns if _key(c) not in wanted]
        if missing or extra:
            parts = ([f"missing {', '.join(missing)}"] if missing else []) + ([f"extra {', '.join(extra)}"] if extra else [])
            problems.append(f"{name}: {'; '.join(parts)}")
    if problems:
        raise ValueError(f"the files must have the same columns as {names[0]} ({', '.join(first)}). " + " | ".join(problems))
    parts = []
    for name, df in zip(names, frames):
        df = df.rename(columns={c: wanted[_key(c)] for c in df.columns})[first]
        df.insert(0, SOURCE, name)
        parts.append(df)
    stacked = pd.concat(parts, ignore_index=True)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stacked.to_csv(out_path, index=False)
    return {"files": [{"name": n, "rows": int(len(f))} for n, f in zip(names, frames)], "rows": int(len(stacked)),
            "columns": [SOURCE] + first}
