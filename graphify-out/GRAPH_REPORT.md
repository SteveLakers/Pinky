# Graph Report - Pinky  (2026-09-27)

## Corpus Check
- 30 files · ~22,248 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: .mdc 5, (none) 5, .csv 3)

## Summary
- 358 nodes · 673 edges · 14 communities (12 shown, 2 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2f307217`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky PRD (Product Requirements Document)
- preprocess.py
- build_labels_for_ticker
- Pinky
- __init__.py
- config.py
- features.py
- Pinky Architecture Plan
- walkforward.py
- train.py
- backtest.py
- Walk-Forward Results
- sharadar.py
- AGENTS.md

## God Nodes (most connected - your core abstractions)
1. `Pinky PRD (Product Requirements Document)` - 14 edges
2. `load_raw_ticker()` - 13 edges
3. `_backtest_lines()` - 13 edges
4. `run_all()` - 13 edges
5. `build_bfm_prediction_features()` - 12 edges
6. `adj_close_series()` - 12 edges
7. `run_horizon()` - 12 edges
8. `iter_walk_forward_folds()` - 12 edges
9. `run_backtest()` - 11 edges
10. `Pinky Architecture Plan` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Backtest defaults` --references--> `with_cost()`  [INFERRED]
  project.md → pinky/backtest.py
- `Feature pipeline` --references--> `build_bfm_prediction_features()`  [INFERRED]
  docs/ARCHITECTURE.md → pinky/features.py
- `Gotchas (learned the hard way)` --references--> `iter_walk_forward_folds()`  [INFERRED]
  project.md → pinky/walkforward.py
- `Decisions` --references--> `dev_rows()`  [INFERRED]
  project.md → pinky/train.py
- `Repo layout` --references--> `backtest_prices()`  [INFERRED]
  project.md → pinky/universe.py

## Import Cycles
- None detected.

## Communities (14 total, 2 thin omitted)

### Community 0 - "Pinky PRD (Product Requirements Document)"
Cohesion: 0.10
Nodes (20): 10. Milestones, 11. Risks, 12. Open decisions, 13. Related docs, 1. Problem, 2. Product goal, 3. Who it’s for, 4. What success looks like (+12 more)

### Community 1 - "preprocess.py"
Cohesion: 0.13
Nodes (21): build_train_dataset(), feature_columns(), load_dataset(), DataFrame, Path, Numeric model inputs only (no ids, no labels)., Inner-join features and labels on Date + Ticker. Does not invent rows. Rows…, Write train-ready panel to parquet. (+13 more)

### Community 2 - "build_labels_for_ticker"
Cohesion: 0.18
Nodes (14): add_top_decile_labels(), build_labels_for_ticker(), build_universe_labels(), _forward_return(), DataFrame, Path, Series, Add `top_{h}` = 1 if the stock's forward excess is in the top `frac` of stocks… (+6 more)

### Community 3 - "Pinky"
Cohesion: 0.12
Nodes (17): dev_rows(), DatetimeIndex, Rows whose label window ends before HOLDOUT_START, so the holdout stays unseen., Backtest defaults, Commands, Decisions, Gotchas (learned the hard way), Honest baseline — v5_pit (2026-09-26) (+9 more)

### Community 5 - "config.py"
Cohesion: 0.08
Nodes (34): numpy, pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe() (+26 more)

### Community 6 - "features.py"
Cohesion: 0.15
Nodes (23): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+15 more)

### Community 7 - "Pinky Architecture Plan"
Cohesion: 0.06
Nodes (28): Build order, Explicit non-goals (for now), Feature pipeline, Goal, Labels (truth the model learns), Locked decisions, Models, Pinky Architecture Plan (+20 more)

### Community 8 - "walkforward.py"
Cohesion: 0.21
Nodes (15): dataclasses, iter_walk_forward_folds(), purge_train(), DataFrame, DatetimeIndex, Timestamp, Walk-forward folds + label-window purge. - Expanding train window, fixed-length…, Small table describing folds (no model training). (+7 more)

### Community 9 - "train.py"
Cohesion: 0.09
Nodes (40): joblib, lightgbm, ndarray, brier_score(), calibration_table(), daily_rank_ic(), _monthly_dates(), precision_at_k() (+32 more)

### Community 10 - "backtest.py"
Cohesion: 0.09
Nodes (46): json, math, os, _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores() (+38 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.10
Nodes (20): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Next levers, Portfolio backtest CAGR (Jan 2018 → Oct 2025, net of 10 bps; SPY +14.1%) (+12 more)

### Community 12 - "sharadar.py"
Cohesion: 0.07
Nodes (47): Index, io, api_key(), bulk_status(), download_bulk(), load(), pull_all(), DataFrame (+39 more)

## Knowledge Gaps
- **64 isolated node(s):** `Agent instructions (Pinky)`, `What it does`, `How it works (high level)`, `What’s public vs private`, `Current status` (+59 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 179 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_bfm_prediction_features()` connect `features.py` to `Pinky Architecture Plan`?**
  _High betweenness centrality (0.239) - this node is a cross-community bridge._
- **Why does `Feature pipeline` connect `Pinky Architecture Plan` to `features.py`?**
  _High betweenness centrality (0.226) - this node is a cross-community bridge._
- **What connects `Agent instructions (Pinky)`, `What it does`, `How it works (high level)` to the rest of the system?**
  _64 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky PRD (Product Requirements Document)` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `preprocess.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13438735177865613 - nodes in this community are weakly interconnected._
- **Should `Pinky` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `config.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08292682926829269 - nodes in this community are weakly interconnected._