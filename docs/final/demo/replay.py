# Replays the DataSage cleaning steps without the agent.
import pandas as pd
df = pd.read_csv('baseline/examples/messy_sales.csv', dtype=str, keep_default_na=False)
df = df.replace({'': pd.NA, 'NA': pd.NA, 'N/A': pd.NA, 'n/a': pd.NA, 'null': pd.NA, 'None': pd.NA})
for col in df.columns:  # same rule as DataSage: convert only columns that are entirely plain numbers
    as_num = pd.to_numeric(df[col], errors='coerce')
    if as_num.notna().sum() == df[col].notna().sum():
        df[col] = as_num
# v1 drop_duplicates (approved): Found one exact duplicate row (row 4), which is a copy of row 3. Keeping only the first occurrence.
df = df.drop_duplicates(keep='first')
# v2 normalize_labels (auto): Merge case and space variants into the allowed labels: 'electronics' → 'Electronics', 'accessories' → 'Accessories'.
df['Category'] = df['Category'].replace({'accessories': 'Accessories', 'electronics': 'Electronics'})
