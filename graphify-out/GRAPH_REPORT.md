# Graph Report - Pinky  (2026-09-25)

## Corpus Check
- 24 files · ~9,081 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .mdc 4)

## Summary
- 249 nodes · 447 edges · 12 communities (11 shown, 1 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `19dfa505`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky Architecture Plan
- dataset.py
- preprocess.py
- Pinky
- __init__.py
- Pinky PRD (Product Requirements Document)
- features.py
- build_labels_for_ticker
- walkforward.py
- train.py
- backtest.py
- v3 — bigger balanced universe + trading-cost backtest (2026-09-25)

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
10. `feature_columns()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Feature pipeline` --references--> `build_bfm_prediction_features()`  [INFERRED]
  docs/ARCHITECTURE.md → pinky/features.py
- `Repo layout` --references--> `build_bfm_prediction_features()`  [INFERRED]
  project.md → pinky/features.py
- `_eval_prepared()` --uses--> `WalkForwardFold`  [INFERRED]
  pinky/train.py → pinky/walkforward.py
- `load_price_panel()` --calls--> `adj_close_series()`  [EXTRACTED]
  pinky/backtest.py → pinky/raw_io.py
- `load_price_panel()` --calls--> `load_raw_ticker()`  [EXTRACTED]
  pinky/backtest.py → pinky/raw_io.py

## Import Cycles
- None detected.

## Communities (12 total, 1 thin omitted)

### Community 0 - "Pinky Architecture Plan"
Cohesion: 0.06
Nodes (28): Build order, Explicit non-goals (for now), Feature pipeline, Goal, Labels (truth the model learns), Locked decisions, Models, Pinky Architecture Plan (+20 more)

### Community 1 - "dataset.py"
Cohesion: 0.11
Nodes (24): pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe(), DataFrame (+16 more)

### Community 2 - "preprocess.py"
Cohesion: 0.13
Nodes (21): build_train_dataset(), feature_columns(), load_dataset(), DataFrame, Path, Numeric model inputs only (no ids, no labels)., Inner-join features and labels on Date + Ticker. Does not invent rows. Rows…, Write train-ready panel to parquet. (+13 more)

### Community 3 - "Pinky"
Cohesion: 0.18
Nodes (10): Build order, Current universe, Pinky, Planned stack (v1), Portfolio backtest defaults, Repo layout, Rules (always on), Status (+2 more)

### Community 5 - "Pinky PRD (Product Requirements Document)"
Cohesion: 0.10
Nodes (20): 10. Milestones, 11. Risks, 12. Open decisions, 13. Related docs, 1. Problem, 2. Product goal, 3. Who it’s for, 4. What success looks like (+12 more)

### Community 6 - "features.py"
Cohesion: 0.15
Nodes (23): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+15 more)

### Community 7 - "build_labels_for_ticker"
Cohesion: 0.22
Nodes (12): build_labels_for_ticker(), build_universe_labels(), _forward_return(), DataFrame, Path, Series, Write stacked label panel to parquet., Return from t to t+horizon_days. NaN near the end where future is unknown. (+4 more)

### Community 8 - "walkforward.py"
Cohesion: 0.21
Nodes (15): dataclasses, iter_walk_forward_folds(), purge_train(), DataFrame, DatetimeIndex, Timestamp, Walk-forward folds + label-window purge. - Expanding train window, fixed-length…, Small table describing folds (no model training). (+7 more)

### Community 9 - "train.py"
Cohesion: 0.09
Nodes (34): joblib, lightgbm, ndarray, numpy, brier_score(), calibration_table(), DataFrame, Evaluation metrics for walk-forward reports (honest, no fake scores). (+26 more)

### Community 10 - "backtest.py"
Cohesion: 0.13
Nodes (30): _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores(), monthly_rebalance_dates(), _next_day(), _period_end() (+22 more)

### Community 11 - "v3 — bigger balanced universe + trading-cost backtest (2026-09-25)"
Cohesion: 0.25
Nodes (7): Honest read, Next levers, Portfolio backtest (Jan 2018 → Oct 2025, net of 10 bps), Ranking metrics (1y, 8 folds), v2 prep (2026-09-23, 58 stocks), v3 — bigger balanced universe + trading-cost backtest (2026-09-25), Walk-Forward Results

## Knowledge Gaps
- **54 isolated node(s):** `What it does`, `How it works (high level)`, `What’s public vs private`, `Current status`, `Quick start (local)` (+49 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 128 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_bfm_prediction_features()` connect `features.py` to `Pinky Architecture Plan`, `Pinky`?**
  _High betweenness centrality (0.393) - this node is a cross-community bridge._
- **Why does `Feature pipeline` connect `Pinky Architecture Plan` to `features.py`?**
  _High betweenness centrality (0.311) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `build_bfm_prediction_features()` (e.g. with `Feature pipeline` and `Repo layout`) actually correct?**
  _`build_bfm_prediction_features()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `What it does`, `How it works (high level)`, `What’s public vs private` to the rest of the system?**
  _54 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky Architecture Plan` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `dataset.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10804597701149425 - nodes in this community are weakly interconnected._
- **Should `preprocess.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13438735177865613 - nodes in this community are weakly interconnected._