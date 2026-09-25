#!/usr/bin/env python3
"""CLI: print walk-forward fold summary (with purge) for each horizon."""

from pinky.dataset import load_dataset
from pinky.config import HORIZONS
from pinky.walkforward import summarize_folds

if __name__ == "__main__":
    df = load_dataset()
    for horizon in HORIZONS:
        summary = summarize_folds(df, horizon)
        print(f"\n=== horizon {horizon} ({HORIZONS[horizon]}d) | folds={len(summary)} ===")
        if summary.empty:
            print("No folds.")
            continue
        print(summary.to_string(index=False))
        print(
            f"purged total={int(summary['n_purged'].sum())} | "
            f"avg train={summary['n_train'].mean():.0f} | "
            f"avg test={summary['n_test'].mean():.0f}"
        )
