import pandas as pd
from pathlib import Path

root = Path(__file__).parent.parent

cities_raw = root / "app" / "data" / "cities.json"
schools_raw = root / "app" / "data" / "schools.json"

cities_processed_out = root / "app" / "data" / "cities_processed.csv"
schools_processed_out = root / "app" / "data" / "schools_processed.csv"
try:
    cities_df = pd.read_json(cities_raw)
    schools_df = pd.read_json(schools_raw)

    cities_export = cities_df.rename(columns={"id": "id", "name": "name"})[
        ["id", "name"]
    ]
    
    schools_export = schools_df.rename(columns={"id": "id", "name": "name", "city_id": "city_id"})[
        ["id", "name", "city_id"]
    ]

    cities_export.to_csv(cities_processed_out, sep=";", index=False, encoding="utf-8")
    schools_export.to_csv(schools_processed_out, sep=";", index=False, encoding="utf-8")
    
    print(f"data processed: {len(cities_export)} cities / {len(schools_export)} schools")
except Exception as e:
    print(f"Error: {e}")
    raise