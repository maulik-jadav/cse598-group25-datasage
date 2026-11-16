"""Robust loading: CSV separators and encodings, Excel sheets, and a replay script that reads the file the same way."""

import pandas as pd

from datasage.report import _read_line
from datasage.session import Session, detect_csv, excel_sheets, load_table


def test_semicolon_tab_and_pipe_csv(tmp_path):
    for sep in (";", "\t", "|"):
        f = tmp_path / "t.csv"
        f.write_text(f"Name{sep}Amount\nAnn{sep}10\nBo{sep}20\n")
        df = load_table(f)
        assert list(df.columns) == ["Name", "Amount"] and df["Amount"].tolist() == [10, 20]
        assert df.attrs["read"]["sep"] == sep


def test_comma_inside_quotes_is_not_a_separator(tmp_path):
    f = tmp_path / "t.csv"
    f.write_text('City,Note\nParis,"a; b; c"\nRome,"d; e"\n')
    assert list(load_table(f).columns) == ["City", "Note"]


def test_windows_1252_file_loads(tmp_path):
    f = tmp_path / "t.csv"
    f.write_bytes("name,city\nJosé,München\n".encode("cp1252"))
    df = load_table(f)
    assert df.iloc[0].tolist() == ["José", "München"] and detect_csv(f)["encoding"] == "cp1252"


def test_utf8_with_bom(tmp_path):
    f = tmp_path / "t.csv"
    f.write_bytes("﻿Name,Qty\nA,1\n".encode("utf-8"))
    assert list(load_table(f).columns) == ["Name", "Qty"]


def test_excel_sheet_choice_and_replay_line(tmp_path):
    f = tmp_path / "book.xlsx"
    with pd.ExcelWriter(f) as w:
        pd.DataFrame({"A": [1]}).to_excel(w, sheet_name="Notes", index=False)
        pd.DataFrame({"Region": ["West"], "Sales": [5]}).to_excel(w, sheet_name="Q3", index=False)
    assert excel_sheets(f) == ["Notes", "Q3"]
    assert list(load_table(f).columns) == ["A"]  # first sheet by default
    df = load_table(f, sheet="Q3")
    assert list(df.columns) == ["Region", "Sales"]
    line = _read_line(Session(df, source=str(f), request="q"))
    assert "read_excel" in line and "sheet_name='Q3'" in line


def test_replay_reads_a_semicolon_latin1_csv_the_same_way(tmp_path):
    f = tmp_path / "t.csv"
    f.write_bytes("Ville;Montant\nSão Paulo;5\n".encode("latin-1"))
    df = load_table(f)
    line = _read_line(Session(df, source=str(f), request="q"))
    assert "sep=';'" in line and "encoding=" in line
    namespace = {"pd": pd}
    exec(line, namespace)
    assert list(namespace["df"].columns) == ["Ville", "Montant"]
