#!/usr/bin/env python3
"""CLI: walk-forward train + evaluate (default focus: 1y).

Usage:
  python scripts/train_walkforward.py [horizons...] [--ex-winners] [--pit] [--without=young,size]
                                      [--with=growth,margins] [--placebo[=<group>]] [--seed=N]
  python scripts/train_walkforward.py --report-only=<run name, e.g. v6_pit>

--ex-winners removes HINDSIGHT_WINNERS from train + test (outputs tagged `ex5`).
--pit uses the Sharadar point-in-time universe (outputs tagged `pit`; 2022+ holdout untouched).
--without switches off some of the pit model fixes (train.MODEL_FIXES) for ablations
  (outputs tagged `no-<fix>`).
--with switches on company data under test (train.FEATURE_GROUPS, off by default; outputs
  tagged `with-<group>`).
--placebo=<group> shuffles that group's features across stocks within each date (the group
  must be on via --with; outputs tagged `placebo-<group>`). Bare --placebo = growth (v8 tag `placebo`).
--seed sets model randomness (outputs tagged `s<N>` unless N is the default 42).
--report-only rebuilds a saved pit run's report from its predictions (no retraining).
"""

import sys

from pinky.config import HINDSIGHT_WINNERS
from pinky.train import DEFAULT_HORIZONS, DEFAULT_SEED, rewrite_summary, run_all

if __name__ == "__main__":
    args = sys.argv[1:]
    ex_winners = "--ex-winners" in args
    pit = "--pit" in args
    placebo = next(
        ("growth" if a == "--placebo" else a.split("=", 1)[1] for a in args if a == "--placebo" or a.startswith("--placebo=")),
        None,
    )
    report_only = next((a.split("=", 1)[1] for a in args if a.startswith("--report-only=")), None)
    without = next((a.split("=", 1)[1].split(",") for a in args if a.startswith("--without=")), [])
    with_ = next((a.split("=", 1)[1].split(",") for a in args if a.startswith("--with=")), [])
    seed = int(next((a.split("=", 1)[1] for a in args if a.startswith("--seed=")), DEFAULT_SEED))
    known = ("--ex-winners", "--pit", "--placebo", "--report-only=", "--without=", "--with=", "--seed=")
    unknown = [a for a in args if a.startswith("--") and not a.startswith(known)]
    unknown += [a for a in args if a.startswith("--placebo") and a != "--placebo" and not a.startswith("--placebo=")]
    if unknown:
        sys.exit(f"Unknown options: {unknown}")
    horizons = [a for a in args if not a.startswith("--")] or list(DEFAULT_HORIZONS)
    if report_only:
        rewrite_summary(report_only, horizons=horizons)
    elif ex_winners:
        run_all(
            horizons=horizons, exclude=list(HINDSIGHT_WINNERS), tag="ex5", pit=pit,
            without=without, with_=with_, placebo=placebo, seed=seed,
        )
    else:
        run_all(horizons=horizons, pit=pit, without=without, with_=with_, placebo=placebo, seed=seed)
