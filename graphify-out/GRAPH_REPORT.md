# Graph Report - Pinky  (2026-09-25)

## Corpus Check
- 26 files · ~17,004 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: .mdc 5, (none) 5, .csv 3)

## Summary
- 285 nodes · 520 edges · 14 communities (12 shown, 2 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2cc28b41`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky Architecture Plan
- dataset.py
- config.py
- Pinky
- __init__.py
- Pinky PRD (Product Requirements Document)
- features.py
- labels.py
- preprocess.py
- build_showcase.py
- train.py
- Walk-Forward Results
- run_horizon
- AGENTS.md

## God Nodes (most connected - your core abstractions)
1. `Pinky PRD (Product Requirements Document)` - 14 edges
2. `load_raw_ticker()` - 13 edges
3. `build_bfm_prediction_features()` - 12 edges
4. `adj_close_series()` - 12 edges
5. `Pinky` - 12 edges
6. `run_backtest()` - 11 edges
7. `run_horizon()` - 11 edges
8. `_backtest_lines()` - 11 edges
9. `Pinky Architecture Plan` - 11 edges
10. `iter_walk_forward_folds()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Feature pipeline` --references--> `build_bfm_prediction_features()`  [INFERRED]
  docs/ARCHITECTURE.md → pinky/features.py
- `Roadmap` --references--> `add_top_decile_labels()`  [INFERRED]
  project.md → pinky/labels.py
- `Roadmap` --references--> `precision_at_k()`  [INFERRED]
  project.md → pinky/metrics.py
- `Roadmap` --references--> `winner_capture()`  [INFERRED]
  project.md → pinky/metrics.py
- `Where we are (2026-09-25)` --references--> `main()`  [INFERRED]
  project.md → scripts/build_showcase.py

## Import Cycles
- None detected.

## Communities (14 total, 2 thin omitted)

### Community 0 - "Pinky Architecture Plan"
Cohesion: 0.06
Nodes (28): Build order, Explicit non-goals (for now), Feature pipeline, Goal, Labels (truth the model learns), Locked decisions, Models, Pinky Architecture Plan (+20 more)

### Community 1 - "dataset.py"
Cohesion: 0.10
Nodes (30): dataclasses, pandas, build_train_dataset(), feature_columns(), label_columns(), load_dataset(), DataFrame, Path (+22 more)

### Community 2 - "config.py"
Cohesion: 0.13
Nodes (19): pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe(), DataFrame, Path (+11 more)

### Community 3 - "Pinky"
Cohesion: 0.14
Nodes (13): Baseline metrics (current 128-stock v4 preds, inflated), Current (old) universe, Decisions, Key findings so far, Pinky, Portfolio backtest defaults, Repo layout, Rules (always on) (+5 more)

### Community 5 - "Pinky PRD (Product Requirements Document)"
Cohesion: 0.10
Nodes (20): 10. Milestones, 11. Risks, 12. Open decisions, 13. Related docs, 1. Problem, 2. Product goal, 3. Who it’s for, 4. What success looks like (+12 more)

### Community 6 - "features.py"
Cohesion: 0.15
Nodes (23): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+15 more)

### Community 7 - "labels.py"
Cohesion: 0.22
Nodes (13): build_labels_for_ticker(), build_universe_labels(), _forward_return(), DataFrame, Path, Series, Labels vs SPY (architecture-locked). For each stock + date + horizon:…, Write stacked label panel to parquet. (+5 more)

### Community 8 - "preprocess.py"
Cohesion: 0.29
Nodes (10): cross_section_zscore(), drop_correlated_features(), prepare_fold_frames(), DataFrame, ranking_feature_cols(), Feature prep for ranking models. 1) Cross-sectional z-score by Date (grade…, For each Date, z-score selected columns across tickers. Constant-within-day…, Greedy drop: among highly correlated pairs on TRAIN only, keep the first. (+2 more)

### Community 9 - "build_showcase.py"
Cohesion: 0.09
Nodes (35): json, ndarray, numpy, os, add_top_decile_labels(), Add `top_{h}` = 1 if the stock's forward excess is in the top `frac` of stocks…, brier_score(), calibration_table() (+27 more)

### Community 10 - "train.py"
Cohesion: 0.10
Nodes (41): joblib, lightgbm, math, _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores() (+33 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.13
Nodes (14): Honest read, Honest read, Honest read, Next levers, Portfolio backtest CAGR (Jan 2018 → Oct 2025, net of 10 bps; SPY +14.1%), Portfolio backtest (Jan 2018 → Oct 2025, net of 10 bps), Ranking metrics (1y, 8 folds), Ranking metrics (1y, 8 folds) (+6 more)

### Community 12 - "run_horizon"
Cohesion: 0.21
Nodes (11): _fit_beat_models(), _fit_return_models(), DataFrame, Train/eval all folds for one horizon with CS prep + tuned LightGBM., Run walk-forward training. Default focus: 1y. `exclude` drops tickers from…, run_all(), run_horizon(), _xy_beat() (+3 more)

## Knowledge Gaps
- **61 isolated node(s):** `Agent instructions (Pinky)`, `What it does`, `How it works (high level)`, `What’s public vs private`, `Current status` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 150 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_bfm_prediction_features()` connect `features.py` to `Pinky Architecture Plan`?**
  _High betweenness centrality (0.288) - this node is a cross-community bridge._
- **Why does `Feature pipeline` connect `Pinky Architecture Plan` to `features.py`?**
  _High betweenness centrality (0.272) - this node is a cross-community bridge._
- **What connects `Agent instructions (Pinky)`, `What it does`, `How it works (high level)` to the rest of the system?**
  _61 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky Architecture Plan` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `dataset.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10338680926916222 - nodes in this community are weakly interconnected._
- **Should `config.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13438735177865613 - nodes in this community are weakly interconnected._
- **Should `Pinky` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._