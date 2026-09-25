#!/usr/bin/env python3
"""CLI: walk-forward train + evaluate (default focus: 1y).

Usage:
  python scripts/train_walkforward.py [horizons...] [--ex-winners]

--ex-winners removes HINDSIGHT_WINNERS from train + test (outputs tagged `ex5`).
"""

import sys

from pinky.config import HINDSIGHT_WINNERS
from pinky.train import DEFAULT_HORIZONS, run_all

if __name__ == "__main__":
    args = sys.argv[1:]
    ex_winners = "--ex-winners" in args
    horizons = [a for a in args if not a.startswith("--")] or list(DEFAULT_HORIZONS)
    if ex_winners:
        run_all(horizons=horizons, exclude=list(HINDSIGHT_WINNERS), tag="ex5")
    else:
        run_all(horizons=horizons)
