
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "demo"

# 1. Baca hasil deteksi dan label sintetis
results = pd.read_csv(DATA_DIR / "detection_results.csv")
labels = pd.read_csv(DATA_DIR / "demo_labels.csv")

# 2. Periksa struktur dan integritas data
required = {"date", "symbol", "alert_type", "evaluable"}

if not required.issubset(results.columns):
    raise ValueError("Kolom detection_results tidak lengkap.")

if not {"date", "symbol", "scenario"}.issubset(labels.columns):
    raise ValueError("Kolom demo_labels tidak lengkap.")

if results.duplicated(["date", "symbol"]).any():
    raise ValueError("Duplikasi pada detection_results.")

if labels.duplicated(["date", "symbol"]).any():
    raise ValueError("Duplikasi pada demo_labels.")

# Konversi flag evaluable menjadi Boolean
results["evaluable"] = (
    results["evaluable"]
    .astype(str)
    .str.lower()
    .map({"true": True, "false": False})
)

if results["evaluable"].isna().any():
    raise ValueError("Nilai evaluable tidak valid.")

# Pastikan semua label memiliki data dan baseline
label_check = labels.merge(
    results[["date", "symbol", "evaluable"]],
    on=["date", "symbol"],
    how="left",
    validate="one_to_one"
)

if label_check["evaluable"].isna().any():
    raise ValueError("Ada label tanpa data deteksi.")

if not label_check["evaluable"].all():
    raise ValueError("Ada label pada periode warmup.")

# 3. Gabungkan prediksi dengan ground truth
df = results.merge(
    labels,
    on=["date", "symbol"],
    how="left",
    validate="one_to_one"
)

# Hanya observasi dengan baseline lengkap
df = df.loc[df["evaluable"]].copy()

valid_classes = {
    "NORMAL", "PRICE_ONLY", "VOLUME_ONLY", "COMBINED"
}

if not df["alert_type"].isin(valid_classes).all():
    raise ValueError("Ada klasifikasi alert tidak valid.")

# Tidak ada label skenario berarti NORMAL
df["actual"] = df["scenario"].fillna("NORMAL")
df["predicted"] = df["alert_type"]

# 4. Evaluasi biner: anomaly vs normal
actual_positive = df["actual"] != "NORMAL"
predicted_positive = df["predicted"] != "NORMAL"

tp = int((actual_positive & predicted_positive).sum())
fp = int((~actual_positive & predicted_positive).sum())
fn = int((actual_positive & ~predicted_positive).sum())
tn = int((~actual_positive & ~predicted_positive).sum())

precision = tp / (tp + fp) if tp + fp else 0.0
recall = tp / (tp + fn) if tp + fn else 0.0

f1 = (
    2 * precision * recall / (precision + recall)
    if precision + recall else 0.0
)

# 5. Periksa kesesuaian jenis anomali
labeled = df.loc[actual_positive].copy()
correct_types = int(
    (labeled["actual"] == labeled["predicted"]).sum()
)

# 6. Tampilkan laporan evaluasi
print("\n=== ANOMALY DETECTION EVALUATION ===")
print(f"Evaluable observations : {len(df)}")
print(f"Ground-truth anomalies : {int(actual_positive.sum())}")
print(f"Predicted alerts       : {int(predicted_positive.sum())}")

print("\n=== CONFUSION MATRIX ===")
print(f"True Positive  : {tp}")
print(f"False Positive : {fp}")
print(f"False Negative : {fn}")
print(f"True Negative  : {tn}")

print("\n=== PERFORMANCE METRICS ===")
print(f"Precision : {precision:.2%}")
print(f"Recall    : {recall:.2%}")
print(f"F1-score  : {f1:.2%}")

print("\n=== ANOMALY TYPE MATCHING ===")
print(f"Correct types: {correct_types}/{len(labeled)}")

print(
    labeled[
        ["date", "actual", "predicted"]
    ].to_string(index=False)
)
