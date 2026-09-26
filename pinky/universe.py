"""
Point-in-time liquid US stock universe from Sharadar (survivorship-free).

A stock is in the universe on day D only if, using data up to D:
- it is an eligible security (common stock / ADR, listed on NYSE / NASDAQ / NYSE American,
  not a blank-check shell), and
- its unadjusted close on D is at least UNIVERSE_MIN_PRICE, and
- its trailing UNIVERSE_ADV_DAYS average dollar volume is at least UNIVERSE_MIN_DOLLAR_VOLUME.

Delisted companies are included for the days they traded. Sharadar tickers are unique
(reused symbols get a numeric suffix), so a ticker always means one company.

Outputs (data/sharadar/panels/*.parquet), all Date x Ticker:
- closeadj: split + dividend adjusted close
- closeunadj: actual traded close (for the price filter)
- volume: split-adjusted shares traded
- dollar_volume: close * volume (both split-adjusted, so their product is real $)
- universe: 1.0 if in the universe that day, else NaN
- tr: delisting-aware total-return index (use this for all forward returns), see
  `total_return_panel`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pinky.config import (
    BENCHMARK,
    DATA_SHARADAR_DIR,
    DELIST_RETURN_PERFORMANCE,
    UNIVERSE_ADV_DAYS,
    UNIVERSE_CATEGORIES,
    UNIVERSE_EXCHANGES,
    UNIVERSE_EXCLUDE_SIC,
    UNIVERSE_MIN_DOLLAR_VOLUME,
    UNIVERSE_MIN_PRICE,
    UNIVERSE_START,
)
from pinky.sharadar import load, query

PANELS_DIR = DATA_SHARADAR_DIR / "panels"
PERFORMANCE_DELIST_ACTIONS = {"bankruptcyliquidation", "regulatorydelisting"}


def eligible_tickers() -> pd.DataFrame:
    """Securities master rows for stocks that may ever enter the universe."""
    t = load("tickers")
    t = t[t["table"] == "SEP"]
    ok = (
        t["category"].isin(UNIVERSE_CATEGORIES)
        & t["exchange"].isin(UNIVERSE_EXCHANGES)
        & ~t["siccode"].isin(UNIVERSE_EXCLUDE_SIC)
    )
    return t[ok].reset_index(drop=True)


def sector_map() -> dict[str, str]:
    """Ticker -> Sharadar sector (current classification) for every eligible stock."""
    t = eligible_tickers()
    return dict(zip(t["ticker"], t["sector"].fillna("Unknown")))


def benchmark_closeadj(start: str = UNIVERSE_START) -> pd.Series:
    """SPY adjusted close from Sharadar funds (cached)."""
    path = DATA_SHARADAR_DIR / f"{BENCHMARK.lower()}.parquet"
    if not path.exists():
        df = query("funds", ticker=BENCHMARK, from_="1997-01-01")
        df[["date", "closeadj"]].to_parquet(path, index=False)
    df = pd.read_parquet(path)
    s = df.set_index(pd.to_datetime(df["date"]))["closeadj"].sort_index().astype(float)
    return s[s.index >= pd.Timestamp(start)].rename(BENCHMARK)


def build_panels(start: str = UNIVERSE_START) -> dict[str, pd.DataFrame]:
    """Pivot daily prices to wide Date x Ticker panels and apply the liquidity rules."""
    keep = set(eligible_tickers()["ticker"])
    px = load("stocks", columns=["ticker", "date", "close", "volume", "closeadj", "closeunadj"])
    px = px[px["ticker"].isin(keep) & (px["date"] >= pd.Timestamp(start))]
    px = px.drop_duplicates(["date", "ticker"], keep="last")

    def wide(col: str) -> pd.DataFrame:
        return px.pivot(index="date", columns="ticker", values=col).sort_index().astype("float32")

    closeadj = wide("closeadj")
    closeunadj = wide("closeunadj")
    volume = wide("volume")
    dollar_volume = (wide("close") * volume).astype("float32")

    adv = dollar_volume.rolling(UNIVERSE_ADV_DAYS, min_periods=UNIVERSE_ADV_DAYS).mean()
    in_univ = (closeunadj >= UNIVERSE_MIN_PRICE) & (adv >= UNIVERSE_MIN_DOLLAR_VOLUME)
    universe = in_univ.astype("float32").where(in_univ)

    panels = {
        "closeadj": closeadj,
        "closeunadj": closeunadj,
        "volume": volume,
        "dollar_volume": dollar_volume,
        "universe": universe,
    }
    panels["tr"] = total_return_panel(closeadj)
    for p in panels.values():
        p.index.name = "Date"
        p.columns.name = "Ticker"
    return panels


def performance_delisted(tickers: pd.Index, last_dates: pd.Series) -> set[str]:
    """Delisted tickers whose exit was a bankruptcy / liquidation / regulatory delisting."""
    a = load("actions", columns=["date", "action", "ticker"])
    a = a[a["action"].isin(PERFORMANCE_DELIST_ACTIONS) & a["ticker"].isin(tickers)]
    last = a["ticker"].map(last_dates)
    near = (a["date"] >= last - pd.Timedelta(days=180)) & (a["date"] <= last + pd.Timedelta(days=365))
    return set(a.loc[near, "ticker"])


def total_return_panel(closeadj: pd.DataFrame) -> pd.DataFrame:
    """
    Delisting-aware total-return index (Date x Ticker).

    - While listed: adjusted close, with short trading gaps forward-filled.
    - After a delisting: the exit value is reinvested in SPY. Exits caused by bankruptcy,
      liquidation or regulatory delisting also take DELIST_RETURN_PERFORMANCE on the last
      price (the last exchange print usually overstates what holders recovered).
    - Stocks still listed at the end of the data stay NaN after their last price.
    - Before the first price: NaN.
    """
    meta = eligible_tickers().set_index("ticker")
    spy = benchmark_closeadj().reindex(closeadj.index).ffill().to_numpy()
    arr = np.array(closeadj.ffill().to_numpy(), dtype="float64", copy=True)
    valid = closeadj.notna().to_numpy()
    n_days = len(closeadj.index)
    has_any = valid.any(axis=0)
    last_pos = np.where(has_any, n_days - 1 - np.argmax(valid[::-1], axis=0), -1)

    cols = closeadj.columns
    last_dates = pd.Series(closeadj.index[np.maximum(last_pos, 0)], index=cols)
    delisted = meta["isdelisted"].reindex(cols).eq("Y").to_numpy()
    perf = performance_delisted(cols, last_dates)

    for j, t in enumerate(cols):
        p = last_pos[j]
        if p < 0 or p == n_days - 1:
            continue
        if not delisted[j]:
            arr[p + 1 :, j] = np.nan
            continue
        exit_value = arr[p, j] * (1.0 + (DELIST_RETURN_PERFORMANCE if t in perf else 0.0))
        arr[p + 1 :, j] = exit_value * spy[p + 1 :] / spy[p]

    return pd.DataFrame(arr.astype("float32"), index=closeadj.index, columns=cols)


def save_panels(panels: dict[str, pd.DataFrame]) -> None:
    PANELS_DIR.mkdir(parents=True, exist_ok=True)
    for name, p in panels.items():
        p.to_parquet(PANELS_DIR / f"{name}.parquet")


def load_panel(name: str) -> pd.DataFrame:
    return pd.read_parquet(PANELS_DIR / f"{name}.parquet")


def backtest_prices() -> pd.DataFrame:
    """Delisting-aware total-return panel plus a SPY column, for `backtest.run_backtest`."""
    tr = load_panel("tr")
    tr[BENCHMARK] = benchmark_closeadj().reindex(tr.index).ffill().astype("float32")
    return tr


def universe_summary(universe: pd.DataFrame) -> pd.DataFrame:
    """Per-year: average stocks in the universe per day, and distinct stocks seen."""
    daily = universe.notna().sum(axis=1)
    by_year = daily.groupby(daily.index.year)
    distinct = universe.notna().groupby(universe.index.year).any().sum(axis=1)
    return pd.DataFrame(
        {"avg_daily_count": by_year.mean().round(0), "min_daily": by_year.min(), "distinct": distinct}
    )


__all__ = [
    "PANELS_DIR",
    "backtest_prices",
    "benchmark_closeadj",
    "build_panels",
    "eligible_tickers",
    "load_panel",
    "save_panels",
    "sector_map",
    "total_return_panel",
    "universe_summary",
]


if __name__ == "__main__":
    panels = build_panels()
    save_panels(panels)
    print(universe_summary(panels["universe"]).to_string())
    print(f"Distinct stocks ever in universe: {int(panels['universe'].notna().any().sum()):,}")
