# Graph Report - Pinky  (2026-10-19)

## Corpus Check
- 46 files · ~55,194 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .csv 3, .mdc 1)

## Summary
- 607 nodes · 1367 edges · 30 communities (27 shown, 3 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `49cf840c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky architecture
- check_growth_features.py
- sharadar.py
- config.py
- __init__.py
- universe.py
- build_labels_for_ticker
- step3_verdict.py
- fundamentals.py
- purge_train
- build_showcase.py
- Walk-Forward Results
- metrics.py
- AGENTS.md
- product_numbers.py
- train.py
- product_page_data.py
- features.py
- preprocess.py
- Pinky project history
- Batch 2 plan: margin expansion
- run_all
- data_pull.py
- build_train_dataset
- score_group_table
- Claude instructions (Pinky)
- Step 3 training runbook (v8 growth features)
- dev_rows
- load_raw_ticker
- Growth round 2 plan (DRAFT)

## God Nodes (most connected - your core abstractions)
1. `run_all()` - 20 edges
2. `benchmark_closeadj()` - 18 edges
3. `Pinky project history` - 18 edges
4. `dev_rows()` - 17 edges
5. `run_backtest()` - 16 edges
6. `feature_columns()` - 15 edges
7. `pit_training_frame()` - 15 edges
8. `backtest_prices()` - 15 edges
9. `_backtest_lines()` - 14 edges
10. `iter_walk_forward_folds()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Batch 2 code: margins (2026-10-16, Claude Opus 5.5)` --references--> `shuffle_within_date()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/fundamentals.py
- `Step 2 notes (model fixes — done)` --references--> `cross_section_rank()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/preprocess.py
- `Training (`pinky/train.py`, `pinky/walkforward.py`, `pinky/preprocess.py`)` --references--> `dev_rows()`  [INFERRED]
  docs/ARCHITECTURE.md → pinky/train.py
- `Decisions (full, as of 2026-10-03)` --references--> `dev_rows()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/train.py
- `Decisions` --references--> `dev_rows()`  [INFERRED]
  project.md → pinky/train.py

## Import Cycles
- None detected.

## Communities (30 total, 3 thin omitted)

### Community 0 - "Pinky architecture"
Cohesion: 0.04
Nodes (44): Backtest (`pinky/backtest.py`), Data (Sharadar Core US Equities Bundle), Dataset (`pinky/pit_dataset.py`), Goal, Legacy (not used by `--pit` runs), Locked decisions, Outputs (`artifacts/`, `models/`; never in git), Pinky architecture (+36 more)

### Community 1 - "check_growth_features.py"
Cohesion: 0.13
Nodes (42): datetime, pinky, feature_columns(), Numeric model inputs only (no ids, no labels)., check(), correlations(), coverage(), dataset_structure() (+34 more)

### Community 2 - "sharadar.py"
Cohesion: 0.13
Nodes (20): io, os, api_key(), bulk_status(), download_bulk(), pull_all(), DataFrame, Path (+12 more)

### Community 3 - "config.py"
Cohesion: 0.17
Nodes (13): dataclasses, pandas, pathlib, Universe + path config for Pinky., label_columns(), Train-ready dataset: join features (X) + labels (y) on Date + Ticker., Label column names for one horizon or all., Labels vs SPY (architecture-locked). For each stock + date + horizon:… (+5 more)

### Community 5 - "universe.py"
Cohesion: 0.07
Nodes (52): Index, joblib, numpy, build_pit_dataset(), load_pit_dataset(), _log_market_cap(), DataFrame, DatetimeIndex (+44 more)

### Community 6 - "build_labels_for_ticker"
Cohesion: 0.18
Nodes (14): add_top_decile_labels(), build_labels_for_ticker(), build_universe_labels(), _forward_return(), DataFrame, Path, Series, Add `top_{h}` = 1 if the stock's forward excess is in the top `frac` of stocks… (+6 more)

### Community 7 - "step3_verdict.py"
Cohesion: 0.22
Nodes (22): main(), needed_runs(), Verdict for a company-data batch (batch 2 on): does each feature set earn its…, seeded(), ic_halves(), main(), mean_stat(), monthly_gap() (+14 more)

### Community 8 - "fundamentals.py"
Cohesion: 0.13
Nodes (39): add_accel(), add_change(), add_yoy(), _asof_attach(), attach_growth_features(), attach_margin_features(), _dates(), earnings_announcements() (+31 more)

### Community 9 - "purge_train"
Cohesion: 0.38
Nodes (7): purge_train(), DataFrame, DatetimeIndex, Timestamp, Drop train rows whose label uses prices on/after test_start. Label at date D…, _slice_by_dates(), _trading_calendar()

### Community 10 - "build_showcase.py"
Cohesion: 0.08
Nodes (53): math, between_years(), _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores(), monthly_rebalance_dates() (+45 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.08
Nodes (25): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read (+17 more)

### Community 12 - "metrics.py"
Cohesion: 0.16
Nodes (19): brier_score(), calibration_table(), daily_rank_ic(), DataFrame, ndarray, Evaluation metrics for walk-forward reports (honest, no fake scores)., Time-weighted capture of big winners. For each calendar year, take the…, Mean Spearman IC across dates (cross-sectional). (+11 more)

### Community 14 - "product_numbers.py"
Cohesion: 0.10
Nodes (30): acquired_share(), _monthly_dates(), precision_at_k(), DatetimeIndex, Series, Share of the monthly top picks whose company is acquired within `days` of the…, First available date of each month (limits overlap from year-long labels)., Share of the model's top-k picks that end up in the future top decile. `frac`… (+22 more)

### Community 15 - "train.py"
Cohesion: 0.18
Nodes (16): lightgbm, _fit_beat_models(), _fit_return_models(), DataFrame, Walk-forward training + evaluation (LightGBM + Ridge baseline). v2 prep: -…, Train/eval all folds for one horizon with CS prep + tuned LightGBM. Returns…, run_horizon(), _xy_beat() (+8 more)

### Community 16 - "product_page_data.py"
Cohesion: 0.15
Nodes (16): Decimal, json, re, build(), lookup(), main(), fill(), q() (+8 more)

### Community 17 - "features.py"
Cohesion: 0.22
Nodes (16): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+8 more)

### Community 18 - "preprocess.py"
Cohesion: 0.26
Nodes (12): cross_section_rank(), cross_section_zscore(), drop_correlated_features(), prepare_fold_frames(), DataFrame, ranking_feature_cols(), Feature prep for ranking models. 1) Cross-sectional z-score or percentile rank…, Stock-differentiating features only (exclude pure macro/regime). (+4 more)

