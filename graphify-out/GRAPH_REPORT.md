# Graph Report - Pinky  (2026-09-25)

## Corpus Check
- 24 files · ~9,984 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .mdc 4)

## Summary
- 257 nodes · 457 edges · 12 communities (11 shown, 1 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e8f21241`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky Architecture Plan
- data_pull.py
- dataset.py
- Pinky
- __init__.py
- Pinky PRD (Product Requirements Document)
- features.py
- build_labels_for_ticker
- preprocess.py
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
10. `run_backtest()` - 9 edges

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

### Community 1 - "data_pull.py"
Cohesion: 0.13
Nodes (21): pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe(), DataFrame (+13 more)

### Community 2 - "dataset.py"
Cohesion: 0.11
Nodes (29): dataclasses, build_train_dataset(), feature_columns(), label_columns(), load_dataset(), DataFrame, Path, Train-ready dataset: join features (X) + labels (y) on Date + Ticker. (+21 more)

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

### Community 8 - "preprocess.py"
Cohesion: 0.29
Nodes (10): cross_section_zscore(), drop_correlated_features(), prepare_fold_frames(), DataFrame, ranking_feature_cols(), Feature prep for ranking models. 1) Cross-sectional z-score by Date (grade…, For each Date, z-score selected columns across tickers. Constant-within-day…, Greedy drop: among highly correlated pairs on TRAIN only, keep the first. (+2 more)

### Community 9 - "train.py"
Cohesion: 0.09
Nodes (36): joblib, lightgbm, ndarray, numpy, brier_score(), calibration_table(), daily_rank_ic(), DataFrame (+28 more)

### Community 10 - "backtest.py"
Cohesion: 0.13
Nodes (31): math, _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores(), monthly_rebalance_dates(), _next_day() (+23 more)

### Community 11 - "v3 — bigger balanced universe + trading-cost backtest (2026-09-25)"
Cohesion: 0.15
Nodes (12): Honest read, Honest read, Next levers, Portfolio backtest CAGR (Jan 2018 → Oct 2025, net of 10 bps; SPY +14.1%), Portfolio backtest (Jan 2018 → Oct 2025, net of 10 bps), Ranking metrics (1y, 8 folds), Ranking metrics (1y, 8 folds), v2 prep (2026-09-23, 58 stocks) (+4 more)

## Knowledge Gaps
- **58 isolated node(s):** `What it does`, `How it works (high level)`, `What’s public vs private`, `Current status`, `Quick start (local)` (+53 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 134 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_bfm_prediction_features()` connect `features.py` to `Pinky Architecture Plan`, `Pinky`?**
  _High betweenness centrality (0.375) - this node is a cross-community bridge._
- **Why does `Feature pipeline` connect `Pinky Architecture Plan` to `features.py`?**
  _High betweenness centrality (0.297) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `build_bfm_prediction_features()` (e.g. with `Feature pipeline` and `Repo layout`) actually correct?**
  _`build_bfm_prediction_features()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `What it does`, `How it works (high level)`, `What’s public vs private` to the rest of the system?**
  _58 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky Architecture Plan` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `data_pull.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12615384615384614 - nodes in this community are weakly interconnected._
- **Should `dataset.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10606060606060606 - nodes in this community are weakly interconnected._