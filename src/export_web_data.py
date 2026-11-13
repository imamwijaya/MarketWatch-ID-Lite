
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "data" / "demo" / "detection_results.csv"
OUTPUT = ROOT / "web" / "src" / "data" / "detection-results.json"

df = pd.read_csv(SOURCE)

required = [
    "date",
    "symbol",
    "close",
    "volume",
    "price_zscore",
    "volume_ratio",
    "alert_type",
    "evaluable",
]

missing = set(required) - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")

if df[["date", "symbol"]].duplicated().any():
    raise ValueError("Duplicate date and symbol records")

def safe_number(value):
    return None if pd.isna(value) else float(value)

records = []

for row in df.itertuples(index=False):
    records.append({
        "date": row.date,
        "symbol": row.symbol,
        "close": float(row.close),
        "volume": int(row.volume),
        "price_zscore": safe_number(row.price_zscore),
        "volume_ratio": safe_number(row.volume_ratio),
        "alert_type": row.alert_type,
        "evaluable": bool(row.evaluable),
    })

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", encoding="utf-8") as file:
    json.dump(
        records,
        file,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )

print("SUCCESS: Web dataset exported")
print(f"Observations : {len(records)}")
print(f"Alerts       : {(df['alert_type'] != 'NORMAL').sum()}")
print(f"Output       : {OUTPUT}")
