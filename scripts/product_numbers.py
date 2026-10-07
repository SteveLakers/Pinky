#!/usr/bin/env python3
"""
Recompute every number the product page (product/index.html) shows, from saved runs. No training.

The page's numbers are hand-copied from this script's output, so re-run it before any page update
and compare. Writes artifacts/product_numbers.json (gitignored). Takes about 5 minutes.

Versions on the page: "best so far" = v6_pit Ridge, top 10% + buffer; "current" / "calm" =
v8_pit_no-growth (same inputs as v7_pit) LightGBM; "hunter" = v7_pit_no-rank_label LightGBM;
growth test = the 12 v8 real / placebo runs (seeds 42, 7, 99).

Usage: PYTHONPATH=. python scripts/product_numbers.py
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from compare_runs import winner_crash_rates
from pinky.backtest import run_backtest, summarize_backtest
from pinky.config import (
    BACKTEST_BUFFER_MULT,
    BACKTEST_MAX_SECTOR_SHARE,
    BACKTEST_TOP_FRAC,
    DATA_SHARADAR_DIR,
    PROJECT_ROOT,
)
from pinky.metrics import acquired_share
from pinky.universe import acquisition_dates, backtest_prices, load_panel, sector_map

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
SEEDS = {42: "", 7: "_s7", 99: "_s99"}
PORT = "Top 10% + buffer"


def stats(run: str, signal: str, portfolio: str = PORT) -> dict:
    s = pd.read_csv(ARTIFACTS_DIR / f"backtest_stats_1y_{run}.csv")
    s = s[(s["signal"] == signal) & (s["portfolio"] == portfolio)].set_index("period")
    return {p: {k: float(s.loc[p, k]) for k in ("cagr_net", "cagr_spy", "cagr_universe_ew")} for p in s.index}


def preds(run: str) -> pd.DataFrame:
    return pd.read_parquet(ARTIFACTS_DIR / f"oos_preds_1y_{run}.parquet")


def base_rates(p: pd.DataFrame) -> tuple[float, float]:
    """Share of all stocks (monthly first test dates) that are big winners / crashes."""
    first = p.groupby(p["Date"].dt.to_period("M"))["Date"].transform("min")
    m = p[p["Date"] == first].dropna(subset=["excess_1y"])
    return float(m["top_1y"].mean()), float((m["excess_1y"] < -0.5).mean())


def fates(p: pd.DataFrame) -> dict:
    """Where the companies in a test set are now: still trading, bought, bankrupt / kicked off, other."""
    t = pd.read_parquet(DATA_SHARADAR_DIR / "tickers.parquet")
    t = t[t["table"] == "SEP"].drop_duplicates("ticker").set_index("ticker")
    a = pd.read_parquet(DATA_SHARADAR_DIR / "actions.parquet", columns=["ticker", "action"])
    tick = pd.Index(p["Ticker"].unique())
    gone = tick[t["isdelisted"].reindex(tick).eq("Y").to_numpy()]
    bought = set(a.loc[a["action"] == "acquisitionby", "ticker"])
    bad = set(a.loc[a["action"].isin(["bankruptcyliquidation", "regulatorydelisting"]), "ticker"])
    out = {"total": len(tick), "still_trade": len(tick) - len(gone),
           "acquired": sum(x in bought for x in gone),
           "bankrupt_or_forced": sum(x not in bought and x in bad for x in gone)}
    out["other"] = len(gone) - out["acquired"] - out["bankrupt_or_forced"]
    return out


def sector_share(bt: pd.DataFrame, sectors: dict[str, str]) -> dict[str, float]:
    share: dict[str, float] = {}
    for picks in bt["picks"]:
        names = picks.split(",")
        for x in names:
            share[sectors.get(x, "Unknown")] = share.get(sectors.get(x, "Unknown"), 0.0) + 1.0 / len(names)
    return {k: round(v / len(bt), 4) for k, v in sorted(share.items(), key=lambda kv: -kv[1])}


def main() -> None:
    n: dict = {}
    n["best_v6_ridge"] = stats("v6_pit", "Ridge")
    n["fancy_v6_lgbm_top10_buffer"] = stats("v6_pit", "LightGBM", "Top-10 + buffer")
    n["calm_current"] = stats("v8_pit_no-growth", "LightGBM")
    n["hunter"] = stats("v7_pit_no-rank_label", "LightGBM")
    for name, base in (("calm", "v8_pit"), ("hunter", "v8_pit_no-rank_label")):
        for kind, tag in (("real", ""), ("placebo", "_placebo")):
            runs = [stats(f"{base}{tag}{s}", "LightGBM") for s in SEEDS.values()]
            n[f"growth_{name}_{kind}"] = {p: float(np.mean([r[p]["cagr_net"] for r in runs])) for p in runs[0]}

    prices, sectors = backtest_prices(), sector_map()
    kw = dict(top_frac=BACKTEST_TOP_FRAC, max_sector_share=BACKTEST_MAX_SECTOR_SHARE,
              buffer_mult=BACKTEST_BUFFER_MULT, sectors=sectors)
    p6, pa, pb = preds("v6_pit"), preds("v8_pit_no-growth"), preds("v7_pit_no-rank_label")
    bt6 = run_backtest(p6, "pred_excess_ridge", prices, **kw)
    bta = run_backtest(pa, "pred_excess_lgbm", prices, **kw)
    btb = run_backtest(pb, "pred_excess_lgbm", prices, **kw)
    grow = lambda r: [10000.0] + [round(float(x)) for x in 10000 * (1 + r).cumprod()]
    n["growth_10k"] = {"best": grow(bt6["net"]), "spy": grow(bt6["spy"]), "current": grow(bta["net"]),
                       "every_stock": grow(bta["universe_ew"]), "hunter": grow(btb["net"]),
                       "dates": [str(bt6["start"].iloc[0].date())] + [str(d.date()) for d in bt6["end"]]}
    n["avg_picks_current"] = float(bta["n_picks"].mean())
    n["check_cagr"] = {k: summarize_backtest(b)["cagr_net"] for k, b in (("best", bt6), ("current", bta), ("hunter", btb))}

    acq = acquisition_dates()
    n["random_big_crash"] = base_rates(pa)
    n["fancy_v6_big_crash"] = winner_crash_rates(p6, "pred_excess_lgbm")
    n["calm_big_crash"] = winner_crash_rates(pa, "pred_excess_lgbm")
    n["hunter_big_crash"] = winner_crash_rates(pb, "pred_excess_lgbm")
    n["simple_v6_acquired_top10"] = acquired_share(p6, "pred_excess_ridge", acq, k=10)
    n["acquired_base_rate"] = acquired_share(p6, "pred_excess_ridge", acq, frac=1.0)

    m = pd.read_csv(ARTIFACTS_DIR / "walkforward_metrics_v8_pit_no-growth.csv")
    n["ic_by_year_calm"] = {str(pd.Timestamp(t).year): round(float(v), 4) for t, v in zip(m["test_start"], m["ic_lgbm"])}
    n["snapshots_last_fold"] = int(m["n_train"].iloc[-1])
    n["snapshots_scored"] = int(len(pa))
    n["stocks_per_date"] = float(pa.groupby("Date").size().mean())
    sg = pd.read_csv(ARTIFACTS_DIR / "score_groups_1y_v8_pit_no-growth.csv")
    n["score_groups_calm"] = sg[sg["signal"] == "LightGBM"].drop(columns="signal").to_dict(orient="records")

    n["fates_test"] = fates(pa)
    n["sectors"] = {"calm": sector_share(bta, sectors), "hunter": sector_share(btb, sectors)}
    first = pa.groupby(pa["Date"].dt.to_period("M"))["Date"].transform("min")
    monthly = pa[pa["Date"] == first]
    mk = monthly["Ticker"].map(sectors).fillna("Unknown").groupby(monthly["Date"]).value_counts(normalize=True)
    n["sectors"]["market"] = {k: round(float(v), 4) for k, v in mk.groupby(level=1).mean().sort_values(ascending=False).items()}

    u = load_panel("universe")
    daily = u.notna().sum(axis=1)
    n["universe_by_year"] = {str(y): int(round(v)) for y, v in daily.groupby(daily.index.year).mean().items()}
    n["universe_distinct"] = int(u.notna().any().sum())

    out = ARTIFACTS_DIR / "product_numbers.json"
    out.write_text(json.dumps(n, indent=1))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
