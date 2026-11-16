"""Make the extra demo tables in examples/demo/ (synthetic, seeded, no real people):

    python examples/make_demo_files.py

- hr_employees.csv + hr_rules.json        "What is the average salary by department?"
- inventory.csv + inventory_rules.json    "What is the total stock value by warehouse?"
- monthly/orders_2026-07.csv, -08, -09     large_sales.csv split into three monthly exports, for the
                                           browser app's "several files with the same columns" mode

Each kind of planted problem stays at 10 rows or fewer, except where a range rule is broken on purpose
by more rows than a check lists (inventory Units), to show exclude_where. The script prints the answer
on the clean data, which is what DataSage should return when every fix is approved.
"""

from __future__ import annotations

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "demo"


def _write(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def _spread(rng: random.Random, n: int, k: int, taken: set) -> list[int]:
    picks = []
    while len(picks) < k:
        i = rng.randrange(n)
        if i not in taken:
            taken.add(i)
            picks.append(i)
    return sorted(picks)


def hr(rng: random.Random) -> dict:
    depts = {"Engineering": (95000, 160000), "Sales": (55000, 110000), "Finance": (70000, 130000),
             "Operations": (45000, 85000), "Marketing": (60000, 115000)}
    rows = []
    for i in range(400):
        dept = rng.choices(list(depts), weights=[30, 25, 15, 20, 10])[0]
        lo, hi = depts[dept]
        hired = date(2015, 1, 1) + timedelta(days=rng.randint(0, 3900))
        rows.append([f"E{1000 + i}", dept, hired.isoformat(), rng.randrange(lo, hi, 500),
                     rng.choice(["North", "South", "East", "West"]), rng.choice(["Full-time"] * 4 + ["Part-time"])])
    clean = {d: round(sum(r[3] for r in rows if r[1] == d) / sum(1 for r in rows if r[1] == d), 2) for d in depts}
    messy, taken = [list(r) for r in rows], set()
    for i in _spread(rng, 400, 9, taken):                       # case and space variants
        messy[i][1] = rng.choice([messy[i][1].lower(), messy[i][1].upper(), " " + messy[i][1]])
    for i in _spread(rng, 400, 5, taken):                       # misspellings
        messy[i][1] = {"Engineering": "Enginering", "Sales": "Saels", "Finance": "Finanse",
                       "Operations": "Operatons", "Marketing": "Marketting"}[messy[i][1]]
    for i in _spread(rng, 400, 6, taken):                       # salaries typed as text
        messy[i][3] = f"${messy[i][3]:,}"
    for i in _spread(rng, 400, 4, taken):                       # an extra zero: breaks the salary range
        messy[i][3] = messy[i][3] * 10 if isinstance(messy[i][3], int) else messy[i][3]
    for i in _spread(rng, 400, 6, taken):                       # unreadable hire dates (not used by the question)
        messy[i][2] = rng.choice(["unknown", "2019-02-30", "n.d."])
    for i in sorted(_spread(rng, 400, 7, taken), reverse=True):  # duplicate rows
        messy.insert(i + 1, list(messy[i]))
    _write(OUT / "hr_employees.csv", ["Employee_ID", "Department", "Hire_Date", "Salary", "Region", "Contract"], messy)
    rules = {"Employee_ID": "unique id", "Department": {"allowed": list(depts)},
             "Hire_Date": {"format": "YYYY-MM-DD"}, "Salary": {"min": 30000, "max": 400000, "note": "yearly, in dollars"}}
    (OUT / "hr_rules.json").write_text(json.dumps(rules, indent=2) + "\n")
    # Rows whose salary got an extra zero break the range rule; the right answer drops them.
    bad = {r[0] for r in messy if isinstance(r[3], int) and r[3] > 400000}
    kept = [r for r in rows if r[0] not in bad]
    after = {d: round(sum(r[3] for r in kept if r[1] == d) / sum(1 for r in kept if r[1] == d), 2) for d in depts}
    return {"file": "hr_employees.csv", "rows": len(messy), "question": "What is the average salary by department?",
            "answer_if_every_fix_is_approved": after, "clean_answer_before_dropping_rule_breakers": clean}


def inventory(rng: random.Random) -> dict:
    products = {"Bolt": 0.4, "Bracket": 3.5, "Cable": 6.0, "Drill": 89.0, "Glove": 4.25, "Ladder": 120.0,
                "Paint": 18.5, "Saw": 42.0, "Tape": 2.75, "Valve": 15.0}
    houses = ["Phoenix", "Tempe", "Mesa", "Tucson"]
    rows = []
    for i in range(600):
        prod, cost = rng.choice(list(products.items()))
        units = rng.randint(1, 400)
        rows.append([f"SKU-{2000 + i}", rng.choice(houses), prod, units, cost, round(units * cost, 2)])
    messy, taken = [list(r) for r in rows], set()
    for i in _spread(rng, 600, 8, taken):                       # warehouse variants
        messy[i][1] = rng.choice([messy[i][1].lower(), messy[i][1] + " ", messy[i][1].upper()])
    for i in _spread(rng, 600, 4, taken):
        messy[i][1] = {"Phoenix": "Pheonix", "Tempe": "Tempee", "Mesa": "Meza", "Tucson": "Tuscon"}[messy[i][1]]
    negative = _spread(rng, 600, 18, taken)                     # 18 > 10: needs exclude_where, not row ids
    for i in negative:
        messy[i][3] = -messy[i][3]
        messy[i][5] = round(messy[i][3] * messy[i][4], 2)
    for i in _spread(rng, 600, 5, taken):                       # stock value that does not match units x cost
        messy[i][5] = round(messy[i][5] * 100, 2)
    for i in sorted(_spread(rng, 600, 6, taken), reverse=True):
        messy.insert(i + 1, list(messy[i]))
    _write(OUT / "inventory.csv", ["SKU", "Warehouse", "Product", "Units", "Unit_Cost", "Stock_Value"], messy)
    rules = {"SKU": "unique id", "Warehouse": {"allowed": houses}, "Units": {"min": 0, "note": "units on hand"},
             "Stock_Value": {"formula": "Stock_Value = Units * Unit_Cost"}}
    (OUT / "inventory_rules.json").write_text(json.dumps(rules, indent=2) + "\n")
    bad = {rows[i][0] for i in negative}
    after = {h: round(sum(r[5] for r in rows if r[1] == h and r[0] not in bad), 2) for h in houses}
    return {"file": "inventory.csv", "rows": len(messy), "question": "What is the total stock value by warehouse?",
            "answer_if_every_fix_is_approved": after}


def monthly() -> dict:
    with open(HERE / "large_sales.csv", newline="") as fh:
        reader = csv.reader(fh)
        header, rows = next(reader), list(reader)
    months: dict[str, list] = {"2026-07": [], "2026-08": [], "2026-09": []}
    last = "2026-07"
    for r in rows:
        m = r[1][:7] if r[1][:7] in months else last   # an unreadable date stays with the rows around it
        months[m].append(r)
        last = m
    for m, part in months.items():
        _write(OUT / "monthly" / f"orders_{m}.csv", header, part)
    return {"files": [f"monthly/orders_{m}.csv" for m in months], "rows": {m: len(p) for m, p in months.items()},
            "note": "together they are large_sales.csv; use examples/messy_sales_rules.json"}


def main() -> None:
    rng = random.Random(598)
    out = {"hr": hr(rng), "inventory": inventory(rng), "monthly": monthly()}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
