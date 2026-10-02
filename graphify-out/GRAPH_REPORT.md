# Graph Report - Pinky  (2026-10-02)

## Corpus Check
- 31 files · ~36,138 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: (none) 7, .mdc 5, .csv 3)

## Summary
- 399 nodes · 786 edges · 14 communities (12 shown, 2 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bfd11b03`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky PRD (Product Requirements Document)
- preprocess.py
- sharadar.py
- Pinky
- __init__.py
- universe.py
- features.py
- Pinky Architecture Plan
- walkforward.py
- config.py
- build_showcase.py
- Walk-Forward Results
- train.py
- AGENTS.md

## God Nodes (most connected - your core abstractions)
1. `run_all()` - 17 edges
2. `_backtest_lines()` - 14 edges
3. `build_data()` - 14 edges
4. `Pinky PRD (Product Requirements Document)` - 14 edges
5. `load_raw_ticker()` - 13 edges
6. `run_backtest()` - 12 edges
7. `build_bfm_prediction_features()` - 12 edges
8. `adj_close_series()` - 12 edges
9. `run_horizon()` - 12 edges
10. `_write_summary()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Backtest defaults` --references--> `with_cost()`  [INFERRED]
  project.md → pinky/backtest.py
- `Feature pipeline` --references--> `build_bfm_prediction_features()`  [INFERRED]
  docs/ARCHITECTURE.md → pinky/features.py
- `▶ Resume here (new chat: read this first)` --references--> `cross_section_rank()`  [INFERRED]
  project.md → pinky/preprocess.py
- `Gotchas (learned the hard way)` --references--> `iter_walk_forward_folds()`  [INFERRED]
  project.md → pinky/walkforward.py
- `Decisions` --references--> `dev_rows()`  [INFERRED]
  project.md → pinky/train.py

## Import Cycles
- None detected.

## Communities (14 total, 2 thin omitted)

### Community 0 - "Pinky PRD (Product Requirements Document)"
Cohesion: 0.10
Nodes (20): 10. Milestones, 11. Risks, 12. Open decisions, 13. Related docs, 1. Problem, 2. Product goal, 3. Who it’s for, 4. What success looks like (+12 more)

### Community 1 - "preprocess.py"
Cohesion: 0.14
Nodes (21): build_train_dataset(), feature_columns(), DataFrame, Path, Numeric model inputs only (no ids, no labels)., Inner-join features and labels on Date + Ticker. Does not invent rows. Rows…, Write train-ready panel to parquet., save_dataset() (+13 more)

### Community 2 - "sharadar.py"
Cohesion: 0.12
Nodes (22): io, os, api_key(), bulk_status(), download_bulk(), pull_all(), DataFrame, Path (+14 more)

### Community 3 - "Pinky"
Cohesion: 0.11
Nodes (18): dev_rows(), DatetimeIndex, Rows whose label window ends before HOLDOUT_START, so the holdout stays unseen., Backtest defaults, Commands, Decisions, Four model fixes — v7_pit + ablations (2026-09-27), Gotchas (learned the hard way) (+10 more)

### Community 5 - "universe.py"
Cohesion: 0.09
Nodes (38): Index, numpy, build_pit_dataset(), load_pit_dataset(), _log_market_cap(), DataFrame, DatetimeIndex, Path (+30 more)

### Community 6 - "features.py"
Cohesion: 0.09
Nodes (38): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+30 more)

### Community 7 - "Pinky Architecture Plan"
Cohesion: 0.06
Nodes (28): Build order, Explicit non-goals (for now), Feature pipeline, Goal, Labels (truth the model learns), Locked decisions, Models, Pinky Architecture Plan (+20 more)

### Community 8 - "walkforward.py"
Cohesion: 0.25
Nodes (14): dataclasses, iter_walk_forward_folds(), purge_train(), DataFrame, DatetimeIndex, Timestamp, Walk-forward folds + label-window purge. - Expanding train window, fixed-length…, Small table describing folds (no model training). (+6 more)

### Community 9 - "config.py"
Cohesion: 0.10
Nodes (26): pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe(), DataFrame (+18 more)

### Community 10 - "build_showcase.py"
Cohesion: 0.07
Nodes (56): math, between_years(), _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores(), monthly_rebalance_dates() (+48 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.09
Nodes (22): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read, Next levers (+14 more)

### Community 12 - "train.py"
Cohesion: 0.06
Nodes (59): joblib, json, lightgbm, ndarray, acquired_share(), brier_score(), calibration_table(), _monthly_dates() (+51 more)

## Knowledge Gaps
- **65 isolated node(s):** `Agent instructions (Pinky)`, `What it does`, `How it works (high level)`, `What’s public vs private`, `Current status` (+60 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 195 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_bfm_prediction_features()` connect `features.py` to `Pinky Architecture Plan`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Why does `Feature pipeline` connect `Pinky Architecture Plan` to `features.py`?**
  _High betweenness centrality (0.207) - this node is a cross-community bridge._
- **What connects `Agent instructions (Pinky)`, `What it does`, `How it works (high level)` to the rest of the system?**
  _65 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky PRD (Product Requirements Document)` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `preprocess.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1383399209486166 - nodes in this community are weakly interconnected._
- **Should `sharadar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11956521739130435 - nodes in this community are weakly interconnected._
- **Should `Pinky` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._