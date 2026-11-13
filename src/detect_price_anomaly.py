
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
df = df.sort_values("date").reset_index(drop=True)

# Menghitung log return
df["log_return"] = np.log(
    df["close"] / df["close"].shift(1)
)

# Baseline 20 return sebelumnya
history = df["log_return"].shift(1)

mean = history.rolling(
    window=WINDOW,
    min_periods=WINDOW
).mean()

std = history.rolling(
    window=WINDOW,
    min_periods=WINDOW
).std()

# Menghitung Z-score
df["price_zscore"] = (
    (df["log_return"] - mean) /
    std.replace(0, np.nan)
)

# Menentukan alert
df["price_alert"] = (
    df["price_zscore"].abs() >= THRESHOLD
).fillna(False)

# Menampilkan hasil
alerts = df.loc[
    df["price_alert"],
    ["date", "symbol", "close", "log_return", "price_zscore"]
].copy()

alerts["date"] = alerts["date"].dt.strftime("%Y-%m-%d")

print("\n=== PRICE ANOMALY DETECTION ===")
print(f"Total observations : {len(df)}")
print(f"Rolling window     : {WINDOW}")
print(f"Z-score threshold  : {THRESHOLD}")
print(f"Price alerts       : {len(alerts)}")

print("\n=== DETECTED ALERTS ===")

if alerts.empty:
    print("No price anomalies detected.")
else:
    print(alerts.to_string(index=False))
