
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "demo"
OUTPUT = ROOT / "web" / "src" / "data" / "evaluation-summary.json"

# Membaca hasil deteksi dan ground truth
results = pd.read_csv(DATA_DIR / "detection_results.csv")
labels = pd.read_csv(DATA_DIR / "demo_labels.csv")

# Memastikan struktur data
required_results = {
    "date", "symbol", "alert_type", "evaluable"
}
required_labels = {"date", "symbol", "scenario"}

if not required_results.issubset(results.columns):
    raise ValueError("Detection results columns are incomplete")

if not required_labels.issubset(labels.columns):
    raise ValueError("Ground-truth columns are incomplete")

if results.duplicated(["date", "symbol"]).any():
    raise ValueError("Duplicate detection records")

if labels.duplicated(["date", "symbol"]).any():
    raise ValueError("Duplicate ground-truth labels")

# Validasi flag evaluable
flags = results["evaluable"].astype("string").str.lower()

if not flags.isin(["true", "false"]).all():
    raise ValueError("Invalid evaluable flag")

results["evaluable"] = flags.eq("true")

valid_types = {
    "NORMAL", "PRICE_ONLY", "VOLUME_ONLY", "COMBINED"
}

if not results["alert_type"].isin(valid_types).all():
    raise ValueError("Invalid alert classification")

if not labels["scenario"].isin(valid_types - {"NORMAL"}).all():
    raise ValueError("Invalid ground-truth classification")

# Pastikan setiap label memiliki observasi yang dapat dievaluasi
label_check = labels.merge(
    results[["date", "symbol", "evaluable"]],
    on=["date", "symbol"],
    how="left",
    validate="one_to_one",
)

if label_check["evaluable"].isna().any():
    raise ValueError("Ground-truth label has no detection record")

if not label_check["evaluable"].all():
    raise ValueError("Ground-truth label is inside warmup period")

# Gabungkan hasil prediksi dan label
df = results.loc[results["evaluable"]].merge(
    labels,
    on=["date", "symbol"],
    how="left",
    validate="one_to_one",
)

df["actual"] = df["scenario"].fillna("NORMAL")
df["predicted"] = df["alert_type"]

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

labeled = df.loc[actual_positive]
correct_types = int(
    (labeled["actual"] == labeled["predicted"]).sum()
)

summary = {
    "dataset": "BBCA_DEMO",
    "observations": len(results),
    "evaluable_observations": len(df),
    "injected_anomalies": int(actual_positive.sum()),
    "predicted_alerts": int(predicted_positive.sum()),
    "precision": precision,
    "recall": recall,
    "f1_score": f1,
    "correct_types": correct_types,
    "total_labeled": len(labeled),
    "confusion_matrix": {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    },
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", encoding="utf-8") as file:
    json.dump(summary, file, indent=2, allow_nan=False)

print("\nSUCCESS: Evaluation summary exported")
print(f"Evaluable : {len(df)}")
print(f"Precision : {precision:.2%}")
print(f"Recall    : {recall:.2%}")
print(f"F1-score  : {f1:.2%}")
print(f"Correct types : {correct_types}/{len(labeled)}")
print(f"Output    : {OUTPUT}")
