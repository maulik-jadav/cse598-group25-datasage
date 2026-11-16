"""Build the hard split: bigger tables with more, mixed and harder planted errors.

The regular benchmark (eval/generate.py) has 40 to 70 rows per table and a handful of errors. The hard
split keeps the same file format (messy.csv, clean.csv, reference.csv, planted.json, rules.json,
tasks.json), so eval/scoring.py, eval/oracle.py and eval/run_eval.py work unchanged, but each table has:

- 300 to 2,000 rows (sales) or 300 to 1,200 rows (penguins, resampled from the real data with small jitter);
- in most tables with a numeric question, 12 to 40 rows that break a range rule in the metric column, more
  than the 10 row ids a check lists, so exclude_where (or another column-wide fix) is needed;
- several problem kinds in the same column (case, space and spelling variants together; text numbers and
  rule breaks together; two kinds of out-of-range values in one column);
- distractors: problems in columns neither question uses. Their correct handling never removes a row, so
  they do not change the reference answer, but they still count as planted errors;
- numbers written as text with currency signs and thousands separators ("$2,400.00", "4,250");
- misspellings that are close to two allowed labels (for example "Northest" is near both "Northeast" and
  "North"); the closest allowed label is always the right one;
- questions with filters (for example "... for Electronics").

The two questions of a table share their metric, so a row that must be excluded matters for both. (In a
Revenue table the rule breaks are negative quantities; Revenue is negative on those rows too, so they show
up in the metric column even though the rule belongs to Quantity.) Reference
answers are computed on the reference table (the clean table with each planted error's correct handling
applied) with the same analysis function every system uses.

Usage: python -m eval.generate_hard --tables 10 --seed 303
       (writes eval/datasets/sales-hard and eval/datasets/penguins-hard)
"""

from __future__ import annotations

import argparse
import difflib
import json
import random
from pathlib import Path

import pandas as pd

from datasage.analyze import run_analysis
from datasage.values import normalize_label
from eval.generate import PENGUIN_RULES, reference_table

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "datasets"

HARD_CATALOG = {
    "Electronics": {"Laptop": 900, "Workstation": 2400, "Monitor": 300, "Projector": 1150, "Headset": 80},
    "Electricals": {"Extension Cord": 18, "Surge Protector": 35, "Power Strip": 25, "Generator": 1450},
    "Accessories": {"Mouse": 25, "Keyboard": 50, "Hub": 40, "Cable": 15},
    "Furniture": {"Desk": 350, "Standing Desk": 1250, "Chair": 180, "Lamp": 45},
    "Office Supplies": {"Notebook": 6, "Pen Pack": 12, "Stapler": 18},
    "Outdoor Supplies": {"Tent": 220, "Cooler": 95, "Grill": 1100},
}
HARD_REGIONS = ["North", "South", "East", "West", "Northeast", "Southeast"]
BAD_DATES = ["not-a-date", "2026-02-30", "13/45/2026", "TBD", "2026-14-01", "2026-06-31", "06/15/2026"]

SALES_HARD_RULES = {
    "Order_ID": "unique order number",
    "Date": {"format": "YYYY-MM-DD"},
    "Category": {"allowed": list(HARD_CATALOG)},
    "Region": {"allowed": HARD_REGIONS},
    "Quantity": {"min": 1, "note": "units sold; always a positive whole number"},
    "Price": {"min": 0, "note": "unit price in dollars"},
    "Revenue": {"formula": "Revenue = Quantity * Price"},
}


def _q(question, group_by, metric, agg, filters=None):
    spec = {"group_by": group_by, "metric": metric, "agg": agg}
    if filters:
        spec["filters"] = [{"column": c, "value": v} for c, v in filters]
    return question, spec


