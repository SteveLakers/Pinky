"""Load saved raw parquet bars."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from pinky.config import DATA_RAW_DIR
from pinky.data_pull import _safe_filename


def load_raw_ticker(ticker: str, raw_dir: Path = DATA_RAW_DIR) -> pd.DataFrame:
    """Load one ticker's raw OHLCV parquet. Raises FileNotFoundError if missing."""
    path = raw_dir / f"{_safe_filename(ticker)}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing raw data for {ticker}: {path}")
    df = pd.read_parquet(path)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def adj_close_series(df: pd.DataFrame) -> pd.Series:
    """Prefer Adj Close for returns; fall back to Close."""
    if "Adj Close" in df.columns:
        return df["Adj Close"].astype(float)
    return df["Close"].astype(float)
