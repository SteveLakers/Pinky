#!/usr/bin/env python3
"""
Fast growers by margin group: do margins separate the fast growers that win from those that
crash? Data only (no models); info, not a gate. Batch 2 plan, "After the runs".

Design fixed before running (2026-10-19), same definitions as the 2026-10-16 data check
(`docs/PROJECT_HISTORY.md` → Residual edge + SHAP):
- Rows: dev rows of the 1y label (`train.dev_rows`), dates 2001–2020, weekly.
- Fast growers: each date's top 20% by 12-month sales growth (`rev_yoy_ttm`) among stocks
  that have it. Second view: top 20% by quarterly growth (`rev_yoy_q`).
- Groups inside the fast growers, per date: quintiles (1 = lowest) of `gm_chg_q` and
  `om_chg_q` (margin change vs the same quarter a year ago), plus "missing". Extra view:
  `om_ttm` (12-month operating margin) as loss-making (< 0) vs profitable (≥ 0).
- Per group: next-year return vs SPY (`excess_1y`) median, share of big winners (top 10% of
  that date, `top_1y`), share of crashes (trails SPY by more than 50%). Each statistic is
  computed per date, then averaged over dates (each date weighs the same). Medians also by
  half (2001–08, 2009–20).

Usage: PYTHONPATH=. python scripts/fast_grower_margins.py
Writes the same text to artifacts/fast_grower_margins.md.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pinky.config import PROJECT_ROOT, REPORT_SPLIT_YEAR
from pinky.pit_dataset import load_pit_dataset
from pinky.train import dev_rows
from pinky.universe import benchmark_closeadj

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
FAST_FRAC, N_GROUPS, CRASH = 0.20, 5, -0.50
FIRST_YEAR, LAST_YEAR = 2001, 2020
OUT: list[str] = []


def say(line: str = "") -> None:
    OUT.append(line)
    print(line)


def per_date(df: pd.DataFrame, group: str) -> pd.DataFrame:
    """Per date x group: median excess, big-winner share, crash share, rows."""
    g = df.groupby(["Date", group], observed=True)
    return pd.DataFrame(
        {
            "median": g["excess_1y"].median(),
            "big": g["top_1y"].mean(),
            "crash": g["crash"].mean(),
            "n": g.size(),
        }
    ).reset_index()


def table(df: pd.DataFrame, group: str, title: str) -> None:
    d = per_date(df, group)
    late = d["Date"].dt.year >= REPORT_SPLIT_YEAR
    say(f"### {title}")
    say("")
    say(f"| Group | Rows/date | Median vs SPY | 2001–08 | 2009–20 | Big winners | Crashes |")
    say("|---|---|---|---|---|---|---|")
    for name, x in d.groupby(group, observed=True, sort=True):
        e, l = x[~late.loc[x.index]], x[late.loc[x.index]]
        say(f"| {name} | {x['n'].mean():.0f} | {x['median'].mean():+.1%} | {e['median'].mean():+.1%} | "
            f"{l['median'].mean():+.1%} | {x['big'].mean():.1%} | {x['crash'].mean():.1%} |")
    say("")


def quintile_label(s: pd.Series, dates: pd.Series) -> pd.Series:
    r = s.groupby(dates).rank(pct=True, method="first")
    q = np.ceil(r * N_GROUPS).clip(1, N_GROUPS)
    names = {1: "1 (falling most)", N_GROUPS: f"{N_GROUPS} (rising most)"}
    return q.map(lambda v: "missing" if np.isnan(v) else names.get(int(v), str(int(v))))


def main() -> int:
    cal = pd.DatetimeIndex(benchmark_closeadj().index)
    cols = ["Date", "Ticker", "rev_yoy_ttm", "rev_yoy_q", "gm_chg_q", "om_chg_q", "om_ttm", "excess_1y", "top_1y"]
    df = dev_rows(load_pit_dataset()[cols], "1y", cal)
    df = df[df["Date"].dt.year.between(FIRST_YEAR, LAST_YEAR) & df["excess_1y"].notna()].copy()
    df["crash"] = (df["excess_1y"] < CRASH).astype(float)

    say("# Fast growers by margin group (data only, info)")
    say("")
    say(f"Dev rows {FIRST_YEAR}–{LAST_YEAR}, weekly; each statistic per date, then averaged over dates. "
        f"Big winner = top 10% next year (random 10%); crash = trails SPY by > 50% next year.")
    say("")
    all_stats = per_date(df.assign(all="all stocks"), "all").mean(numeric_only=True)
    say(f"- All stocks: median {all_stats['median']:+.1%}, big winners {all_stats['big']:.1%}, crashes {all_stats['crash']:.1%}")
    say("")
    for growth, label in (("rev_yoy_ttm", "12-month sales growth"), ("rev_yoy_q", "quarterly sales growth")):
        has = df[df[growth].notna()]
        fast = has[has.groupby("Date")[growth].rank(pct=True) > 1.0 - FAST_FRAC].copy()
        say(f"## Fastest 20% by {label} (`{growth}`; median growth {fast[growth].median():+.0%})")
        say("")
        base = per_date(fast.assign(all="all fast growers"), "all").mean(numeric_only=True)
        say(f"- All fast growers: median {base['median']:+.1%}, big winners {base['big']:.1%}, crashes {base['crash']:.1%}")
        say("")
        for col, name in (("gm_chg_q", "gross margin change vs a year ago"), ("om_chg_q", "operating margin change vs a year ago")):
            fast[f"{col}_group"] = quintile_label(fast[col], fast["Date"])
            table(fast, f"{col}_group", f"By {name} (`{col}`), quintiles within each date's fast growers")
        fast["profit"] = np.where(fast["om_ttm"].isna(), "missing", np.where(fast["om_ttm"] < 0, "loss-making", "profitable"))
        table(fast, "profit", "By 12-month operating margin (`om_ttm`): loss-making vs profitable")

    out = ARTIFACTS_DIR / "fast_grower_margins.md"
    out.write_text("\n".join(OUT) + "\n")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
