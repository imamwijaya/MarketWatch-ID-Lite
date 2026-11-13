
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="MarketWatch-ID Lite API",
    description=(
        "Read-only backend API for a synthetic "
        "equity anomaly surveillance prototype."
    ),
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "marketwatch-id-lite-api",
        "mode": "synthetic-demo",
    }


# ========================================
# DATASET API
# ========================================

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    ROOT / "data" / "demo" / "detection_results.csv"
)


@app.get("/api/observations")
def get_observations():

    if not DATA_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="Detection dataset is unavailable",
        )

    # Read existing Python detection results
    df = pd.read_csv(DATA_PATH)

    required_columns = [
        "date",
        "symbol",
        "close",
        "volume",
        "price_zscore",
        "volume_ratio",
        "alert_type",
        "evaluable",
    ]

    missing = set(required_columns) - set(df.columns)

    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Missing dataset columns: {sorted(missing)}",
        )

    if df[["date", "symbol"]].duplicated().any():
        raise HTTPException(
            status_code=500,
            detail="Duplicate observation records",
        )

    # Convert evaluable flags to proper booleans
    flags = (
        df["evaluable"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False})
    )

    if flags.isna().any():
        raise HTTPException(
            status_code=500,
            detail="Invalid evaluable flag",
        )

    df["evaluable"] = flags.astype(bool)

    # Sort observations by date
    df = df.sort_values(
        ["date", "symbol"]
    ).reset_index(drop=True)

    # Select only fields needed by the frontend
    data = df[required_columns].copy()

    # Replace missing numerical values with JSON null
    data = data.astype(object).where(
        pd.notna(data),
        None,
    )

    records = data.to_dict(orient="records")

    return {
        "dataset": "BBCA_DEMO",
        "count": len(records),
        "observations": records,
    }


# ========================================
# ANOMALY ALERTS API
# ========================================

@app.get("/api/alerts")
def get_alerts():
    # Reuse the validated observations endpoint
    dataset = get_observations()

    # Keep only observations with detected anomalies
    alerts = [
        record
        for record in dataset["observations"]
        if record["alert_type"] != "NORMAL"
    ]

    return {
        "dataset": dataset["dataset"],
        "count": len(alerts),
        "alerts": alerts,
    }


# ========================================
# EVALUATION API
# ========================================

LABEL_PATH = ROOT / "data" / "demo" / "demo_labels.csv"


@app.get("/api/evaluation")
def get_evaluation():

    if not LABEL_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="Ground-truth labels are unavailable",
        )

    # Reuse validated detection observations
    dataset = get_observations()
    results = pd.DataFrame(dataset["observations"])

    labels = pd.read_csv(LABEL_PATH)

    required = {"date", "symbol", "scenario"}

    if not required.issubset(labels.columns):
        raise HTTPException(
            status_code=500,
            detail="Invalid ground-truth schema",
        )

    if labels.duplicated(["date", "symbol"]).any():
        raise HTTPException(
            status_code=500,
            detail="Duplicate ground-truth labels",
        )

    valid_scenarios = {
        "PRICE_ONLY",
        "VOLUME_ONLY",
        "COMBINED",
    }

    if not labels["scenario"].isin(valid_scenarios).all():
        raise HTTPException(
            status_code=500,
            detail="Invalid ground-truth scenario",
        )

    # Only observations with complete baselines
    evaluable = results.loc[
        results["evaluable"]
    ].copy()

    # Check that every label belongs to an evaluable record
    label_check = labels.merge(
        evaluable[["date", "symbol"]],
        on=["date", "symbol"],
        how="left",
        indicator=True,
        validate="one_to_one",
    )

    if not label_check["_merge"].eq("both").all():
        raise HTTPException(
            status_code=500,
            detail="Ground-truth alignment failed",
        )

    # Match predictions against injected labels
    df = evaluable.merge(
        labels,
        on=["date", "symbol"],
        how="left",
        validate="one_to_one",
    )

    actual = df["scenario"].fillna("NORMAL")
    predicted = df["alert_type"]

    actual_anomaly = actual != "NORMAL"
    predicted_anomaly = predicted != "NORMAL"

    tp = int((actual_anomaly & predicted_anomaly).sum())
    fp = int((~actual_anomaly & predicted_anomaly).sum())
    fn = int((actual_anomaly & ~predicted_anomaly).sum())
    tn = int((~actual_anomaly & ~predicted_anomaly).sum())

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    correct_types = int(
        (
            actual[actual_anomaly]
            == predicted[actual_anomaly]
        ).sum()
    )

    return {
        "dataset": dataset["dataset"],
        "observations": dataset["count"],
        "evaluable_observations": len(df),
        "injected_anomalies": int(actual_anomaly.sum()),
        "predicted_alerts": int(predicted_anomaly.sum()),
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "correct_types": correct_types,
        "total_labeled": int(actual_anomaly.sum()),
        "confusion_matrix": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
        },
    }
