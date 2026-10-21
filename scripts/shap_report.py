#!/usr/bin/env python3
"""SHAP: which inputs drive the LightGBM return model's scores, fold by fold (= test year).

Design fixed before looking at any result (2026-10-16):
- Model: each fold's LightGBM return model (`models/<run>/1y/fold_NN/lgbm_return.joblib`), the
  "LightGBM" signal that picks the stocks. Explained output: its raw prediction (A: the day's
  return rank - 0.5; B: 1-year return vs SPY), so compare shares within a version, not raw sizes
  across A and B.
- Rows: every fold's held-out test rows, rebuilt with the training pipeline; rebuilt predictions
  must equal the saved out-of-sample predictions exactly.
- Explainer: shap.TreeExplainer, tree_path_dependent (background = the training rows behind each
  tree split); additivity checked on every fold.
- Importance = mean |SHAP| per input, as a share of the fold's total. Families sum signed SHAP
  within the family first. Direction = Spearman correlation of an input's value (per-day rank)
  with its SHAP value. Top picks = each date's top 10% by predicted score; a family's lift share =
  its mean SHAP on those rows / (their mean prediction - base value), so the shares sum to 100%.
- A version with several runs (seeds) averages the runs' numbers.
Added after the first results (2026-10-16): ranking share = the same share after removing each
date's mean SHAP, i.e. only the part that moves a stock relative to the other stocks that day.
A shift shared by all normal stocks (e.g. `history_1y` in B) counts in the plain share but cannot
change which stocks get picked.
SHAP describes what the model uses, not what makes money, and is not causal.

Usage: python scripts/shap_report.py NAME=run[,run...] [NAME=run[,run...] ...] [--max-folds=N]
(--max-folds: quick test on the first N folds only.)
Writes artifacts/shap/<NAME>_folds.csv (fold x input) and artifacts/shap/<NAME>.md.
"""

from __future__ import annotations

import json
import sys
import time

import joblib
import numpy as np
import pandas as pd
import shap

from pinky.config import REPORT_SPLIT_YEAR
from pinky.fundamentals import GROWTH2_FEATURES, GROWTH_FEATURES, MARGIN_FEATURES
from pinky.pit_dataset import load_pit_dataset
from pinky.preprocess import prepare_fold_frames
from pinky.train import ARTIFACTS_DIR, MODELS_DIR, dev_rows, pit_training_frame
from pinky.universe import benchmark_closeadj
from pinky.walkforward import iter_walk_forward_folds

OUT = ARTIFACTS_DIR / "shap"
HORIZON = "1y"
TOP_FRAC = 0.10
FAMILIES = {
    "short-term moves": ["ret_1d", "ret_5d", "ret_21d", "rsi_14"],
    "volatility": ["vol_21", "vol_63"],
    "trend": ["mom_63", "mom_126", "mom_252", "mom_252_skip_21", "dist_sma_50", "dist_sma_200"],
    "volume": ["volume_ratio_21"],
    "size": ["log_mcap"],
    "stock age": ["history_1y"],
    "growth": list(GROWTH_FEATURES),
    "margins": list(MARGIN_FEATURES),
    "growth round 2": list(GROWTH2_FEATURES),
}
LABELS = {
    "ret_1d": "last day's return", "ret_5d": "last week's return", "ret_21d": "last month's return",
    "rsi_14": "RSI (14 days)", "vol_21": "price swings, 1 month", "vol_63": "price swings, 3 months",
    "mom_63": "3-month return", "mom_126": "6-month return", "mom_252": "12-month return",
    "mom_252_skip_21": "12-month return skipping last month", "dist_sma_50": "price vs 50-day average",
    "dist_sma_200": "price vs 200-day average", "volume_ratio_21": "volume vs its 21-day average",
    "log_mcap": "company size", "history_1y": "share of the last year traded",
    "rev_yoy_q": "sales growth vs a year ago (quarter)", "rev_accel": "sales growth speeding up",
    "gp_yoy_q": "gross profit growth (quarter)", "rev_yoy_ttm": "sales growth (12 months)",
    "days_since_news": "days since last report", "has_growth": "has growth data",
    "gm_ttm": "gross margin (12 months)", "gm_chg_q": "gross margin change vs a year ago (quarter)",
    "om_ttm": "operating margin (12 months)", "om_chg_q": "operating margin change vs a year ago (quarter)",
    "ear_3d": "price reaction to the last report (3 days)", "rev_sue": "sales surprise vs own trend",
    "rev_cagr_3y": "sales growth per year over 3 years", "rev_up_quarters": "quarters of growth (last 8)",
}


