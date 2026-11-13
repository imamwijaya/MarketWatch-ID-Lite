
from pathlib import Path

import numpy as np
import pandas as pd

# Konfigurasi
WINDOW = 20
THRESHOLD = 3.0

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "demo" / "demo_ohlcv.csv"

# Membaca dataset
df = pd.read_csv(DATA_PATH, parse_dates=["date"])
df = df.sort_values(["symbol", "date"]).reset_index(drop=True)

# Menghitung median volume dari 20 observasi sebelumnya
history = df.groupby("symbol")["volume"].shift(1)

df["volume_baseline"] = history.groupby(
    df["symbol"]
).transform(
    lambda x: x.rolling(
        window=WINDOW,
        min_periods=WINDOW
    ).median()
)

# Menghindari pembagian dengan nol
baseline = df["volume_baseline"].replace(0, np.nan)

# Menghitung volume ratio
df["volume_ratio"] = df["volume"] / baseline

# Menentukan alert
df["volume_alert"] = (
    df["volume_ratio"] >= THRESHOLD
).fillna(False)

# Menampilkan hasil
alerts = df.loc[
    df["volume_alert"],
    ["date", "symbol", "volume",
     "volume_baseline", "volume_ratio"]
].copy()

alerts["date"] = alerts["date"].dt.strftime("%Y-%m-%d")

print("\n=== VOLUME SPIKE DETECTION ===")
print(f"Total observations : {len(df)}")
print(f"Rolling window     : {WINDOW}")
print(f"Volume threshold   : {THRESHOLD}")
print(f"Volume alerts      : {len(alerts)}")

print("\n=== DETECTED ALERTS ===")

if alerts.empty:
    print("No volume anomalies detected.")
else:
    print(alerts.to_string(index=False))
