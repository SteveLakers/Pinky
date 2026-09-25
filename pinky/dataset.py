"""
Train-ready dataset: join features (X) + labels (y) on Date + Ticker.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from pinky.config import DATA_DATASET_DIR, DATA_FEATURES_DIR, DATA_LABELS_DIR, HORIZONS


LABEL_PREFIXES = ("excess_", "beat_", "stock_fwd_", "spy_fwd_")


def feature_columns(df: pd.DataFrame) -> list[str]:
    """Numeric model inputs only (no ids, no labels)."""
    skip = {"Date", "Ticker"}
    cols = []
    for c in df.columns:
        if c in skip:
            continue
        if any(c.startswith(p) for p in LABEL_PREFIXES):
            continue
        cols.append(c)
    return cols


def label_columns(horizon: str | None = None) -> list[str]:
    """Label column names for one horizon or all."""
    names = list(HORIZONS) if horizon is None else [horizon]
    cols: list[str] = []
    for h in names:
        cols.extend(
            [
                f"excess_{h}",
                f"beat_{h}",
                f"stock_fwd_{h}",
                f"spy_fwd_{h}",
            ]
        )
    return cols


def build_train_dataset(
    features_path: Path | None = None,
    labels_path: Path | None = None,
) -> pd.DataFrame:
    """
    Inner-join features and labels on Date + Ticker.

    Does not invent rows. Rows missing either side are dropped.
    """
    features_path = features_path or (DATA_FEATURES_DIR / "features_panel.parquet")
    labels_path = labels_path or (DATA_LABELS_DIR / "labels_panel.parquet")

    if not features_path.exists():
        raise FileNotFoundError(f"Missing features: {features_path}")
    if not labels_path.exists():
        raise FileNotFoundError(f"Missing labels: {labels_path}")

    feat = pd.read_parquet(features_path).reset_index()
    lab = pd.read_parquet(labels_path).reset_index()

    feat["Date"] = pd.to_datetime(feat["Date"])
    lab["Date"] = pd.to_datetime(lab["Date"])

    merged = feat.merge(lab, on=["Date", "Ticker"], how="inner", validate="one_to_one")
    merged = merged.sort_values(["Date", "Ticker"]).reset_index(drop=True)

    # Feature side should be complete; drop accidental all-NaN feature rows
    fcols = feature_columns(merged)
    before = len(merged)
    merged = merged.dropna(subset=fcols)
    dropped = before - len(merged)
    if dropped:
        print(f"[warn] dropped {dropped} rows with NaN features")

    print(
        f"Dataset: {len(merged)} rows | "
        f"{merged['Ticker'].nunique()} tickers | "
        f"{merged['Date'].min().date()} → {merged['Date'].max().date()} | "
        f"{len(fcols)} features"
    )
    return merged


def save_dataset(df: pd.DataFrame, out_dir: Path = DATA_DATASET_DIR) -> Path:
    """Write train-ready panel to parquet."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "train_dataset.parquet"
    df.to_parquet(path, index=False)
    return path


def load_dataset(path: Path | None = None) -> pd.DataFrame:
    """Load saved train-ready dataset."""
    path = path or (DATA_DATASET_DIR / "train_dataset.parquet")
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}. Run scripts/build_dataset.py")
    df = pd.read_parquet(path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


if __name__ == "__main__":
    ds = build_train_dataset()
    path = save_dataset(ds)
    print(f"Wrote {path}")
