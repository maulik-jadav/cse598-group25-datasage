# DataSage report

- Input: `inventory.csv`
- Question: How many units are there per store?
- Model: `test-model`; stop reason: `finish`; tool calls: 6; approvals asked: 2; time: 1.0s

## Problems found

| Type | Column | Count | Rows (first 10) |
|---|---|---:|---|
| duplicates | * | 1 | [3] |
| label_variant | Store | 1 | [1] |
| negative | Units | 1 | [2] |

## Changes

| Version | Fix | Risk | Approval | What changed | Reason |
|---|---|---|---|---|---|
| v1 | drop_duplicates | medium | approved | removed 1 exact duplicate row(s) | Row 3 repeats row 0. |
| v2 | normalize_labels | low | auto | Store: merged 1 label variant(s), 1 cells | 'north' and 'North' differ only by case. |
| - | exclude_rows | high | rejected | excluded 1 row(s): [2] (not applied) | Units = -4 breaks the rule that Units is at least 0. |

## Answer

sum of `Units` by ['Store'] (rows used: 3, version v2)

| Group | Value |
|---|---:|
| North | 16.00 |
| South | -4.00 |

## Summary

Removed 1 duplicate row and merged 1 label variant. The row with Units = -4 was kept because excluding it was rejected.
