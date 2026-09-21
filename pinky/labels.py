"""
Labels vs SPY (architecture-locked).

For each stock + date + horizon:
  excess_return = stock_forward_return - SPY_forward_return
  beat_spy      = 1 if excess_return > 0 else 0

Forward returns use trading-day shifts from Adj Close.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from pinky.config import (
    BENCHMARK,
    DATA_LABELS_DIR,
    DATA_RAW_DIR,
    HORIZONS,
    UNIVERSE_STOCKS,
)
from pinky.raw_io import adj_close_series, load_raw_ticker


def _forward_return(price: pd.Series, horizon_days: int) -> pd.Series:
    """Return from t to t+horizon_days. NaN near the end where future is unknown."""
    future = price.shift(-horizon_days)
    return future / price - 1.0


def build_labels_for_ticker(
    ticker: str,
    spy_px: pd.Series | None = None,
    raw_dir: Path = DATA_RAW_DIR,
    horizons: dict[str, int] | None = None,
) -> pd.DataFrame:
    """
    Build excess-return and beat labels for one stock across all horizons.

    Rows with incomplete forward windows are dropped (honest: no fake labels).
    """
    if ticker == BENCHMARK:
        raise ValueError("Do not label the benchmark against itself")

    horizons = horizons or HORIZONS
    stock = load_raw_ticker(ticker, raw_dir=raw_dir)
    stock_px = adj_close_series(stock)

    if spy_px is None:
        spy_px = adj_close_series(load_raw_ticker(BENCHMARK, raw_dir=raw_dir))

    idx = stock_px.index.intersection(spy_px.index)
    stock_px = stock_px.loc[idx]
    spy = spy_px.loc[idx]

    out = pd.DataFrame(index=idx)
    out["Ticker"] = ticker

    for name, days in horizons.items():
        stock_fwd = _forward_return(stock_px, days)
        spy_fwd = _forward_return(spy, days)
        excess = stock_fwd - spy_fwd
        out[f"excess_{name}"] = excess
        out[f"beat_{name}"] = np.where(excess.notna(), (excess > 0).astype(float), np.nan)
        out[f"stock_fwd_{name}"] = stock_fwd
        out[f"spy_fwd_{name}"] = spy_fwd

    # Keep rows that have at least one complete horizon (do not fake missing long horizons)
    excess_cols = [f"excess_{name}" for name in horizons]
    out = out.dropna(subset=excess_cols, how="all")
    out.index.name = "Date"
    return out


def build_universe_labels(
    tickers: list[str] | None = None,
    raw_dir: Path = DATA_RAW_DIR,
) -> pd.DataFrame:
    """Build and stack labels for all starter stocks."""
    tickers = tickers or list(UNIVERSE_STOCKS)
    spy_px = adj_close_series(load_raw_ticker(BENCHMARK, raw_dir=raw_dir))
    frames: list[pd.DataFrame] = []
    errors: dict[str, str] = {}

    for ticker in tickers:
        try:
            lab = build_labels_for_ticker(ticker, spy_px=spy_px, raw_dir=raw_dir)
            frames.append(lab)
            print(f"[ok] {ticker}: {len(lab)} labeled rows")
        except Exception as exc:  # noqa: BLE001
            errors[ticker] = str(exc)
            print(f"[fail] {ticker}: {exc}")

    if not frames:
        raise RuntimeError(f"No labels built. Errors: {errors}")

    panel = pd.concat(frames).sort_index()
    if errors:
        print(f"\nFailed {len(errors)}/{len(tickers)} tickers:")
        for t, msg in errors.items():
            print(f"  - {t}: {msg}")

    # Quick honesty checks
    for name in HORIZONS:
        beat_rate = panel[f"beat_{name}"].mean()
        print(f"beat rate {name}: {beat_rate:.3f}")

    print(f"\nPanel: {len(panel)} rows, {panel['Ticker'].nunique()} tickers")
    return panel


def save_labels(panel: pd.DataFrame, out_dir: Path = DATA_LABELS_DIR) -> Path:
    """Write stacked label panel to parquet."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "labels_panel.parquet"
    panel.to_parquet(path)
    return path


if __name__ == "__main__":
    panel = build_universe_labels()
    path = save_labels(panel)
    print(f"Wrote {path}")
