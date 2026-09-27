"""
Feature prep for ranking models.

1) Cross-sectional z-score or percentile rank by Date (grade stocks on a curve each day)
2) Drop highly correlated features (fit on train only — no test peeking)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pinky.dataset import feature_columns


# Features that are (almost) the same for every stock on a given day.
# They don't help rank stocks vs each other after CS-normalization.
MACRO_OR_REGIME = {
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
    "regime_bull",
    "regime_high_vol",
}


def cross_section_zscore(
    df: pd.DataFrame,
    cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    For each Date, z-score selected columns across tickers.

    Constant-within-day columns become 0 (no ranking info).
    """
    out = df.copy()
    cols = cols or [c for c in feature_columns(out) if c not in MACRO_OR_REGIME]

    for c in cols:
        g = out.groupby("Date")[c]
        mu = g.transform("mean")
        sd = g.transform("std")
        # pandas group std uses ddof=1; treat tiny/zero as missing
        sd = sd.mask(sd.isna() | (sd < 1e-12), np.nan)
        out[c] = (out[c].astype(float) - mu) / sd

    out[cols] = out[cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return out


def cross_section_rank(
    df: pd.DataFrame,
    cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    For each Date, percentile-rank selected columns across tickers, centered on 0 (-0.5 … +0.5).

    Outliers can't dominate. Missing values become 0 (the middle of the day).
    Uses only each day's cross-section, so it can run once before the walk-forward split.
    """
    out = df.copy()
    cols = cols or ranking_feature_cols(out)
    ranks = out[["Date", *cols]].replace([np.inf, -np.inf], np.nan).groupby("Date")[cols].rank(pct=True)
    out[cols] = (ranks - 0.5).fillna(0.0).astype("float32")
    return out


def drop_correlated_features(
    train: pd.DataFrame,
    cols: list[str],
    threshold: float = 0.92,
) -> list[str]:
    """
    Greedy drop: among highly correlated pairs on TRAIN only, keep the first.
    """
    if len(cols) < 2:
        return list(cols)

    corr = train[cols].corr().abs()
    keep: list[str] = []
    dropped: list[str] = []

    for c in cols:
        if c in dropped:
            continue
        keep.append(c)
        for other in cols:
            if other == c or other in dropped or other in keep:
                continue
            if corr.loc[c, other] >= threshold:
                dropped.append(other)

    if dropped:
        print(f"[prep] dropped {len(dropped)} correlated features: {dropped}")
    return keep


def ranking_feature_cols(df: pd.DataFrame) -> list[str]:
    """Stock-differentiating features only (exclude pure macro/regime)."""
    return [c for c in feature_columns(df) if c not in MACRO_OR_REGIME]


def prepare_fold_frames(
    train: pd.DataFrame,
    test: pd.DataFrame,
    corr_threshold: float = 0.92,
    zscore: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """
    Apply CS z-score to train/test (skip with `zscore=False` if features are already
    ranked), then select de-correlated feature set from train.
    """
    base_cols = ranking_feature_cols(train)
    if zscore:
        train = cross_section_zscore(train, cols=base_cols)
        test = cross_section_zscore(test, cols=base_cols)
    kept = drop_correlated_features(train, base_cols, threshold=corr_threshold)
    return train, test, kept
