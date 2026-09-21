"""
Build tabular prediction features (v1).

Architecture name: build_bfm_prediction_features()
Same feature set for all horizons; tune later if needed.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from pinky.config import (
    BENCHMARK,
    DATA_FEATURES_DIR,
    DATA_RAW_DIR,
    FEATURE_WARMUP_DAYS,
    UNIVERSE_STOCKS,
)
from pinky.raw_io import adj_close_series, load_raw_ticker


def _pct_change(series: pd.Series, periods: int) -> pd.Series:
    return series / series.shift(periods) - 1.0


def _rolling_vol(returns: pd.Series, window: int) -> pd.Series:
    return returns.rolling(window).std() * np.sqrt(252)


def _rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0).rolling(window).mean()
    loss = (-delta.clip(upper=0.0)).rolling(window).mean()
    rs = gain / loss.replace(0.0, np.nan)
    return 100.0 - (100.0 / (1.0 + rs))


def _helper_frame() -> pd.DataFrame:
    """Shared market / macro series aligned on calendar dates."""
    spy = load_raw_ticker("SPY")
    iwm = load_raw_ticker("IWM")
    vix = load_raw_ticker("^VIX")
    tnx = load_raw_ticker("^TNX")
    irx = load_raw_ticker("^IRX")

    spy_px = adj_close_series(spy)
    iwm_px = adj_close_series(iwm)
    vix_px = adj_close_series(vix)
    tnx_px = adj_close_series(tnx)
    irx_px = adj_close_series(irx)

    spy_ret = spy_px.pct_change()

    out = pd.DataFrame(index=spy_px.index)
    out["spy_ret_1d"] = spy_ret
    out["spy_ret_21"] = _pct_change(spy_px, 21)
    out["spy_ret_63"] = _pct_change(spy_px, 63)
    out["spy_vol_21"] = _rolling_vol(spy_ret, 21)
    out["spy_sma_200"] = spy_px.rolling(200).mean()
    out["regime_bull"] = (spy_px > out["spy_sma_200"]).astype(float)
    # High-vol regime: realized vol above its own 1y median (point-in-time)
    vol_med = out["spy_vol_21"].rolling(252, min_periods=63).median()
    out["regime_high_vol"] = (out["spy_vol_21"] > vol_med).astype(float)

    out["iwm_ret_21"] = _pct_change(iwm_px, 21)
    out["iwm_ret_63"] = _pct_change(iwm_px, 63)

    out["vix_level"] = vix_px.reindex(out.index).ffill()
    out["vix_chg_5"] = _pct_change(out["vix_level"], 5)
    out["vix_chg_21"] = _pct_change(out["vix_level"], 21)

    out["tnx_level"] = tnx_px.reindex(out.index).ffill()
    out["irx_level"] = irx_px.reindex(out.index).ffill()
    out["tnx_chg_21"] = out["tnx_level"] - out["tnx_level"].shift(21)
    out["irx_chg_21"] = out["irx_level"] - out["irx_level"].shift(21)
    out["yield_curve"] = out["tnx_level"] - out["irx_level"]

    # Keep helper return series for RS joins
    out["spy_px"] = spy_px
    out["iwm_px"] = iwm_px.reindex(out.index).ffill()
    return out


def build_bfm_prediction_features(
    ticker: str,
    raw_dir: Path = DATA_RAW_DIR,
    helpers: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Build feature matrix X for one stock.

    Returns rows indexed by Date with columns: Ticker + numeric features.
    Only uses information available on/before each date (no peeking ahead).
    """
    if ticker == BENCHMARK:
        raise ValueError("Do not build stock features for the benchmark itself")

    stock = load_raw_ticker(ticker, raw_dir=raw_dir)
    close = adj_close_series(stock)
    volume = stock["Volume"].astype(float)
    helpers = helpers if helpers is not None else _helper_frame()

    # Align stock to SPY calendar (inner join keeps trading days both exist)
    idx = close.index.intersection(helpers.index)
    close = close.loc[idx]
    volume = volume.reindex(idx)
    h = helpers.loc[idx]

    ret = close.pct_change()
    feat = pd.DataFrame(index=idx)
    feat["Ticker"] = ticker

    # --- stock technicals ---
    feat["ret_1d"] = ret
    feat["ret_5d"] = _pct_change(close, 5)
    feat["ret_21d"] = _pct_change(close, 21)
    feat["vol_21"] = _rolling_vol(ret, 21)
    feat["vol_63"] = _rolling_vol(ret, 63)
    vol_ma = volume.rolling(21).mean()
    feat["volume_ratio_21"] = volume / vol_ma.replace(0.0, np.nan)
    feat["rsi_14"] = _rsi(close, 14)
    sma_50 = close.rolling(50).mean()
    sma_200 = close.rolling(200).mean()
    feat["dist_sma_50"] = close / sma_50 - 1.0
    feat["dist_sma_200"] = close / sma_200 - 1.0

    # --- multi-period momentum ---
    feat["mom_63"] = _pct_change(close, 63)
    feat["mom_126"] = _pct_change(close, 126)
    feat["mom_252"] = _pct_change(close, 252)
    # 12-1 style: 252d momentum excluding most recent 21d
    feat["mom_252_skip_21"] = close.shift(21) / close.shift(252) - 1.0

    # --- relative strength vs SPY / IWM ---
    feat["rs_spy_21"] = feat["ret_21d"] - h["spy_ret_21"]
    feat["rs_spy_63"] = feat["mom_63"] - h["spy_ret_63"]
    feat["rs_spy_126"] = feat["mom_126"] - _pct_change(h["spy_px"], 126)
    feat["rs_iwm_21"] = feat["ret_21d"] - h["iwm_ret_21"]
    feat["rs_iwm_63"] = feat["mom_63"] - h["iwm_ret_63"]

    # --- macro environment (shared) ---
    for col in [
        "vix_level",
        "vix_chg_5",
        "vix_chg_21",
        "tnx_level",
        "irx_level",
        "tnx_chg_21",
        "irx_chg_21",
        "yield_curve",
        "spy_ret_21",
        "spy_ret_63",
        "spy_vol_21",
    ]:
        feat[col] = h[col]

    # --- market regime ---
    feat["regime_bull"] = h["regime_bull"]
    feat["regime_high_vol"] = h["regime_high_vol"]

    # Warm-up: drop early rows lacking enough history
    feat = feat.iloc[FEATURE_WARMUP_DAYS:].copy()
    feat = feat.replace([np.inf, -np.inf], np.nan).dropna()
    feat.index.name = "Date"
    return feat


