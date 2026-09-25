# Graph Report - Pinky  (2026-09-25)

## Corpus Check
- 24 files · ~10,922 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: .mdc 5, (none) 5, .csv 3)

## Summary
- 268 nodes · 478 edges · 11 communities (10 shown, 1 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b3e18078`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky Architecture Plan
- dataset.py
- Pinky
- __init__.py
- Pinky PRD (Product Requirements Document)
- features.py
- build_labels_for_ticker
- preprocess.py
- train.py
- backtest.py
- Walk-Forward Results

## God Nodes (most connected - your core abstractions)
1. `Pinky PRD (Product Requirements Document)` - 14 edges
2. `build_bfm_prediction_features()` - 13 edges
3. `load_raw_ticker()` - 13 edges
4. `adj_close_series()` - 12 edges
5. `run_horizon()` - 11 edges
6. `_backtest_lines()` - 11 edges
7. `Pinky Architecture Plan` - 11 edges
8. `iter_walk_forward_folds()` - 10 edges
9. `Pinky` - 10 edges
10. `run_backtest()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Feature pipeline` --references--> `build_bfm_prediction_features()`  [INFERRED]
  docs/ARCHITECTURE.md → pinky/features.py
- `Repo layout` --references--> `build_bfm_prediction_features()`  [INFERRED]
  project.md → pinky/features.py
- `Status` --references--> `add_top_decile_labels()`  [INFERRED]
  project.md → pinky/labels.py
- `Status` --references--> `precision_at_k()`  [INFERRED]
  project.md → pinky/metrics.py
- `Status` --references--> `winner_capture()`  [INFERRED]
  project.md → pinky/metrics.py

## Import Cycles
- None detected.

## Communities (11 total, 1 thin omitted)

### Community 0 - "Pinky Architecture Plan"
Cohesion: 0.06
Nodes (28): Build order, Explicit non-goals (for now), Feature pipeline, Goal, Labels (truth the model learns), Locked decisions, Models, Pinky Architecture Plan (+20 more)

### Community 1 - "dataset.py"
Cohesion: 0.07
Nodes (41): dataclasses, pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe() (+33 more)

### Community 3 - "Pinky"
Cohesion: 0.12
Nodes (18): _monthly_dates(), precision_at_k(), DataFrame, DatetimeIndex, First available date of each month (limits overlap from year-long labels)., Share of the model's top-k picks that end up in the future top decile. Sampled…, Time-weighted capture of big winners. For each calendar year, take the…, winner_capture() (+10 more)

### Community 5 - "Pinky PRD (Product Requirements Document)"
Cohesion: 0.10
Nodes (20): 10. Milestones, 11. Risks, 12. Open decisions, 13. Related docs, 1. Problem, 2. Product goal, 3. Who it’s for, 4. What success looks like (+12 more)

### Community 6 - "features.py"
Cohesion: 0.15
Nodes (23): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+15 more)

### Community 7 - "build_labels_for_ticker"
Cohesion: 0.18
Nodes (14): add_top_decile_labels(), build_labels_for_ticker(), build_universe_labels(), _forward_return(), DataFrame, Path, Series, Add `top_{h}` = 1 if the stock's forward excess is in the top `frac` of stocks… (+6 more)

### Community 8 - "preprocess.py"
Cohesion: 0.15
Nodes (19): build_train_dataset(), feature_columns(), DataFrame, Path, Numeric model inputs only (no ids, no labels)., Inner-join features and labels on Date + Ticker. Does not invent rows. Rows…, Write train-ready panel to parquet., save_dataset() (+11 more)

### Community 9 - "train.py"
Cohesion: 0.09
Nodes (33): joblib, lightgbm, ndarray, numpy, brier_score(), calibration_table(), Evaluation metrics for walk-forward reports (honest, no fake scores)., Reliability-style bins: predicted prob vs realized frequency. (+25 more)

### Community 10 - "backtest.py"
Cohesion: 0.12
Nodes (33): math, _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores(), monthly_rebalance_dates(), _next_day() (+25 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.13
Nodes (14): Honest read, Honest read, Honest read, Next levers, Portfolio backtest CAGR (Jan 2018 → Oct 2025, net of 10 bps; SPY +14.1%), Portfolio backtest (Jan 2018 → Oct 2025, net of 10 bps), Ranking metrics (1y, 8 folds), Ranking metrics (1y, 8 folds) (+6 more)

## Knowledge Gaps
- **58 isolated node(s):** `What it does`, `How it works (high level)`, `What’s public vs private`, `Current status`, `Quick start (local)` (+53 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 139 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_bfm_prediction_features()` connect `features.py` to `Pinky Architecture Plan`, `Pinky`?**
  _High betweenness centrality (0.325) - this node is a cross-community bridge._
- **Why does `Feature pipeline` connect `Pinky Architecture Plan` to `features.py`?**
  _High betweenness centrality (0.286) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `build_bfm_prediction_features()` (e.g. with `Feature pipeline` and `Repo layout`) actually correct?**
  _`build_bfm_prediction_features()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `What it does`, `How it works (high level)`, `What’s public vs private` to the rest of the system?**
  _58 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky Architecture Plan` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `dataset.py` be split into smaller, more focused modules?**
  _Cohesion score 0.070578231292517 - nodes in this community are weakly interconnected._
- **Should `Pinky` be split into smaller, more focused modules?**
  _Cohesion score 0.12280701754385964 - nodes in this community are weakly interconnected._