# DataSage report

- Input: `baseline/examples/messy_sales.csv`
- Question: What was total revenue by category?
- Model: `qwen3-30b-a3b-instruct-2507`; stop reason: `finish`; tool calls: 14; approvals asked: 3; time: 13.07s

## Problems found

| Type | Column | Count | Rows (first 10) |
|---|---|---:|---|
| duplicates | * | 1 | [4] |
| label_variant | Category | 2 | [1, 7] |
| negative | Quantity | 1 | [6] |
| out_of_range | Quantity | 1 | [6] |
| negative | Revenue | 1 | [6] |
| invalid_date | Date | 1 | [5] |

## Changes

| Version | Fix | Risk | Approval | What changed | Reason |
|---|---|---|---|---|---|
| v1 | drop_duplicates | medium | approved | removed 1 exact duplicate row(s) | Found one exact duplicate row (row 4), which is a copy of row 3. Keeping only the first occurrence. |
| v2 | normalize_labels | low | auto | Category: merged 2 label variant(s), 2 cells | Merge case and space variants into the allowed labels: 'electronics' → 'Electronics', 'accessories' → 'Accessories'. |
| - | exclude_rows | high | rejected | excluded 1 row(s): [6] (not applied) | Quantity = -1 is invalid (must be ≥ 1 per rules). This row has negative quantity and invalid revenue. |
| - | set_missing | high | rejected | Date: set 1 value(s) to missing (not applied) | Value 'not-a-date' is not a valid YYYY-MM-DD date. |

## Answer

sum of `Revenue` by ['Category'] (rows used: 7, version v2)

| Group | Value |
|---|---:|
| Accessories | 830.00 |
| Electronics | 2,185.00 |

## Summary

Found and fixed the following issues: 1 duplicate row (row 4) was removed; 'electronics' and 'accessories' in the Category column were normalized to 'Electronics' and 'Accessories' respectively. Two rows (6 and 5) had invalid data: row 6 has Quantity = -1 (invalid per rules) and row 5 has an invalid date 'not-a-date'. These were not fixed as the user rejected the proposed fixes. The analysis was run on the cleaned data, yielding total revenue by category: Accessories $830.00, Electronics $2185.00.
