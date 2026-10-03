# Graph Report - Pinky  (2026-10-03)

## Corpus Check
- 35 files · ~42,507 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: (none) 8, .mdc 5, .csv 3)

## Summary
- 481 nodes · 1028 edges · 19 communities (17 shown, 2 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 12 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `340e8660`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky PRD (Product Requirements Document)
- check_growth_features.py
- sharadar.py
- preprocess.py
- __init__.py
- universe.py
- features.py
- Pinky Architecture Plan
- fundamentals.py
- config.py
- build_showcase.py
- Walk-Forward Results
- train.py
- AGENTS.md
- step3_verdict.py
- Pinky Eval Checklist (v1)
- Pinky
- 5. In scope (v1)
- Metrics to report

## God Nodes (most connected - your core abstractions)
1. `run_all()` - 16 edges
2. `run_backtest()` - 14 edges
3. `_backtest_lines()` - 14 edges
4. `build_data()` - 14 edges
5. `Pinky PRD (Product Requirements Document)` - 14 edges
6. `load_raw_ticker()` - 13 edges
7. `backtest_prices()` - 13 edges
8. `main()` - 13 edges
9. `feature_columns()` - 12 edges
10. `build_bfm_prediction_features()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Backtest defaults` --references--> `with_cost()`  [INFERRED]
  project.md → pinky/backtest.py
- `Feature pipeline` --references--> `build_bfm_prediction_features()`  [INFERRED]
  docs/ARCHITECTURE.md → pinky/features.py
- `Gotchas (learned the hard way)` --references--> `iter_walk_forward_folds()`  [INFERRED]
  project.md → pinky/walkforward.py
- `▶ Resume here (new chat: read this first)` --references--> `cross_section_rank()`  [INFERRED]
  project.md → pinky/preprocess.py
- `Decisions` --references--> `dev_rows()`  [INFERRED]
  project.md → pinky/train.py

## Import Cycles
- None detected.

## Communities (19 total, 2 thin omitted)

### Community 0 - "Pinky PRD (Product Requirements Document)"
Cohesion: 0.15
Nodes (13): 10. Milestones, 11. Risks, 12. Open decisions, 13. Related docs, 1. Problem, 2. Product goal, 3. Who it’s for, 4. What success looks like (+5 more)

### Community 1 - "check_growth_features.py"
Cohesion: 0.16
Nodes (27): datetime, pinky, feature_columns(), Numeric model inputs only (no ids, no labels)., check(), correlations(), coverage(), dataset_structure() (+19 more)

### Community 2 - "sharadar.py"
Cohesion: 0.12
Nodes (22): io, os, api_key(), bulk_status(), download_bulk(), pull_all(), DataFrame, Path (+14 more)

### Community 3 - "preprocess.py"
Cohesion: 0.08
Nodes (29): cross_section_rank(), cross_section_zscore(), drop_correlated_features(), prepare_fold_frames(), DataFrame, ranking_feature_cols(), Feature prep for ranking models. 1) Cross-sectional z-score or percentile rank…, Stock-differentiating features only (exclude pure macro/regime). (+21 more)

### Community 5 - "universe.py"
Cohesion: 0.10
Nodes (34): Index, numpy, build_pit_dataset(), load_pit_dataset(), _log_market_cap(), DataFrame, DatetimeIndex, Path (+26 more)

### Community 6 - "features.py"
Cohesion: 0.09
Nodes (38): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+30 more)

### Community 7 - "Pinky Architecture Plan"
Cohesion: 0.18
Nodes (11): Build order, Explicit non-goals (for now), Feature pipeline, Goal, Labels (truth the model learns), Locked decisions, Models, Pinky Architecture Plan (+3 more)

### Community 8 - "fundamentals.py"
Cohesion: 0.18
Nodes (25): add_accel(), add_yoy(), _asof_attach(), attach_growth_features(), _dates(), earnings_announcements(), first_filed(), growth_feature_frame() (+17 more)

### Community 9 - "config.py"
Cohesion: 0.06
Nodes (47): dataclasses, pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe() (+39 more)

### Community 10 - "build_showcase.py"
Cohesion: 0.08
Nodes (52): math, between_years(), _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores(), monthly_rebalance_dates() (+44 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.09
Nodes (22): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read, Next levers (+14 more)

### Community 12 - "train.py"
Cohesion: 0.05
Nodes (70): joblib, json, lightgbm, Placebo: give each row another same-date row's six growth values (block kept…, shuffle_growth_within_date(), acquired_share(), brier_score(), calibration_table() (+62 more)

### Community 14 - "step3_verdict.py"
Cohesion: 0.18
Nodes (22): Ticker -> Sharadar sector (current classification) for every eligible stock., sector_map(), DataFrame, Monthly top-k picks (first test date of each month): share in the day's top…, winner_crash_rates(), ic_halves(), main(), mean_stat() (+14 more)

### Community 15 - "Pinky Eval Checklist (v1)"
Cohesion: 0.25
Nodes (4): Fail conditions (do not ship / do not trust), Must-pass rules, Pass bar (first useful prototype), Pinky Eval Checklist (v1)

### Community 16 - "Pinky"
Cohesion: 0.25
Nodes (8): Current status, Design principles, Disclaimer, How it works (high level), Pinky, Quick start (local), What it does, What’s public vs private

### Community 17 - "5. In scope (v1)"
Cohesion: 0.29
Nodes (7): 5. In scope (v1), Data, Delivery (v1), Features, Labels, Models, Validation

### Community 18 - "Metrics to report"
Cohesion: 0.40
Nodes (5): Basket vs SPY, Honesty checks, Metrics to report, Probability calibration (beat model), Ranking quality

## Knowledge Gaps
- **65 isolated node(s):** `Agent instructions (Pinky)`, `What it does`, `How it works (high level)`, `What’s public vs private`, `Current status` (+60 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 219 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_bfm_prediction_features()` connect `features.py` to `Pinky Architecture Plan`?**
  _High betweenness centrality (0.189) - this node is a cross-community bridge._
- **Why does `Pinky Architecture Plan` connect `Pinky Architecture Plan` to `Pinky Eval Checklist (v1)`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Why does `Feature pipeline` connect `Pinky Architecture Plan` to `features.py`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **What connects `Agent instructions (Pinky)`, `What it does`, `How it works (high level)` to the rest of the system?**
  _65 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `sharadar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11956521739130435 - nodes in this community are weakly interconnected._
- **Should `preprocess.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08172043010752689 - nodes in this community are weakly interconnected._
- **Should `universe.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1006006006006006 - nodes in this community are weakly interconnected._