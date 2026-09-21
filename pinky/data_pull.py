"""Download daily OHLCV via yfinance and save to data/raw/."""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import yfinance as yf

from pinky.config import DATA_RAW_DIR, HISTORY_START, all_tickers


REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]


def _safe_filename(ticker: str) -> str:
    """Turn ^VIX into VIX-index style names for files."""
    return ticker.replace("^", "").replace("/", "-")


def download_ticker(ticker: str, start: str = HISTORY_START) -> pd.DataFrame:
    """
    Pull one ticker's daily history.

    Raises ValueError if the download is empty or missing required columns.
    """
    raw = yf.download(
        ticker,
        start=start,
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    if raw is None or raw.empty:
        raise ValueError(f"{ticker}: empty download")

    # yfinance sometimes returns MultiIndex columns even for one ticker
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [c[0] if isinstance(c, tuple) else c for c in raw.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
    if missing:
        raise ValueError(f"{ticker}: missing columns {missing}; got {list(raw.columns)}")

    out = raw[REQUIRED_COLUMNS].copy()
    out.index = pd.to_datetime(out.index).tz_localize(None)
    out.index.name = "Date"
    out["Ticker"] = ticker
    return out


def save_ticker(df: pd.DataFrame, ticker: str, out_dir: Path = DATA_RAW_DIR) -> Path:
    """Write one ticker to parquet under data/raw/."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{_safe_filename(ticker)}.parquet"
    df.to_parquet(path)
    return path


def pull_universe(
    tickers: list[str] | None = None,
    start: str = HISTORY_START,
    out_dir: Path = DATA_RAW_DIR,
    sleep_s: float = 0.2,
) -> dict[str, Path]:
    """
    Download and save each ticker.

    Returns mapping ticker -> parquet path for successes.
    Failed tickers are collected and reported; does not invent data.
    """
    tickers = tickers or all_tickers()
    saved: dict[str, Path] = {}
    errors: dict[str, str] = {}

    for i, ticker in enumerate(tickers):
        try:
            df = download_ticker(ticker, start=start)
            path = save_ticker(df, ticker, out_dir=out_dir)
            saved[ticker] = path
            print(f"[ok] {ticker}: {len(df)} rows -> {path.name}")
        except Exception as exc:  # noqa: BLE001 — surface real failure per ticker
            errors[ticker] = str(exc)
            print(f"[fail] {ticker}: {exc}")

        if i < len(tickers) - 1 and sleep_s > 0:
            time.sleep(sleep_s)

    if errors:
        print(f"\nFailed {len(errors)}/{len(tickers)} tickers:")
        for t, msg in errors.items():
            print(f"  - {t}: {msg}")

    print(f"\nSaved {len(saved)}/{len(tickers)} tickers to {out_dir}")
    return saved


if __name__ == "__main__":
    pull_universe()
