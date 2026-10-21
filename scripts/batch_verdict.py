#!/usr/bin/env python3
"""
Verdict for a company-data batch (batch 2 on): does each feature set earn its place? Reads saved
runs; no training. Generalizes step3_verdict.py (its helpers are reused) to a list of tests,
each with its own real, placebo and baseline runs.

Locked rule (user-approved 2026-10-09, before any batch 2 results). Judged on LightGBM,
Top 10% + buffer, 10 bps, monthly; each side = mean over seeds 42, 7, 99. KEEP only if both:
1. real − placebo ≥ +1.0%/yr over 2001–2020 AND ≥ +0.5%/yr in each of 2001–08 and 2009–20;
2. real ≥ the baseline (same 3 seeds) over 2001–2020.
- Real − placebo above +3.0%/yr → leak audit before anything else (ON HOLD).
- Baseline means must match project.md (A +7.14%/yr, B +6.10%/yr), else ON HOLD.
- Tie-break fixed before results: if two tests KEEP for the same version, the one with the
  higher real mean wins.
- A vs B (final runs): both continue unless one trails the other by more than 4%/yr.
- Scoreboard (shown, never decides): as in step 3.

Batch 3 = growth round 2 (one column at a time, then all four; run one test at a time): tests
whose 12 runs exist are judged; the final pick and A vs B wait until every test is in.

Usage: PYTHONPATH=. python scripts/batch_verdict.py 2   (or 3)
Writes the same text to artifacts/batch<N>_verdict.md.
"""

from __future__ import annotations

import sys

import step3_verdict as v3
from step3_verdict import mean_stat, monthly_gap, pct, periods, same_backtest, say, scoreboard, stats

ARTIFACTS_DIR = v3.ARTIFACTS_DIR
SEEDS = v3.SEEDS
KEEP_ALL, KEEP_HALF, LEAK_GAP, AB_GAP = v3.KEEP_ALL, v3.KEEP_HALF, v3.LEAK_GAP, v3.AB_GAP
BASELINE_TOL = 0.0001
A, B = "A (rank label)", "B (raw return)"
# Expected baseline means (backtest version 1, as batch 2 judged them). A batch can override them
# with "baselines" (batch 3: backtest version 2, re-scored after the 2026-10-21 code review).
BASELINES = {A: ("v9_pit", 0.0714), B: ("v9_pit_no-rank_label", 0.0610)}
BATCHES = {
    "2": {
        "title": "Batch 2 verdict — margins (Part 1: margins alone; Part 2: growth + margins)",
        "tests": [
            ("Part 1 margins", A, "v9_pit_with-margins", "v9_pit_with-margins_placebo-margins"),
            ("Part 1 margins", B, "v9_pit_no-rank_label_with-margins", "v9_pit_no-rank_label_with-margins_placebo-margins"),
            ("Part 2 growth + margins", A, "v9_pit_with-growth_with-margins", "v9_pit_with-growth_with-margins_placebo-margins"),
            (
                "Part 2 growth + margins", B,
                "v9_pit_no-rank_label_with-growth_with-margins",
                "v9_pit_no-rank_label_with-growth_with-margins_placebo-margins",
            ),
        ],
    },
    "3": {
        "title": "Batch 3 verdict — growth round 2 (one column at a time, then all four)",
        # v10 baselines (RSI fix + backtest version 2), retrained 2026-10-21
        "baselines": {A: ("v10_pit", 0.0715), B: ("v10_pit_no-rank_label", 0.0637)},
        "tests": [
            (f"Test {i} {label}", version, f"{base}_with-{g}", f"{base}_with-{g}_placebo-{g}")
            for i, (g, label) in enumerate(
                [
                    ("ear", "ear_3d (reaction to earnings)"),
                    ("sue", "rev_sue (sales surprise)"),
                    ("cagr", "rev_cagr_3y (3-year sales growth)"),
                    ("steady", "rev_up_quarters (steady growth)"),
                    ("growth2", "all four together"),
                ],
                start=1,
            )
            for version, base in ((A, "v10_pit"), (B, "v10_pit_no-rank_label"))
        ],
    },
}


def has_run(run: str) -> bool:
    return (ARTIFACTS_DIR / f"backtest_stats_1y_{run}.csv").exists()


def seeded(base: str) -> list[str]:
    return [base if s == 42 else f"{base}_s{s}" for s in SEEDS]


def needed_runs(tests: list[tuple], baselines: dict = BASELINES) -> list[str]:
    bases = [b for _, _, real, fake in tests for b in (real, fake)] + [b for b, _ in baselines.values()]
    return [r for b in dict.fromkeys(bases) for r in seeded(b)]


