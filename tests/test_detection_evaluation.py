
from pathlib import Path
import subprocess
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "demo"


def test_evaluation_metrics():
    """Pastikan evaluator menghasilkan metrik baseline."""
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "src" / "evaluate_detection.py"),
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    expected = [
        "Evaluable observations : 119",
        "True Positive  : 3",
        "False Positive : 2",
        "False Negative : 0",
        "True Negative  : 114",
        "Precision : 60.00%",
        "Recall    : 100.00%",
        "F1-score  : 75.00%",
        "Correct types: 3/3",
    ]

    for item in expected:
        assert item in result.stdout


def test_injected_anomaly_classification():
    """Periksa klasifikasi tiga skenario sintetis."""
    results = pd.read_csv(
        DATA_DIR / "detection_results.csv"
    )
    labels = pd.read_csv(
        DATA_DIR / "demo_labels.csv"
    )

    merged = labels.merge(
        results,
        on=["date", "symbol"],
        how="left",
        validate="one_to_one",
    )

    assert len(merged) == 3
    assert merged["alert_type"].notna().all()

    assert (
        merged["scenario"] == merged["alert_type"]
    ).all()


def test_alert_counts():
    """Periksa jumlah alert pada dataset demo tetap."""
    results = pd.read_csv(
        DATA_DIR / "detection_results.csv"
    )

    assert len(results) == 140
    assert int(results["price_alert"].sum()) == 4
    assert int(results["volume_alert"].sum()) == 2

    assert (
        results["alert_type"] == "COMBINED"
    ).sum() == 1

    assert (
        results["alert_type"] != "NORMAL"
    ).sum() == 5
