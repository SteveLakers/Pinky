#!/usr/bin/env python3
"""
Step 3 verdict: do the growth features earn their place? Reads saved runs; no training.

Locked rule (decided 2026-10-03, before any v8 results). Judged on LightGBM, Top 10% + buffer,
10 bps, monthly; each side = mean over seeds 42, 7, 99:
- Keep growth for a version only if real beats placebo by ≥ +1.0%/yr over 2001–2020
  AND by ≥ +0.5%/yr in each of 2001–08 and 2009–20.
- Real − placebo above +3.0%/yr → leak audit before anything else.
- A vs B: both continue unless one trails the other by more than 4%/yr.
- Scoreboard (shown, never decides): > +8.7%/yr, ≥ SPY in both halves, ≥ equal-weight
  universe, monthly top-10 crash rate ≤ 10%, big-winner rate, LightGBM IC > 0 in both halves.
- `--weekly`: weekly trading wins only if ≥ +1.0%/yr better at 10 bps and not worse at 25 bps.

Usage: PYTHONPATH=. python scripts/step3_verdict.py [--weekly]
Writes the same text to artifacts/step3_verdict.md.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from compare_runs import winner_crash_rates
from pinky.backtest import run_backtest, summarize_backtest, with_cost
from pinky.config import (
    BACKTEST_BUFFER_MULT,
    BACKTEST_MAX_SECTOR_SHARE,
    BACKTEST_TOP_FRAC,
    PROJECT_ROOT,
    REPORT_SPLIT_YEAR,
)
from pinky.universe import backtest_prices, sector_map

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
SEEDS = (42, 7, 99)
SIGNAL, PORTFOLIO = "LightGBM", "Top 10% + buffer"
KEEP_ALL, KEEP_HALF, LEAK_GAP, AB_GAP, WEEKLY_GAIN = 0.010, 0.005, 0.030, 0.040, 0.010
BEST_SO_FAR, CRASH_MAX, CONTROL_TOL = 0.087, 0.10, 0.005
VERSIONS = {
    "A (rank label)": {"base": "v8_pit", "no_growth": "v8_pit_no-growth", "v7": "v7_pit"},
    "B (raw return)": {"base": "v8_pit_no-rank_label", "no_growth": "v7_pit_no-rank_label", "v7": "v7_pit_no-rank_label"},
}
OUT: list[str] = []


def say(line: str = "") -> None:
    OUT.append(line)
    print(line)


def pct(x: float) -> str:
    return f"{100 * x:+.2f}%"


def run_name(base: str, placebo: bool, seed: int) -> str:
    return "_".join([base, *(["placebo"] if placebo else []), *([f"s{seed}"] if seed != 42 else [])])


def needed_runs() -> list[str]:
    runs = [run_name(v["base"], p, s) for v in VERSIONS.values() for p in (False, True) for s in SEEDS]
    return runs + [v["no_growth"] for v in VERSIONS.values()] + [v["v7"] for v in VERSIONS.values()]


def stats(run: str) -> pd.DataFrame:
    s = pd.read_csv(ARTIFACTS_DIR / f"backtest_stats_1y_{run}.csv")
    return s[(s["signal"] == SIGNAL) & (s["portfolio"] == PORTFOLIO)].set_index("period")


def periods(run: str) -> list[str]:
    return ["all", *sorted(p for p in stats(run).index if p != "all")]


def mean_stat(runs: list[str], col: str = "cagr_net") -> pd.Series:
    return pd.concat([stats(r)[col] for r in runs], axis=1).mean(axis=1)


def nw_se(x: np.ndarray, lag: int = 6) -> float:
    x = x - x.mean()
    n = len(x)
    s = x @ x / n + 2 * sum((1 - k / (lag + 1)) * (x[k:] @ x[:-k]) / n for k in range(1, lag + 1))
    return float(np.sqrt(s / n))


def monthly_gap(real: list[str], fake: list[str]) -> str:
    paths = [ARTIFACTS_DIR / f"backtest_periods_1y_{r}.csv" for r in real + fake]
    if not all(p.exists() for p in paths):
        return "paired monthly test: skipped (monthly returns not saved for these runs)"

    def mean_net(runs: list[str]) -> pd.Series:
        parts = []
        for r in runs:
            p = pd.read_csv(ARTIFACTS_DIR / f"backtest_periods_1y_{r}.csv", parse_dates=["start"])
            p = p[(p["signal"] == SIGNAL) & (p["portfolio"] == PORTFOLIO)]
            parts.append(p.set_index("start")["net"])
        return pd.concat(parts, axis=1).mean(axis=1)

    d = (mean_net(real) - mean_net(fake)).dropna().to_numpy()
    m, se = 12 * d.mean(), 12 * nw_se(d)
    return f"paired monthly test: {pct(m)}/yr ± {100 * se:.2f} (t = {m / se:+.2f}, {len(d)} months)"


def ic_halves(run: str) -> tuple[float, float]:
    m = pd.read_csv(ARTIFACTS_DIR / f"walkforward_metrics_{run}.csv")
    late = pd.to_datetime(m["test_start"]).dt.year >= REPORT_SPLIT_YEAR
    return float(m.loc[~late, "ic_lgbm"].mean()), float(m.loc[late, "ic_lgbm"].mean())


def scoreboard(name: str, runs: list[str]) -> float:
    cagr = mean_stat(runs)
    spy, ew = stats(runs[0])["cagr_spy"], stats(runs[0])["cagr_universe_ew"]
    early, late = periods(runs[0])[1:]
    rates = [winner_crash_rates(pd.read_parquet(ARTIFACTS_DIR / f"oos_preds_1y_{r}.parquet"), "pred_excess_lgbm") for r in runs]
    big, crash = np.mean([b for b, _ in rates]), np.mean([c for _, c in rates])
    ics = np.mean([ic_halves(r) for r in runs], axis=0)
    say(f"### Scoreboard — {name} ({', '.join(runs)})")
    say("")
    say(f"- CAGR {pct(cagr['all'])} | {early} {pct(cagr[early])} | {late} {pct(cagr[late])}")
    say(f"- Beats best so far (+8.7%/yr): {'yes' if cagr['all'] > BEST_SO_FAR else 'no'}")
    say(f"- ≥ SPY in both halves: {'yes' if cagr[early] >= spy[early] and cagr[late] >= spy[late] else 'no'} "
        f"(SPY {pct(spy[early])} / {pct(spy[late])})")
    say(f"- ≥ equal-weight universe: {'yes' if cagr['all'] >= ew['all'] else 'no'} (universe {pct(ew['all'])})")
    say(f"- Monthly top-10 crash rate ≤ 10%: {'yes' if crash <= CRASH_MAX else 'no'} ({crash:.1%}); big winners {big:.1%} (random 10%)")
    say(f"- LightGBM IC > 0 in both halves: {'yes' if ics[0] > 0 and ics[1] > 0 else 'no'} ({ics[0]:+.3f} / {ics[1]:+.3f})")
    say("")
    return float(cagr["all"])


def weekly_test(name: str, runs: list[str], prices: pd.DataFrame, sectors: dict[str, str]) -> None:
    rows = []
    for r in runs:
        preds = pd.read_parquet(ARTIFACTS_DIR / f"oos_preds_1y_{r}.parquet")
        bt = run_backtest(
            preds, "pred_excess_lgbm", prices, sectors=sectors, top_frac=BACKTEST_TOP_FRAC,
            max_sector_share=BACKTEST_MAX_SECTOR_SHARE, buffer_mult=BACKTEST_BUFFER_MULT, rebalance="weekly",
        )
        s = stats(r).loc["all"]
        rows.append((s["cagr_net"], s["cagr_net_25bps"], summarize_backtest(bt)["cagr_net"], summarize_backtest(with_cost(bt, 25.0))["cagr_net"]))
    m10, m25, w10, w25 = np.mean(rows, axis=0)
    wins = w10 - m10 >= WEEKLY_GAIN and w25 >= m25
    say(f"### Weekly vs monthly — {name}")
    say("")
    say(f"- 10 bps: monthly {pct(m10)} | weekly {pct(w10)} ({pct(w10 - m10)})")
    say(f"- 25 bps: monthly {pct(m25)} | weekly {pct(w25)} ({pct(w25 - m25)})")
    say(f"- **{'Weekly wins' if wins else 'Stay monthly'}** (needs ≥ +1.00%/yr at 10 bps and not worse at 25 bps)")
    say("")


def main(args: list[str]) -> int:
    missing = [r for r in needed_runs() if not (ARTIFACTS_DIR / f"backtest_stats_1y_{r}.csv").exists()]
    if missing:
        print("Missing runs (train them first):\n  " + "\n  ".join(missing))
        return 1

    say("# Step 3 verdict — growth features (batch 1)")
    say("")
    say(f"Judged on {SIGNAL}, {PORTFOLIO}, 10 bps, monthly; mean of seeds {', '.join(map(str, SEEDS))}.")
    say("")
    finals: dict[str, list[str]] = {}
    hold = False
    for name, v in VERSIONS.items():
        real = [run_name(v["base"], False, s) for s in SEEDS]
        fake = [run_name(v["base"], True, s) for s in SEEDS]
        ps = periods(real[0])
        r, f = mean_stat(real), mean_stat(fake)
        gap = r - f
        keep = gap["all"] >= KEEP_ALL and all(gap[p] >= KEEP_HALF for p in ps[1:])
        leak = gap["all"] > LEAK_GAP
        hold |= leak
        say(f"## {name}")
        say("")
        say("| | " + " | ".join(ps) + " |")
        say("|---|" + "---|" * len(ps))
        for label, row in (("Real (mean)", r), ("Placebo (mean)", f), ("Real − placebo", gap)):
            say(f"| {label} | " + " | ".join(pct(row[p]) for p in ps) + " |")
        for label, runs in (("Real", real), ("Placebo", fake)):
            per = [stats(x).loc["all", "cagr_net"] for x in runs]
            say(f"- {label} by seed: " + ", ".join(f"{s}: {pct(c)}" for s, c in zip(SEEDS, per)))
        say(f"- {monthly_gap(real, fake)}")
        if name.startswith("A"):
            c, o = stats(v["no_growth"])["cagr_net"], stats(v["v7"])["cagr_net"]
            worst = max(abs(c[p] - o[p]) for p in ps)
            say(f"- Control `{v['no_growth']}` vs `{v['v7']}`: " + ", ".join(f"{p} {pct(c[p] - o[p])}" for p in ps)
                + (" (reproduces v7)" if worst <= CONTROL_TOL else " — **does not reproduce v7: investigate first**"))
            hold |= worst > CONTROL_TOL
        if leak:
            say(f"- **Gap above +3.0%/yr: leak audit before anything else.**")
        say(f"- **Growth: {'KEEP' if keep else 'DROP'}** (needs ≥ +1.00%/yr overall and ≥ +0.50%/yr in each half)")
        say("")
        finals[name] = real if keep else [v["no_growth"]]

    cagr = {name: scoreboard(name, runs) for name, runs in finals.items()}
    (a, ca), (b, cb) = cagr.items()
    say("## A vs B")
    say("")
    if abs(ca - cb) > AB_GAP:
        loser = a if ca < cb else b
        say(f"- {a} {pct(ca)} vs {b} {pct(cb)}: **drop {loser}** (trails by more than 4%/yr)")
    else:
        say(f"- {a} {pct(ca)} vs {b} {pct(cb)}: **both continue** (gap ≤ 4%/yr)")
    say("")

    if "--weekly" in args:
        prices, sectors = backtest_prices(), sector_map()
        for name, runs in finals.items():
            weekly_test(name, runs, prices, sectors)
    if hold:
        say("**ON HOLD: resolve the flags above before acting on this verdict.**")
    (ARTIFACTS_DIR / "step3_verdict.md").write_text("\n".join(OUT) + "\n")
    print(f"\nWrote {ARTIFACTS_DIR / 'step3_verdict.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
