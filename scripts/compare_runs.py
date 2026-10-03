#!/usr/bin/env python3
"""
Compare saved pit runs side by side (no retraining).

Reads each run's walk-forward metrics, backtest stats and out-of-sample predictions
from `artifacts/` and prints one markdown table (rows = metrics, columns = runs).

Usage: PYTHONPATH=. python scripts/compare_runs.py v6_pit v7_pit [more runs...]
"""

from __future__ import annotations

import sys

import pandas as pd

from pinky.config import BACKTEST_TOP_N, PROJECT_ROOT, REPORT_SPLIT_YEAR
from pinky.metrics import acquired_share, precision_at_k
from pinky.universe import acquisition_dates

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
SIGNALS = {"Ridge": "pred_excess_ridge", "LightGBM": "pred_excess_lgbm", "Blend": "pred_excess_blend"}
PORTFOLIOS = ["Top-10 + buffer", "Top 10% + buffer"]


def _pct(x: float) -> str:
    return f"{100 * x:+.1f}%"


def winner_crash_rates(p: pd.DataFrame, pred: str, k: int = BACKTEST_TOP_N) -> tuple[float, float]:
    """Monthly top-k picks (first test date of each month): share in the day's top 10%, share < −50% vs SPY."""
    first = p.groupby(p["Date"].dt.to_period("M"))["Date"].transform("min")
    m = p[p["Date"] == first].dropna(subset=["excess_1y"])
    top = m.sort_values(["Date", pred], ascending=[True, False]).groupby("Date").head(k)
    return float(top["top_1y"].mean()), float((top["excess_1y"] < -0.5).mean())


def run_column(run: str, acq: pd.Series) -> dict[str, str]:
    m = pd.read_csv(ARTIFACTS_DIR / f"walkforward_metrics_{run}.csv")
    s = pd.read_csv(ARTIFACTS_DIR / f"backtest_stats_1y_{run}.csv")
    p = pd.read_parquet(ARTIFACTS_DIR / f"oos_preds_1y_{run}.parquet")
    late = pd.to_datetime(m["test_start"]).dt.year >= REPORT_SPLIT_YEAR
    split = next(x for x in s["period"].unique() if str(x).startswith(str(REPORT_SPLIT_YEAR)))

    col: dict[str, str] = {"Stocks scored per date (avg)": f"{p.groupby('Date').size().mean():,.0f}"}
    for name in ("ridge", "lgbm", "blend"):
        col[f"Rank IC, {name}"] = f"{m[f'ic_{name}'].mean():.3f}"
        col[f"Rank IC {split}, {name}"] = f"{m.loc[late, f'ic_{name}'].mean():.3f}"

    def cagr(signal: str, portfolio: str, period: str = "all") -> float:
        r = s[(s["signal"] == signal) & (s["portfolio"] == portfolio) & (s["period"] == period)]
        return float(r["cagr_net"].iloc[0])

    for portfolio in PORTFOLIOS:
        for signal in SIGNALS:
            col[f"CAGR {portfolio}, {signal}"] = _pct(cagr(signal, portfolio))
            col[f"CAGR {portfolio} {split}, {signal}"] = _pct(cagr(signal, portfolio, split))
    spy = s[s["period"] == "all"]["cagr_spy"].iloc[0]
    spy_late = s[s["period"] == split]["cagr_spy"].iloc[0]
    col["SPY CAGR (all / late)"] = f"{_pct(spy)} / {_pct(spy_late)}"
    ew = s[s["period"] == "all"]["cagr_universe_ew"].iloc[0]
    ew_late = s[s["period"] == split]["cagr_universe_ew"].iloc[0]
    col["Equal-weight universe CAGR (all / late)"] = f"{_pct(ew)} / {_pct(ew_late)}"

    for signal, pred in SIGNALS.items():
        col[f"Precision@{BACKTEST_TOP_N}, {signal}"] = f"{precision_at_k(p, pred, 'top_1y', k=BACKTEST_TOP_N):.3f}"
        col[f"Acquired ≤ 6m, top-{BACKTEST_TOP_N}, {signal}"] = (
            f"{acquired_share(p, pred, acq, k=BACKTEST_TOP_N):.1%}"
        )
        big, crash = winner_crash_rates(p, pred)
        col[f"Monthly top-{BACKTEST_TOP_N} big winners / crashes, {signal}"] = f"{big:.1%} / {crash:.1%}"
    return col


def main(runs: list[str]) -> str:
    acq = acquisition_dates()
    cols = {run: run_column(run, acq) for run in runs}
    rows = list(next(iter(cols.values())))
    lines = ["| Metric | " + " | ".join(runs) + " |", "|---|" + "---|" * len(runs)]
    lines += [f"| {r} | " + " | ".join(cols[run].get(r, "") for run in runs) + " |" for r in rows]
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print(main(sys.argv[1:]))
