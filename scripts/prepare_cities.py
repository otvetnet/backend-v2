import pandas as pd
from pathlib import Path

root = Path(__file__).parent.parent

file = root / "app" / "data" / "cities.csv"
out = root / "app" / "data" / "prepared_cities.csv"

try:
    df = pd.read_csv(file)

    df_p = df[["city"]].rename(columns={'city': 'name'})
    df_p = df_p.drop_duplicates()
    df_p = df_p.sort_values('name')
    df_p = df_p.reset_index(drop=True)
    df_p.to_csv(out, index=False)

    print(f"Made {len(df_p)} cities total")
except Exception as e:
    print(f"Error: {e}")
    raise