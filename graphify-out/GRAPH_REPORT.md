# Graph Report - Pinky  (2026-09-26)

## Corpus Check
- 30 files · ~20,769 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: .mdc 5, (none) 5, .csv 3)

## Summary
- 354 nodes · 666 edges · 13 communities (11 shown, 2 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `91789685`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky PRD (Product Requirements Document)
- dataset.py
- adj_close_series
- Pinky
- __init__.py
- universe.py
- build_bfm_prediction_features
- Pinky
- train.py
- backtest.py
- Walk-Forward Results
- sharadar.py
- AGENTS.md

## God Nodes (most connected - your core abstractions)
1. `Pinky PRD (Product Requirements Document)` - 14 edges
2. `load_raw_ticker()` - 13 edges
3. `run_all()` - 13 edges
4. `build_bfm_prediction_features()` - 12 edges
5. `adj_close_series()` - 12 edges
6. `run_horizon()` - 12 edges
7. `Pinky` - 12 edges
8. `run_backtest()` - 11 edges
9. `_backtest_lines()` - 11 edges
10. `iter_walk_forward_folds()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Feature pipeline` --references--> `build_bfm_prediction_features()`  [INFERRED]
  docs/ARCHITECTURE.md → pinky/features.py
- `Decisions` --references--> `dev_rows()`  [INFERRED]
  project.md → pinky/train.py
- `Where we are (2026-09-26)` --references--> `main()`  [INFERRED]
  project.md → scripts/build_showcase.py
- `Roadmap` --references--> `add_top_decile_labels()`  [INFERRED]
  project.md → pinky/labels.py
- `Roadmap` --references--> `precision_at_k()`  [INFERRED]
  project.md → pinky/metrics.py

## Import Cycles
- None detected.

## Communities (13 total, 2 thin omitted)

### Community 0 - "Pinky PRD (Product Requirements Document)"
Cohesion: 0.10
Nodes (20): 10. Milestones, 11. Risks, 12. Open decisions, 13. Related docs, 1. Problem, 2. Product goal, 3. Who it’s for, 4. What success looks like (+12 more)

### Community 1 - "dataset.py"
Cohesion: 0.08
Nodes (39): dataclasses, build_train_dataset(), feature_columns(), label_columns(), load_dataset(), DataFrame, Path, Train-ready dataset: join features (X) + labels (y) on Date + Ticker. (+31 more)

### Community 2 - "adj_close_series"
Cohesion: 0.16
Nodes (16): build_labels_for_ticker(), build_universe_labels(), _forward_return(), DataFrame, Path, Series, Write stacked label panel to parquet., Return from t to t+horizon_days. NaN near the end where future is unknown. (+8 more)

### Community 3 - "Pinky"
Cohesion: 0.14
Nodes (13): Baseline metrics, Honest baseline — v5_pit (2026-09-26), Key findings so far, Old 128-stock results (inflated — kept for reference), Old (legacy) universe, Open items, Pinky, Portfolio backtest defaults (+5 more)

### Community 5 - "universe.py"
Cohesion: 0.06
Nodes (55): Index, numpy, pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker() (+47 more)

### Community 6 - "build_bfm_prediction_features"
Cohesion: 0.10
Nodes (26): Build order, Explicit non-goals (for now), Feature pipeline, Goal, Labels (truth the model learns), Locked decisions, Models, Pinky Architecture Plan (+18 more)

### Community 7 - "Pinky"
Cohesion: 0.10
Nodes (17): Basket vs SPY, Fail conditions (do not ship / do not trust), Honesty checks, Metrics to report, Must-pass rules, Pass bar (first useful prototype), Pinky Eval Checklist (v1), Probability calibration (beat model) (+9 more)

### Community 9 - "train.py"
Cohesion: 0.07
Nodes (54): joblib, lightgbm, ndarray, add_top_decile_labels(), Add `top_{h}` = 1 if the stock's forward excess is in the top `frac` of stocks…, brier_score(), calibration_table(), daily_rank_ic() (+46 more)

### Community 10 - "backtest.py"
Cohesion: 0.10
Nodes (40): json, math, _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores(), monthly_rebalance_dates() (+32 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.11
Nodes (18): Data checks done, Honest read, Honest read, Honest read, Honest read, Next levers, Portfolio backtest CAGR (Jan 2018 → Oct 2025, net of 10 bps; SPY +14.1%), Portfolio backtest (Jan 2018 → Oct 2025, net of 10 bps) (+10 more)

### Community 12 - "sharadar.py"
Cohesion: 0.12
Nodes (23): io, os, api_key(), bulk_status(), download_bulk(), load(), pull_all(), DataFrame (+15 more)

## Knowledge Gaps
- **65 isolated node(s):** `Agent instructions (Pinky)`, `What it does`, `How it works (high level)`, `What’s public vs private`, `Current status` (+60 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 178 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_bfm_prediction_features()` connect `build_bfm_prediction_features` to `adj_close_series`, `universe.py`?**
  _High betweenness centrality (0.243) - this node is a cross-community bridge._
- **Why does `Pinky Architecture Plan` connect `build_bfm_prediction_features` to `Pinky`?**
  _High betweenness centrality (0.232) - this node is a cross-community bridge._
- **What connects `Agent instructions (Pinky)`, `What it does`, `How it works (high level)` to the rest of the system?**
  _65 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky PRD (Product Requirements Document)` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `dataset.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08139534883720931 - nodes in this community are weakly interconnected._
- **Should `Pinky` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Should `universe.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05803571428571429 - nodes in this community are weakly interconnected._