### Community 19 - "Pinky project history"
Cohesion: 0.08
Nodes (25): Bar to beat (v6_pit: Jan 2001 → Jan 2021; SPY +7.3%/yr, equal-weight universe +8.2%/yr), Batch 2 code: margins (2026-10-16, Claude Opus 5.5), Batch 2 decisions (2026-10-09, Claude Opus 5.5), Batch 2 results: margins (2026-10-19, Claude Opus 5.5), Claude and plugin setup (moved from project.md 2026-10-12, unchanged), Data facts for Phase 2, Decisions (full, as of 2026-10-03), First Claude chat (2026-10-05, Claude Opus 5.5) (+17 more)

### Community 20 - "Batch 2 plan: margin expansion"
Cohesion: 0.20
Nodes (9): After the runs (info only, not gates), Batch 2 plan: margin expansion, Code (before any run), Code checks (2026-10-16), Features (new opt-in group `margins`, 4 columns), Goal, Keep rule (locked; user-approved 2026-10-09), Runbook (only after the user says `run`) (+1 more)

### Community 21 - "run_all"
Cohesion: 0.13
Nodes (20): load_dataset(), Load saved train-ready dataset., pit_tag(), _pit_universe_desc(), placebo_group(), _prep_desc(), Path, Series (+12 more)

### Community 22 - "data_pull.py"
Cohesion: 0.16
Nodes (16): all_tickers(), Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe(), DataFrame, Path, Download daily OHLCV via yfinance and save to data/raw/., Turn ^VIX into VIX-index style names for files. (+8 more)

### Community 23 - "build_train_dataset"
Cohesion: 0.32
Nodes (7): build_train_dataset(), DataFrame, Path, Inner-join features and labels on Date + Ticker. Does not invent rows. Rows…, Write train-ready panel to parquet., save_dataset(), CLI: join features + labels into data/dataset/train_dataset.parquet.

### Community 24 - "score_group_table"
Cohesion: 0.33
Nodes (6): State log (snapshot 2026-10-03), What each score group did next: shows where a model's ranking skill sits. Every…, score_group_table(), _fmt_pct(), Where the ranking skill sits: what each score group did next., _score_group_lines()

### Community 26 - "Step 3 training runbook (v8 growth features)"
Cohesion: 0.50
Nodes (3): Runbook (done 2026-10-03; reuse for the next batch), Step 3 notes (company data batch 1 — plan locked 2026-10-03), Step 3 training runbook (v8 growth features)

### Community 27 - "dev_rows"
Cohesion: 0.29
Nodes (8): Repo layout (full, as of 2026-10-03), dev_rows(), pit_training_frame(), DatetimeIndex, Rows whose label window ends before HOLDOUT_START, so the holdout stays unseen., Pit dataset → model frame for the given fixes (placebo shuffle before ranking)., explain_runs(), Per run x fold x input/family numbers; runs that share inputs share one rebuild.

### Community 28 - "load_raw_ticker"
Cohesion: 0.29
Nodes (7): adj_close_series(), load_raw_ticker(), DataFrame, Path, Series, Load one ticker's raw OHLCV parquet. Raises FileNotFoundError if missing., Prefer Adj Close for returns; fall back to Close.

### Community 29 - "Growth round 2 plan (DRAFT)"
Cohesion: 0.33
Nodes (5): Candidate ideas (pick 2–3 before any results), Decisions for the user (after batch 2's verdict), Growth round 2 plan (DRAFT), Recommendation, Why a round 2

## Knowledge Gaps
- **88 isolated node(s):** `Agent instructions (Pinky)`, `Claude app notes`, `How it works`, `What's in git and what isn't`, `Quick start (local)` (+83 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 266 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Pinky` connect `Pinky architecture` to `train.py`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `dev_rows()` connect `dev_rows` to `Pinky architecture`, `check_growth_features.py`, `universe.py`, `train.py`, `Pinky project history`, `run_all`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `Gotchas (learned the hard way)` connect `train.py` to `fundamentals.py`, `Pinky architecture`, `run_all`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **What connects `Agent instructions (Pinky)`, `Claude app notes`, `How it works` to the rest of the system?**
  _88 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky architecture` be split into smaller, more focused modules?**
  _Cohesion score 0.04081632653061224 - nodes in this community are weakly interconnected._
- **Should `check_growth_features.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12755102040816327 - nodes in this community are weakly interconnected._
- **Should `sharadar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1341991341991342 - nodes in this community are weakly interconnected._