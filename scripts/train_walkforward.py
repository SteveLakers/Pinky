#!/usr/bin/env python3
"""CLI: walk-forward train + evaluate (default focus: 1y).

Usage:
  python scripts/train_walkforward.py [horizons...] [--ex-winners] [--pit] [--without=young,size]
  python scripts/train_walkforward.py --report-only=<run name, e.g. v6_pit>

--ex-winners removes HINDSIGHT_WINNERS from train + test (outputs tagged `ex5`).
--pit uses the Sharadar point-in-time universe (outputs tagged `pit`; 2022+ holdout untouched).
--without switches off some of the pit model fixes (train.MODEL_FIXES) for ablations
  (outputs tagged `no-<fix>`).
--report-only rebuilds a saved pit run's report from its predictions (no retraining).
"""

import sys

from pinky.config import HINDSIGHT_WINNERS
from pinky.train import DEFAULT_HORIZONS, rewrite_summary, run_all

if __name__ == "__main__":
    args = sys.argv[1:]
    ex_winners = "--ex-winners" in args
    pit = "--pit" in args
    report_only = next((a.split("=", 1)[1] for a in args if a.startswith("--report-only=")), None)
    without = next((a.split("=", 1)[1].split(",") for a in args if a.startswith("--without=")), [])
    horizons = [a for a in args if not a.startswith("--")] or list(DEFAULT_HORIZONS)
    if report_only:
        rewrite_summary(report_only, horizons=horizons)
    elif ex_winners:
        run_all(horizons=horizons, exclude=list(HINDSIGHT_WINNERS), tag="ex5", pit=pit, without=without)
    else:
        run_all(horizons=horizons, pit=pit, without=without)
