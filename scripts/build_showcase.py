"""
Build a self-contained one-page showcase for Pinky.

Reads the real walk-forward predictions in `artifacts/`, re-runs the portfolio
backtests, and writes `showcase/index.html` with every number embedded as JSON.
No training, no network, no CDNs: the page renders offline with inline SVG.

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
    default_prices,
    momentum_scores,
    pick_sector_share,
    run_backtest,
    summarize_backtest,
)
from pinky.config import (
    BACKTEST_COST_BPS,
    BACKTEST_MAX_SECTOR_SHARE,
    BACKTEST_TOP_N,
    HINDSIGHT_WINNERS,
    PROJECT_ROOT,
)
from pinky.labels import add_top_decile_labels
from pinky.metrics import precision_at_k, winner_capture

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
OUT_DIR = PROJECT_ROOT / "showcase"
START_CAPITAL = 10_000.0
RANDOM_SEEDS = 20


def equity_curve(bt: pd.DataFrame, col: str) -> list[dict]:
    """Growth of $10k, one point per holding period (plus the starting point)."""
    pts = [{"t": bt["start"].iloc[0].date().isoformat(), "v": START_CAPITAL}]
    value = START_CAPITAL
    for _, row in bt.iterrows():
        value *= 1.0 + float(row[col])
        pts.append({"t": row["end"].date().isoformat(), "v": round(value, 2)})
    return pts


def ranking_metrics(preds: pd.DataFrame) -> dict:
    """precision@10 and winner capture for LightGBM, Ridge and random picking."""
    df = add_top_decile_labels(preds.copy(), ["1y"])

    out = {}
    for name, col in [("lgbm", "pred_excess_lgbm"), ("ridge", "pred_excess_ridge")]:
        out[name] = {
            "precision_at_10": precision_at_k(df, col, "top_1y", k=BACKTEST_TOP_N),
            "winner_capture": winner_capture(df, col, "excess_1y", k=BACKTEST_TOP_N),
        }

    prec, cap = [], []
    for seed in range(RANDOM_SEEDS):
        df["_rand"] = np.random.default_rng(seed).random(len(df))
        prec.append(precision_at_k(df, "_rand", "top_1y", k=BACKTEST_TOP_N))
        cap.append(winner_capture(df, "_rand", "excess_1y", k=BACKTEST_TOP_N))
    out["random"] = {
        "precision_at_10": float(np.mean(prec)),
        "winner_capture": float(np.mean(cap)),
        "seeds": RANDOM_SEEDS,
    }
    return out


def build_data() -> dict:
    preds = pd.read_parquet(ARTIFACTS_DIR / "oos_preds_1y_v4.parquet")
    preds_ex5 = pd.read_parquet(ARTIFACTS_DIR / "oos_preds_1y_v4_ex5.parquet")

    prices = default_prices()
    prices_ex5 = prices.drop(columns=[t for t in HINDSIGHT_WINNERS if t in prices.columns])

    cap = BACKTEST_MAX_SECTOR_SHARE
    bt_lgbm = run_backtest(preds, "pred_excess_lgbm", prices, max_sector_share=cap)
    bt_lgbm_ex5 = run_backtest(preds_ex5, "pred_excess_lgbm", prices_ex5, max_sector_share=cap)
    bt_ridge_ex5 = run_backtest(preds_ex5, "pred_excess_ridge", prices_ex5)
    mom_ex5 = momentum_scores(preds_ex5, prices_ex5)
    bt_mom_ex5 = run_backtest(mom_ex5, "mom_12_1", prices_ex5)

    s_lgbm = summarize_backtest(bt_lgbm)
    s_lgbm_ex5 = summarize_backtest(bt_lgbm_ex5)
    s_ridge_ex5 = summarize_backtest(bt_ridge_ex5)
    s_mom_ex5 = summarize_backtest(bt_mom_ex5)

    # The four curves must share a period grid to be plotted on one axis.
    for other in (bt_lgbm_ex5, bt_mom_ex5):
        assert list(bt_lgbm["end"]) == list(other["end"]), "backtest period grids differ"

    curves = [
        {
            "key": "spy",
            "label": "SPY (S&P 500)",
            "color": "#94a3b8",
            "points": equity_curve(bt_lgbm, "spy"),
            "cagr": s_lgbm["cagr_spy"],
            "max_dd": s_lgbm["max_dd_spy"],
            "note": "Just buying the index.",
        },
        {
            "key": "lgbm",
            "label": "Pinky · 128 stocks",
            "color": "#22d3ee",
            "points": equity_curve(bt_lgbm, "net"),
            "cagr": s_lgbm["cagr_net"],
            "max_dd": s_lgbm["max_dd_net"],
            "note": "Looks great. Inflated by hindsight — see below.",
        },
        {
            "key": "lgbm_ex5",
            "label": "Pinky · 5 winners removed",
            "color": "#a78bfa",
            "points": equity_curve(bt_lgbm_ex5, "net"),
            "cagr": s_lgbm_ex5["cagr_net"],
            "max_dd": s_lgbm_ex5["max_dd_net"],
            "note": "The honest version. Retrained without NVDA, SMCI, TSLA, PLTR, AVGO.",
        },
        {
            "key": "mom_ex5",
            "label": "Naive momentum · 5 winners removed",
            "color": "#f59e0b",
            "points": equity_curve(bt_mom_ex5, "net"),
            "cagr": s_mom_ex5["cagr_net"],
            "max_dd": s_mom_ex5["max_dd_net"],
            "note": "No machine learning: just buy what went up last year.",
        },
    ]
    for c in curves:
        c["final"] = c["points"][-1]["v"]

    sectors = pick_sector_share(bt_lgbm)
    sector_rows = [{"sector": s, "share": float(v)} for s, v in sectors.items()]

    return {
        "meta": {
            "generated": pd.Timestamp.today().date().isoformat(),
            "start": s_lgbm["start"],
            "end": s_lgbm["end"],
            "months": s_lgbm["months"],
            "n_stocks": int(preds["Ticker"].nunique()),
            "n_stocks_ex5": int(preds_ex5["Ticker"].nunique()),
            "top_n": BACKTEST_TOP_N,
            "cost_bps": BACKTEST_COST_BPS,
            "sector_cap": cap,
            "start_capital": START_CAPITAL,
            "hindsight_winners": list(HINDSIGHT_WINNERS),
        },
        "curves": curves,
        "extras": {
            "universe_ew_128": s_lgbm["cagr_universe_ew"],
            "universe_ew_123": s_lgbm_ex5["cagr_universe_ew"],
            "ridge_ex5_uncapped": s_ridge_ex5["cagr_net"],
            "months_beat_spy": s_lgbm_ex5["months_beat_spy"],
            "turnover": s_lgbm_ex5["avg_monthly_turnover"],
            "cost_drag": s_lgbm_ex5["annual_cost_drag"],
        },
        "sectors": sector_rows,
        "metrics": {
            "full": ranking_metrics(preds),
            "ex5": ranking_metrics(preds_ex5),
        },
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
  .vs{display:grid; grid-template-columns:1fr auto 1fr; gap:14px; align-items:center; margin:20px 0 6px; max-width:520px}
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
      It is a machine-learning model that reads years of price history and, once a month, ranks
      every stock it follows. It buys the top 10 and holds them until the next month.
      It leans toward tech and tries to spot big winners early — but it still buys energy,
      industrials and other sectors when they rank best.
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
      <div class="step"><span class="n">01</span><b>Price data</b><span class="d">Daily prices for the stocks we follow, plus the S&amp;P 500.</span></div>
      <div class="step"><span class="n">02</span><b>Features</b><span class="d">Turn raw prices into signals: trend, volatility, strength vs the market.</span></div>
      <div class="step"><span class="n">03</span><b>Walk-forward training</b><span class="d">Train on the past, test on the next unseen stretch. Repeat. Never peek ahead.</span></div>
      <div class="step"><span class="n">04</span><b>Ranking</b><span class="d">Each stock gets a score: how much it should beat the index over the next year.</span></div>
      <div class="step"><span class="n">05</span><b>Top-10 portfolio</b><span class="d">Buy the 10 best, equal amounts, max 60% from any one sector.</span></div>
      <div class="step"><span class="n">06</span><b>Costs &amp; scoring</b><span class="d">Charge trading costs, then compare honestly against the S&amp;P 500.</span></div>
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
        <thead><tr><th>Strategy</th><th>Growth per year</th><th>Worst drop</th><th>$10,000 became</th></tr></thead>
        <tbody id="statsRows"></tbody>
      </table>
    </div>
    <p class="note" id="statsNote"></p>

    <!-- REALITY CHECK -->
    <div class="reality">
      <h3>Reality check: the big number is not real</h3>
      <p>
        The list of stocks was chosen <em>today</em>, so it already contains companies we now know did
        brilliantly. Remove just five of them — <span id="winnerList"></span> — from both the training
        data and the test, and most of the advantage disappears.
      </p>
      <div class="vs">
        <div class="vsb">
          <div class="big" style="color:var(--cyan)" id="bigA"></div>
          <div class="cap">per year, with the five winners in the list</div>
        </div>
        <div class="arrow">→</div>
        <div class="vsb">
          <div class="big" style="color:var(--violet)" id="bigB"></div>
          <div class="cap">per year, with them removed</div>
        </div>
      </div>
      <p class="note" id="realityNote"></p>
    </div>
  </section>

  <!-- SECTORS -->
  <section>
    <div class="eyebrow">What it buys</div>
    <h2>Tech-heavy, but not tech-only</h2>
    <p class="lead" id="sectorLead"></p>
    <div class="card" style="margin-top:22px"><div id="sectorChart"></div></div>
    <p class="note">Average share of the 10 monthly picks, by sector. The 60% cap forces the model out of tech once it holds six tech names.</p>
  </section>

  <!-- BIG WINNERS -->
  <section>
    <div class="eyebrow">Is it actually skill?</div>
    <h2>Better than guessing — by a clear margin</h2>
    <p class="lead">Two simple tests, both on the full 128-stock list. Random picking is the bar to clear.</p>
    <div class="grid g2" style="margin-top:22px">
      <div class="card">
        <h3>Hit rate of the top 10</h3>
        <p class="note" style="margin:0 0 14px">How often a pick really lands in the best 10% of stocks for the year.</p>
        <div id="precChart"></div>
      </div>
      <div class="card">
        <h3>Holding the year's big winners</h3>
        <p class="note" style="margin:0 0 14px">Share of the year's 20 best stocks the model was actually holding, month by month.</p>
        <div id="capChart"></div>
      </div>
    </div>
    <p class="note" id="metricsNote"></p>
  </section>

  <!-- ROADMAP -->
  <section>
    <div class="eyebrow">What's next</div>
    <h2>Fix the data first, then get smarter</h2>
    <div class="grid g3" style="margin-top:22px">
      <div class="phase">
        <span class="tag t1">Phase 1 · in progress</span>
        <h3>Honest evaluation</h3>
        <ul>
          <li>Buy proper historical data (Sharadar), including <b>companies that went bust or got bought</b>.</li>
          <li>Widen from 128 hand-picked names to <b>~2,500–4,000 liquid US stocks</b>, as they existed at the time.</li>
          <li>Re-score today's model to get a baseline we can trust.</li>
        </ul>
      </div>
      <div class="phase">
        <span class="tag t2">Phase 2 · next</span>
        <h3>Look at the companies</h3>
        <ul>
          <li><b>Growth and revenue acceleration</b> — first, and most important.</li>
          <li>Margins, earnings reactions, R&amp;D spending and returns on capital.</li>
          <li>Quality and safety checks, plus insider buying.</li>
          <li>Added one batch at a time; anything that doesn't beat the baseline gets dropped.</li>
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
  var M = D.meta, X = D.extras;

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

  /* ---------- hero badges ---------- */
  var badges = [
    ['Stocks followed', M.n_stocks],
    ['Tested over', monthYear(M.start) + ' – ' + monthYear(M.end)],
    ['Rebalanced', 'Every month'],
    ['Held at a time', M.top_n + ' stocks'],
    ['Trading cost charged', M.cost_bps + ' bps per side'],
    ['Max per sector', Math.round(M.sector_cap*100) + '%']
  ];
  el('heroBadges').innerHTML = badges.map(function(b){
    return '<span class="badge">' + b[0] + ' <b>' + esc(b[1]) + '</b></span>';
  }).join('');

  var byKey = {};
  D.curves.forEach(function(c){ byKey[c.key] = c; });

  el('heroHonesty').textContent =
    'Up front: these are backtests on a list of ' + M.n_stocks + ' stocks picked today, so it is stuffed ' +
    'with companies we already know did well. The headline ' + sgn(byKey.lgbm.cagr,0) +
    '/yr falls to ' + sgn(byKey.lgbm_ex5.cagr,0) + '/yr once five of them are taken out. ' +
    'Nothing here has been traded with real money.';

  el('resultsLead').textContent =
    'Every strategy below starts with $' + M.start_capital.toLocaleString('en-US') + ' on ' +
    monthYear(M.start) + ', rebalances monthly, and pays ' + M.cost_bps +
    ' bps of trading cost on every trade. ' + M.months + ' months in total.';

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
    Object.keys(years).forEach(function(y){
      var x = xAt(years[y]);
      s += '<line x1="'+x+'" y1="'+PT+'" x2="'+x+'" y2="'+(H-PB)+'" stroke="#161b26" stroke-width="1"/>';
      s += '<text x="'+x+'" y="'+(H-PB+20)+'" text-anchor="middle" font-size="11" fill="#7b8598">'+y+'</text>';
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
           ' <b style="color:'+c.color+'">'+sgn(c.cagr,0)+'/yr</b></span>';
  }).join('');

  /* ---------- stats table ---------- */
  el('statsRows').innerHTML = D.curves.map(function(c){
    return '<tr><td><span class="tick" style="background:'+c.color+'"></span>'+esc(c.label)+
           '<span class="sub">'+esc(c.note)+'</span></td>'+
           '<td class="num" style="color:'+c.color+';font-weight:600">'+sgn(c.cagr)+'</td>'+
           '<td class="num">'+pct(c.max_dd)+'</td>'+
           '<td class="num">'+money(c.final)+'</td></tr>';
  }).join('');

  el('statsNote').textContent =
    '"Worst drop" is the deepest fall from a peak during the test. Every Pinky version fell harder than ' +
    'the S&P 500 (' + pct(byKey.spy.max_dd) + '), so the extra return came with extra pain. ' +
    'Simply owning all ' + M.n_stocks + ' stocks equally returned ' + sgn(X.universe_ew_128,0) + '/yr.';

  /* ---------- reality check ---------- */
  el('winnerList').textContent = M.hindsight_winners.join(', ');
  el('bigA').textContent = sgn(byKey.lgbm.cagr,0);
  el('bigB').textContent = sgn(byKey.lgbm_ex5.cagr,0);
  el('realityNote').innerHTML =
    'For scale: the S&P 500 did ' + sgn(byKey.spy.cagr,0) + '/yr, owning the remaining ' + M.n_stocks_ex5 +
    ' stocks equally did ' + sgn(X.universe_ew_123,0) + '/yr, and plain "buy last year\\'s winners" momentum did ' +
    sgn(byKey.mom_ex5.cagr,0) + '/yr. So the honest edge over a naive strategy is about ' +
    ((byKey.lgbm_ex5.cagr - byKey.mom_ex5.cagr)*100).toFixed(1) +
    ' points per year — small enough that it could be luck. A simple linear model (Ridge) actually scored higher (' +
    sgn(X.ridge_ex5_uncapped,0) + '/yr) on the same test, which is another sign the machine learning is not doing much yet.';

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

  var secMax = D.sectors[0].share;
  hBars('sectorChart', D.sectors.map(function(r){
    return {
      label: r.sector,
      v: r.share,
      text: pct(r.share,0),
      color: r.sector.indexOf('Tech') === 0 ? '#22d3ee' : '#3f7f8f'
    };
  }), {max: secMax*1.15, labelWidth: 150, aria: 'Average share of picks by sector'});

  var top = D.sectors[0], second = D.sectors[1];
  el('sectorLead').textContent =
    'On average ' + pct(top.share,0) + ' of the monthly picks are ' + top.sector +
    ' names, with ' + second.sector + ' the next biggest at ' + pct(second.share,0) +
    '. A hard 60% cap stops the portfolio from becoming one big tech bet.';

  var mf = D.metrics.full;
  hBars('precChart', [
    {label:'Pinky (LightGBM)', v:mf.lgbm.precision_at_10,  text:pct(mf.lgbm.precision_at_10,0),  color:'#22d3ee'},
    {label:'Simple model (Ridge)', v:mf.ridge.precision_at_10, text:pct(mf.ridge.precision_at_10,0), color:'#a78bfa'},
    {label:'Random picking', v:mf.random.precision_at_10, text:pct(mf.random.precision_at_10,0), color:'#4b5566'}
  ], {labelWidth:210, aria:'Hit rate of top 10 picks'});

  hBars('capChart', [
    {label:'Pinky (LightGBM)', v:mf.lgbm.winner_capture,  text:pct(mf.lgbm.winner_capture,0),  color:'#22d3ee'},
    {label:'Simple model (Ridge)', v:mf.ridge.winner_capture, text:pct(mf.ridge.winner_capture,0), color:'#a78bfa'},
    {label:'Random picking', v:mf.random.winner_capture, text:pct(mf.random.winner_capture,0), color:'#4b5566'}
  ], {labelWidth:210, aria:'Share of the year\\'s biggest winners held'});

  var me = D.metrics.ex5;
  el('metricsNote').textContent =
    'Random picking is the average of ' + mf.random.seeds + ' random-score runs. These two tests are the ' +
    'most encouraging thing here — but they run on the same survivorship-biased list. With the five known ' +
    'winners removed, the hit rate is ' + pct(me.lgbm.precision_at_10,0) + ' and winner capture ' +
    pct(me.lgbm.winner_capture,0) + '. Note the simple Ridge model does just as well, so the fancier ' +
    'machine learning is not adding much yet.';

  el('footNote').textContent =
    'Pinky is a personal experiment. All figures are computed from walk-forward out-of-sample predictions on ' +
    M.n_stocks + ' stocks, ' + monthYear(M.start) + '–' + monthYear(M.end) + ', ' + M.months +
    ' monthly periods, net of ' + M.cost_bps + ' bps per side. The stock list was chosen in ' +
    M.generated.slice(0,4) + ', so it is biased toward companies that survived and did well. ' +
    'No live money has ever been traded. Page generated ' + M.generated + '.';
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
        print(f"  {c['label']:<40} CAGR {c['cagr']:+.2%}  maxDD {c['max_dd']:.1%}  ${c['final']:,.0f}")
    tops = ", ".join("{} {:.0%}".format(r["sector"], r["share"]) for r in data["sectors"][:3])
    print("  top sectors: " + tops)
    m = data["metrics"]["full"]
    print(
        f"  precision@10 lgbm {m['lgbm']['precision_at_10']:.2f} "
        f"ridge {m['ridge']['precision_at_10']:.2f} random {m['random']['precision_at_10']:.2f}"
    )
    print(
        f"  winner capture lgbm {m['lgbm']['winner_capture']:.2f} "
        f"ridge {m['ridge']['winner_capture']:.2f} random {m['random']['winner_capture']:.2f}"
    )
    return out


if __name__ == "__main__":
    main()
