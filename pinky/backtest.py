"""
Tradeable portfolio backtest on out-of-sample (walk-forward test) predictions.

- Rebalance on the first test day of each month.
- Hold equal-weight top-N by model score until the next rebalance
  (N fixed, or a fraction of each date's stocks).
- Optional sector cap: no sector may exceed `max_sector_share` of picks
  (skip to the next-best name in another sector).
- Optional holding buffer: a holding is kept while it ranks in the top `buffer_mult` x N.
- Costs: `cost_bps` per side on every dollar traded (buys + sells),
  using drifted weights, so only real turnover is charged.
- Compare to SPY and to an equal-weight universe basket over the same windows.
"""

from __future__ import annotations

import math

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


def _next_day(d: pd.Timestamp, calendar: pd.DatetimeIndex, lag: int = 1) -> pd.Timestamp | None:
    pos = calendar.searchsorted(d) + lag
    return calendar[pos] if pos < len(calendar) else None


def _period_end(
    i: int,
    rebal: list[pd.Timestamp],
    calendar: pd.DatetimeIndex,
) -> pd.Timestamp | None:
    if i + 1 < len(rebal):
        return _next_day(rebal[i + 1], calendar)
    pos = calendar.searchsorted(rebal[i]) + 1 + HOLD_DAYS_LAST
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
) -> pd.DataFrame:
    """
    One row per holding period (gross, cost, net, SPY, universe, turnover).

    Signal at close of rebalance day D; trade at close of D+1 (no same-close fill).
    `top_frac` holds the top fraction of each date's stocks instead of `top_n`.
    `buffer_mult` keeps a holding while it ranks in the top `buffer_mult` x N.
    """
    calendar = prices.index
    rebal = monthly_rebalance_dates(preds["Date"])
    by_date = {d: g for d, g in preds.groupby("Date")}
    prev_drift = pd.Series(dtype=float)
    rows = []

    for i, signal_day in enumerate(rebal):
        d = _next_day(signal_day, calendar)
        end = _period_end(i, rebal, calendar)
        if d is None or end is None or end <= d:
            continue

        g = by_date[signal_day]
        g = g[g["Ticker"].isin(prices.columns)]
        if exclude:
            g = g[~g["Ticker"].isin(exclude)]
        p0 = prices.loc[d, g["Ticker"]]
        g = g[p0.notna().to_numpy()]
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

        all_names = target.index.union(prev_drift.index)
        turnover = float(
            (target.reindex(all_names, fill_value=0.0)
             - prev_drift.reindex(all_names, fill_value=0.0)).abs().sum()
        )
        cost = turnover * cost_bps / 1e4

        gross = float((target * stock_ret.reindex(picks)).sum())
        net = (1.0 - cost) * (1.0 + gross) - 1.0

        spy = float(prices.loc[end, BENCHMARK] / prices.loc[d, BENCHMARK] - 1.0)
        univ = float(stock_ret.mean())

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
            }
        )

    return pd.DataFrame(rows)


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
    curve = (1.0 + period_rets).cumprod()
    return float((curve / curve.cummax() - 1.0).min())


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
        "max_dd_net": _max_drawdown(bt["net"]),
        "max_dd_spy": _max_drawdown(bt["spy"]),
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
    "default_prices",
    "load_price_panel",
    "momentum_scores",
    "monthly_rebalance_dates",
    "pick_sector_share",
    "pick_top",
    "run_backtest",
    "summarize_backtest",
    "top_winners",
    "with_cost",
    "within_sector_ic",
    "yearly_table",
]
