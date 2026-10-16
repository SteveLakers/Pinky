# Graph Report - Pinky  (2026-10-16)

## Corpus Check
- 44 files · ~52,605 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .csv 3, .mdc 1)

## Summary
- 589 nodes · 1332 edges · 27 communities (24 shown, 3 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fa1ca297`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky architecture
- check_growth_features.py
- sharadar.py
- config.py
- __init__.py
- shap_report.py
- load_raw_ticker
- step3_verdict.py
- fundamentals.py
- walkforward.py
- backtest.py
- Walk-Forward Results
- metrics.py
- AGENTS.md
- universe.py
- build_showcase.py
- product_page_data.py
- features.py
- pit_training_frame
- Pinky project history
- Batch 2 plan: margin expansion
- train.py
- pull_universe
- build_train_dataset
- score_group_table
- Claude instructions (Pinky)
- Step 3 training runbook (v8 growth features)

## God Nodes (most connected - your core abstractions)
1. `run_all()` - 20 edges
2. `Pinky project history` - 18 edges
3. `run_backtest()` - 16 edges
4. `benchmark_closeadj()` - 16 edges
5. `feature_columns()` - 15 edges
6. `dev_rows()` - 15 edges
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
- `Step 3 notes (company data batch 1 — plan locked 2026-10-03)` --references--> `pit_training_frame()`  [INFERRED]
  docs/STEP3_RUNBOOK.md → pinky/train.py
- `Gotchas (learned the hard way)` --references--> `first_filed()`  [INFERRED]
  project.md → pinky/fundamentals.py

## Import Cycles
- None detected.

## Communities (27 total, 3 thin omitted)

### Community 0 - "Pinky architecture"
Cohesion: 0.04
Nodes (44): Backtest (`pinky/backtest.py`), Data (Sharadar Core US Equities Bundle), Dataset (`pinky/pit_dataset.py`), Goal, Legacy (not used by `--pit` runs), Locked decisions, Outputs (`artifacts/`, `models/`; never in git), Pinky architecture (+36 more)

### Community 1 - "check_growth_features.py"
Cohesion: 0.11
Nodes (47): datetime, Decisions (full, as of 2026-10-03), pinky, feature_columns(), Numeric model inputs only (no ids, no labels)., dev_rows(), DatetimeIndex, Rows whose label window ends before HOLDOUT_START, so the holdout stays unseen. (+39 more)

### Community 2 - "sharadar.py"
Cohesion: 0.13
Nodes (20): io, os, api_key(), bulk_status(), download_bulk(), pull_all(), DataFrame, Path (+12 more)

### Community 3 - "config.py"
Cohesion: 0.15
Nodes (15): pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., Download daily OHLCV via yfinance and save to data/raw/., Turn ^VIX into VIX-index style names for files., _safe_filename() (+7 more)

### Community 5 - "shap_report.py"
Cohesion: 0.10
Nodes (30): joblib, attach_growth_features(), attach_margin_features(), Add the six growth columns to a Date/Ticker frame (row order kept)., Add the four margin columns to a Date/Ticker frame (row order kept)., build_pit_dataset(), load_pit_dataset(), _log_market_cap() (+22 more)

### Community 6 - "load_raw_ticker"
Cohesion: 0.13
Nodes (21): add_top_decile_labels(), build_labels_for_ticker(), build_universe_labels(), _forward_return(), DataFrame, Path, Series, Add `top_{h}` = 1 if the stock's forward excess is in the top `frac` of stocks… (+13 more)

### Community 7 - "step3_verdict.py"
Cohesion: 0.14
Nodes (30): main(), needed_runs(), Verdict for a company-data batch (batch 2 on): does each feature set earn its…, seeded(), main(), _pct(), DataFrame, Series (+22 more)

### Community 8 - "fundamentals.py"
Cohesion: 0.15
Nodes (34): Repo layout (full, as of 2026-10-03), add_accel(), add_change(), add_yoy(), _asof_attach(), _dates(), earnings_announcements(), first_filed() (+26 more)

### Community 9 - "walkforward.py"
Cohesion: 0.25
Nodes (14): dataclasses, iter_walk_forward_folds(), purge_train(), DataFrame, DatetimeIndex, Timestamp, Walk-forward folds + label-window purge. - Expanding train window, fixed-length…, Small table describing folds (no model training). (+6 more)

### Community 10 - "backtest.py"
Cohesion: 0.12
Nodes (33): math, _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores(), monthly_rebalance_dates(), _next_day() (+25 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.08
Nodes (24): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read (+16 more)

### Community 12 - "metrics.py"
Cohesion: 0.13
Nodes (23): acquired_share(), brier_score(), calibration_table(), _monthly_dates(), DataFrame, DatetimeIndex, ndarray, Series (+15 more)

### Community 14 - "universe.py"
Cohesion: 0.10
Nodes (36): Index, numpy, load(), Rebuild a pit run's report from its saved metrics + predictions (no retraining)., rewrite_summary(), acquisition_dates(), backtest_prices(), build_panels() (+28 more)

### Community 15 - "build_showcase.py"
Cohesion: 0.13
Nodes (24): between_years(), Holding periods that start in [first, last] (either end open)., Same trades re-priced at another cost level (picks and turnover don't depend on…, with_cost(), precision_at_k(), Share of the model's top-k picks that end up in the future top decile. `frac`…, build_data(), buyout_split() (+16 more)

### Community 16 - "product_page_data.py"
Cohesion: 0.15
Nodes (16): Decimal, json, re, build(), lookup(), main(), fill(), q() (+8 more)

### Community 17 - "features.py"
Cohesion: 0.22
Nodes (16): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+8 more)

### Community 18 - "pit_training_frame"
Cohesion: 0.18
Nodes (16): Placebo: give each row another same-date row's values of `cols` (block kept…, shuffle_within_date(), cross_section_rank(), cross_section_zscore(), drop_correlated_features(), prepare_fold_frames(), DataFrame, ranking_feature_cols() (+8 more)

### Community 19 - "Pinky project history"
Cohesion: 0.08
Nodes (23): Bar to beat (v6_pit: Jan 2001 → Jan 2021; SPY +7.3%/yr, equal-weight universe +8.2%/yr), Batch 2 code: margins (2026-10-16, Claude Opus 5.5), Batch 2 decisions (2026-10-09, Claude Opus 5.5), Claude and plugin setup (moved from project.md 2026-10-12, unchanged), Data facts for Phase 2, First Claude chat (2026-10-05, Claude Opus 5.5), Four model fixes — v7_pit + ablations (2026-09-27), Honest baseline — v5_pit (2026-09-26) (+15 more)

### Community 20 - "Batch 2 plan: margin expansion"
Cohesion: 0.20
Nodes (9): After the runs (info only, not gates), Batch 2 plan: margin expansion, Code (before any run), Code checks (2026-10-16), Features (new opt-in group `margins`, 4 columns), Goal, Keep rule (locked; user-approved 2026-10-09), Runbook (only after the user says `run`) (+1 more)

### Community 21 - "train.py"
Cohesion: 0.11
Nodes (30): lightgbm, load_dataset(), Load saved train-ready dataset., _fit_beat_models(), _fit_return_models(), pit_tag(), _pit_universe_desc(), placebo_group() (+22 more)

### Community 22 - "pull_universe"
Cohesion: 0.24
Nodes (9): download_ticker(), pull_universe(), DataFrame, Path, Pull one ticker's daily history. Raises ValueError if the download is empty or…, Write one ticker to parquet under data/raw/., Download and save each ticker. Returns mapping ticker -> parquet path for…, save_ticker() (+1 more)

### Community 23 - "build_train_dataset"
Cohesion: 0.32
Nodes (7): build_train_dataset(), DataFrame, Path, Inner-join features and labels on Date + Ticker. Does not invent rows. Rows…, Write train-ready panel to parquet., save_dataset(), CLI: join features + labels into data/dataset/train_dataset.parquet.

### Community 24 - "score_group_table"
Cohesion: 0.33
Nodes (6): State log (snapshot 2026-10-03), What each score group did next: shows where a model's ranking skill sits. Every…, score_group_table(), _fmt_pct(), Where the ranking skill sits: what each score group did next., _score_group_lines()

### Community 26 - "Step 3 training runbook (v8 growth features)"
Cohesion: 0.50
Nodes (3): Runbook (done 2026-10-03; reuse for the next batch), Step 3 notes (company data batch 1 — plan locked 2026-10-03), Step 3 training runbook (v8 growth features)

## Knowledge Gaps
- **82 isolated node(s):** `Agent instructions (Pinky)`, `Claude app notes`, `How it works`, `What's in git and what isn't`, `Quick start (local)` (+77 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 256 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Pinky` connect `Pinky architecture` to `check_growth_features.py`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `dev_rows()` connect `check_growth_features.py` to `Pinky architecture`, `fundamentals.py`, `shap_report.py`, `train.py`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Why does `Gotchas (learned the hard way)` connect `Pinky architecture` to `fundamentals.py`, `walkforward.py`, `train.py`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **What connects `Agent instructions (Pinky)`, `Claude app notes`, `How it works` to the rest of the system?**
  _82 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky architecture` be split into smaller, more focused modules?**
  _Cohesion score 0.04081632653061224 - nodes in this community are weakly interconnected._
- **Should `check_growth_features.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11041229909154437 - nodes in this community are weakly interconnected._
- **Should `sharadar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1341991341991342 - nodes in this community are weakly interconnected._