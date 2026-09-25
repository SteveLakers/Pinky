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