# Question groups. A table takes two questions from one group, so both share the metric column.
SALES_GROUPS = {
    "Revenue": [
        _q("What is the total revenue by category?", ["Category"], "Revenue", "sum"),
        _q("What is the total revenue by region for Electronics?", ["Region"], "Revenue", "sum", [("Category", "Electronics")]),
        _q("What is the total revenue per month in the North region?", ["Date:month"], "Revenue", "sum", [("Region", "North")]),
        _q("What is the average revenue per order in each category for the West region?", ["Category"], "Revenue", "mean",
           [("Region", "West")]),
    ],
    "Quantity": [
        _q("How many units were sold in each region?", ["Region"], "Quantity", "sum"),
        _q("How many units were sold in each category in the South region?", ["Category"], "Quantity", "sum", [("Region", "South")]),
        _q("What is the average quantity per order in each region for Furniture?", ["Region"], "Quantity", "mean",
           [("Category", "Furniture")]),
    ],
    "Price": [
        _q("What is the average unit price in each category?", ["Category"], "Price", "mean"),
        _q("What is the median unit price in each region for Electronics?", ["Region"], "Price", "median", [("Category", "Electronics")]),
        _q("What is the highest unit price in each category in the East region?", ["Category"], "Price", "max", [("Region", "East")]),
    ],
    "count": [
        _q("How many orders are there in each category in the East region?", ["Category"], None, "count", [("Region", "East")]),
        _q("How many orders are there in each region?", ["Region"], None, "count"),
        _q("How many orders are there in each category?", ["Category"], None, "count"),
    ],
}
PENGUIN_GROUPS = {
    "body_mass_g": [
        _q("What is the average body mass for each species?", ["species"], "body_mass_g", "mean"),
        _q("What is the average body mass for each sex among Gentoo penguins?", ["sex"], "body_mass_g", "mean", [("species", "Gentoo")]),
        _q("What is the total body mass by island for Adelie penguins?", ["island"], "body_mass_g", "sum", [("species", "Adelie")]),
        _q("What is the median body mass for each species?", ["species"], "body_mass_g", "median"),
    ],
    "flipper_length_mm": [
        _q("What is the average flipper length for each species?", ["species"], "flipper_length_mm", "mean"),
        _q("What is the average flipper length by island for Adelie penguins?", ["island"], "flipper_length_mm", "mean",
           [("species", "Adelie")]),
        _q("What is the longest flipper length for each sex?", ["sex"], "flipper_length_mm", "max"),
    ],
    "bill_length_mm": [
        _q("What is the average bill length by island for Adelie penguins?", ["island"], "bill_length_mm", "mean",
           [("species", "Adelie")]),
        _q("What is the average bill length for each species?", ["species"], "bill_length_mm", "mean"),
        _q("What is the average bill length for each sex on Biscoe island?", ["sex"], "bill_length_mm", "mean", [("island", "Biscoe")]),
    ],
    "count": [
        _q("How many penguins were measured on each island?", ["island"], None, "count"),
        _q("How many penguins of each species were measured on Biscoe island?", ["species"], None, "count", [("island", "Biscoe")]),
        _q("How many penguins of each sex are there among Chinstrap penguins?", ["sex"], None, "count", [("species", "Chinstrap")]),
    ],
}

SALES_LABELS = {"Category": list(HARD_CATALOG), "Region": HARD_REGIONS}
PENGUIN_LABELS = {k: v["allowed"] for k, v in PENGUIN_RULES.items() if isinstance(v, dict) and "allowed" in v}


def question_columns(spec: dict) -> set[str]:
    cols = {g.split(":")[0] for g in spec["group_by"]} | {f["column"] for f in spec.get("filters", [])}
    return cols | ({spec["metric"]} if spec.get("metric") else set())


# ---------------------------------------------------------------- clean tables

def clean_sales_hard(rng: random.Random, n: int) -> pd.DataFrame:
    rows = []
    for i in range(n):
        category = rng.choice(list(HARD_CATALOG))
        product, price = rng.choice(list(HARD_CATALOG[category].items()))
        qty = rng.randint(1, 8)
        rows.append({"Order_ID": 30001 + i, "Date": f"2026-{rng.randint(1, 6):02d}-{rng.randint(1, 28):02d}",
                     "Product": product, "Category": category, "Quantity": qty, "Price": price,
                     "Region": rng.choice(HARD_REGIONS), "Revenue": qty * price})
    return pd.DataFrame(rows)


