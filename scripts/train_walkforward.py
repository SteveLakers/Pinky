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
  tagged `with-<group>`): growth, margins, and growth round 2's ear, sue, cagr, steady
  (one column each) or growth2 (all four; not together with the single ones).
--placebo=<group> shuffles that group's features across stocks within each date (the group
  must be on via --with; outputs tagged `placebo-<group>`). Bare --placebo = growth (v8 tag `placebo`).
--seed sets model randomness (outputs tagged `s<N>` unless N is the default 42).
--report-only re-scores a saved pit run from its predictions with today's backtest (no retraining;
  old outputs are copied to artifacts/superseded/ first).
Misspelled, empty or repeated options stop the run before any data loads.
"""

import sys

from pinky.config import HINDSIGHT_WINNERS
from pinky.train import DEFAULT_HORIZONS, DEFAULT_SEED, rewrite_summary, run_all

FLAGS = ("--ex-winners", "--pit", "--placebo")
VALUES = ("--placebo=", "--report-only=", "--without=", "--with=", "--seed=")


def parse_args(args: list[str]) -> dict:
    """Exact flags only: a misspelled or malformed option (e.g. `--pit=true`) stops the run."""
    unknown = [a for a in args if a.startswith("--") and a not in FLAGS and not a.startswith(VALUES)]
    empty = [a for a in args if a.startswith(VALUES) and not a.split("=", 1)[1]]
    repeated = sorted({a.split("=", 1)[0] for a in args if a.startswith("--")
                       and sum(b.split("=", 1)[0] == a.split("=", 1)[0] for b in args) > 1})
    if unknown or empty or repeated:
        raise SystemExit(f"Bad options: unknown {unknown}, empty {empty}, repeated {repeated}")

    def value(prefix: str) -> str | None:
        return next((a.split("=", 1)[1] for a in args if a.startswith(prefix)), None)

    return {
        "horizons": [a for a in args if not a.startswith("--")] or list(DEFAULT_HORIZONS),
        "ex_winners": "--ex-winners" in args,
        "pit": "--pit" in args,
        "placebo": "growth" if "--placebo" in args else value("--placebo="),
        "report_only": value("--report-only="),
        "without": value("--without=").split(",") if value("--without=") else [],
        "with_": value("--with=").split(",") if value("--with=") else [],
        "seed": int(value("--seed=") or DEFAULT_SEED),
    }


if __name__ == "__main__":
    o = parse_args(sys.argv[1:])
    common = dict(pit=o["pit"], without=o["without"], with_=o["with_"], placebo=o["placebo"], seed=o["seed"])
    if o["report_only"]:
        rewrite_summary(o["report_only"], horizons=o["horizons"])
    elif o["ex_winners"]:
        run_all(horizons=o["horizons"], exclude=list(HINDSIGHT_WINNERS), tag="ex5", **common)
    else:
        run_all(horizons=o["horizons"], **common)
