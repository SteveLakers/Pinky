#!/usr/bin/env python3
"""Residual-edge check: is a version's monthly return more than cheap, simple exposure?

Wraps the residual-edge-analyzer skill (`.agents/skills/residual-edge-analyzer/`, untracked)
with the inputs of docs/STEP3_RUNBOOK.md step 8. Design fixed before looking at any result
(2026-10-16):
- Strategy: LightGBM, Top 10% + buffer, gross monthly returns from
  artifacts/backtest_periods_1y_<run>.csv. A version with several runs (seeds) uses the average
  monthly return of its runs (= holding a third of each seed's portfolio).
- Primary baseline: the equal-weight universe (same point-in-time universe, equal weight: the
  simplest copy of the strategy). Alternates: SPY; equal-weight + 12-1 momentum (Top 10% +
  buffer, same rules); SPY + momentum. Everything gross and monthly.
- Regimes: 2001-2008 vs 2009-2020 (REPORT_SPLIT_YEAR). Rolling window 36 months. The analyzer's
  default thresholds.

Usage: python scripts/residual_edge.py NAME=run[,run...] [NAME=run[,run...] ...]
  e.g. python scripts/residual_edge.py A=v9_pit,v9_pit_s7,v9_pit_s99 A42=v9_pit
Writes artifacts/residual_edge/<NAME>.csv / .config.json / .json / .md and prints a summary.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd

from pinky.config import PROJECT_ROOT, REPORT_SPLIT_YEAR

ARTIFACTS = PROJECT_ROOT / "artifacts"
OUT = ARTIFACTS / "residual_edge"
ANALYZER = PROJECT_ROOT / ".agents/skills/residual-edge-analyzer/scripts/analyze_residual_edge.py"
SIGNAL, MOMENTUM, PORTFOLIO = "LightGBM", "Momentum 12-1", "Top 10% + buffer"
BASELINES = ["market_return", "equal_weight_return", "momentum_return"]
CONFIG = {
    "schema_version": "1.0",
    "date_column": "date",
    "strategy_column": "strategy_return",
    "return_unit": "decimal",
    "frequency": "monthly",
    "primary_model": {"name": "equal_weight", "baseline_columns": ["equal_weight_return"]},
    "sensitivity_models": [
        {"name": "market", "baseline_columns": ["market_return"]},
        {"name": "equal_weight_plus_momentum", "baseline_columns": ["equal_weight_return", "momentum_return"]},
        {"name": "market_plus_momentum", "baseline_columns": ["market_return", "momentum_return"]},
    ],
    "regime_columns": ["period"],
    "rolling_window": 36,
    "minimum_observations": 60,
    "minimum_regime_observations": 20,
    "minimum_rolling_windows": 12,
    "hac_lags": "auto",
    "include_series": False,
    "data_declarations": {
        "baseline_selection": "predeclared",
        "strategy_return_basis": "gross",
        "baseline_return_basis": "gross",
        # Walk-forward predictions (each fold tested after its training window); the 2001-2020
        # dev period did shape design choices, and the 2022+ holdout stays untouched.
        "analysis_scope": "out_of_sample",
        "universe_data": "point_in_time",
    },
}


def monthly_returns(run: str) -> pd.DataFrame:
    p = pd.read_csv(ARTIFACTS / f"backtest_periods_1y_{run}.csv")
    pick = lambda signal: p[(p["signal"] == signal) & (p["portfolio"] == PORTFOLIO)].set_index("start")
    s, m = pick(SIGNAL), pick(MOMENTUM)
    if not s.index.equals(m.index):
        raise ValueError(f"{run}: strategy and momentum months differ")
    return pd.DataFrame(
        {
            "strategy_return": s["gross"],
            "market_return": s["spy"],
            "equal_weight_return": s["universe_ew"],
            "momentum_return": m["gross"],
        }
    )


def build_input(runs: list[str]) -> pd.DataFrame:
    frames = [monthly_returns(r) for r in runs]
    out = frames[0].copy()
    for run, f in zip(runs[1:], frames[1:]):
        if not (f.index.equals(out.index) and f[BASELINES].equals(out[BASELINES])):
            raise ValueError(f"{run}: months or baseline returns differ from {runs[0]}")
    out["strategy_return"] = sum(f["strategy_return"] for f in frames) / len(frames)
    years = pd.to_datetime(out.index).year
    first, last = years.min(), years.max()
    out["period"] = [f"{first}-{REPORT_SPLIT_YEAR - 1}" if y < REPORT_SPLIT_YEAR else f"{REPORT_SPLIT_YEAR}-{last}" for y in years]
    out.index.name = "date"
    return out


def run_analyzer(name: str, runs: list[str]) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    data = build_input(runs)
    csv, cfg, js, md = (OUT / f"{name}{ext}" for ext in (".csv", ".config.json", ".json", ".md"))
    data.to_csv(csv)
    cfg.write_text(json.dumps(CONFIG, indent=1))
    subprocess.run(
        [sys.executable, str(ANALYZER), "--input", str(csv), "--config", str(cfg),
         "--output-json", str(js), "--output-markdown", str(md)],
        check=True,
    )
    return json.loads(js.read_text())


def summary(name: str, runs: list[str], rep: dict) -> str:
    pct = lambda x: f"{x:+.2%}" if x is not None else "n/a"
    num = lambda x: f"{x:.2f}" if x is not None else "n/a"
    d = rep["data"]
    lines = [
        f"{name} = {', '.join(runs)}: {d['observation_count']} months {d['start_date']}..{d['end_date']}",
        f"  {'model':30} {'alpha/yr':>9} {'t':>6} {'R2':>5} {'edge':>6} {'+alpha windows':>15}  status",
    ]
    for m in rep["models"]:
        roll = m["rolling"]
        pos = f"{roll['positive_alpha_fraction']:.0%}" if roll.get("enabled") else "n/a"
        lines.append(
            f"  {m['name'] + (' (primary)' if m['role'] == 'primary' else ''):30} "
            f"{pct(m['alpha']['annualized_arithmetic']):>9} {num(m['alpha']['t_stat']):>6} "
            f"{m['r_squared']:5.2f} {num(m['residual']['residual_edge_ratio']):>6} {pos:>15}  {m['diagnostic_status']}"
        )
        loads = ", ".join(f"{c['name']} {c['estimate']:.2f}" for c in m["coefficients"][1:])
        vif = m.get("vif") or {}
        lines.append(f"  {'':30} loadings: {loads}" + (f" | VIF {vif}" if len(m["coefficients"]) > 2 else ""))
    for g in rep["regime_analysis"]["period"]:
        a = g["active_return_metrics"]
        lines.append(
            f"  active return {g['label']}: {pct(a['annualized_arithmetic_return'])}/yr, "
            f"{g['positive_fraction']:.0%} of {g['observation_count']} months positive ({g['evidence_status']})"
        )
    v = rep["verdict"]
    lines.append(f"  VERDICT: {v['status']} | {v['decision_eligibility']} | " + " ".join(v["reasons"]))
    for w in rep["warnings"]:
        lines.append(f"  warning ({w['severity']}): {w['message']}")
    return "\n".join(lines)


if __name__ == "__main__":
    specs = [a.split("=", 1) for a in sys.argv[1:]]
    if not specs or any(len(s) != 2 for s in specs):
        sys.exit(__doc__)
    for name, runs in specs:
        runs = runs.split(",")
        print(summary(name, runs, run_analyzer(name, runs)), "\n")
