"""Tests for cleaning recipes (datasage/recipes.py). Synthetic data only; no API key or network."""

import hashlib
import json

import pandas as pd
import pytest

from datasage import recipes

MONTH1 = (
    "Order_ID,Date,Category,Quantity,Price\n"
    "1,2026-08-01,Electronics,2,$10.00\n"
    "2,2026-08-02,electronics,1,$5.00\n"
    "3,2026-08-03,Accessories,3,$7.50\n"
)
RULES = '{"Category": {"allowed": ["Electronics", "Accessories"]}}\n'


@pytest.fixture
def month1(tmp_path):
    path = tmp_path / "month1.csv"
    path.write_text(MONTH1)
    return path


@pytest.fixture
def rules(tmp_path):
    path = tmp_path / "rules" / "sales_rules.json"
    path.parent.mkdir()
    path.write_text(RULES)
    return path


def _recipe(path, rules_path=None):
    source, schema = recipes.describe_input(path)
    return recipes.Recipe(
        source=source,
        schema=schema,
        rules=recipes.rules_ref(rules_path),
        steps=[
            recipes.Step(fix="normalize_labels", args={"column": "Category", "mapping": {"electronics": "Electronics"}},
                         risk="low", approved_by="auto", portable=True),
            recipes.Step(fix="exclude_rows", args={"rows": [2]}, risk="high", approved_by="approved", portable=False),
        ],
    )


def test_save_and_load_round_trip(tmp_path, month1, rules):
    recipe = _recipe(month1, rules)
    path = recipes.save_recipe(recipe, tmp_path / "recipe.json")

    assert recipes.load_recipe(path) == recipe
    data = json.loads(path.read_text())
    assert data["recipe_version"] == 1
    assert data["source"] == {"name": "month1.csv", "sha256": hashlib.sha256(MONTH1.encode()).hexdigest(), "rows": 3}
    assert data["rules"] == {"name": "sales_rules.json", "sha256": hashlib.sha256(RULES.encode()).hexdigest()}
    assert str(tmp_path) not in path.read_text()  # file names only, no local folders
    # Schema of the raw input as load_table reads it: "$10.00" keeps Price as text.
    assert data["schema"]["columns"] == ["Order_ID", "Date", "Category", "Quantity", "Price"]
    assert data["schema"]["dtypes"] == {"Order_ID": "number", "Date": "text", "Category": "text",
                                        "Quantity": "number", "Price": "text"}


def test_recipe_without_rules_file(tmp_path, month1):
    path = recipes.save_recipe(_recipe(month1), tmp_path / "recipe.json")
    assert json.loads(path.read_text())["rules"] is None
    assert recipes.load_recipe(path).rules is None


def test_fingerprint_ignores_column_order_but_not_names_or_kinds():
    df = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    assert recipes.schema_fingerprint(df) == recipes.schema_fingerprint(df[["y", "x"]])
    assert recipes.schema_fingerprint(df) != recipes.schema_fingerprint(df.rename(columns={"x": "z"}))
    assert recipes.schema_fingerprint(df) != recipes.schema_fingerprint(df.astype({"x": str}))


def test_load_refuses_unknown_version_and_broken_files(tmp_path, month1):
    path = recipes.save_recipe(_recipe(month1), tmp_path / "recipe.json")
    data = json.loads(path.read_text())

    path.write_text(json.dumps({**data, "recipe_version": 2}))
    with pytest.raises(ValueError, match="recipe_version 2"):
        recipes.load_recipe(path)

    del data["schema"]
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="not a valid recipe"):
        recipes.load_recipe(path)
