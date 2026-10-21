"""
Tradeable portfolio backtest on out-of-sample (walk-forward test) predictions.

- Rebalance on the first test day of each month (or every test date with `rebalance="weekly"`).
- Hold equal-weight top-N by model score until the next rebalance
  (N fixed, or a fraction of each date's stocks).
- Optional sector cap: no sector may exceed `max_sector_share` of picks
  (skip to the next-best name in another sector).
- Optional holding buffer: a holding is kept while it ranks in the top `buffer_mult` x N.
- Costs: `cost_bps` per side on every dollar traded (buys + sells),
  using drifted weights, so only real turnover is charged.
- Compare to SPY and to an equal-weight universe basket over the same windows.
- With `tradeable` (Date x Ticker, True = a real traded close that day), new buys and the
  universe basket need a real price on the trade day; holdings already owned may stay (their
  value keeps following the delisting-aware `prices`).
- Max drawdown uses the daily value of each holding period (`path` columns), costs included.

Version 2 (2026-10-21, code review): `tradeable` fills + daily drawdown from the starting value.
Version 1 (through batch 2): new buys could fill at synthetic post-delisting prices; drawdown
was sampled at rebalance dates and skipped a loss in the first period.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from pinky.config import (
    BACKTEST_COST_BPS,
    BACKTEST_TOP_N,
    BENCHMARK,
    TICKER_SECTOR,
    UNIVERSE_STOCKS,
)
from pinky.metrics import daily_rank_ic
from pinky.raw_io import adj_close_series, load_raw_ticker

HOLD_DAYS_LAST = 21  # final period has no next rebalance; hold ~1 month
HOLD_DAYS_LAST_WEEKLY = 5
BACKTEST_VERSION = 2
PATH_COLS = ["path", "spy_path"]  # daily values within each period (not saved to CSV)


def load_price_panel(tickers: list[str]) -> pd.DataFrame:
    """Date x ticker adjusted close. Missing tickers are skipped (reported)."""
    cols = {}
    missing = []
    for t in tickers:
        try:
            cols[t] = adj_close_series(load_raw_ticker(t))
        except FileNotFoundError:
            missing.append(t)
    if missing:
        print(f"[backtest] missing raw prices for: {missing}")
    return pd.DataFrame(cols).sort_index()


def monthly_rebalance_dates(pred_dates: pd.Series) -> list[pd.Timestamp]:
    d = pd.DatetimeIndex(sorted(pd.unique(pred_dates)))
    first_of_month = pd.Series(d, index=d).groupby(d.to_period("M")).min()
    return list(first_of_month)


def rebalance_dates(pred_dates: pd.Series, rebalance: str = "monthly") -> list[pd.Timestamp]:
    if rebalance == "monthly":
        return monthly_rebalance_dates(pred_dates)
    if rebalance == "weekly":
        return list(pd.DatetimeIndex(sorted(pd.unique(pred_dates))))
    raise ValueError(f"rebalance must be 'monthly' or 'weekly', got {rebalance!r}")


def _next_day(d: pd.Timestamp, calendar: pd.DatetimeIndex, lag: int = 1) -> pd.Timestamp | None:
    pos = calendar.searchsorted(d) + lag
    return calendar[pos] if pos < len(calendar) else None


def _period_end(
    i: int,
    rebal: list[pd.Timestamp],
    calendar: pd.DatetimeIndex,
    hold_last: int = HOLD_DAYS_LAST,
) -> pd.Timestamp | None:
    if i + 1 < len(rebal):
        return _next_day(rebal[i + 1], calendar)
    pos = calendar.searchsorted(rebal[i]) + 1 + hold_last
    return calendar[min(pos, len(calendar) - 1)]


def pick_top(
    g: pd.DataFrame,
    score_col: str,
    top_n: int,
    max_sector_share: float | None = None,
    sectors: dict[str, str] | None = None,
    held: set[str] | None = None,
    hold_rank: int | None = None,
) -> list[str]:
    """
    Top-N tickers by score, optionally capping names per sector.

    With `held` and `hold_rank`, current holdings still ranked in the top `hold_rank`
    are kept first; the remaining slots go to the best-ranked other names.
    """
    ranked = g.sort_values(score_col, ascending=False)["Ticker"].tolist()
    n = min(top_n, len(ranked))
    if held and hold_rank:
        keep = [t for t in ranked[:hold_rank] if t in held]
        kept = set(keep)
        ranked = keep + [t for t in ranked if t not in kept]
    if max_sector_share is None:
        return ranked[:n]
    sectors = sectors or TICKER_SECTOR
    cap = max(1, math.floor(max_sector_share * n + 1e-9))
    counts: dict[str, int] = {}
    picks: list[str] = []
    for t in ranked:
        s = sectors.get(t, "Other")
        if counts.get(s, 0) >= cap:
            continue
        picks.append(t)
        counts[s] = counts.get(s, 0) + 1
        if len(picks) == n:
            break
    return picks


def run_backtest(
    preds: pd.DataFrame,
    score_col: str,
    prices: pd.DataFrame,
    top_n: int = BACKTEST_TOP_N,
    cost_bps: float = BACKTEST_COST_BPS,
    exclude: set[str] | None = None,
    max_sector_share: float | None = None,
    sectors: dict[str, str] | None = None,
    top_frac: float | None = None,
    buffer_mult: float | None = None,
    rebalance: str = "monthly",
    tradeable: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    One row per holding period (gross, cost, net, SPY, universe, turnover, daily paths).

    Signal at close of rebalance day D; trade at close of D+1 (no same-close fill).
    `top_frac` holds the top fraction of each date's stocks instead of `top_n`.
    `buffer_mult` keeps a holding while it ranks in the top `buffer_mult` x N.
    `rebalance="weekly"` trades on every prediction date instead of monthly.
    `tradeable` (see module docstring): names without a real price on D+1 can't be bought.
    """
    calendar = prices.index
    rebal = rebalance_dates(preds["Date"], rebalance)
    hold_last = HOLD_DAYS_LAST_WEEKLY if rebalance == "weekly" else HOLD_DAYS_LAST
    by_date = {d: g for d, g in preds.groupby("Date")}
    prev_drift = pd.Series(dtype=float)
    rows = []

    for i, signal_day in enumerate(rebal):
        d = _next_day(signal_day, calendar)
        end = _period_end(i, rebal, calendar, hold_last)
        if d is None or end is None or end <= d:
            continue

        g = by_date[signal_day]
        g = g[g["Ticker"].isin(prices.columns)]
        if exclude:
            g = g[~g["Ticker"].isin(exclude)]
        p0 = prices.loc[d, g["Ticker"]]
        g = g[p0.notna().to_numpy()]
        fresh = np.ones(len(g), dtype=bool)  # can be bought on day d
        if tradeable is not None:
            fresh = tradeable.loc[d].reindex(g["Ticker"], fill_value=False).to_numpy(dtype=bool)
            keep = fresh | g["Ticker"].isin(prev_drift.index).to_numpy()
            g, fresh = g[keep], fresh[keep]
        if g.empty:
            continue

        stock_ret = prices.loc[end, g["Ticker"]] / prices.loc[d, g["Ticker"]] - 1.0
        stock_ret = stock_ret.fillna(0.0)

        n = max(1, math.ceil(top_frac * len(g))) if top_frac else top_n
        hold_rank = math.ceil(buffer_mult * n) if buffer_mult else None
        picks = pick_top(
            g, score_col, n, max_sector_share, sectors,
            held=set(prev_drift.index), hold_rank=hold_rank,
        )
        target = pd.Series(1.0 / len(picks), index=picks)
        window = prices.loc[d:end, picks]
        rel = (window / window.iloc[0]).ffill().fillna(1.0)
        rel.iloc[-1] = 1.0 + stock_ret.reindex(picks).to_numpy()
        spy_window = prices.loc[d:end, BENCHMARK]

        all_names = target.index.union(prev_drift.index)
        turnover = float(
            (target.reindex(all_names, fill_value=0.0)
             - prev_drift.reindex(all_names, fill_value=0.0)).abs().sum()
        )
        cost = turnover * cost_bps / 1e4

        gross = float((target * stock_ret.reindex(picks)).sum())
        net = (1.0 - cost) * (1.0 + gross) - 1.0

        spy = float(prices.loc[end, BENCHMARK] / prices.loc[d, BENCHMARK] - 1.0)
        univ = float(stock_ret.to_numpy()[fresh].mean())

        grown = target * (1.0 + stock_ret.reindex(picks))
        prev_drift = grown / grown.sum()

        rows.append(
            {
                "start": d,
                "end": end,
                "n_picks": len(picks),
                "picks": ",".join(picks),
                "turnover": turnover,
                "cost": cost,
                "gross": gross,
                "net": net,
                "spy": spy,
                "universe_ew": univ,
                "net_minus_spy": net - spy,
                "path": tuple(rel.to_numpy(dtype=float) @ target.to_numpy()),
                "spy_path": tuple(spy_window.to_numpy(dtype=float) / float(spy_window.iloc[0])),
            }
        )

    return pd.DataFrame(rows)