def family_of(feature: str) -> str:
    return next((f for f, members in FAMILIES.items() if feature in members), feature)


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ok = ~(np.isnan(a) | np.isnan(b))
    if ok.sum() < 3:
        return np.nan
    return float(pd.Series(a[ok]).rank().corr(pd.Series(b[ok]).rank()))


def explain_fold(model, x, fcols, dates, saved_pred) -> tuple[list[dict], dict]:
    pred = model.predict(x)
    if not np.array_equal(pred, saved_pred):
        raise ValueError("rebuilt predictions differ from the saved out-of-sample predictions")
    exp = shap.TreeExplainer(model, feature_perturbation="tree_path_dependent")(x)
    values, base = exp.values, float(np.ravel(exp.base_values)[0])
    additivity = float(np.max(np.abs(base + values.sum(axis=1) - pred)))
    top = pd.Series(pred).groupby(dates).rank(pct=True, method="first").to_numpy() > 1.0 - TOP_FRAC
    lift = pred[top].mean() - base
    by_day = lambda v: v - pd.DataFrame(v).groupby(dates).transform("mean").to_numpy()
    within = by_day(values)
    rows = []
    fam_idx: dict[str, list[int]] = {}
    for j, f in enumerate(fcols):
        fam_idx.setdefault(family_of(f), []).append(j)
        rows.append({"kind": "input", "name": f, "family": family_of(f), "mean_abs": np.abs(values[:, j]).mean(),
                     "rank_abs": np.abs(within[:, j]).mean(),
                     "top_lift": values[top, j].mean() / lift, "direction": spearman(x[:, j], values[:, j])})
    for fam, idx in fam_idx.items():
        v = values[:, idx].sum(axis=1)
        rows.append({"kind": "family", "name": fam, "family": fam, "mean_abs": np.abs(v).mean(),
                     "rank_abs": np.abs(by_day(v[:, None])[:, 0]).mean(),
                     "top_lift": v[top].mean() / lift, "direction": np.nan})
    for kind in ("input", "family"):
        total = sum(r["mean_abs"] for r in rows if r["kind"] == kind)
        total_rank = sum(r["rank_abs"] for r in rows if r["kind"] == kind)
        for r in rows:
            if r["kind"] == kind:
                r["share"] = r["mean_abs"] / total
                r["rank_share"] = r["rank_abs"] / total_rank
    return rows, {"n_rows": len(x), "n_top": int(top.sum()), "additivity_max_err": additivity, "base": base}


