# Chicago food inspections

Source: City of Chicago Food Inspections, https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5

This file is not the full table. It is every inspection with `inspection_date` from 2024-06-03 up to but not including 2024-06-10, ordered by `inspection_id` (411 rows). The values were not cleaned. The download was:

```
https://data.cityofchicago.org/resource/4ijn-s7e5.csv
  $where=inspection_date >= '2024-06-03T00:00:00' AND inspection_date < '2024-06-10T00:00:00'
  $order=inspection_id
  $limit=5000
```

The City of Chicago publishes this on its data portal for public use, under the City's data terms of use: https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html
The terms allow use. Because this extract is a subset, the City's required notice for a modified copy is:

This site provides applications using data that has been modified for use from its original source, www.cityofchicago.org, the official website of the City of Chicago. The City of Chicago makes no claims as to the content, accuracy, timeliness, or completeness of any of the data provided at this site. The data provided at this site is subject to change at any time. It is understood that the data provided at this site is being used at one's own risk.