def clean_penguins_hard(rng: random.Random, n: int) -> pd.DataFrame:
    """Resample the real penguins (with replacement) and jitter the measurements a little, inside the rules."""
    source = pd.read_csv(ROOT / "sources" / "penguins.csv").dropna().reset_index(drop=True)
    rows = []
    for i in range(n):
        r = source.iloc[rng.randrange(len(source))]
        rows.append({
            "penguin_id": f"Q{i:05d}",
            "species": r["species"], "island": r["island"],
            "bill_length_mm": round(min(59.5, max(30.5, float(r["bill_length_mm"]) + rng.uniform(-0.6, 0.6))), 1),
            "bill_depth_mm": round(float(r["bill_depth_mm"]) + rng.uniform(-0.3, 0.3), 1),
            "flipper_length_mm": int(min(233, max(172, int(r["flipper_length_mm"]) + rng.randint(-3, 3)))),
            "body_mass_g": int(min(6400, max(2600, int(r["body_mass_g"]) + 25 * rng.randint(-4, 4)))),
            "sex": r["sex"], "year": int(r["year"]),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- label variants

_TYPO_CACHE: dict[tuple[str, tuple[str, ...]], tuple[list[str], list[str]]] = {}


def _ratio(possibility: str, word: str) -> float:
    # Same orientation as difflib.get_close_matches (seq1 = possibility, seq2 = word).
    return difflib.SequenceMatcher(None, possibility, word).ratio()


def typo_candidates(label: str, allowed: list[str]) -> tuple[list[str], list[str]]:
    """Misspellings of `label` whose closest allowed label is `label`.

    Returns (near_two, near_one): near_two are also within the 0.75 cutoff of a second allowed label
    (but strictly further from it), near_one are close to `label` only.
    """
    key = (label, tuple(allowed))
    if key in _TYPO_CACHE:
        return _TYPO_CACHE[key]
    norm = {normalize_label(a): a for a in allowed}
    cands = set()
    for i in range(len(label)):
        cands.add(label[:i] + label[i + 1:])  # drop a letter
        cands.add(label[:i] + label[i] + label[i:])  # double a letter
        if i < len(label) - 1:
            cands.add(label[:i] + label[i + 1] + label[i] + label[i + 2:])  # swap two letters
    near_two, near_one = [], []
    for c in sorted(cands):
        n = normalize_label(c)
        if not c.strip() or c != c.strip() or n in norm or "  " in c:
            continue
        match = difflib.get_close_matches(n, list(norm), n=2, cutoff=0.75)
        if not match or norm[match[0]] != label:
            continue
        if len(match) == 2:
            if _ratio(match[0], n) > _ratio(match[1], n):
                near_two.append(c)
        else:
            near_one.append(c)
    _TYPO_CACHE[key] = (near_two, near_one)
    return near_two, near_one


def label_variant(rng: random.Random, value: str, kind: str, allowed: list[str]) -> tuple[str, str] | None:
    """A messy form of `value` and its subtype, or None if no such form exists."""
    if kind == "label_case":
        forms = [value.lower(), value.upper(), value.swapcase()]
        forms = [f for f in forms if f != value]
        return rng.choice(forms), kind
    if kind == "label_space":
        return rng.choice([value + " ", " " + value, "  " + value + " "]), kind
    near_two, near_one = typo_candidates(value, allowed)
    if near_two and (rng.random() < 0.7 or not near_one):
        return rng.choice(near_two), "label_typo_near_two"
    if near_one:
        return rng.choice(near_one), "label_typo"
    return None


# ---------------------------------------------------------------- planting

class Planter:
    def __init__(self, rng: random.Random, clean: pd.DataFrame, id_col: str):
        self.rng, self.clean, self.id_col = rng, clean, id_col
        self.messy = clean.astype(object).copy()
        self.planted: list[dict] = []
        self.used: set[int] = set()
        self.free = list(range(len(clean)))

    def rows(self, k: int, where=None) -> list[int]:
        pool = [i for i in self.free if i not in self.used and (where is None or where(i))]
        pick = self.rng.sample(pool, min(k, len(pool)))
        self.used.update(pick)
        return sorted(pick)

    def add(self, type_: str, column: str, i: int, resolution: str, clean_value, messy_value, subtype=None):
        self.planted.append({"type": type_, "subtype": subtype or type_, "column": column,
                             "id": str(self.clean.at[i, self.id_col]), "resolution": resolution,
                             "clean_value": clean_value, "messy_value": messy_value})

    def labels(self, column: str, allowed: list[str], kinds: list[str], low: int, high: int) -> None:
        for kind in kinds:
            for i in self.rows(self.rng.randint(low, high)):
                value = str(self.clean.at[i, column])
                made = label_variant(self.rng, value, kind, allowed)
                if made is None:
                    self.used.discard(i)
                    continue
                new, subtype = made
                self.messy.at[i, column] = new
                self.add("label_variant", column, i, "restore", value, new, subtype=subtype)

    def text_numbers(self, column: str, k: int, formats, big: float | None = None) -> None:
        """Numbers written as text; about half are picked from values >= `big` so they carry a thousands separator."""
        half = k // 2 if big is not None else 0
        picks = self.rows(half, lambda i: float(self.clean.at[i, column]) >= big) if half else []
        picks += self.rows(k - len(picks))
        for i in sorted(picks):
            value = self.clean.at[i, column]
            new = self.rng.choice(formats)(value)
            self.messy.at[i, column] = new
            self.add("text_number", column, i, "restore", float(value), new)

    def missing(self, column: str, k: int) -> None:
        for i in self.rows(k):
            self.add("missing", column, i, "keep_missing", None, "")
            self.messy.at[i, column] = ""

    def duplicates(self, k: int) -> None:
        order = list(range(len(self.messy)))
        for i in self.rows(k):
            pos = self.rng.randint(order.index(i) + 1, len(order))
            order.insert(pos, i)
            self.add("duplicates", "*", i, "drop_copy", None, None)
        self.messy = self.messy.iloc[order].reset_index(drop=True)


def _money(v):
    return f"${float(v):,.2f}"


def _money_space(v):
    return f"$ {float(v):,.2f}"


def _thousands(v):
    return f"{int(v):,}" if float(v).is_integer() else f"{float(v):,.2f}"


def _thousands_dec(v):
    return f"{float(v):,.1f}"


def range_count(rng: random.Random, mass: bool) -> int:
    return rng.randint(12, 40) if mass else rng.randint(2, 6)


def plant_sales(rng: random.Random, clean: pd.DataFrame, group: str, specs: list[dict], mass: bool) -> tuple[pd.DataFrame, list[dict]]:
    p = Planter(rng, clean, "Order_ID")
    used_cols = set().union(*(question_columns(s) for s in specs))
    date_used = any("Date:month" in s["group_by"] for s in specs)

    # 1. Rule breaks in the metric column (rows to exclude), two kinds where the rules allow it.
    if group == "Revenue":
        for i in p.rows(range_count(rng, mass)):  # negative quantity, so Revenue is negative too
            p.messy.at[i, "Quantity"] = -clean.at[i, "Quantity"]
            p.messy.at[i, "Revenue"] = -clean.at[i, "Revenue"]
            p.add("negative", "Quantity", i, "exclude", float(clean.at[i, "Quantity"]), float(p.messy.at[i, "Quantity"]))
        p.text_numbers("Revenue", rng.randint(6, 25), [_money, _thousands, _money_space], big=1000)
        for i in p.rows(rng.randint(2, 5)):
            wrong = clean.at[i, "Revenue"] * rng.choice([10, 100]) + rng.choice([0, 5])
            p.messy.at[i, "Revenue"] = wrong
            p.add("cross_column", "Revenue", i, "restore", float(clean.at[i, "Revenue"]), float(wrong))
    elif group == "Quantity":
        total = range_count(rng, mass)
        zeros = total // 3
        for i in p.rows(total - zeros):
            p.messy.at[i, "Quantity"] = -clean.at[i, "Quantity"]
            p.messy.at[i, "Revenue"] = -clean.at[i, "Revenue"]
            p.add("negative", "Quantity", i, "exclude", float(clean.at[i, "Quantity"]), float(p.messy.at[i, "Quantity"]))
        for i in p.rows(zeros):
            p.messy.at[i, "Quantity"] = 0
            p.messy.at[i, "Revenue"] = 0
            p.add("out_of_range", "Quantity", i, "exclude", float(clean.at[i, "Quantity"]), 0.0)
    elif group == "Price":
        for i in p.rows(range_count(rng, mass)):
            p.messy.at[i, "Price"] = -clean.at[i, "Price"]
            p.messy.at[i, "Revenue"] = -clean.at[i, "Revenue"]
            p.add("negative", "Price", i, "exclude", float(clean.at[i, "Price"]), float(p.messy.at[i, "Price"]))
        p.text_numbers("Price", rng.randint(6, 25), [_money, _thousands, _money_space], big=1000)

    # 2. Several kinds of label problems in each label column the questions use.
    for column in ("Category", "Region"):
        if column in used_cols:
            kinds = rng.sample(["label_case", "label_space", "label_typo"], rng.randint(2, 3))
            if "label_typo" not in kinds and rng.random() < 0.6:
                kinds.append("label_typo")
            p.labels(column, SALES_LABELS[column], kinds, 2, 8)
    if "Region" in used_cols and rng.random() < 0.6:
        p.missing("Region", rng.randint(2, 5))
    if date_used:
        for i in p.rows(rng.randint(3, 8)):
            new = rng.choice(BAD_DATES)
            p.add("invalid_date", "Date", i, "set_missing", clean.at[i, "Date"], new)
            p.messy.at[i, "Date"] = new

    # 3. Distractors: problems in columns no question uses; none of them removes a row.
    options = []
    if not date_used:
        options.append("dates")
    options += [f"labels:{c}" for c in ("Category", "Region") if c not in used_cols]
    if "Price" not in used_cols:
        options.append("price_text")
    if "Revenue" not in used_cols:
        options.append("revenue_cross")
    if "Region" not in used_cols:
        options.append("region_missing")
    for option in rng.sample(options, min(len(options), rng.randint(2, 3))):
        if option == "dates":
            for i in p.rows(rng.randint(3, 10)):
                new = rng.choice(BAD_DATES)
                p.add("invalid_date", "Date", i, "set_missing", clean.at[i, "Date"], new)
                p.messy.at[i, "Date"] = new
        elif option.startswith("labels:"):
            column = option.split(":")[1]
            p.labels(column, SALES_LABELS[column], ["label_case", "label_typo"], 2, 6)
        elif option == "price_text":
            p.text_numbers("Price", rng.randint(4, 12), [_money, _thousands], big=1000)
        elif option == "revenue_cross":
            for i in p.rows(rng.randint(2, 4)):
                wrong = clean.at[i, "Revenue"] * 10
                p.messy.at[i, "Revenue"] = wrong
                p.add("cross_column", "Revenue", i, "restore", float(clean.at[i, "Revenue"]), float(wrong))
        elif option == "region_missing":
            p.missing("Region", rng.randint(2, 5))

    p.duplicates(rng.randint(2, 6))
    return p.messy, p.planted


def plant_penguins(rng: random.Random, clean: pd.DataFrame, group: str, specs: list[dict], mass: bool) -> tuple[pd.DataFrame, list[dict]]:
    p = Planter(rng, clean, "penguin_id")
    used_cols = set().union(*(question_columns(s) for s in specs))

    # 1. Rule breaks in the metric column, two kinds mixed in one column.
    total = range_count(rng, mass)
    low = total // 3
    if group == "body_mass_g":
        for i in p.rows(total - low):  # recorded in milligrams
            p.messy.at[i, "body_mass_g"] = int(clean.at[i, "body_mass_g"]) * 1000
            p.add("out_of_range", "body_mass_g", i, "exclude", float(clean.at[i, "body_mass_g"]), float(p.messy.at[i, "body_mass_g"]))
        for i in p.rows(low):  # recorded in kilograms
            p.messy.at[i, "body_mass_g"] = round(int(clean.at[i, "body_mass_g"]) / 1000, 3)
            p.add("out_of_range", "body_mass_g", i, "exclude", float(clean.at[i, "body_mass_g"]), float(p.messy.at[i, "body_mass_g"]))
        p.text_numbers("body_mass_g", rng.randint(6, 25), [_thousands, _thousands_dec])
    elif group == "flipper_length_mm":
        for i in p.rows(total - low):
            p.messy.at[i, "flipper_length_mm"] = -int(clean.at[i, "flipper_length_mm"])
            p.add("negative", "flipper_length_mm", i, "exclude", float(clean.at[i, "flipper_length_mm"]),
                  float(p.messy.at[i, "flipper_length_mm"]))
        for i in p.rows(low):  # recorded in tenths of a millimetre
            p.messy.at[i, "flipper_length_mm"] = int(clean.at[i, "flipper_length_mm"]) * 10
            p.add("out_of_range", "flipper_length_mm", i, "exclude", float(clean.at[i, "flipper_length_mm"]),
                  float(p.messy.at[i, "flipper_length_mm"]))
    elif group == "bill_length_mm":
        for i in p.rows(total - low):
            p.messy.at[i, "bill_length_mm"] = round(float(clean.at[i, "bill_length_mm"]) * 10, 1)
            p.add("out_of_range", "bill_length_mm", i, "exclude", float(clean.at[i, "bill_length_mm"]),
                  float(p.messy.at[i, "bill_length_mm"]))
        for i in p.rows(low):
            p.messy.at[i, "bill_length_mm"] = -float(clean.at[i, "bill_length_mm"])
            p.add("negative", "bill_length_mm", i, "exclude", float(clean.at[i, "bill_length_mm"]),
                  float(p.messy.at[i, "bill_length_mm"]))

    # 2. Several kinds of label problems in each label column the questions use.
    for column in ("species", "island", "sex"):
        if column in used_cols:
            kinds = rng.sample(["label_case", "label_space", "label_typo"], rng.randint(2, 3))
            if column == "sex" and "label_typo" not in kinds:
                kinds.append("label_typo")  # sex typos ("femle") are close to both labels
            p.labels(column, PENGUIN_LABELS[column], kinds, 2, 8)
    if "sex" in used_cols:
        p.missing("sex", rng.randint(2, 6))

    # 3. Distractors in columns no question uses; none of them removes a row.
    options = [f"labels:{c}" for c in ("species", "island", "sex") if c not in used_cols]
    if "body_mass_g" not in used_cols:
        options.append("mass_text")
    if "sex" not in used_cols:
        options.append("sex_missing")
    for option in rng.sample(options, min(len(options), rng.randint(2, 3))):
        if option.startswith("labels:"):
            column = option.split(":")[1]
            p.labels(column, PENGUIN_LABELS[column], ["label_case", "label_typo"], 2, 6)
        elif option == "mass_text":
            p.text_numbers("body_mass_g", rng.randint(4, 12), [_thousands, _thousands_dec])
        elif option == "sex_missing":
            p.missing("sex", rng.randint(2, 6))

    p.duplicates(rng.randint(2, 6))
    return p.messy, p.planted


# ---------------------------------------------------------------- build

def build(kind: str, tables: int, seed: int, split: str = "hard", out: Path = OUT) -> int:
    rng = random.Random(f"{kind}-{split}-{seed}")
    name = f"{kind}{split}"  # table folders like saleshard_00
    id_col = "Order_ID" if kind == "sales" else "penguin_id"
    rules = SALES_HARD_RULES if kind == "sales" else PENGUIN_RULES
    groups = SALES_GROUPS if kind == "sales" else PENGUIN_GROUPS
    order = list(groups)
    count = 0
    for t in range(tables):
        group = order[t % len(order)]
        pair = rng.sample(groups[group], 2)
        specs = [spec for _, spec in pair]
        mass = group != "count" and rng.random() < 0.7
        if kind == "sales":
            clean = clean_sales_hard(rng, rng.randint(300, 2000))
            messy, planted = plant_sales(rng, clean, group, specs, mass)
        else:
            clean = clean_penguins_hard(rng, rng.randint(300, 1200))
            messy, planted = plant_penguins(rng, clean, group, specs, mass)
        ref = reference_table(clean, planted, id_col)
        folder = out / f"{kind}-{split}" / f"{name}_{t:02d}"
        folder.mkdir(parents=True, exist_ok=True)
        messy.to_csv(folder / "messy.csv", index=False)
        clean.to_csv(folder / "clean.csv", index=False)
        ref.to_csv(folder / "reference.csv", index=False)
        (folder / "rules.json").write_text(json.dumps(rules, indent=2))
        (folder / "planted.json").write_text(json.dumps({"id_column": id_col, "errors": planted}, indent=2, default=str))
        tasks = []
        for j, (question, spec) in enumerate(pair):
            answer = run_analysis(ref, spec["group_by"], spec["metric"], spec["agg"], spec.get("filters"))["result"]
            tasks.append({"task_id": f"{name}_{t:02d}_q{j}", "question": question, "spec": spec, "reference_answer": answer})
            count += 1
        (folder / "tasks.json").write_text(json.dumps(tasks, indent=2))
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tables", type=int, default=10)
    parser.add_argument("--seed", type=int, default=303)
    parser.add_argument("--split", default="hard", help="writes datasets/<kind>-<split>, e.g. sales-hard")
    args = parser.parse_args()
    for kind in ("sales", "penguins"):
        n = build(kind, args.tables, args.seed, args.split)
        print(f"{kind}: {args.tables} tables, {n} tasks -> {OUT / f'{kind}-{args.split}'}")


if __name__ == "__main__":
    main()
