# Graph Report - Pinky  (2026-09-27)

## Corpus Check
- 31 files · ~26,766 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: .mdc 5, (none) 5, .csv 3)

## Summary
- 394 nodes · 775 edges · 13 communities (11 shown, 2 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cf84035e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky PRD (Product Requirements Document)
- preprocess.py
- sharadar.py
- Pinky
- __init__.py
- universe.py
- config.py
- Pinky Architecture Plan
- dataset.py
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
10. `iter_walk_forward_folds()` - 12 edges

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

## Communities (13 total, 2 thin omitted)

### Community 0 - "Pinky PRD (Product Requirements Document)"
Cohesion: 0.10
Nodes (20): 10. Milestones, 11. Risks, 12. Open decisions, 13. Related docs, 1. Problem, 2. Product goal, 3. Who it’s for, 4. What success looks like (+12 more)

### Community 1 - "preprocess.py"
Cohesion: 0.23
Nodes (13): numpy, cross_section_rank(), cross_section_zscore(), drop_correlated_features(), prepare_fold_frames(), DataFrame, ranking_feature_cols(), Feature prep for ranking models. 1) Cross-sectional z-score or percentile rank… (+5 more)

### Community 2 - "sharadar.py"
Cohesion: 0.12
Nodes (22): io, os, api_key(), bulk_status(), download_bulk(), pull_all(), DataFrame, Path (+14 more)

### Community 3 - "Pinky"
Cohesion: 0.11
Nodes (18): dev_rows(), DatetimeIndex, Rows whose label window ends before HOLDOUT_START, so the holdout stays unseen., Backtest defaults, Commands, Decisions, Four model fixes — v7_pit + ablations (2026-09-27), Gotchas (learned the hard way) (+10 more)

### Community 5 - "universe.py"
Cohesion: 0.10
Nodes (33): Index, build_pit_dataset(), load_pit_dataset(), _log_market_cap(), DataFrame, DatetimeIndex, Path, Point-in-time training dataset on the Sharadar liquid universe (survivorship-… (+25 more)

### Community 6 - "config.py"
Cohesion: 0.06
Nodes (58): pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe(), DataFrame (+50 more)

### Community 7 - "Pinky Architecture Plan"
Cohesion: 0.06
Nodes (28): Build order, Explicit non-goals (for now), Feature pipeline, Goal, Labels (truth the model learns), Locked decisions, Models, Pinky Architecture Plan (+20 more)

### Community 8 - "dataset.py"
Cohesion: 0.11
Nodes (27): dataclasses, build_train_dataset(), feature_columns(), label_columns(), DataFrame, Path, Train-ready dataset: join features (X) + labels (y) on Date + Ticker., Numeric model inputs only (no ids, no labels). (+19 more)

### Community 10 - "build_showcase.py"
Cohesion: 0.08
Nodes (54): json, math, between_years(), _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores() (+46 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.09
Nodes (22): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read, Next levers (+14 more)

### Community 12 - "train.py"
Cohesion: 0.06
Nodes (63): joblib, lightgbm, ndarray, load_dataset(), Load saved train-ready dataset., acquired_share(), brier_score(), calibration_table() (+55 more)

## Knowledge Gaps
- **65 isolated node(s):** `Agent instructions (Pinky)`, `What it does`, `How it works (high level)`, `What’s public vs private`, `Current status` (+60 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 192 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_bfm_prediction_features()` connect `config.py` to `Pinky Architecture Plan`?**
  _High betweenness centrality (0.221) - this node is a cross-community bridge._
- **Why does `Feature pipeline` connect `Pinky Architecture Plan` to `config.py`?**
  _High betweenness centrality (0.209) - this node is a cross-community bridge._
- **What connects `Agent instructions (Pinky)`, `What it does`, `How it works (high level)` to the rest of the system?**
  _65 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky PRD (Product Requirements Document)` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `sharadar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11956521739130435 - nodes in this community are weakly interconnected._
- **Should `Pinky` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._
- **Should `universe.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10317460317460317 - nodes in this community are weakly interconnected._