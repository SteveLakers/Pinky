# Graph Report - Pinky  (2026-09-23)

## Corpus Check
- 21 files · ~6,697 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .mdc 4)

## Summary
- 199 nodes · 332 edges · 11 communities (10 shown, 1 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3470e056`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky Architecture Plan
- data_pull.py
- walkforward.py
- Pinky
- __init__.py
- Pinky PRD (Product Requirements Document)
- features.py
- build_labels_for_ticker
- iter_walk_forward_folds
- train.py
- Metrics to report

## God Nodes (most connected - your core abstractions)
1. `Pinky PRD (Product Requirements Document)` - 14 edges
2. `build_bfm_prediction_features()` - 13 edges
3. `load_raw_ticker()` - 11 edges
4. `run_horizon()` - 11 edges
5. `Pinky Architecture Plan` - 11 edges
6. `adj_close_series()` - 10 edges
7. `iter_walk_forward_folds()` - 10 edges
8. `_helper_frame()` - 9 edges
9. `build_labels_for_ticker()` - 9 edges
10. `Pinky` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Feature pipeline` --references--> `build_bfm_prediction_features()`  [INFERRED]
  docs/ARCHITECTURE.md → pinky/features.py
- `Repo layout` --references--> `build_bfm_prediction_features()`  [INFERRED]
  project.md → pinky/features.py
- `_eval_fold()` --uses--> `WalkForwardFold`  [INFERRED]
  pinky/train.py → pinky/walkforward.py
- `load_raw_ticker()` --calls--> `_safe_filename()`  [EXTRACTED]
  pinky/raw_io.py → pinky/data_pull.py
- `run_horizon()` --calls--> `feature_columns()`  [EXTRACTED]
  pinky/train.py → pinky/dataset.py

## Import Cycles
- None detected.

## Communities (11 total, 1 thin omitted)

### Community 0 - "Pinky Architecture Plan"
Cohesion: 0.09
Nodes (19): Build order, Explicit non-goals (for now), Feature pipeline, Goal, Labels (truth the model learns), Locked decisions, Models, Pinky Architecture Plan (+11 more)

### Community 1 - "data_pull.py"
Cohesion: 0.16
Nodes (16): all_tickers(), Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe(), DataFrame, Path, Download daily OHLCV via yfinance and save to data/raw/., Turn ^VIX into VIX-index style names for files. (+8 more)

### Community 2 - "walkforward.py"
Cohesion: 0.11
Nodes (24): dataclasses, pandas, pathlib, Universe + path config for Pinky v1 prototype., build_train_dataset(), feature_columns(), label_columns(), load_dataset() (+16 more)

### Community 3 - "Pinky"
Cohesion: 0.20
Nodes (9): Build order, Current universe, Pinky, Planned stack (v1), Repo layout, Rules (always on), Status, What it will do (+1 more)

### Community 5 - "Pinky PRD (Product Requirements Document)"
Cohesion: 0.10
Nodes (20): 10. Milestones, 11. Risks, 12. Open decisions, 13. Related docs, 1. Problem, 2. Product goal, 3. Who it’s for, 4. What success looks like (+12 more)

### Community 6 - "features.py"
Cohesion: 0.15
Nodes (23): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+15 more)

### Community 7 - "build_labels_for_ticker"
Cohesion: 0.22
Nodes (12): build_labels_for_ticker(), build_universe_labels(), _forward_return(), DataFrame, Path, Series, Write stacked label panel to parquet., Return from t to t+horizon_days. NaN near the end where future is unknown. (+4 more)

### Community 8 - "iter_walk_forward_folds"
Cohesion: 0.31
Nodes (10): DatetimeIndex, iter_walk_forward_folds(), purge_train(), DataFrame, Drop train rows whose label uses prices on/after test_start. Label at date D…, Yield purged walk-forward folds for one horizon. Train = all rows with Date <…, _slice_by_dates(), _trading_calendar() (+2 more)

### Community 9 - "train.py"
Cohesion: 0.10
Nodes (35): lightgbm, ndarray, numpy, brier_score(), calibration_table(), daily_rank_ic(), DataFrame, Evaluation metrics for walk-forward reports (honest, no fake scores). (+27 more)

### Community 10 - "Metrics to report"
Cohesion: 0.22
Nodes (9): Basket vs SPY, Fail conditions (do not ship / do not trust), Honesty checks, Metrics to report, Must-pass rules, Pass bar (first useful prototype), Pinky Eval Checklist (v1), Probability calibration (beat model) (+1 more)

## Knowledge Gaps
- **48 isolated node(s):** `What it does`, `How it works (high level)`, `What’s public vs private`, `Current status`, `Quick start (local)` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 107 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_bfm_prediction_features()` connect `features.py` to `Pinky Architecture Plan`, `Pinky`?**
  _High betweenness centrality (0.468) - this node is a cross-community bridge._
- **Why does `Feature pipeline` connect `Pinky Architecture Plan` to `features.py`?**
  _High betweenness centrality (0.379) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `build_bfm_prediction_features()` (e.g. with `Feature pipeline` and `Repo layout`) actually correct?**
  _`build_bfm_prediction_features()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `What it does`, `How it works (high level)`, `What’s public vs private` to the rest of the system?**
  _48 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky Architecture Plan` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._
- **Should `walkforward.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11182795698924732 - nodes in this community are weakly interconnected._
- **Should `Pinky PRD (Product Requirements Document)` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._