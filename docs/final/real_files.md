# Real messy files

The demo tables in `examples/demo/` are synthetic. These two files are public city inspection data.
Each extract is a short date window, not the full portal table, and the values were not cleaned before
the run. Rules and the hand-checked answers are in `eval/real/`. DataSage was the default agent
(`datasage-m3`, Qwen3-30B) with `--approve auto`, so a risky fix was applied without a prompt.

```bash
python -m datasage --input eval/real/chicago_inspections/inspections.csv \
  --rules eval/real/chicago_inspections/rules.json \
  --request "<question>" --approve auto --out outputs/real/chicago_qN
python -m datasage --input eval/real/nyc_restaurants/inspections.csv \
  --rules eval/real/nyc_restaurants/rules.json \
  --request "<question>" --approve auto --out outputs/real/nyc_qN
```

Three of the six answers matched. The runs are under `outputs/real/`, which git ignores.

## Chicago food inspections

Source: City of Chicago, Food Inspections,
https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5.
Use is allowed under the City's data terms,
https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html.
This copy is a subset (every inspection from 2024-06-03 up to 2024-06-10, 411 rows), so the City's
notice applies: the data was modified for use from www.cityofchicago.org, the City makes no claim
about accuracy or completeness, and it is used at our own risk. The query is in
`eval/real/chicago_inspections/SOURCE.md`.

The mess in this window is small: one city value `CHICAGO.`, three blank facility types, and five
facility types in all capitals or all lowercase (`TAVERN`, `HOTEL`, `DINING HALL`, `GREENHOUSE`,
`banquets`). Dates are timestamps (`2024-06-03T00:00:00.000`) rather than `YYYY-MM-DD`.

| Question | Hand answer | DataSage | |
|---|---|---|---|
| Inspections by result | Pass 198, Fail 75, Pass w/ Conditions 60, Out of Business 42, No Entry 26, Not Ready 10 | same | match |
| Fail inspections by risk | High 67, Medium 6, Low 2 | High 66, Medium 5, Low 2 | miss |
| Inspections by facility type, with case folded and blanks left out | 20 types, Restaurant 291 down to Greenhouse 1 (see `questions.json`) | same | match |

On the miss, `parse_dates` treated every timestamp as an invalid date and set all 411 dates to
missing. The agent then dropped the first 12 rows for that reason. Two of those rows were Fail
inspections, one high risk and one medium risk, so both of those counts are short by one. The
question did not depend on the date.

## New York restaurant inspections

Source: NYC Department of Health and Mental Hygiene, DOHMH New York City Restaurant Inspection
Results, https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j.
NYC Open Data has no use restrictions (https://www.nyc.gov/opendata/get-started/FAQs).
This copy is every row from 2024-06-03 up to 2024-06-05: 628 violation rows, 164 inspections.
One inspection is several rows when there are several violations. The query is in
`eval/real/nyc_restaurants/SOURCE.md`.

| Question | Hand answer | DataSage | |
|---|---|---|---|
| Grade counts, one row per restaurant per date, blanks skipped | A 74, P 3, B 2, C 1 | no answer | miss |
| Mean score by borough, one row per restaurant per date, blanks skipped | Bronx 18.53, Brooklyn 22.20, Manhattan 16.59, Queens 22.55, Staten Island 32.60 | 21.88, 28.22, 22.89, 31.91, 39.27 | miss |
| Critical violation rows by cuisine | 333 rows, 33 cuisines (American 35 down to a few 1s) | same except Donuts is missing (3 rows) | miss |

The grade question never got a number. The agent could not pass a blank grade into `analyze`, then
filtered grade to A and B and C at the same time, which matches no row. It also grouped by restaurant
and date together, so the counts would have been visits rather than grades even if the filter had
worked. `parse_dates` again set every date to missing.

The score question averaged every remaining violation row. A restaurant with four violations was
counted four times, so every borough mean is high. It did drop some blank scores, but not as one
row per inspection.

The cuisine question was right except for Donuts. Three Dunkin' rows, all Critical, were dropped
because their longitude was 0. The question does not use longitude.
