"""
Walk-forward folds + label-window purge.

- Expanding train window, fixed-length test folds (no random splits).
- Purge removes train rows whose forward label window overlaps the test period.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from pinky.config import HORIZONS, WF_MIN_TRAIN_DAYS, WF_STEP_DAYS, WF_TEST_DAYS
from pinky.dataset import feature_columns


@dataclass(frozen=True)
class WalkForwardFold:
    fold_id: int
    horizon: str
    horizon_days: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    train: pd.DataFrame
    test: pd.DataFrame
    n_train_before_purge: int
    n_purged: int


def _trading_calendar(df: pd.DataFrame) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(sorted(df["Date"].unique()))


def _slice_by_dates(
    df: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.DataFrame:
    mask = (df["Date"] >= start) & (df["Date"] <= end)
    return df.loc[mask].copy()


def purge_train(
    train: pd.DataFrame,
    test_start: pd.Timestamp,
    calendar: pd.DatetimeIndex,
    horizon_days: int,
) -> tuple[pd.DataFrame, int]:
    """
    Drop train rows whose label uses prices on/after test_start.

    Label at date D with horizon H uses trading day D+H.
    Purge if D is among the last `horizon_days` trading days before test_start
    (i.e. D + H would reach into the test window).
    """
    if horizon_days <= 0:
        raise ValueError("horizon_days must be positive")

    # First calendar position at or after test_start
    pos = calendar.searchsorted(test_start)
    if pos == 0:
        # Nothing before test — purge everything
        return train.iloc[0:0].copy(), len(train)

    purge_start_pos = max(0, pos - horizon_days)
    purge_start = calendar[purge_start_pos]

    before = len(train)
    kept = train.loc[train["Date"] < purge_start].copy()
    n_purged = before - len(kept)
    return kept, n_purged


def iter_walk_forward_folds(
    df: pd.DataFrame,
    horizon: str,
    min_train_days: int = WF_MIN_TRAIN_DAYS,
    test_days: int = WF_TEST_DAYS,
    step_days: int = WF_STEP_DAYS,
):
    """
    Yield purged walk-forward folds for one horizon.

    Train = all rows with Date < test_start (then purged).
    Test = [test_start, test_end] and must have a non-null label for this horizon.
    """
    if horizon not in HORIZONS:
        raise ValueError(f"Unknown horizon {horizon!r}; expected one of {list(HORIZONS)}")

    horizon_days = HORIZONS[horizon]
    excess_col = f"excess_{horizon}"
    beat_col = f"beat_{horizon}"

    calendar = _trading_calendar(df)
    if len(calendar) < min_train_days + test_days:
        raise ValueError(
            f"Not enough trading days ({len(calendar)}) for "
            f"min_train={min_train_days} + test={test_days}"
        )

    fold_id = 0
    # First test starts after min_train_days of history
    test_start_pos = min_train_days

    while test_start_pos + test_days <= len(calendar):
        test_start = calendar[test_start_pos]
        test_end = calendar[test_start_pos + test_days - 1]
        train_start = calendar[0]
        train_end = calendar[test_start_pos - 1]

        raw_train = _slice_by_dates(df, train_start, train_end)
        raw_test = _slice_by_dates(df, test_start, test_end)

        # Test rows need this horizon's labels
        test = raw_test.dropna(subset=[excess_col, beat_col]).copy()
        train_purged, n_purged = purge_train(
            raw_train, test_start, calendar, horizon_days
        )
        # Train also needs labels for this horizon
        train = train_purged.dropna(subset=[excess_col, beat_col]).copy()

        if len(train) == 0 or len(test) == 0:
            test_start_pos += step_days
            continue

        yield WalkForwardFold(
            fold_id=fold_id,
            horizon=horizon,
            horizon_days=horizon_days,
            train_start=train_start,
            train_end=train_end,
            test_start=test_start,
            test_end=test_end,
            train=train,
            test=test,
            n_train_before_purge=len(raw_train),
            n_purged=n_purged,
        )
        fold_id += 1
        test_start_pos += step_days


def summarize_folds(df: pd.DataFrame, horizon: str) -> pd.DataFrame:
    """Small table describing folds (no model training)."""
    rows = []
    for fold in iter_walk_forward_folds(df, horizon):
        rows.append(
            {
                "fold_id": fold.fold_id,
                "horizon": fold.horizon,
                "train_start": fold.train_start.date(),
                "train_end": fold.train_end.date(),
                "test_start": fold.test_start.date(),
                "test_end": fold.test_end.date(),
                "n_train": len(fold.train),
                "n_test": len(fold.test),
                "n_purged": fold.n_purged,
                "n_features": len(feature_columns(fold.train)),
            }
        )
    return pd.DataFrame(rows)
