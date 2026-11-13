
from pathlib import Path

import numpy as np
import pandas as pd

# Konfigurasi
WINDOW = 20
PRICE_THRESHOLD = 3.0
VOLUME_THRESHOLD = 3.0

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "demo" / "demo_ohlcv.csv"

# Membaca dataset
df = pd.read_csv(DATA_PATH, parse_dates=["date"])
df = df.sort_values(["symbol", "date"]).reset_index(drop=True)

# ========================================
# 1. PRICE ANOMALY
# ========================================

df["log_return"] = df.groupby("symbol")["close"].transform(
    lambda s: np.log(s / s.shift(1))
)

df["price_mean"] = df.groupby("symbol")["log_return"].transform(
    lambda s: s.shift(1).rolling(
        WINDOW, min_periods=WINDOW
    ).mean()
)

df["price_std"] = df.groupby("symbol")["log_return"].transform(
    lambda s: s.shift(1).rolling(
        WINDOW, min_periods=WINDOW
    ).std()
)

df["price_zscore"] = (
    (df["log_return"] - df["price_mean"])
    / df["price_std"].replace(0, np.nan)
)

df["price_alert"] = (
    df["price_zscore"].abs() >= PRICE_THRESHOLD
).fillna(False)

# ========================================
# 2. VOLUME ANOMALY
# ========================================

df["volume_baseline"] = df.groupby("symbol")["volume"].transform(
    lambda s: s.shift(1).rolling(
        WINDOW, min_periods=WINDOW
    ).median()
)

df["volume_ratio"] = (
    df["volume"]
    / df["volume_baseline"].replace(0, np.nan)
)

df["volume_alert"] = (
    df["volume_ratio"] >= VOLUME_THRESHOLD
).fillna(False)

# ========================================
# 3. COMBINED CLASSIFICATION
# ========================================

df["alert_type"] = np.select(
    [
        df["price_alert"] & df["volume_alert"],
        df["price_alert"],
        df["volume_alert"],
    ],
    [
        "COMBINED",
        "PRICE_ONLY",
        "VOLUME_ONLY",
    ],
    default="NORMAL"
)


# ========================================
# SAVE DETECTION RESULTS
# ========================================

# Penanda observasi yang memiliki baseline lengkap
df["evaluable"] = (
    df["price_mean"].notna()
    & df["price_std"].gt(0)
    & df["volume_baseline"].gt(0)
)

# Simpan seluruh observasi untuk evaluasi
results = df[
    [
        "date",
        "symbol",
        "close",
        "volume",
        "price_zscore",
        "volume_ratio",
        "price_alert",
        "volume_alert",
        "alert_type",
        "evaluable",
    ]
].copy()

results["date"] = results["date"].dt.strftime("%Y-%m-%d")

output_path = ROOT / "data" / "demo" / "detection_results.csv"
results.to_csv(output_path, index=False)

print(f"\nDetection results saved: {output_path}")


# Hanya tampilkan tanggal dengan alert
alerts = df.loc[
    df["alert_type"] != "NORMAL",
    [
        "date",
        "symbol",
        "price_zscore",
        "volume_ratio",
        "alert_type",
    ]
].copy()

alerts["date"] = alerts["date"].dt.strftime("%Y-%m-%d")

# ========================================
# 4. SUMMARY
# ========================================

print("\n=== COMBINED ANOMALY DETECTION ===")
print(f"Total observations : {len(df)}")
print(f"Price alerts       : {df['price_alert'].sum()}")
print(f"Volume alerts      : {df['volume_alert'].sum()}")
print(f"Combined alerts    : {(df['alert_type'] == 'COMBINED').sum()}")
print(f"Unique alert dates : {len(alerts)}")

print("\n=== DETECTED ALERTS ===")

if alerts.empty:
    print("No anomalies detected.")
else:
    print(alerts.to_string(index=False))