def build_universe_features(
    tickers: list[str] | None = None,
    raw_dir: Path = DATA_RAW_DIR,
) -> pd.DataFrame:
    """Build and stack features for all starter stocks."""
    tickers = tickers or list(UNIVERSE_STOCKS)
    helpers = _helper_frame()
    frames: list[pd.DataFrame] = []
    errors: dict[str, str] = {}

    for ticker in tickers:
        try:
            f = build_bfm_prediction_features(ticker, raw_dir=raw_dir, helpers=helpers)
            frames.append(f)
            print(f"[ok] {ticker}: {len(f)} feature rows")
        except Exception as exc:  # noqa: BLE001
            errors[ticker] = str(exc)
            print(f"[fail] {ticker}: {exc}")

    if not frames:
        raise RuntimeError(f"No features built. Errors: {errors}")

    panel = pd.concat(frames).sort_index()
    if errors:
        print(f"\nFailed {len(errors)}/{len(tickers)} tickers:")
        for t, msg in errors.items():
            print(f"  - {t}: {msg}")
    print(f"\nPanel: {len(panel)} rows, {panel['Ticker'].nunique()} tickers")
    return panel


def save_features(panel: pd.DataFrame, out_dir: Path = DATA_FEATURES_DIR) -> Path:
    """Write stacked feature panel to parquet."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "features_panel.parquet"
    panel.to_parquet(path)
    return path


if __name__ == "__main__":
    panel = build_universe_features()
    path = save_features(panel)
    print(f"Wrote {path}")
