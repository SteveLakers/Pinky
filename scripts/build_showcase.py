"""
Build a self-contained one-page showcase for Pinky.

Reads saved walk-forward predictions in `artifacts/` — the honest point-in-time run (`RUN`)
plus the old 128-stock run (`OLD_RUN`) for the "why +41% was not real" section — re-runs
the portfolio backtests, and writes `showcase/index.html` with every number embedded as JSON.
No training, no network, no CDNs: the page renders offline with inline SVG.
Only aggregate results are embedded (no vendor price data).

Run: PYTHONPATH=. python scripts/build_showcase.py
"""

from __future__ import annotations

import os
import warnings

os.environ.setdefault("PYTHONWARNINGS", "ignore")
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")
warnings.filterwarnings("ignore")

import json
from pathlib import Path

import numpy as np
import pandas as pd

from pinky.backtest import (
    between_years,
    default_prices,
    momentum_scores,
    pick_sector_share,
    run_backtest,
    summarize_backtest,
    with_cost,
)
from pinky.config import (
    BACKTEST_BUFFER_MULT,
    BACKTEST_COST_BPS,
    BACKTEST_MAX_SECTOR_SHARE,
    BACKTEST_TOP_FRAC,
    BACKTEST_TOP_N,
    HINDSIGHT_WINNERS,
    HOLDOUT_START,
    PROJECT_ROOT,
    REPORT_SPLIT_YEAR,
    UNIVERSE_MIN_DOLLAR_VOLUME,
    UNIVERSE_MIN_PRICE,
)
from pinky.metrics import acquired_share, precision_at_k, winner_capture
from pinky.pit_dataset import DATASET_PATH
from pinky.universe import acquisition_dates, backtest_prices, sector_map

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
OUT_DIR = PROJECT_ROOT / "showcase"
RUN = "v6_pit"
OLD_RUN = "v4"
START_CAPITAL = 10_000.0
HIGH_COST_BPS = 25.0
CRASH_EXCESS = -0.5  # a pick "crashes" if it trails SPY by more than 50% over the next year


def equity_curve(bt: pd.DataFrame, col: str) -> list[dict]:
    """Growth of $10k, one point per holding period (plus the starting point)."""
    pts = [{"t": bt["start"].iloc[0].date().isoformat(), "v": START_CAPITAL}]
    value = START_CAPITAL
    for _, row in bt.iterrows():
        value *= 1.0 + float(row[col])
        pts.append({"t": row["end"].date().isoformat(), "v": round(value, 2)})
    return pts


def period_cagr(bt: pd.DataFrame, col: str, first: int | None = None, last: int | None = None) -> float:
    b = between_years(bt, first, last)
    years = (b["end"].iloc[-1] - b["start"].iloc[0]).days / 365.25
    return float((1.0 + b[col]).prod() ** (1.0 / years) - 1.0)


def max_drawdown(bt: pd.DataFrame, col: str) -> float:
    curve = (1.0 + bt[col]).cumprod()
    return float((curve / curve.cummax() - 1.0).min())


def make_curve(key: str, label: str, color: str, bt: pd.DataFrame, col: str, note: str) -> dict:
    points = equity_curve(bt, col)
    return {
        "key": key,
        "label": label,
        "color": color,
        "note": note,
        "points": points,
        "final": points[-1]["v"],
        "cagr": period_cagr(bt, col),
        "cagr_pre": period_cagr(bt, col, last=REPORT_SPLIT_YEAR - 1),
        "cagr_post": period_cagr(bt, col, first=REPORT_SPLIT_YEAR),
        "max_dd": max_drawdown(bt, col),
    }


def skill_metrics(preds: pd.DataFrame, mom: pd.DataFrame, acq: pd.Series) -> dict:
    """Hit rate, crash rate, buyout rate and winner capture of the monthly top-10."""
    n = BACKTEST_TOP_N
    preds = preds.assign(
        crash=np.where(preds["excess_1y"].isna(), np.nan, preds["excess_1y"] < CRASH_EXCESS)
    )
    mom = mom.merge(
        preds[["Date", "Ticker", "top_1y", "stock_fwd_1y", "crash"]], on=["Date", "Ticker"]
    )
    signals = {
        "lgbm": (preds, "pred_excess_lgbm"),
        "ridge": (preds, "pred_excess_ridge"),
        "mom": (mom, "mom_12_1"),
    }
    out = {
        name: {
            "precision": precision_at_k(frame, col, "top_1y", k=n),
            "crash": precision_at_k(frame, col, "crash", k=n),
            "acquired": acquired_share(frame, col, acq, k=n),
            "winner_capture": winner_capture(frame, col, "stock_fwd_1y", k=n),
        }
        for name, (frame, col) in signals.items()
    }
    avg_n = preds.groupby("Date").size().mean()
    out["random"] = {
        "precision": precision_at_k(preds, "pred_excess_ridge", "top_1y", frac=1.0),
        "crash": precision_at_k(preds, "pred_excess_ridge", "crash", frac=1.0),
        "acquired": acquired_share(preds, "pred_excess_ridge", acq, frac=1.0),
        "winner_capture": n / avg_n,
    }
    return out


def buyout_split(
    preds: pd.DataFrame, col: str, acq: pd.Series, vol: pd.DataFrame, k: int, days: int = 183
) -> dict:
    """Monthly top-k picks: the ones bought out within `days` vs the rest."""
    d = preds["Date"]
    monthly = preds[d.isin(set(d.groupby(d.dt.to_period("M")).min()))]
    top = monthly.sort_values(col, ascending=False).groupby("Date").head(k)
    deal = top["Ticker"].map(acq)
    top = top.assign(bought=(deal > top["Date"]) & (deal <= top["Date"] + pd.Timedelta(days=days)))
    top = top.merge(vol, on=["Date", "Ticker"], how="left")

    def stats(part: pd.DataFrame) -> dict:
        excess = part["excess_1y"].dropna().astype(float)
        return {
            "n": int(len(part)),
            "vol": float(part["vol_63"].median()),
            "crash": float((excess < CRASH_EXCESS).mean()),
            "excess": float(excess.mean()),
        }

    return {"bought": stats(top[top["bought"]]), "other": stats(top[~top["bought"]])}


