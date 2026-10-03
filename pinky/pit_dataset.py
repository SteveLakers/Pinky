"""
Point-in-time training dataset on the Sharadar liquid universe (survivorship-free).

Rows: one per (sample date, stock in the universe that day). Sample dates are every
`DATASET_SAMPLE_EVERY` trading days (1y labels overlap heavily, so daily rows add little).

Features: the same stock-level price features as the legacy model (features.py).
The legacy market-wide features are left out: prep drops them before ranking, and
`rs_*` features equal plain returns after the per-day z-score.
Plus `history_1y` (share of the last year the stock has traded) and `log_mcap` (size).
Stocks need ~1 month of prices; younger than 1y, the long-window features are missing.
Plus six company growth features (fundamentals.py), used only after their news date.

Labels come from the delisting-aware total-return index (`universe.total_return_panel`),
so stocks that go bankrupt or get acquired inside the horizon stay in the data.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from pinky.config import DATA_SHARADAR_DIR, FEATURE_WARMUP_DAYS, HORIZONS
from pinky.fundamentals import GROWTH_FEATURES, attach_growth_features
from pinky.universe import benchmark_closeadj, load_panel

DERIVED_DIR = DATA_SHARADAR_DIR / "derived"
DATASET_PATH = DERIVED_DIR / "pit_dataset.parquet"
DATASET_SAMPLE_EVERY = 5
TOP_FRAC = 0.1
HISTORY_FULL_DAYS = 252
# Rows missing any of these (< ~1 month of prices) are dropped. Longer-window features
# may be missing for stocks younger than 1y; prep fills them with the day's middle value.
SHORT_FEATURES = ["ret_1d", "ret_5d", "ret_21d", "vol_21", "volume_ratio_21", "rsi_14"]


def _rsi(close: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    delta = close.diff()
    gain = delta.clip(lower=0.0).rolling(window).mean()
    loss = (-delta.clip(upper=0.0)).rolling(window).mean()
    rs = gain / loss.where(loss != 0.0)
    return 100.0 - (100.0 / (1.0 + rs))


def _wide_features(tr: pd.DataFrame, volume: pd.DataFrame):
    """Yield (name, Date x Ticker frame) for each price feature; same math as features.py."""
    ret = tr / tr.shift(1) - 1.0
    yield "ret_1d", ret
    yield "ret_5d", tr / tr.shift(5) - 1.0
    yield "ret_21d", tr / tr.shift(21) - 1.0
    yield "vol_21", ret.rolling(21).std() * np.sqrt(252)
    yield "vol_63", ret.rolling(63).std() * np.sqrt(252)
    del ret
    vol_ma = volume.rolling(21).mean()
    yield "volume_ratio_21", volume / vol_ma.where(vol_ma != 0.0)
    del vol_ma
    yield "rsi_14", _rsi(tr, 14)
    yield "dist_sma_50", tr / tr.rolling(50).mean() - 1.0
    yield "dist_sma_200", tr / tr.rolling(200).mean() - 1.0
    yield "mom_63", tr / tr.shift(63) - 1.0
    yield "mom_126", tr / tr.shift(126) - 1.0
    yield "mom_252", tr / tr.shift(252) - 1.0
    yield "mom_252_skip_21", tr.shift(21) / tr.shift(252) - 1.0


def _log_market_cap(dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Date, Ticker, log_mcap from Sharadar DAILY. Point-in-time: shares update on SEC filing dates."""
    d = pd.read_parquet(
        DATA_SHARADAR_DIR / "daily.parquet",
        columns=["ticker", "date", "marketcap"],
        filters=[("date", "in", list(dates))],
    )
    d = d[d["marketcap"] > 0].drop_duplicates(["ticker", "date"], keep="last")
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(d["date"]).to_numpy(),
            "Ticker": d["ticker"].astype(str).to_numpy(),
            "log_mcap": np.log(d["marketcap"].to_numpy(dtype="float64")).astype("float32"),
        }
    )


