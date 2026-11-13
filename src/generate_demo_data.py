
from pathlib import Path

import numpy as np
import pandas as pd

# Konfigurasi dataset
SEED = 42
N_DAYS = 140
SYMBOL = "BBCA_DEMO"

rng = np.random.default_rng(SEED)

# Tanggal hari kerja simulasi (belum memakai kalender resmi IDX)
dates = pd.bdate_range("2025-01-02", periods=N_DAYS)

# Simulasi return dan volume normal
returns = rng.normal(0.0002, 0.0075, N_DAYS)
volume = rng.integers(1_000_000, 3_000_000, N_DAYS)

# Sisipkan tiga skenario anomali
returns[50] = 0.10           # Price anomaly
volume[85] *= 6              # Volume anomaly
returns[110] = -0.12         # Combined anomaly
volume[110] *= 8

# Bentuk data OHLC
close = 9000 * np.exp(np.cumsum(returns))
previous_close = np.r_[9000.0, close[:-1]]

open_price = previous_close * (
    1 + rng.normal(0, 0.002, N_DAYS)
)

high = np.maximum(open_price, close) * (
    1 + rng.uniform(0.001, 0.006, N_DAYS)
)

low = np.minimum(open_price, close) * (
    1 - rng.uniform(0.001, 0.006, N_DAYS)
)

# Dataset OHLCV
df = pd.DataFrame({
    "date": dates.strftime("%Y-%m-%d"),
    "symbol": SYMBOL,
    "open": open_price,
    "high": high,
    "low": low,
    "close": close,
    "volume": volume,
})

price_columns = ["open", "high", "low", "close"]
df[price_columns] = df[price_columns].round(2)

# Ground-truth skenario terpisah
labels = pd.DataFrame({
    "date": dates[[50, 85, 110]].strftime("%Y-%m-%d"),
    "symbol": SYMBOL,
    "scenario": [
        "PRICE_ONLY",
        "VOLUME_ONLY",
        "COMBINED",
    ],
})

# Simpan ke data/demo
project_root = Path(__file__).resolve().parents[1]
output_dir = project_root / "data" / "demo"
output_dir.mkdir(parents=True, exist_ok=True)

df.to_csv(output_dir / "demo_ohlcv.csv", index=False)
labels.to_csv(output_dir / "demo_labels.csv", index=False)

print("SUCCESS: Synthetic dataset created")
print(f"Total observations: {len(df)}")
print(f"Injected scenarios: {len(labels)}")
print(f"Output folder: {output_dir}")
