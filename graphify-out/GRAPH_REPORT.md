# Graph Report - Pinky  (2026-09-27)

## Corpus Check
- 30 files · ~24,691 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: .mdc 5, (none) 5, .csv 3)

## Summary
- 378 nodes · 736 edges · 14 communities (12 shown, 2 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5be6e835`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky PRD (Product Requirements Document)
- preprocess.py
- sharadar.py
- Pinky
- __init__.py
- config.py
- features.py
- Pinky Architecture Plan
- walkforward.py
- build_showcase.py
- backtest.py
- Walk-Forward Results
- train.py
- AGENTS.md

## God Nodes (most connected - your core abstractions)
1. `run_all()` - 15 edges
2. `_backtest_lines()` - 14 edges
3. `build_data()` - 14 edges
4. `Pinky PRD (Product Requirements Document)` - 14 edges
5. `load_raw_ticker()` - 13 edges
6. `run_backtest()` - 12 edges
7. `build_bfm_prediction_features()` - 12 edges
8. `adj_close_series()` - 12 edges
9. `run_horizon()` - 12 edges
10. `iter_walk_forward_folds()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Backtest defaults` --references--> `with_cost()`  [INFERRED]
  project.md → pinky/backtest.py
- `Feature pipeline` --references--> `build_bfm_prediction_features()`  [INFERRED]
  docs/ARCHITECTURE.md → pinky/features.py
- `Decisions` --references--> `dev_rows()`  [INFERRED]
  project.md → pinky/train.py
- `Gotchas (learned the hard way)` --references--> `iter_walk_forward_folds()`  [INFERRED]
  project.md → pinky/walkforward.py
- `Repo layout` --references--> `dev_rows()`  [INFERRED]
  project.md → pinky/train.py

## Import Cycles
- None detected.

## Communities (14 total, 2 thin omitted)

### Community 0 - "Pinky PRD (Product Requirements Document)"
Cohesion: 0.10
Nodes (20): 10. Milestones, 11. Risks, 12. Open decisions, 13. Related docs, 1. Problem, 2. Product goal, 3. Who it’s for, 4. What success looks like (+12 more)

### Community 1 - "preprocess.py"
Cohesion: 0.15
Nodes (19): build_train_dataset(), feature_columns(), DataFrame, Path, Numeric model inputs only (no ids, no labels)., Inner-join features and labels on Date + Ticker. Does not invent rows. Rows…, Write train-ready panel to parquet., save_dataset() (+11 more)

### Community 2 - "sharadar.py"
Cohesion: 0.12
Nodes (22): io, os, api_key(), bulk_status(), download_bulk(), pull_all(), DataFrame, Path (+14 more)

### Community 3 - "Pinky"
Cohesion: 0.14
Nodes (13): Backtest defaults, Commands, Decisions, Gotchas (learned the hard way), Honest baseline — v5_pit (2026-09-26), Key findings, New yardstick — v6_pit (2026-09-26), Old 128-stock results (inflated by survivorship + hindsight) (+5 more)

### Community 5 - "config.py"
Cohesion: 0.08
Nodes (36): numpy, pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe() (+28 more)

### Community 6 - "features.py"
Cohesion: 0.09
Nodes (37): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+29 more)

### Community 7 - "Pinky Architecture Plan"
Cohesion: 0.06
Nodes (28): Build order, Explicit non-goals (for now), Feature pipeline, Goal, Labels (truth the model learns), Locked decisions, Models, Pinky Architecture Plan (+20 more)

### Community 8 - "walkforward.py"
Cohesion: 0.25
Nodes (14): dataclasses, iter_walk_forward_folds(), purge_train(), DataFrame, DatetimeIndex, Timestamp, Walk-forward folds + label-window purge. - Expanding train window, fixed-length…, Small table describing folds (no model training). (+6 more)

### Community 9 - "build_showcase.py"
Cohesion: 0.08
Nodes (42): json, ndarray, acquired_share(), brier_score(), _monthly_dates(), precision_at_k(), DataFrame, DatetimeIndex (+34 more)

### Community 10 - "backtest.py"
Cohesion: 0.11
Nodes (37): math, between_years(), _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores(), monthly_rebalance_dates() (+29 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.10
Nodes (20): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Next levers, Portfolio backtest CAGR (Jan 2018 → Oct 2025, net of 10 bps; SPY +14.1%) (+12 more)

### Community 12 - "train.py"
Cohesion: 0.06
Nodes (56): Index, joblib, lightgbm, calibration_table(), Reliability-style bins: predicted prob vs realized frequency., load_pit_dataset(), load(), dev_rows() (+48 more)

## Knowledge Gaps
- **64 isolated node(s):** `Agent instructions (Pinky)`, `What it does`, `How it works (high level)`, `What’s public vs private`, `Current status` (+59 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 186 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_bfm_prediction_features()` connect `features.py` to `Pinky Architecture Plan`?**
  _High betweenness centrality (0.229) - this node is a cross-community bridge._
- **Why does `Feature pipeline` connect `Pinky Architecture Plan` to `features.py`?**
  _High betweenness centrality (0.217) - this node is a cross-community bridge._
- **What connects `Agent instructions (Pinky)`, `What it does`, `How it works (high level)` to the rest of the system?**
  _64 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky PRD (Product Requirements Document)` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `preprocess.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14761904761904762 - nodes in this community are weakly interconnected._
- **Should `sharadar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11956521739130435 - nodes in this community are weakly interconnected._
- **Should `Pinky` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._