def main(args: list[str]) -> int:
    if not args or args[0] not in BATCHES:
        print(f"Usage: batch_verdict.py <batch>; batches: {list(BATCHES)}")
        return 1
    batch = args[0]
    cfg = BATCHES[batch]
    baselines = cfg.get("baselines", BASELINES)
    ready = [t for t in cfg["tests"] if all(has_run(r) for r in seeded(t[2]) + seeded(t[3]))]
    waiting = [t for t in cfg["tests"] if t not in ready]
    missing = [r for r in needed_runs(ready or cfg["tests"], baselines) if not has_run(r)]
    if missing or not ready:
        print("Missing runs (train them first):\n  " + "\n  ".join(missing))
        return 1

    say(f"# {cfg['title']}")
    say("")
    say(f"Judged on {v3.SIGNAL}, {v3.PORTFOLIO}, 10 bps, monthly; mean of seeds {', '.join(map(str, SEEDS))}.")
    say("")
    hold = not same_backtest(needed_runs(ready, baselines))
    base_mean = {}
    for version, (base, expected) in baselines.items():
        m = mean_stat(seeded(base))
        base_mean[version] = m
        ok = abs(m["all"] - expected) <= BASELINE_TOL
        hold |= not ok
        say(f"- Baseline {version} `{base}` (+ seeds): {pct(m['all'])}/yr"
            + ("" if ok else f" — **expected {pct(expected)}: investigate first**"))
    say("")

    kept: dict[str, list[tuple[float, str, list[str]]]] = {A: [], B: []}
    for name, version, real_base, fake_base in ready:
        real, fake, baseline = seeded(real_base), seeded(fake_base), seeded(baselines[version][0])
        ps = periods(real[0])
        r, f, b = mean_stat(real), mean_stat(fake), base_mean[version]
        gap, vs_base = r - f, r - b
        rule1 = gap["all"] >= KEEP_ALL and all(gap[p] >= KEEP_HALF for p in ps[1:])
        rule2 = r["all"] >= b["all"]
        leak = gap["all"] > LEAK_GAP
        hold |= leak
        say(f"## {name} — {version}")
        say("")
        say("| | " + " | ".join(ps) + " |")
        say("|---|" + "---|" * len(ps))
        for label, row in (("Real (mean)", r), ("Placebo (mean)", f), ("Baseline (mean)", b),
                           ("Real − placebo", gap), ("Real − baseline", vs_base)):
            say(f"| {label} | " + " | ".join(pct(row[p]) for p in ps) + " |")
        for label, runs in (("Real", real), ("Placebo", fake)):
            per = [stats(x).loc["all", "cagr_net"] for x in runs]
            say(f"- {label} by seed: " + ", ".join(f"{s}: {pct(c)}" for s, c in zip(SEEDS, per)))
        say(f"- vs placebo, {monthly_gap(real, fake)}")
        say(f"- vs baseline, {monthly_gap(real, baseline)}")
        if leak:
            say("- **Gap above +3.0%/yr: leak audit before anything else.**")
        say(f"- Rule 1 (real − placebo ≥ +1.00%/yr, ≥ +0.50%/yr each half): {'pass' if rule1 else 'fail'}")
        say(f"- Rule 2 (real ≥ baseline): {'pass' if rule2 else 'fail'}")
        say(f"- **{name}: {'KEEP' if rule1 and rule2 else 'DROP'}**")
        say("")
        if rule1 and rule2:
            kept[version].append((float(r["all"]), name, real))

    if waiting:
        say("## Not run yet")
        say("")
        for name, version, _, _ in waiting:
            say(f"- {name} — {version}")
        say("")
        say("Final versions and A vs B: once every test is in.")
        if hold:
            say("")
            say("**ON HOLD: resolve the flags above before acting on this verdict.**")
        out = ARTIFACTS_DIR / f"batch{batch}_verdict.md"
        out.write_text("\n".join(v3.OUT) + "\n")
        print(f"\nWrote {out}")
        return 0

    say("## Final versions")
    say("")
    finals: dict[str, list[str]] = {}
    for version, options in kept.items():
        if options:
            cagr, name, runs = max(options)
            say(f"- {version}: **{name}** ({pct(cagr)}/yr)" + (f"; also kept: {', '.join(n for _, n, _ in options if n != name)}" if len(options) > 1 else ""))
            finals[version] = runs
        else:
            say(f"- {version}: **baseline** (nothing kept)")
            finals[version] = seeded(baselines[version][0])
    say("")

    cagr = {version: scoreboard(version, runs) for version, runs in finals.items()}
    ca, cb = cagr[A], cagr[B]
    say("## A vs B")
    say("")
    if abs(ca - cb) > AB_GAP:
        say(f"- A {pct(ca)} vs B {pct(cb)}: **drop {A if ca < cb else B}** (trails by more than 4%/yr)")
    else:
        say(f"- A {pct(ca)} vs B {pct(cb)}: **both continue** (gap ≤ 4%/yr)")
    say("")
    if hold:
        say("**ON HOLD: resolve the flags above before acting on this verdict.**")
    out = ARTIFACTS_DIR / f"batch{batch}_verdict.md"
    out.write_text("\n".join(v3.OUT) + "\n")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
