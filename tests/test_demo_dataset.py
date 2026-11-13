
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "demo"


def load_data():
    df = pd.read_csv(DATA_DIR / "demo_ohlcv.csv")
    labels = pd.read_csv(DATA_DIR / "demo_labels.csv")
    return df, labels


def test_dataset_structure():
    df, _ = load_data()

    expected_columns = [
        "date", "symbol", "open", "high",
        "low", "close", "volume"
    ]

    assert list(df.columns) == expected_columns
    assert len(df) == 140
    assert df["symbol"].eq("BBCA_DEMO").all()


def test_missing_and_duplicates():
    df, _ = load_data()

    assert not df.isna().any().any()
    assert not df.duplicated(
        subset=["date", "symbol"]
    ).any()

    dates = pd.to_datetime(df["date"], errors="coerce")
    assert dates.notna().all()
    assert dates.is_monotonic_increasing


def test_ohlcv_consistency():
    df, _ = load_data()

    prices = df[["open", "high", "low", "close"]]

    assert (prices > 0).all().all()

    assert (
        df["high"] >= prices[["open", "low", "close"]].max(axis=1)
    ).all()

    assert (
        df["low"] <= prices[["open", "high", "close"]].min(axis=1)
    ).all()

    assert (df["volume"] >= 0).all()
    assert (df["volume"] % 1 == 0).all()


def test_ground_truth_labels():
    df, labels = load_data()

    expected = {
        "PRICE_ONLY",
        "VOLUME_ONLY",
        "COMBINED"
    }

    assert len(labels) == 3
    assert set(labels["scenario"]) == expected
    assert not labels[["date", "symbol"]].duplicated().any()

    data_keys = set(zip(df["date"], df["symbol"]))
    label_keys = set(zip(labels["date"], labels["symbol"]))

    assert label_keys.issubset(data_keys)
