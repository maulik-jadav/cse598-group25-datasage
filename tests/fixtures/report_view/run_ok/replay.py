import pandas as pd
df = pd.read_csv('inventory.csv', dtype=str, keep_default_na=False).drop_duplicates(keep='first')
