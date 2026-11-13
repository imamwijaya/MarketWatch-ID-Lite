
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "demo"

df = pd.read_csv(DATA_DIR / "demo_ohlcv.csv")
labels = pd.read_csv(DATA_DIR / "demo_labels.csv")

required = [
    "date", "symbol", "open", "high",
    "low", "close", "volume"
]

errors = []

# 1. Periksa kolom
missing_cols = set(required) - set(df.columns)

if missing_cols:
    raise ValueError(f"Missing columns: {missing_cols}")

# 2. Periksa jumlah data
if len(df) != 140:
    errors.append("Jumlah observasi bukan 140")

# 3. Periksa tanggal
df["date"] = pd.to_datetime(df["date"], errors="coerce")

if df["date"].isna().any():
    errors.append("Tanggal tidak valid")

if df.duplicated(subset=["date", "symbol"]).any():
    errors.append("Ditemukan duplikasi tanggal dan simbol")

# 4. Periksa missing values
if df[required].isna().any().any():
    errors.append("Ditemukan missing values")

# 5. Periksa OHLCV
numeric_cols = ["open", "high", "low", "close", "volume"]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

if df[numeric_cols].isna().any().any():
    errors.append("Ditemukan nilai numerik tidak valid")

elif (
    (df[["open", "high", "low", "close"]] <= 0)
    .any().any()
):
    errors.append("Ditemukan harga nol atau negatif")

if (
    df["high"] < df[["open", "close", "low"]].max(axis=1)
).any():
    errors.append("Nilai High tidak konsisten")

if (
    df["low"] > df[["open", "close", "high"]].min(axis=1)
).any():
    errors.append("Nilai Low tidak konsisten")

if (df["volume"] < 0).any():
    errors.append("Volume negatif")

if (df["volume"].dropna() % 1 != 0).any():
    errors.append("Volume bukan bilangan bulat")

# 6. Periksa label anomali
expected = {"PRICE_ONLY", "VOLUME_ONLY", "COMBINED"}

if set(labels.columns) != {"date", "symbol", "scenario"}:
    errors.append("Struktur label tidak sesuai")

elif (
    len(labels) != 3
    or set(labels["scenario"]) != expected
    or labels[["date", "symbol"]].duplicated().any()
):
    errors.append("Label anomali tidak sesuai")

else:
    data_keys = set(
        zip(df["date"].dt.strftime("%Y-%m-%d"), df["symbol"])
    )
    label_keys = set(zip(labels["date"], labels["symbol"]))

    if not label_keys.issubset(data_keys):
        errors.append("Tanggal atau simbol label tidak ditemukan")

# 7. Tampilkan hasil
print("\n=== DATA VALIDATION REPORT ===")
print(f"Total observations : {len(df)}")
print(f"Total scenarios    : {len(labels)}")
print(f"Missing values     : {df[required].isna().sum().sum()}")
print(f"Duplicate records  : {df.duplicated(['date', 'symbol']).sum()}")

if errors:
    print("\nSTATUS: FAILED")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("\nSTATUS: PASSED")
print("Dataset passed basic OHLCV validation.")
