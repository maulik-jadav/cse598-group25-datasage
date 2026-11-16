"""The hard split generator (eval/generate_hard.py): deterministic, same file format, and the planned difficulty."""

import difflib
import filecmp
import json
from pathlib import Path

import pandas as pd
import pytest

from datasage.analyze import answers_match, run_analysis
from datasage.values import normalize_label
from eval import generate, generate_hard
from eval.generate import reference_table
from eval.scoring import SystemOutput, load_bundle, score

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("hard")
    for kind in ("sales", "penguins"):
        generate_hard.build(kind, 10, 303, out=out)
    return out


def _tables(out: Path):
    return [f for kind in ("sales", "penguins") for f in sorted((out / f"{kind}-hard").iterdir())]


def _files(folder: Path) -> list[str]:
    return sorted(p.name for p in folder.iterdir())


def test_same_seed_gives_identical_files_and_another_seed_does_not(tmp_path):
    for name in ("a", "b", "c"):
        generate_hard.build("sales", 2, 303 if name != "c" else 304, out=tmp_path / name)
        generate_hard.build("penguins", 2, 303 if name != "c" else 304, out=tmp_path / name)
    for kind in ("sales", "penguins"):
        for table in (f"{kind}hard_00", f"{kind}hard_01"):
            a, b, c = (tmp_path / n / f"{kind}-hard" / table for n in "abc")
            match, mismatch, errors = filecmp.cmpfiles(a, b, _files(a), shallow=False)
            assert not mismatch and not errors and len(match) == 6
            assert not filecmp.cmp(a / "messy.csv", c / "messy.csv", shallow=False)


def test_regular_generator_output_is_unchanged(tmp_path, monkeypatch):
    """Adding the hard split must not change the committed dev split (seed 7)."""
    monkeypatch.setattr(generate, "OUT", tmp_path)
    generate.build("sales", 2, 7)
    for table in ("sales_00", "sales_01"):
        for name in ("messy.csv", "planted.json", "tasks.json"):
            assert (tmp_path / "sales" / table / name).read_bytes() == (REPO / "eval/datasets/sales" / table / name).read_bytes()


def test_reference_answers_come_from_the_clean_table_with_planted_handling(built):
    for folder in _tables(built):
        planted = json.loads((folder / "planted.json").read_text())
        clean = pd.read_csv(folder / "clean.csv")
        ref = reference_table(clean, planted["errors"], planted["id_column"])
        excluded = {p["id"] for p in planted["errors"] if p["resolution"] == "exclude"}
        assert len(ref) == len(clean) - len(excluded)
        for task in json.loads((folder / "tasks.json").read_text()):
            spec = task["spec"]
            again = run_analysis(ref, spec["group_by"], spec["metric"], spec["agg"], spec.get("filters"))["result"]
            assert again == task["reference_answer"]


def test_scoring_works_unchanged_and_a_perfect_cleaning_scores_full_marks(built):
    for folder in _tables(built)[::4]:
        bundle = load_bundle(folder)
        task = bundle.tasks[0]
        out = SystemOutput(answer=task["reference_answer"], cleaned=bundle.reference.copy(), issues=bundle.truth_issues)
        result = score(bundle, task, out)
        assert result["analysis_correct"] and result["detect_fn"] == 0 and result["detect_fp"] == 0
        assert result["corrections"] == result["planted"] and result["damaged_rows"] == result["damaged_cells"] == 0


def test_tables_are_big_and_questions_have_filters(built):
    sizes = {f.name: len(pd.read_csv(f / "clean.csv")) for f in _tables(built)}
    assert all(300 <= n <= 2000 for n in sizes.values())
    assert max(n for name, n in sizes.items() if name.startswith("sales")) > 1000
    tasks = [t for f in _tables(built) for t in json.loads((f / "tasks.json").read_text())]
    assert len(tasks) == 40 and len({t["task_id"] for t in tasks}) == 40
    assert sum(bool(t["spec"].get("filters")) for t in tasks) >= 10


def test_some_tables_have_more_rule_breaking_rows_than_a_check_lists(built):
    big = 0
    for folder in _tables(built):
        errors = json.loads((folder / "planted.json").read_text())["errors"]
        per_column: dict[str, int] = {}
        for p in errors:
            if p["resolution"] == "exclude":
                per_column[p["column"]] = per_column.get(p["column"], 0) + 1
        big += any(n > 10 for n in per_column.values())
    assert big >= 6


def test_several_problem_kinds_share_a_column(built):
    mixed = 0
    for folder in _tables(built):
        errors = json.loads((folder / "planted.json").read_text())["errors"]
        kinds: dict[str, set[str]] = {}
        for p in errors:
            kinds.setdefault(p["column"], set()).add(p["subtype"])
        mixed += any(len(k) >= 3 for k in kinds.values())
    assert mixed >= 15


def test_text_numbers_carry_currency_and_thousands_separators(built):
    texts = [p["messy_value"] for f in _tables(built) for p in json.loads((f / "planted.json").read_text())["errors"]
             if p["type"] == "text_number"]
    assert any("$" in t and "," in t for t in texts) and any("," in t and "$" not in t for t in texts)


def test_near_two_misspellings_are_closest_to_the_right_label(built):
    seen = 0
    for folder in _tables(built):
        rules = json.loads((folder / "rules.json").read_text())
        for p in json.loads((folder / "planted.json").read_text())["errors"]:
            if p["subtype"] != "label_typo_near_two":
                continue
            allowed = {normalize_label(a): a for a in rules[p["column"]]["allowed"]}
            match = difflib.get_close_matches(normalize_label(p["messy_value"]), list(allowed), n=2, cutoff=0.75)
            assert len(match) == 2 and allowed[match[0]] == p["clean_value"]
            seen += 1
    assert seen >= 10


def test_distractors_do_not_change_the_reference_answer(built):
    found = 0
    for folder in _tables(built):
        planted = json.loads((folder / "planted.json").read_text())
        tasks = json.loads((folder / "tasks.json").read_text())
        used = set().union(*(generate_hard.question_columns(t["spec"]) for t in tasks))
        outside = [p for p in planted["errors"] if p["column"] not in used and p["column"] != "*"]
        # The one planned exception: a negative Quantity in a Revenue table also makes Revenue negative, so the
        # row breaks a rule in the metric column and must be excluded. Everything else outside is a distractor.
        assert all(p["column"] == "Quantity" and "Revenue" in used for p in outside if p["resolution"] == "exclude")
        distractors = [p for p in outside if p["resolution"] != "exclude"]
        found += len(distractors)
        assert all(p["resolution"] in ("restore", "set_missing", "keep_missing") for p in distractors)
        clean = pd.read_csv(folder / "clean.csv")
        ref = reference_table(clean, [p for p in planted["errors"] if p not in distractors], planted["id_column"])
        for task in tasks:
            spec = task["spec"]
            answer = run_analysis(ref, spec["group_by"], spec["metric"], spec["agg"], spec.get("filters"))["result"]
            assert answers_match(answer, task["reference_answer"])
    assert found >= 100