def old_results() -> dict:
    """The original 128-stock run (survivorship-biased), for the 'what changed' section."""
    preds = pd.read_parquet(ARTIFACTS_DIR / f"oos_preds_1y_{OLD_RUN}.parquet")
    preds_ex5 = pd.read_parquet(ARTIFACTS_DIR / f"oos_preds_1y_{OLD_RUN}_ex5.parquet")
    prices = default_prices()
    prices_ex5 = prices.drop(columns=[t for t in HINDSIGHT_WINNERS if t in prices.columns])
    cap = BACKTEST_MAX_SECTOR_SHARE
    s = summarize_backtest(run_backtest(preds, "pred_excess_lgbm", prices, max_sector_share=cap))
    s_ex5 = summarize_backtest(
        run_backtest(preds_ex5, "pred_excess_lgbm", prices_ex5, max_sector_share=cap)
    )
    return {
        "n_stocks": int(preds["Ticker"].nunique()),
        "start": s["start"],
        "end": s["end"],
        "cagr": s["cagr_net"],
        "cagr_ex5": s_ex5["cagr_net"],
        "cagr_spy": s["cagr_spy"],
        "winners": list(HINDSIGHT_WINNERS),
    }


def build_data() -> dict:
    preds = pd.read_parquet(ARTIFACTS_DIR / f"oos_preds_1y_{RUN}.parquet")
    prices, sectors, acq = backtest_prices(), sector_map(), acquisition_dates()
    n, frac = BACKTEST_TOP_N, BACKTEST_TOP_FRAC
    common = {
        "sectors": sectors,
        "max_sector_share": BACKTEST_MAX_SECTOR_SHARE,
        "buffer_mult": BACKTEST_BUFFER_MULT,
    }
    bt_broad = run_backtest(preds, "pred_excess_ridge", prices, top_frac=frac, **common)
    bt_ridge10 = run_backtest(preds, "pred_excess_ridge", prices, top_n=n, **common)
    bt_lgbm10 = run_backtest(preds, "pred_excess_lgbm", prices, top_n=n, **common)
    mom = momentum_scores(preds, prices)
    bt_mom10 = run_backtest(mom, "mom_12_1", prices, top_n=n, **common)
    vol = pd.read_parquet(DATASET_PATH, columns=["Date", "Ticker", "vol_63"])
    # The curves must share a period grid to be plotted on one axis.
    for other in (bt_ridge10, bt_lgbm10):
        assert list(bt_broad["end"]) == list(other["end"]), "backtest period grids differ"

    avg_n = float(preds.groupby("Date").size().mean())
    curves = [
        make_curve("spy", "S&P 500 (SPY)", "#94a3b8", bt_broad, "spy", "Just buying the index."),
        make_curve(
            "ew", "Own every stock equally", "#34d399", bt_broad, "universe_ew",
            f"All ~{avg_n:,.0f} stocks in the universe, rebalanced monthly (no trading costs).",
        ),
        make_curve(
            "ridge_broad", f"Ridge · top {frac:.0%}", "#a78bfa", bt_broad, "net",
            "Best version so far: a simple linear model holding its top 10% of stocks.",
        ),
        make_curve(
            "ridge10", f"Ridge · top {n}", "#f472b6", bt_ridge10, "net",
            "Same model, only its 10 favorite stocks. Many are takeover targets.",
        ),
        make_curve(
            "lgbm10", f"LightGBM · top {n}", "#22d3ee", bt_lgbm10, "net",
            "The machine-learning model. It picks volatile “lottery tickets”.",
        ),
    ]

    s = summarize_backtest(bt_broad)
    years = bt_broad["start"].dt.year
    sector_rows = [
        {"sector": sec, "share": float(v)} for sec, v in pick_sector_share(bt_broad, sectors).items()
    ]
    high_cost = {
        key: summarize_backtest(with_cost(bt, HIGH_COST_BPS))["cagr_net"]
        for key, bt in [("ridge_broad", bt_broad), ("ridge10", bt_ridge10), ("lgbm10", bt_lgbm10)]
    }
    return {
        "meta": {
            "generated": pd.Timestamp.today().date().isoformat(),
            "run": RUN,
            "start": s["start"],
            "end": s["end"],
            "months": s["months"],
            "first_year": int(years.min()),
            "last_year": int(years.max()),
            "split_year": REPORT_SPLIT_YEAR,
            "n_stocks": int(preds["Ticker"].nunique()),
            "avg_per_date": avg_n,
            "per_date_min": int(preds.groupby("Date").size().min()),
            "per_date_max": int(preds.groupby("Date").size().max()),
            "min_price": UNIVERSE_MIN_PRICE,
            "min_dollar_volume": UNIVERSE_MIN_DOLLAR_VOLUME,
            "top_n": n,
            "top_frac": frac,
            "buffer_mult": BACKTEST_BUFFER_MULT,
            "cost_bps": BACKTEST_COST_BPS,
            "high_cost_bps": HIGH_COST_BPS,
            "sector_cap": BACKTEST_MAX_SECTOR_SHARE,
            "start_capital": START_CAPITAL,
            "holdout_start": HOLDOUT_START,
            "crash_excess": CRASH_EXCESS,
        },
        "curves": curves,
        "high_cost": high_cost,
        "old": old_results(),
        "sectors": sector_rows,
        "skill": skill_metrics(preds, mom, acq),
        "top10_cagr": {
            "lgbm": summarize_backtest(bt_lgbm10)["cagr_net"],
            "mom": summarize_backtest(bt_mom10)["cagr_net"],
        },
        "buyouts": buyout_split(preds, "pred_excess_ridge", acq, vol, n),
    }


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pinky — a stock-ranking research project</title>
<style>
  :root{
    --bg:#080a0f; --panel:#11141c; --panel2:#161a24; --line:#232836;
    --ink:#eef2f8; --muted:#97a1b5; --cyan:#22d3ee; --violet:#a78bfa;
    --amber:#f59e0b; --slate:#94a3b8; --red:#fb7185; --green:#34d399;
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{
    margin:0; background:var(--bg); color:var(--ink);
    font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
    -webkit-font-smoothing:antialiased;
  }
  .wrap{max-width:1080px; margin:0 auto; padding:0 22px}
  section{padding:70px 0; border-top:1px solid var(--line)}
  section:first-of-type{border-top:0}
  h1,h2,h3{line-height:1.2; margin:0 0 14px}
  h1{font-size:clamp(34px,6vw,60px); letter-spacing:-.025em; font-weight:700}
  h2{font-size:clamp(24px,3.4vw,34px); letter-spacing:-.02em}
  h3{font-size:17px; letter-spacing:-.01em}
  p{margin:0 0 14px; color:var(--muted)}
  .lead{font-size:clamp(17px,2.1vw,20px); color:#c6cede; max-width:62ch}
  .eyebrow{
    font-size:12px; font-weight:700; letter-spacing:.16em; text-transform:uppercase;
    color:var(--cyan); margin-bottom:12px;
  }

  /* hero */
  .hero{position:relative; overflow:hidden; padding:84px 0 60px}
  .hero::before{
    content:""; position:absolute; inset:-40% 30% auto -10%; height:640px;
    background:radial-gradient(circle at 30% 30%, rgba(34,211,238,.16), transparent 62%);
    pointer-events:none;
  }
  .hero::after{
    content:""; position:absolute; inset:-30% -20% auto 40%; height:600px;
    background:radial-gradient(circle at 60% 30%, rgba(167,139,250,.14), transparent 62%);
    pointer-events:none;
  }
  .hero > *{position:relative}
  .pill{
    display:inline-flex; align-items:center; gap:8px; padding:6px 13px; border-radius:999px;
    border:1px solid var(--line); background:rgba(255,255,255,.03);
    font-size:12.5px; color:var(--muted);
  }
  .dot{width:7px;height:7px;border-radius:50%;background:var(--cyan)}
  .grad{background:linear-gradient(95deg,#22d3ee,#a78bfa 55%,#f472b6);
        -webkit-background-clip:text; background-clip:text; color:transparent}
  .badges{display:flex; flex-wrap:wrap; gap:9px; margin-top:26px}
  .badge{
    padding:7px 13px; border-radius:9px; border:1px solid var(--line);
    background:var(--panel); font-size:13px; color:#c6cede;
  }
  .badge b{color:var(--ink); font-weight:600}

  /* generic blocks */
  .card{background:var(--panel); border:1px solid var(--line); border-radius:15px; padding:22px}
  .grid{display:grid; gap:16px}
  .g2{grid-template-columns:repeat(2,1fr)}
  .g3{grid-template-columns:repeat(3,1fr)}
  .note{font-size:13.5px; color:var(--muted); margin:10px 0 0}

  /* pipeline */
  .pipe{display:grid; grid-template-columns:repeat(6,1fr); gap:10px; margin-top:26px}
  .step{
    background:var(--panel); border:1px solid var(--line); border-radius:13px; padding:16px 14px;
    position:relative;
  }
  .step .n{
    font-size:11px; font-weight:700; letter-spacing:.1em; color:var(--cyan);
    display:block; margin-bottom:8px;
  }
  .step b{display:block; font-size:14.5px; margin-bottom:5px}
  .step span.d{font-size:12.5px; color:var(--muted); display:block; line-height:1.5}
  .step:not(:last-child)::after{
    content:"›"; position:absolute; right:-9px; top:50%; transform:translateY(-50%);
    color:#3b4256; font-size:20px; z-index:2;
  }

  /* chart */
  .chartbox{background:var(--panel); border:1px solid var(--line); border-radius:15px; padding:20px 18px 12px}
  .charthead{display:flex; flex-wrap:wrap; gap:12px; align-items:baseline; justify-content:space-between; margin-bottom:6px}
  .legend{display:flex; flex-wrap:wrap; gap:8px 16px; margin:14px 2px 4px}
  .lg{display:flex; align-items:center; gap:7px; font-size:13px; color:#c6cede; cursor:default}
  .sw{width:11px;height:11px;border-radius:3px;flex:none}
  .toggle{
    display:flex; gap:2px; padding:3px; border:1px solid var(--line);
    border-radius:9px; background:var(--panel2);
  }
  .toggle button{
    border:0; background:transparent; color:var(--muted); font:inherit; font-size:12.5px;
    padding:5px 12px; border-radius:7px; cursor:pointer;
  }
  .toggle button.on{background:#232a38; color:var(--ink)}
  .svgwrap{position:relative}
  svg{display:block; width:100%; height:auto; overflow:visible}
  .tip{
    position:absolute; pointer-events:none; opacity:0; transition:opacity .1s;
    background:#0d1017; border:1px solid #2b3244; border-radius:11px; padding:10px 12px;
    font-size:12.5px; box-shadow:0 12px 34px rgba(0,0,0,.6); min-width:190px; z-index:5;
  }
  .tip .tt{color:var(--muted); font-size:11.5px; margin-bottom:7px; letter-spacing:.02em}
  .tip .tr{display:flex; align-items:center; gap:7px; justify-content:space-between; margin-top:3px}
  .tip .tr span{display:flex; align-items:center; gap:7px; color:#c6cede}
  .tip .tr b{font-variant-numeric:tabular-nums; color:var(--ink); font-weight:600}

  /* table */
  table{width:100%; border-collapse:collapse; font-size:14.5px}
  th,td{padding:12px 10px; text-align:right; border-bottom:1px solid var(--line)}
  th:first-child,td:first-child{text-align:left}
  thead th{font-size:11.5px; letter-spacing:.09em; text-transform:uppercase; color:var(--muted); font-weight:600}
  tbody tr:last-child td{border-bottom:0}
  td.num{font-variant-numeric:tabular-nums}
  .tick{display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:9px;vertical-align:middle}
  .sub{display:block; font-size:12px; color:var(--muted); margin-top:3px}

  /* reality check */
  .reality{
    border:1px solid rgba(251,113,133,.35); border-radius:15px; padding:24px;
    background:linear-gradient(180deg, rgba(251,113,133,.09), rgba(251,113,133,.03));
    margin-top:26px;
  }
  .reality h3{color:#fda4af; display:flex; align-items:center; gap:9px}
  .vs{display:grid; grid-template-columns:1fr auto 1fr; gap:14px; align-items:center; margin:20px 0 6px; max-width:560px}
  .vsb{background:rgba(0,0,0,.28); border:1px solid var(--line); border-radius:12px; padding:14px 16px}
  .vsb .big{font-size:32px; font-weight:700; letter-spacing:-.02em; font-variant-numeric:tabular-nums}
  .vsb .cap{font-size:12px; color:var(--muted); margin-top:2px; line-height:1.45}
  .arrow{color:#fb7185; font-size:22px; text-align:center}

  /* roadmap */
  .phase{background:var(--panel); border:1px solid var(--line); border-radius:15px; padding:20px}
  .phase .tag{
    display:inline-block; font-size:11px; font-weight:700; letter-spacing:.12em; text-transform:uppercase;
    padding:4px 10px; border-radius:999px; margin-bottom:12px;
  }
  .t1{background:rgba(34,211,238,.14); color:var(--cyan)}
  .t2{background:rgba(167,139,250,.14); color:var(--violet)}
  .t3{background:rgba(148,163,184,.13); color:var(--slate)}
  .phase ul{margin:0; padding-left:18px}
  .phase li{color:var(--muted); font-size:14px; margin-bottom:7px}
  .phase li b{color:#c6cede; font-weight:600}

  footer{border-top:1px solid var(--line); padding:34px 0 56px; color:var(--muted); font-size:13.5px}
  footer strong{color:#c6cede}

  @media (max-width:900px){
    .pipe{grid-template-columns:repeat(2,1fr)}
    .step:not(:last-child)::after{display:none}
    .g3{grid-template-columns:1fr}
    .g2{grid-template-columns:1fr}
    section{padding:52px 0}
  }
  @media (max-width:560px){
    .vs{grid-template-columns:1fr; max-width:none}
    .arrow{transform:rotate(90deg)}
    th,td{padding:10px 6px; font-size:13.5px}
  }
</style>
</head>
<body>

<div class="wrap">

  <!-- HERO -->
  <section class="hero">
    <span class="pill"><span class="dot"></span> Research project · not investment advice</span>
    <h1>Pinky tries to pick the stocks<br>that <span class="grad">beat the S&amp;P 500</span>.</h1>
    <p class="lead">
      Once a month it ranks the liquid US stocks and buys the best-ranked ones. The aim is to spot
      big winners early. Tech is the sector we like most, but the model can buy any sector.
    </p>
    <p class="lead" style="color:#fda4af;border-left:2px solid rgba(251,113,133,.5);padding-left:14px"
       id="heroHonesty"></p>
    <div class="badges" id="heroBadges"></div>
  </section>

  <!-- HOW IT WORKS -->
  <section>
    <div class="eyebrow">How it works</div>
    <h2>Six steps, repeated every month</h2>
    <p class="lead">Nothing here is hand-picked. The model only ever sees the past when it makes a choice.</p>
    <div class="pipe">
      <div class="step"><span class="n">01</span><b>Honest data</b><span class="d">Daily prices for every US stock, including companies that later went bust or were bought.</span></div>
      <div class="step"><span class="n">02</span><b>Liquid universe</b><span class="d" id="stepUniverse"></span></div>
      <div class="step"><span class="n">03</span><b>Features</b><span class="d">Price signals only, so far: trend, momentum, volatility, volume.</span></div>
      <div class="step"><span class="n">04</span><b>Walk-forward</b><span class="d">Train on the past, test on the next unseen year. Repeat. Never peek ahead.</span></div>
      <div class="step"><span class="n">05</span><b>Portfolio</b><span class="d">Buy the top-ranked stocks in equal amounts, max 60% per sector. Keep a holding while it stays near the top.</span></div>
      <div class="step"><span class="n">06</span><b>Costs &amp; scoring</b><span class="d">Charge trading costs, then compare with the S&amp;P 500 and with owning every stock.</span></div>
    </div>
  </section>

  <!-- RESULTS -->
  <section>
    <div class="eyebrow">Results</div>
    <h2>What $10,000 would have done</h2>
    <p class="lead" id="resultsLead"></p>

    <div class="chartbox">
      <div class="charthead">
        <div style="font-size:13px;color:var(--muted)">Growth of $10,000 · after trading costs</div>
        <div class="toggle">
          <button id="btnLin" class="on">Linear</button>
          <button id="btnLog">Log</button>
        </div>
      </div>
      <div class="svgwrap">
        <div id="chart"></div>
        <div class="tip" id="tip"></div>
      </div>
      <div class="legend" id="legend"></div>
    </div>

    <div class="card" style="margin-top:16px;padding:6px 18px">
      <table>
        <thead><tr>
          <th>Strategy</th><th>Per year</th><th id="thPre"></th><th id="thPost"></th>
          <th>Worst drop</th><th>$10,000 became</th>
        </tr></thead>
        <tbody id="statsRows"></tbody>
      </table>
    </div>
    <p class="note" id="statsNote"></p>

    <!-- REALITY CHECK -->
    <div class="reality">
      <h3>Why the old +41% was not real</h3>
      <p id="oldText"></p>
      <div class="vs">
        <div class="vsb">
          <div class="big" style="color:var(--cyan)" id="bigA"></div>
          <div class="cap" id="capA"></div>
        </div>
        <div class="arrow">→</div>
        <div class="vsb">
          <div class="big" style="color:#fb7185" id="bigB"></div>
          <div class="cap" id="capB"></div>
        </div>
      </div>
      <p class="note" id="realityNote"></p>
    </div>
  </section>

  <!-- SKILL -->
  <section>
    <div class="eyebrow">Is it actually skill?</div>
    <h2>Finding winners is not the same as making money</h2>
    <p class="lead" id="skillLead"></p>
    <div class="grid g2" style="margin-top:22px">
      <div class="card">
        <h3>Top-10 picks that become big winners</h3>
        <p class="note" style="margin:0 0 14px">Share of picks that land in the best 10% of stocks over the next year.</p>
        <div id="precChart"></div>
      </div>
      <div class="card">
        <h3>Top-10 picks that crash</h3>
        <p class="note" style="margin:0 0 14px">Share of picks that trail the S&amp;P 500 by more than 50% over the next year.</p>
        <div id="crashChart"></div>
      </div>
      <div class="card">
        <h3>Top-10 picks that get bought out</h3>
        <p class="note" style="margin:0 0 14px">Share of picks whose company is acquired within 6 months.</p>
        <div id="acqChart"></div>
      </div>
      <div class="card">
        <h3>Holding the year’s biggest winners</h3>
        <p class="note" style="margin:0 0 14px">Share of each year’s 20 best stocks held, month by month.</p>
        <div id="capChart"></div>
      </div>
    </div>
    <p class="note" id="skillNote"></p>
  </section>

  <!-- SECTORS -->
  <section>
    <div class="eyebrow">What it buys</div>
    <h2>Spread across sectors</h2>
    <p class="lead" id="sectorLead"></p>
    <div class="card" style="margin-top:22px"><div id="sectorChart"></div></div>
    <p class="note">Average share of picks by sector. The 60% sector cap is a hard limit, but it rarely comes into play on a universe this wide.</p>
  </section>

  <!-- ROADMAP -->
  <section>
    <div class="eyebrow">What’s next</div>
    <h2>Price alone is not enough. Next: look at the companies.</h2>
    <div class="grid g3" style="margin-top:22px">
      <div class="phase">
        <span class="tag t1">Phase 1 · done</span>
        <h3>Honest evaluation</h3>
        <ul>
          <li>Proper historical data, including <b>companies that went bust or got bought</b>.</li>
          <li>Liquid US stocks as they existed at the time: <b id="universeRange"></b>.</li>
          <li>Result: price data alone gives <b>no reliable edge</b>.</li>
        </ul>
      </div>
      <div class="phase">
        <span class="tag t2">Phase 2 · in progress</span>
        <h3>Look at the companies</h3>
        <ul>
          <li><b>Done:</b> a stricter yardstick (2020 crash tested, holding buffer, wider portfolios).</li>
          <li><b>Next:</b> model fixes, then <b>growth and revenue acceleration</b>.</li>
          <li>Then margins, earnings reactions, R&amp;D, quality and insiders. Anything that doesn’t beat the baseline gets dropped.</li>
        </ul>
      </div>
      <div class="phase">
        <span class="tag t3">Phase 3 · only if it works</span>
        <h3>Paper trading</h3>
        <ul>
          <li>Publish a monthly picks report.</li>
          <li>Track it live with fake money for a long stretch.</li>
          <li>Real money only after that, if ever.</li>
        </ul>
      </div>
    </div>
  </section>

  <footer>
    <p><strong>Research project, not investment advice. Backtests are hypothetical.</strong></p>
    <p style="margin:0" id="footNote"></p>
  </footer>
</div>

<script id="pinky-data" type="application/json">__DATA__</script>
<script>
(function(){
  "use strict";
  var D = JSON.parse(document.getElementById('pinky-data').textContent);
  var M = D.meta, O = D.old, S = D.skill;

  var pct = function(x, d){ return (x*100).toFixed(d===undefined?1:d) + '%'; };
  var sgn = function(x, d){ return (x>=0?'+':'') + pct(x, d); };
  var money = function(v){ return '$' + Math.round(v).toLocaleString('en-US'); };
  var monthYear = function(iso){
    var p = iso.split('-');
    var names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    return names[parseInt(p[1],10)-1] + ' ' + p[0];
  };
  var el = function(id){ return document.getElementById(id); };
  var esc = function(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;'); };

  var byKey = {};
  D.curves.forEach(function(c){ byKey[c.key] = c; });
  var spy = byKey.spy, best = byKey.ridge_broad, lgbm = byKey.lgbm10;
  var span = M.first_year + '–' + M.last_year;
  var pre = M.first_year + '–' + (M.split_year - 1), post = M.split_year + '–' + M.last_year;

  /* ---------- hero ---------- */
  var badges = [
    ['Stocks tested', M.n_stocks.toLocaleString('en-US')],
    ['Choices per month', '~' + Math.round(M.avg_per_date).toLocaleString('en-US')],
    ['Tested over', monthYear(M.start) + ' – ' + monthYear(M.end)],
    ['Rebalanced', 'Every month'],
    ['Trading cost charged', M.cost_bps + ' bps per side'],
    ['Max per sector', Math.round(M.sector_cap*100) + '%'],
    ['Final test', M.holdout_start.slice(0,4) + '+ locked, untouched']
  ];
  el('heroBadges').innerHTML = badges.map(function(b){
    return '<span class="badge">' + b[0] + ' <b>' + esc(b[1]) + '</b></span>';
  }).join('');

  el('heroHonesty').textContent =
    'Honest result so far: tested on liquid US stocks as they existed at the time, including ' +
    'companies that went bust or were bought, the current price-only model does not reliably beat ' +
    'the S&P 500. Its best version made ' + sgn(best.cagr) + '/yr vs ' + sgn(spy.cagr) +
    ' for the index (' + span + ')' +
    (best.cagr_post < spy.cagr_post
      ? ', and all of that lead came before ' + M.split_year + '; since then it trails the index. '
      : '. ') +
    'Nothing here has been traded with real money.';

  el('stepUniverse').textContent =
    'Each day, keep US stocks above $' + M.min_price + ' that trade at least $' +
    (M.min_dollar_volume/1e6) + 'M a day.';

  el('resultsLead').textContent =
    'Every strategy starts with $' + M.start_capital.toLocaleString('en-US') + ' in ' +
    monthYear(M.start) + ' and rebalances monthly. The model portfolios pay ' + M.cost_bps +
    ' bps of trading cost on every trade. ' + M.months + ' months, including the 2001–02 crash, ' +
    '2008 and the 2020 COVID crash.';
  el('universeRange').textContent =
    M.per_date_min.toLocaleString('en-US') + '–' + M.per_date_max.toLocaleString('en-US') +
    ' scored per test date';

  /* ---------- line chart ---------- */
  var W = 900, H = 400, PL = 62, PR = 18, PT = 18, PB = 34;
  var pts0 = D.curves[0].points;
  var n = pts0.length;
  var logMode = false;

  function niceTicks(lo, hi, count){
    var raw = (hi-lo)/count, mag = Math.pow(10, Math.floor(Math.log(raw)/Math.LN10));
    var norm = raw/mag, step = mag * (norm>=5?10:norm>=2?5:norm>=1?2:1);
    var out = [], v = Math.ceil(lo/step)*step;
    for(; v<=hi+1e-9; v+=step) out.push(v);
    return out;
  }

  function drawLine(){
    var lo = Infinity, hi = -Infinity;
    D.curves.forEach(function(c){
      c.points.forEach(function(p){ if(p.v<lo) lo=p.v; if(p.v>hi) hi=p.v; });
    });
    var f = logMode ? Math.log : function(v){ return v; };
    var ylo = logMode ? f(lo*0.92) : 0;
    var yhi = f(hi*1.06);

    var xAt = function(i){ return PL + i*(W-PL-PR)/(n-1); };
    var yAt = function(v){ return PT + (yhi - f(v))/(yhi-ylo)*(H-PT-PB); };

    var ticks;
    if(logMode){
      ticks = [];
      var d = Math.pow(10, Math.floor(Math.log(lo)/Math.LN10));
      for(var t=d; t<=hi*1.06; t*=10){ [1,2,5].forEach(function(m){
        if(t*m>=lo*0.92 && t*m<=hi*1.06) ticks.push(t*m);
      }); }
    } else {
      ticks = niceTicks(0, hi*1.06, 5);
    }

    var s = '<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Growth of $10,000 by strategy">';
    s += '<defs><clipPath id="cp"><rect x="'+PL+'" y="0" width="'+(W-PL-PR)+'" height="'+H+'"/></clipPath></defs>';

    ticks.forEach(function(v){
      var y = yAt(v);
      if(y < PT-2 || y > H-PB+2) return;
      s += '<line x1="'+PL+'" y1="'+y+'" x2="'+(W-PR)+'" y2="'+y+'" stroke="#1d2230" stroke-width="1"/>';
      s += '<text x="'+(PL-10)+'" y="'+(y+4)+'" text-anchor="end" font-size="11" fill="#7b8598">'+money(v)+'</text>';
    });

    var years = {};
    pts0.forEach(function(p,i){ var y = p.t.slice(0,4); if(!(y in years)) years[y] = i; });
    Object.keys(years).forEach(function(y, j){
      var x = xAt(years[y]);
      s += '<line x1="'+x+'" y1="'+PT+'" x2="'+x+'" y2="'+(H-PB)+'" stroke="#161b26" stroke-width="1"/>';
      if(j % 2 === 0){
        s += '<text x="'+x+'" y="'+(H-PB+20)+'" text-anchor="middle" font-size="11" fill="#7b8598">'+y+'</text>';
      }
    });

    D.curves.forEach(function(c){
      var d = c.points.map(function(p,i){ return (i?'L':'M') + xAt(i).toFixed(1) + ' ' + yAt(p.v).toFixed(1); }).join(' ');
      s += '<path d="'+d+'" fill="none" stroke="'+c.color+'" stroke-width="'+(c.key==='spy'?2:2.4)+'"'
         + (c.key==='spy'?' stroke-dasharray="5 4"':'')
         + ' stroke-linejoin="round" stroke-linecap="round" clip-path="url(#cp)" data-k="'+c.key+'"/>';
      var last = c.points[c.points.length-1];
      s += '<circle cx="'+xAt(n-1)+'" cy="'+yAt(last.v)+'" r="3.4" fill="'+c.color+'" data-k="'+c.key+'"/>';
    });

    s += '<line id="hl" x1="0" y1="'+PT+'" x2="0" y2="'+(H-PB)+'" stroke="#3b4458" stroke-width="1" opacity="0"/>';
    D.curves.forEach(function(c){
      s += '<circle class="hd" data-k="'+c.key+'" r="4.5" fill="'+c.color+'" stroke="#080a0f" stroke-width="2" opacity="0"/>';
    });
    s += '<rect id="hit" x="'+PL+'" y="'+PT+'" width="'+(W-PL-PR)+'" height="'+(H-PT-PB)+'" fill="transparent"/>';
    s += '</svg>';
    el('chart').innerHTML = s;

    var svg = el('chart').querySelector('svg');
    var tip = el('tip'), hl = svg.querySelector('#hl');
    var dots = svg.querySelectorAll('.hd');

    function move(ev){
      var r = svg.getBoundingClientRect();
      var cx = ev.touches ? ev.touches[0].clientX : ev.clientX;
      var vx = (cx - r.left) / r.width * W;
      var i = Math.round((vx - PL) / ((W-PL-PR)/(n-1)));
      i = Math.max(0, Math.min(n-1, i));
      hl.setAttribute('x1', xAt(i)); hl.setAttribute('x2', xAt(i)); hl.setAttribute('opacity','1');
      var rows = '';
      D.curves.forEach(function(c){
        var p = c.points[i];
        rows += '<div class="tr"><span><i class="sw" style="background:'+c.color+'"></i>'+esc(c.label)+'</span><b>'+money(p.v)+'</b></div>';
      });
      tip.innerHTML = '<div class="tt">'+monthYear(pts0[i].t)+'</div>'+rows;
      tip.style.opacity = '1';
      dots.forEach(function(dt){
        var c = byKey[dt.getAttribute('data-k')];
        dt.setAttribute('cx', xAt(i)); dt.setAttribute('cy', yAt(c.points[i].v)); dt.setAttribute('opacity','1');
      });
      var wrap = el('chart').parentNode.getBoundingClientRect();
      var px = (xAt(i)/W) * wrap.width;
      var tw = tip.offsetWidth || 210;
      tip.style.left = Math.max(4, Math.min(wrap.width - tw - 4, px + 16)) + 'px';
      tip.style.top = '14px';
    }
    function leave(){
      tip.style.opacity='0'; hl.setAttribute('opacity','0');
      dots.forEach(function(dt){ dt.setAttribute('opacity','0'); });
    }
    svg.addEventListener('mousemove', move);
    svg.addEventListener('touchmove', function(e){ move(e); }, {passive:true});
    svg.addEventListener('mouseleave', leave);
    svg.addEventListener('touchend', leave);
  }
  drawLine();

  el('btnLin').addEventListener('click', function(){
    logMode=false; this.classList.add('on'); el('btnLog').classList.remove('on'); drawLine();
  });
  el('btnLog').addEventListener('click', function(){
    logMode=true; this.classList.add('on'); el('btnLin').classList.remove('on'); drawLine();
  });

  el('legend').innerHTML = D.curves.map(function(c){
    return '<span class="lg"><i class="sw" style="background:'+c.color+'"></i>'+esc(c.label)+
           ' <b style="color:'+c.color+'">'+sgn(c.cagr,1)+'/yr</b></span>';
  }).join('');

  /* ---------- stats table ---------- */
  el('thPre').textContent = pre;
  el('thPost').textContent = post;
  el('statsRows').innerHTML = D.curves.map(function(c){
    return '<tr><td><span class="tick" style="background:'+c.color+'"></span>'+esc(c.label)+
           '<span class="sub">'+esc(c.note)+'</span></td>'+
           '<td class="num" style="color:'+c.color+';font-weight:600">'+sgn(c.cagr)+'</td>'+
           '<td class="num">'+sgn(c.cagr_pre)+'</td>'+
           '<td class="num">'+sgn(c.cagr_post)+'</td>'+
           '<td class="num">'+pct(c.max_dd)+'</td>'+
           '<td class="num">'+money(c.final)+'</td></tr>';
  }).join('');

  var beatPost = D.curves.filter(function(c){ return c.key !== 'spy' && c.cagr_post > spy.cagr_post; });
  el('statsNote').textContent =
    '"Per year" is after ' + M.cost_bps + ' bps of trading cost per side (owning every stock is ' +
    'shown without costs). At ' + M.high_cost_bps + ' bps, Ridge top 10% drops to ' +
    sgn(D.high_cost.ridge_broad) + '/yr. "Worst drop" is the deepest fall from a peak. ' +
    (beatPost.length === 0
      ? 'Since ' + M.split_year + ', none of these strategies beat the S&P 500.'
      : 'Since ' + M.split_year + ', only ' + beatPost.map(function(c){ return c.label; }).join(', ') +
        ' beat the S&P 500.');

  /* ---------- reality check ---------- */
  el('oldText').textContent =
    'The first version was tested on ' + O.n_stocks + ' stocks picked today, a list already full of ' +
    'companies we now know did brilliantly. On that list the model made ' + sgn(O.cagr,0) + '/yr (' +
    O.start.slice(0,4) + '–' + O.end.slice(0,4) + ', S&P 500: ' + sgn(O.cagr_spy,0) + '). Removing just ' +
    'five known winners (' + O.winners.join(', ') + ') cut it to ' + sgn(O.cagr_ex5,0) + '/yr. ' +
    'Then we rebuilt the test properly: the liquid US stocks as they existed at the time, failures included.';
  el('bigA').textContent = sgn(O.cagr,0);
  el('capA').textContent = 'per year · ' + O.n_stocks + ' stocks picked today (' +
    O.start.slice(0,4) + '–' + O.end.slice(0,4) + ')';
  el('bigB').textContent = sgn(lgbm.cagr,0);
  el('capB').textContent = 'per year · the same kind of model on liquid US stocks as they existed (' + span + ')';
  el('realityNote').textContent =
    'This is survivorship bias: a list picked today leaves out the companies that failed. ' +
    'Put them back and the machine-learning model loses money. The best honest version (Ridge, top 10%) ' +
    'made ' + sgn(best.cagr) + '/yr against ' + sgn(spy.cagr) + ' for the S&P 500.';

  /* ---------- bar charts ---------- */
  function hBars(target, rows, opts){
    opts = opts || {};
    var w = 900, rowH = 34, pad = 8, lw = opts.labelWidth || 150;
    var h = rows.length*rowH + pad*2;
    var max = opts.max || Math.max.apply(null, rows.map(function(r){ return r.v; })) * 1.12;
    var s = '<svg viewBox="0 0 '+w+' '+h+'" role="img" aria-label="'+esc(opts.aria||'bar chart')+'">';
    rows.forEach(function(r, i){
      var y = pad + i*rowH, bh = 17;
      var bw = Math.max(2, (r.v/max) * (w - lw - 80));
      s += '<text x="0" y="'+(y+bh-3)+'" font-size="13" fill="#c6cede">'+esc(r.label)+'</text>';
      s += '<rect x="'+lw+'" y="'+y+'" width="'+(w-lw-80)+'" height="'+bh+'" rx="4" fill="#1a1f2b"/>';
      s += '<rect x="'+lw+'" y="'+y+'" width="'+bw.toFixed(1)+'" height="'+bh+'" rx="4" fill="'+(r.color||'#22d3ee')+'"/>';
      s += '<text x="'+(lw+bw+10)+'" y="'+(y+bh-3)+'" font-size="13" font-weight="600" fill="#eef2f8">'+esc(r.text)+'</text>';
    });
    s += '</svg>';
    el(target).innerHTML = s;
  }

  function skillBars(target, key, aria, digits){
    hBars(target, [
      {label:'LightGBM (machine learning)', v:S.lgbm[key],  text:pct(S.lgbm[key], digits),  color:'#22d3ee'},
      {label:'Ridge (simple model)',        v:S.ridge[key], text:pct(S.ridge[key], digits), color:'#f472b6'},
      {label:'Momentum (buy last year’s winners)', v:S.mom[key], text:pct(S.mom[key], digits), color:'#f59e0b'},
      {label:'Random picking',              v:S.random[key], text:pct(S.random[key], digits), color:'#4b5566'}
    ], {labelWidth:290, aria:aria});
  }
  skillBars('precChart', 'precision', 'Share of top-10 picks that become big winners', 0);
  skillBars('crashChart', 'crash', 'Share of top-10 picks that crash', 0);
  skillBars('acqChart', 'acquired', 'Share of top-10 picks that get bought out', 1);
  skillBars('capChart', 'winner_capture', 'Share of the year’s biggest winners held', 1);

  var vsRandom = function(a, b, more, fewer){ return a > b ? more : fewer; };
  var T = D.top10_cagr, B = D.buyouts;
  el('skillLead').textContent =
    'LightGBM and plain momentum find more big winners than random picking (' + pct(S.lgbm.precision,0) +
    ' and ' + pct(S.mom.precision,0) + ' vs ' + pct(S.random.precision,0) + '), but they also pick far ' +
    'more stocks that crash (' + pct(S.lgbm.crash,0) + ' and ' + pct(S.mom.crash,0) + ' vs ' +
    pct(S.random.crash,0) + '). Their top-10 portfolios made ' + sgn(T.lgbm) + ' and ' + sgn(T.mom) +
    ' a year. Ridge crashes ' +
    vsRandom(S.ridge.crash, S.random.crash, 'a bit more often than random', 'less often than random') +
    ' (' + pct(S.ridge.crash,0) + ' vs ' + pct(S.random.crash,0) + ') and finds ' +
    vsRandom(S.ridge.precision, S.random.precision, 'more', 'fewer') + ' big winners than random (' +
    pct(S.ridge.precision,0) + ' vs ' + pct(S.random.precision,0) + '). And ' + pct(S.ridge.acquired,0) +
    ' of its favorite stocks get bought ' +
    'out within 6 months (' + pct(S.random.acquired,1) + ' for a random stock). A company with a deal ' +
    'pending barely moves (typical volatility ' + pct(B.bought.vol,0) + ' vs ' + pct(B.other.vol,0) +
    ' for its other picks), and Ridge likes calm stocks. Those picks ' +
    vsRandom(B.bought.crash, B.other.crash, 'crash more', 'crash less') + ' (' + pct(B.bought.crash,0) +
    ' vs ' + pct(B.other.crash,0) + '), but on average they return ' + sgn(B.bought.excess) +
    ' vs the S&P 500 over the next year: a safe place to wait, not a way to find big winners.';
  el('skillNote').textContent =
    'All four tests use each month’s top 10 picks, ' + span + '. "Random picking" is what choosing ' +
    'stocks at random would score on average. Buyouts are checked with later deal dates, so they are ' +
    'only a diagnostic, never an input to the model.';

  /* ---------- sectors ---------- */
  var secMax = D.sectors[0].share;
  hBars('sectorChart', D.sectors.map(function(r){
    return {
      label: r.sector,
      v: r.share,
      text: pct(r.share,0),
      color: r.sector.indexOf('Tech') === 0 ? '#22d3ee' : '#3f7f8f'
    };
  }), {max: secMax*1.15, labelWidth: 190, aria: 'Average share of picks by sector'});

  var top = D.sectors[0], second = D.sectors[1];
  var tech = D.sectors.filter(function(r){ return r.sector.indexOf('Tech') === 0; })[0];
  el('sectorLead').textContent =
    'For the best version so far (Ridge, top 10%), ' + top.sector + ' is the biggest slice at ' +
    pct(top.share,0) + ' of picks, then ' + second.sector + ' at ' + pct(second.share,0) + '.' +
    (tech ? ' Technology is only ' + pct(tech.share,0) + '. On price data alone, Ridge favors calm, ' +
            'low-volatility stocks.' : '');

  el('footNote').textContent =
    'Pinky is a personal experiment. Apart from the old ' + O.n_stocks + '-stock test, all figures come ' +
    'from walk-forward out-of-sample predictions, ' + monthYear(M.start) + '–' + monthYear(M.end) + ', ' +
    M.months + ' monthly periods; model portfolios are net of ' + M.cost_bps + ' bps per side. ' +
    'Universe: US stocks above $' + M.min_price + ' trading at least $' + (M.min_dollar_volume/1e6) +
    'M a day, as they existed at the time, including delisted companies. Stocks need a year of price ' +
    'history before they are scored. Data from ' + M.holdout_start.slice(0,4) + ' onward is locked for ' +
    'one final test; the current models never used it. ' +
    'No live money has ever been traded. Page generated ' + M.generated + ' from run ' + M.run + '.';
})();
</script>
</body>
</html>
"""


def main() -> Path:
    data = build_data()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, separators=(",", ":"))
    html = HTML_TEMPLATE.replace("__DATA__", payload)
    out = OUT_DIR / "index.html"
    out.write_text(html, encoding="utf-8")

    print(f"[showcase] wrote {out} ({out.stat().st_size / 1024:.0f} KB)")
    for c in data["curves"]:
        print(
            f"  {c['label']:<26} CAGR {c['cagr']:+.2%} | pre {c['cagr_pre']:+.2%} "
            f"post {c['cagr_post']:+.2%} | maxDD {c['max_dd']:.1%} | ${c['final']:,.0f}"
        )
    o = data["old"]
    print(f"  old 128-stock LightGBM {o['cagr']:+.2%} | ex5 {o['cagr_ex5']:+.2%} | SPY {o['cagr_spy']:+.2%}")
    for name, m in data["skill"].items():
        print(
            f"  {name:<6} precision {m['precision']:.3f} crash {m['crash']:.3f} "
            f"acquired {m['acquired']:.3f} winner capture {m['winner_capture']:.3f}"
        )
    t = data["top10_cagr"]
    print(f"  top-10 + buffer CAGR: LightGBM {t['lgbm']:+.2%} | momentum {t['mom']:+.2%}")
    for part, m in data["buyouts"].items():
        print(
            f"  Ridge top-10 {part:<7} n {m['n']} vol {m['vol']:.3f} crash {m['crash']:.3f} "
            f"mean excess {m['excess']:+.4f}"
        )
    tops = ", ".join("{} {:.0%}".format(r["sector"], r["share"]) for r in data["sectors"][:3])
    print("  top sectors: " + tops)
    return out


if __name__ == "__main__":
    main()