def explain_runs(runs: list[str], max_folds: int | None = None) -> pd.DataFrame:
    """Per run x fold x input/family numbers; runs that share inputs share one rebuild."""
    cal = pd.DatetimeIndex(benchmark_closeadj().index)
    configs = {r: json.loads((ARTIFACTS_DIR / f"run_config_{r}.json").read_text()) for r in runs}
    groups: dict[tuple, list[str]] = {}
    for r, c in configs.items():  # rank_label changes the label, not the inputs
        key = (tuple(f for f in c["fixes"] if f != "rank_label"), c["placebo"], c["seed"] if c["placebo"] else None)
        groups.setdefault(key, []).append(r)
    base = load_pit_dataset()
    out = []
    for (fixes, placebo, seed), group in groups.items():
        t0 = time.time()
        fixes = list(fixes)
        df = dev_rows(pit_training_frame(base, fixes, placebo, seed or 42), HORIZON, cal)
        saved = {r: pd.read_parquet(ARTIFACTS_DIR / f"oos_preds_{HORIZON}_{r}.parquet", columns=["fold_id", "pred_excess_lgbm"]) for r in group}
        for fold in iter_walk_forward_folds(df, HORIZON, calendar=cal):
            if max_folds is not None and fold.fold_id >= max_folds:
                break
            _, test_cs, fcols = prepare_fold_frames(fold.train, fold.test, zscore="rank_features" not in fixes)
            x = test_cs[fcols].to_numpy(dtype=float)
            for r in group:
                d = MODELS_DIR / r / HORIZON / f"fold_{fold.fold_id:02d}"
                if (d / "feature_cols.txt").read_text().split("\n") != fcols:
                    raise ValueError(f"{r} fold {fold.fold_id}: feature columns differ from the saved model")
                s = saved[r]
                rows, info = explain_fold(
                    joblib.load(d / "lgbm_return.joblib"), x, fcols, test_cs["Date"].to_numpy(),
                    s.loc[s["fold_id"] == fold.fold_id, "pred_excess_lgbm"].to_numpy(),
                )
                for row in rows:
                    out.append({"run": r, "fold_id": fold.fold_id, "test_year": fold.test_start.year, **info, **row})
            print(f"  fold {fold.fold_id} ({fold.test_start.date()}): {len(x):,} rows explained for {len(group)} run(s)", flush=True)
        print(f"[shap] {', '.join(group)}: {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(out)


def report(name: str, runs: list[str], t: pd.DataFrame) -> str:
    span = f"{t['test_year'].min()}–{REPORT_SPLIT_YEAR - 1}", f"{REPORT_SPLIT_YEAR}–{t['test_year'].max()}"
    pct = lambda v: f"{v:.0%}"
    lines = [
        f"# SHAP: {name} ({', '.join(runs)})",
        "",
        f"LightGBM return model, every fold's held-out test rows ({t.groupby(['run', 'fold_id'])['n_rows'].first().sum():,} explained "
        f"rows over {t['run'].nunique()} run(s)). Rebuilt predictions = saved predictions on every fold; max additivity error "
        f"{t['additivity_max_err'].max():.1e}. Shares: each fold's mean |SHAP| share, averaged over folds (each year counts "
        f"once) and runs. Ranking share (added after the first results): the same after removing each date's mean SHAP "
        f"(only what moves a stock against the other stocks that day; the period columns and min–max use it). Lift: share of the top-10% picks' score above the average stock (sums to 100%; negative = pushes "
        f"top picks down). Direction: + means a higher value gives a higher score.",
        "",
    ]
    for kind, title in (("family", "Families"), ("input", "Inputs")):
        k = t[t["kind"] == kind]
        early = k["test_year"] < REPORT_SPLIT_YEAR
        g = k.groupby("name")
        tab = pd.DataFrame({
            "rank_share": g["rank_share"].mean(),
            "share": g["share"].mean(),
            span[0]: k[early].groupby("name")["rank_share"].mean(),
            span[1]: k[~early].groupby("name")["rank_share"].mean(),
            "fold min–max": g["rank_share"].min().map(pct) + "–" + g["rank_share"].max().map(pct),
            "top-pick lift": g["top_lift"].mean(),
            "direction": g["direction"].mean(),
        }).sort_values("rank_share", ascending=False)
        lines += [f"## {title}", "", "| | Ranking share | " + " | ".join(span) + " | Fold min–max | Plain share | Top-pick lift | Direction |",
                  "|---|---|---|---|---|---|---|---|"]
        for n, r in tab.iterrows():
            label = n if kind == "family" else f"{LABELS.get(n, n)} (`{n}`)"
            direction = "" if np.isnan(r["direction"]) else f"{r['direction']:+.2f}"
            lines.append(f"| {label} | {pct(r['rank_share'])} | {pct(r[span[0]])} | {pct(r[span[1]])} | {r['fold min–max']} | "
                         f"{pct(r['share'])} | {r['top-pick lift']:+.0%} | {direction} |")
        lines.append("")
    fam = t[t["kind"] == "family"].pivot_table(index="test_year", columns="name", values="rank_share", aggfunc="mean")
    order = fam.mean().sort_values(ascending=False).index
    lines += ["## Family ranking share by test year", "", "| Year | " + " | ".join(order) + " |", "|---" * (len(order) + 1) + "|"]
    lines += [f"| {y} | " + " | ".join(pct(fam.loc[y, c]) for c in order) + " |" for y in fam.index]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    args = sys.argv[1:]
    max_folds = next((int(a.split("=", 1)[1]) for a in args if a.startswith("--max-folds=")), None)
    specs = [a.split("=", 1) for a in args if not a.startswith("--")]
    if not specs or any(len(s) != 2 for s in specs):
        sys.exit(__doc__)
    OUT.mkdir(parents=True, exist_ok=True)
    all_runs = sorted({r for _, runs in specs for r in runs.split(",")})
    print(f"[shap] SHAP {shap.__version__}; runs: {', '.join(all_runs)}", flush=True)
    table = explain_runs(all_runs, max_folds)
    for name, runs in specs:
        runs = runs.split(",")
        t = table[table["run"].isin(runs)]
        t.to_csv(OUT / f"{name}_folds.csv", index=False)
        md = report(name, runs, t)
        (OUT / f"{name}.md").write_text(md)
        print(f"\nWrote {OUT / name}.md\n{md}")