def build_pit_dataset(sample_every: int = DATASET_SAMPLE_EVERY) -> pd.DataFrame:
    tr = load_panel("tr")
    universe = load_panel("universe")
    volume = load_panel("volume")
    dates = tr.index
    n_days = len(dates)

    sample_pos = np.arange(FEATURE_WARMUP_DAYS, n_days, sample_every)
    in_univ = universe.notna().to_numpy()[sample_pos]
    r_idx, c_idx = np.nonzero(in_univ)
    rows = sample_pos[r_idx]
    print(f"[pit] {len(sample_pos)} sample dates | {len(rows):,} universe stock-dates")

    out = pd.DataFrame(
        {"Date": dates[rows], "Ticker": tr.columns[c_idx].astype(str)}
    )
    fcols = []
    for name, wide in _wide_features(tr, volume):
        vals = wide.to_numpy(dtype="float64")[rows, c_idx]
        out[name] = np.where(np.isfinite(vals), vals, np.nan).astype("float32")
        fcols.append(name)

    px = tr.to_numpy(dtype="float64")
    history = np.cumsum(np.isfinite(px), axis=0, dtype=np.int32)[rows, c_idx]
    out["history_1y"] = (np.minimum(history, HISTORY_FULL_DAYS) / HISTORY_FULL_DAYS).astype("float32")
    del history
    spy = benchmark_closeadj().reindex(dates).ffill().to_numpy()
    for h, days in HORIZONS.items():
        fwd_pos = rows + days
        ok = fwd_pos < n_days
        stock_fwd = np.full(len(rows), np.nan)
        spy_fwd = np.full(len(rows), np.nan)
        stock_fwd[ok] = px[fwd_pos[ok], c_idx[ok]] / px[rows[ok], c_idx[ok]] - 1.0
        spy_fwd[ok] = spy[fwd_pos[ok]] / spy[rows[ok]] - 1.0
        excess = stock_fwd - spy_fwd
        out[f"excess_{h}"] = excess.astype("float32")
        out[f"beat_{h}"] = np.where(np.isnan(excess), np.nan, (excess > 0).astype(float)).astype("float32")
        out[f"stock_fwd_{h}"] = stock_fwd.astype("float32")
        out[f"spy_fwd_{h}"] = spy_fwd.astype("float32")

    before = len(out)
    out = out.dropna(subset=SHORT_FEATURES).reset_index(drop=True)
    print(f"[pit] dropped {before - len(out):,} rows with < ~1 month of prices")
    print(f"[pit] {(out['history_1y'] < 1.0).sum():,} rows with < 1y of history (long features missing)")

    out = out.merge(_log_market_cap(dates[sample_pos]), on=["Date", "Ticker"], how="left")
    print(f"[pit] market cap found for {out['log_mcap'].notna().mean():.1%} of rows")
    fcols += ["history_1y", "log_mcap"]

    out = attach_growth_features(out)
    cover = ", ".join(f"{c} {out[c].notna().mean():.1%}" for c in GROWTH_FEATURES[:4])
    print(f"[pit] growth found: {cover}")
    fcols += GROWTH_FEATURES

    for h in HORIZONS:
        col = f"excess_{h}"
        pct = out.groupby("Date")[col].rank(pct=True)
        out[f"top_{h}"] = np.where(
            out[col].notna(), (pct > 1.0 - TOP_FRAC).astype(float), np.nan
        ).astype("float32")

    print(
        f"[pit] dataset {len(out):,} rows | {out['Ticker'].nunique():,} stocks | "
        f"{out['Date'].min().date()} → {out['Date'].max().date()} | {len(fcols)} features"
    )
    return out


def save_pit_dataset(df: pd.DataFrame, path: Path = DATASET_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path


def load_pit_dataset(path: Path = DATASET_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run: python -m pinky.pit_dataset")
    return pd.read_parquet(path)


__all__ = ["DATASET_PATH", "build_pit_dataset", "load_pit_dataset", "save_pit_dataset"]


if __name__ == "__main__":
    ds = build_pit_dataset()
    print(f"Wrote {save_pit_dataset(ds)}")
