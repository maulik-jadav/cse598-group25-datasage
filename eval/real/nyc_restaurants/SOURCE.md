# New York restaurant inspections

Source: NYC Department of Health and Mental Hygiene, DOHMH New York City Restaurant Inspection Results, https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j

This file is not the full table. It is every row with `inspection_date` from 2024-06-03 up to but not including 2024-06-05 (628 rows). One inspection is often several rows, one per violation. The values were not cleaned. The download was:

```
https://data.cityofnewyork.us/resource/43nn-pn8j.csv
  $where=inspection_date >= '2024-06-03T00:00:00' AND inspection_date < '2024-06-05T00:00:00'
  $order=camis,inspection_date
  $limit=5000
```

NYC Open Data has no restrictions on use: https://www.nyc.gov/opendata/get-started/FAQs
The data belongs to the City of New York and is published by DOHMH.