def between_years(bt: pd.DataFrame, first: int | None = None, last: int | None = None) -> pd.DataFrame:
    """Holding periods that start in [first, last] (either end open)."""
    year = bt["start"].dt.year
    mask = pd.Series(True, index=bt.index)
    if first is not None:
        mask &= year >= first
    if last is not None:
        mask &= year <= last
    return bt[mask]


def with_cost(bt: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    """Same trades re-priced at another cost level (picks and turnover don't depend on cost)."""
    cost = bt["turnover"] * cost_bps / 1e4
    net = (1.0 - cost) * (1.0 + bt["gross"]) - 1.0
    return bt.assign(cost=cost, net=net, net_minus_spy=net - bt["spy"])


def _cagr(period_rets: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> float:
    years = (end - start).days / 365.25
    total = float((1.0 + period_rets).prod())
    return total ** (1.0 / years) - 1.0 if years > 0 else float("nan")


def _max_drawdown(period_rets: pd.Series) -> float:
    """Worst fall from a peak, sampled at period ends; the starting value 1 counts as a peak."""
    curve = np.concatenate([[1.0], (1.0 + period_rets.to_numpy(dtype=float)).cumprod()])
    return float((curve / np.maximum.accumulate(curve) - 1.0).min())


def _daily_drawdown(paths: pd.Series, costs: pd.Series | None = None) -> float:
    """Worst fall from a peak using each period's daily values; costs come off at the period start."""
    value, pieces = 1.0, [np.array([1.0])]
    for i, path in enumerate(paths):
        keep = 1.0 - (float(costs.iloc[i]) if costs is not None else 0.0)
        piece = value * keep * np.asarray(path, dtype=float)
        pieces.append(piece)
        value = piece[-1]
    curve = np.concatenate(pieces)
    return float((curve / np.maximum.accumulate(curve) - 1.0).min())


def summarize_backtest(bt: pd.DataFrame) -> dict:
    if bt.empty:
        return {}
    start, end = bt["start"].iloc[0], bt["end"].iloc[-1]
    years = (end - start).days / 365.25
    return {
        "start": start.date().isoformat(),
        "end": end.date().isoformat(),
        "months": len(bt),
        "cagr_net": _cagr(bt["net"], start, end),
        "cagr_gross": _cagr(bt["gross"], start, end),
        "cagr_spy": _cagr(bt["spy"], start, end),
        "cagr_universe_ew": _cagr(bt["universe_ew"], start, end),
        "total_net": float((1.0 + bt["net"]).prod() - 1.0),
        "total_spy": float((1.0 + bt["spy"]).prod() - 1.0),
        "months_beat_spy": float((bt["net"] > bt["spy"]).mean()),
        "avg_monthly_turnover": float(bt["turnover"].mean()),
        "annual_cost_drag": float(bt["cost"].sum() / years) if years > 0 else float("nan"),
        "max_dd_net": _daily_drawdown(bt["path"], bt["cost"]) if "path" in bt else _max_drawdown(bt["net"]),
        "max_dd_spy": _daily_drawdown(bt["spy_path"]) if "spy_path" in bt else _max_drawdown(bt["spy"]),
        "backtest_version": BACKTEST_VERSION,
    }


def yearly_table(bt: pd.DataFrame) -> pd.DataFrame:
    y = bt.assign(year=bt["start"].dt.year).groupby("year")
    return pd.DataFrame(
        {
            "net": y["net"].apply(lambda r: (1 + r).prod() - 1),
            "spy": y["spy"].apply(lambda r: (1 + r).prod() - 1),
            "universe_ew": y["universe_ew"].apply(lambda r: (1 + r).prod() - 1),
        }
    ).assign(net_minus_spy=lambda t: t["net"] - t["spy"])


def pick_sector_share(bt: pd.DataFrame, sectors: dict[str, str] | None = None) -> pd.Series:
    """Average share of picks per sector (checks tech concentration)."""
    sectors = sectors or TICKER_SECTOR
    counts: dict[str, float] = {}
    for picks in bt["picks"]:
        names = picks.split(",")
        for t in names:
            s = sectors.get(t, "Other")
            counts[s] = counts.get(s, 0.0) + 1.0 / len(names)
    return (pd.Series(counts) / len(bt)).sort_values(ascending=False)


def momentum_scores(preds: pd.DataFrame, prices: pd.DataFrame, lookback: int = 252) -> pd.DataFrame:
    """Naive baseline: score = trailing 12m return (skip last month), same dates/names as preds."""
    dates = pd.DatetimeIndex(sorted(preds["Date"].unique()))
    pos = prices.index.get_indexer(dates)
    ok = pos >= lookback
    a = prices.to_numpy(dtype=float)
    mom = pd.DataFrame(
        a[pos[ok] - 21] / a[pos[ok] - lookback] - 1.0, index=dates[ok], columns=prices.columns
    )
    mom.index.name, mom.columns.name = "Date", "Ticker"
    long = mom.stack().rename("mom_12_1").reset_index()
    return preds[["Date", "Ticker"]].merge(long, on=["Date", "Ticker"], how="left").dropna()


def top_winners(prices: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, k: int = 5) -> list[str]:
    """The k best total-return stocks over [start, end] (hindsight set for a stress test)."""
    window = prices.loc[start:end].drop(columns=[BENCHMARK], errors="ignore")
    total = window.ffill().iloc[-1] / window.bfill().iloc[0] - 1.0
    return total.nlargest(k).index.tolist()


def default_prices() -> pd.DataFrame:
    return load_price_panel([BENCHMARK, *UNIVERSE_STOCKS])


def within_sector_ic(
    preds: pd.DataFrame, score_col: str, actual_col: str, sectors: dict[str, str] | None = None
) -> pd.Series:
    """Mean daily rank IC computed inside each sector (does the model rank within a sector?)."""
    sectors = sectors or TICKER_SECTOR
    df = preds.assign(sector=preds["Ticker"].map(sectors).fillna("Other"))
    out = {s: daily_rank_ic(g, score_col, actual_col) for s, g in df.groupby("sector")}
    return pd.Series(out).sort_values(ascending=False)


__all__ = [
    "BACKTEST_VERSION",
    "PATH_COLS",
    "between_years",
    "default_prices",
    "load_price_panel",
    "momentum_scores",
    "monthly_rebalance_dates",
    "pick_sector_share",
    "pick_top",
    "rebalance_dates",
    "run_backtest",
    "summarize_backtest",
    "top_winners",
    "with_cost",
    "within_sector_ic",
    "yearly_table",
]
