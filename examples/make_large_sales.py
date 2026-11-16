"""Make examples/large_sales.csv: a 1,200-row synthetic sales table with planted problems, for demos.

    python examples/make_large_sales.py            # writes examples/large_sales.csv and prints the clean answer

Same columns and rules as the stakeholder's messy_sales.csv (use examples/messy_sales_rules.json).
Each kind of problem stays at 10 rows or fewer, because a check lists at most 10 row ids to the agent.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROWS = 1200
SEED = 2026
PRODUCTS = {
    "Electronics": {"Laptop": 900, "Monitor": 300, "Phone": 650, "Tablet": 420, "Headset": 80, "Webcam": 60, "Speaker": 120},
    "Accessories": {"Mouse": 25, "Keyboard": 50, "Hub": 40, "Cable": 12, "Charger": 30, "Case": 18, "Stand": 45},
}
REGIONS = ["North", "South", "East", "West"]
OUT = Path(__file__).resolve().parent / "large_sales.csv"


def clean_rows(rng: random.Random) -> list[list]:
    start = date(2026, 7, 1)
    rows = []
    for i in range(ROWS):
        category = rng.choices(list(PRODUCTS), weights=[0.45, 0.55])[0]
        product, price = rng.choice(list(PRODUCTS[category].items()))
        qty = rng.choices([1, 2, 3, 4, 5, 6, 8, 10], weights=[30, 25, 15, 10, 8, 5, 4, 3])[0]
        day = start + timedelta(days=rng.randint(0, 91))
        rows.append([10001 + i, day.isoformat(), product, category, qty, price, rng.choice(REGIONS), qty * price])
    return rows


def main() -> None:
    rng = random.Random(SEED)
    rows = clean_rows(rng)
    clean_total = {c: sum(r[7] for r in rows if r[3] == c) for c in PRODUCTS}

    # Positions for each problem, spread through the file; a few land in the first rows so they show at once.
    free = list(range(len(rows)))
    rng.shuffle(free)
    early = [2, 5, 9, 14, 21, 27]
    for e in early:
        free.remove(e)

    def take(k: int, first: int | None = None) -> list[int]:
        picked = ([first] if first is not None else []) + [free.pop() for _ in range(k - (first is not None))]
        return sorted(picked)

    messy = [list(r) for r in rows]
    # Case and space variants of the allowed labels (safe, low risk).
    for i in take(9, early[1]):
        messy[i][3] = rng.choice([messy[i][3].lower(), messy[i][3].upper(), messy[i][3] + " "])
    # Misspellings (need approval).
    for i in take(6):
        messy[i][3] = {"Electronics": "Electornics", "Accessories": "Acessories"}[messy[i][3]]
    # Unreadable dates (the question does not use dates).
    for i in take(7, early[2]):
        messy[i][1] = rng.choice(["not-a-date", "2026-02-30", "TBD"])
    # Negative quantities: rows that break the rule Quantity >= 1.
    for i in take(6, early[3]):
        messy[i][4] = -messy[i][4]
        messy[i][7] = messy[i][4] * messy[i][5]
    # Revenue that does not equal Quantity * Price.
    for i in take(5, early[4]):
        messy[i][7] = messy[i][7] * 10
    # Revenue written as text with a thousands separator.
    big = [i for i in free if rows[i][7] >= 1000][:4]
    for i in big:
        free.remove(i)
        messy[i][7] = f"{rows[i][7]:,}"
    # Blank regions (not used by the question).
    for i in take(5):
        messy[i][6] = ""
    # Exact duplicates of earlier rows, inserted right after the original.
    dup_of = sorted(take(8, early[0]), reverse=True)
    for i in dup_of:
        messy.insert(i + 1, list(messy[i]))

    with open(OUT, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Order_ID", "Date", "Product", "Category", "Quantity", "Price", "Region", "Revenue"])
        writer.writerows(messy)
    print(f"wrote {OUT.name}: {len(messy)} rows")
    print("clean answer (sum of Revenue by Category, before any rule-breaking rows are removed):", clean_total)


if __name__ == "__main__":
    main()
