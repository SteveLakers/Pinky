"""Evaluation metrics for walk-forward reports (honest, no fake scores)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def _safe_spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")
    if np.nanstd(a) == 0 or np.nanstd(b) == 0:
        return float("nan")
    corr, _ = spearmanr(a, b)
    return float(corr)


def daily_rank_ic(df: pd.DataFrame, pred_col: str, actual_col: str) -> float:
    """Mean Spearman IC across dates (cross-sectional)."""
    ics = []
    for _, g in df.groupby("Date"):
        ic = _safe_spearman(g[pred_col].to_numpy(), g[actual_col].to_numpy())
        if not np.isnan(ic):
            ics.append(ic)
    return float(np.mean(ics)) if ics else float("nan")


def top_decile_hit_rate(
    df: pd.DataFrame,
    pred_col: str,
    beat_col: str,
    frac: float = 0.1,
) -> float:
    """Mean realized beat-rate among top predicted names each day."""
    rates = []
    for _, g in df.groupby("Date"):
        n = max(1, int(np.ceil(len(g) * frac)))
        top = g.nlargest(n, pred_col)
        rates.append(float(top[beat_col].mean()))
    return float(np.mean(rates)) if rates else float("nan")


def top_n_basket_excess(
    df: pd.DataFrame,
    pred_col: str,
    excess_col: str,
    n: int = 5,
) -> float:
    """Mean equal-weight excess of top-N predicted names each day."""
    vals = []
    for _, g in df.groupby("Date"):
        k = min(n, len(g))
        top = g.nlargest(k, pred_col)
        vals.append(float(top[excess_col].mean()))
    return float(np.mean(vals)) if vals else float("nan")


def universe_mean_excess(df: pd.DataFrame, excess_col: str) -> float:
    """Equal-weight all-names excess each day, then average."""
    vals = [float(g[excess_col].mean()) for _, g in df.groupby("Date")]
    return float(np.mean(vals)) if vals else float("nan")


def _monthly_dates(df: pd.DataFrame) -> pd.DatetimeIndex:
    """First available date of each month (limits overlap from year-long labels)."""
    d = pd.DatetimeIndex(sorted(pd.unique(df["Date"])))
    return pd.DatetimeIndex(pd.Series(d, index=d).groupby(d.to_period("M")).min())


def precision_at_k(df: pd.DataFrame, pred_col: str, top_col: str, k: int = 10) -> float:
    """
    Share of the model's top-k picks that end up in the future top decile.

    Sampled monthly. Random picking scores ~0.10 with a 10% top label.
    """
    months = set(_monthly_dates(df))
    vals = []
    for d, g in df[df["Date"].isin(months)].groupby("Date"):
        g = g.dropna(subset=[top_col])
        if len(g) < k:
            continue
        vals.append(float(g.nlargest(k, pred_col)[top_col].mean()))
    return float(np.mean(vals)) if vals else float("nan")


def winner_capture(
    df: pd.DataFrame,
    pred_col: str,
    stock_fwd_col: str,
    k: int = 10,
    n_winners: int = 20,
) -> float:
    """
    Time-weighted capture of big winners.

    For each calendar year, take the `n_winners` biggest forward-return stocks as of the
    first month; return the average share of that year's months each winner sat in the
    model's monthly top-k. Time-weighted so constant churn can't fake coverage:
    random picking scores ~k / universe size.
    """
    monthly = df[df["Date"].isin(set(_monthly_dates(df)))]
    rates = []
    for _, g in monthly.groupby(monthly["Date"].dt.year):
        first = g[g["Date"] == g["Date"].min()].dropna(subset=[stock_fwd_col])
        if len(first) < n_winners:
            continue
        winners = set(first.nlargest(n_winners, stock_fwd_col)["Ticker"])
        months = [set(m.nlargest(min(k, len(m)), pred_col)["Ticker"]) for _, m in g.groupby("Date")]
        rates.append(np.mean([len(winners & held) / len(winners) for held in months]))
    return float(np.mean(rates)) if rates else float("nan")


def brier_score(y_true: np.ndarray, p_pred: np.ndarray) -> float:
    return float(np.mean((p_pred - y_true) ** 2))


def calibration_table(
    y_true: np.ndarray,
    p_pred: np.ndarray,
    n_bins: int = 10,
) -> pd.DataFrame:
    """Reliability-style bins: predicted prob vs realized frequency."""
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    rows = []
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        if i == n_bins - 1:
            mask = (p_pred >= lo) & (p_pred <= hi)
        else:
            mask = (p_pred >= lo) & (p_pred < hi)
        if mask.sum() == 0:
            continue
        rows.append(
            {
                "bin_lo": lo,
                "bin_hi": hi,
                "n": int(mask.sum()),
                "pred_mean": float(p_pred[mask].mean()),
                "actual_rate": float(y_true[mask].mean()),
            }
        )
    return pd.DataFrame(rows)
