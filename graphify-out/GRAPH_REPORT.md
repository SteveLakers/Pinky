# Graph Report - Pinky  (2026-09-25)

## Corpus Check
- 24 files · ~9,778 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .mdc 4)

## Summary
- 256 nodes · 456 edges · 12 communities (11 shown, 1 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d22acaf0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky Architecture Plan
- pull_universe
- dataset.py
- Pinky
- __init__.py
- Pinky PRD (Product Requirements Document)
- features.py
- build_labels_for_ticker
- walkforward.py
- metrics.py
- train.py
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
Nodes (27): Build order, Explicit non-goals (for now), Goal, Labels (truth the model learns), Locked decisions, Models, Pinky Architecture Plan, Prediction flow (+19 more)

### Community 1 - "pull_universe"
Cohesion: 0.24
Nodes (9): download_ticker(), pull_universe(), DataFrame, Path, Pull one ticker's daily history. Raises ValueError if the download is empty or…, Write one ticker to parquet under data/raw/., Download and save each ticker. Returns mapping ticker -> parquet path for…, save_ticker() (+1 more)

### Community 2 - "dataset.py"
Cohesion: 0.11
Nodes (25): build_train_dataset(), feature_columns(), label_columns(), load_dataset(), DataFrame, Path, Train-ready dataset: join features (X) + labels (y) on Date + Ticker., Numeric model inputs only (no ids, no labels). (+17 more)

### Community 3 - "Pinky"
Cohesion: 0.20
Nodes (9): Build order, Current universe, Pinky, Planned stack (v1), Portfolio backtest defaults, Rules (always on), Status, What it will do (+1 more)

### Community 5 - "Pinky PRD (Product Requirements Document)"
Cohesion: 0.10
Nodes (20): 10. Milestones, 11. Risks, 12. Open decisions, 13. Related docs, 1. Problem, 2. Product goal, 3. Who it’s for, 4. What success looks like (+12 more)

### Community 6 - "features.py"
Cohesion: 0.09
Nodes (38): Feature pipeline, numpy, pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., Download daily OHLCV via yfinance and save to data/raw/. (+30 more)

### Community 7 - "build_labels_for_ticker"
Cohesion: 0.22
Nodes (12): build_labels_for_ticker(), build_universe_labels(), _forward_return(), DataFrame, Path, Series, Write stacked label panel to parquet., Return from t to t+horizon_days. NaN near the end where future is unknown. (+4 more)

### Community 8 - "walkforward.py"
Cohesion: 0.24
Nodes (14): dataclasses, iter_walk_forward_folds(), purge_train(), DataFrame, DatetimeIndex, Timestamp, Walk-forward folds + label-window purge. - Expanding train window, fixed-length…, Small table describing folds (no model training). (+6 more)

### Community 9 - "metrics.py"
Cohesion: 0.18
Nodes (17): ndarray, brier_score(), calibration_table(), daily_rank_ic(), DataFrame, Evaluation metrics for walk-forward reports (honest, no fake scores)., Mean Spearman IC across dates (cross-sectional)., Mean realized beat-rate among top predicted names each day. (+9 more)

### Community 10 - "train.py"
Cohesion: 0.08
Nodes (49): joblib, lightgbm, math, _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores() (+41 more)

### Community 11 - "v3 — bigger balanced universe + trading-cost backtest (2026-09-25)"
Cohesion: 0.17
Nodes (11): Honest read, Honest read, Next levers, Portfolio backtest CAGR (Jan 2018 → Oct 2025, net of 10 bps; SPY +14.1%), Portfolio backtest (Jan 2018 → Oct 2025, net of 10 bps), Ranking metrics (1y, 8 folds), Ranking metrics (1y, 8 folds), v2 prep (2026-09-23, 58 stocks) (+3 more)

## Knowledge Gaps
- **57 isolated node(s):** `What it does`, `How it works (high level)`, `What’s public vs private`, `Current status`, `Quick start (local)` (+52 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 133 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Pinky Architecture Plan` connect `Pinky Architecture Plan` to `features.py`?**
  _High betweenness centrality (0.307) - this node is a cross-community bridge._
- **Why does `Feature pipeline` connect `features.py` to `Pinky Architecture Plan`?**
  _High betweenness centrality (0.299) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `build_bfm_prediction_features()` (e.g. with `Feature pipeline` and `Repo layout`) actually correct?**
  _`build_bfm_prediction_features()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `What it does`, `How it works (high level)`, `What’s public vs private` to the rest of the system?**
  _57 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky Architecture Plan` be split into smaller, more focused modules?**
  _Cohesion score 0.06451612903225806 - nodes in this community are weakly interconnected._
- **Should `dataset.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11330049261083744 - nodes in this community are weakly interconnected._
- **Should `Pinky PRD (Product Requirements Document)` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._