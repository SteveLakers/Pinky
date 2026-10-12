# Graph Report - Pinky  (2026-10-12)

## Corpus Check
- 39 files · ~44,338 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .csv 3, .mdc 1)

## Summary
- 519 nodes · 1111 edges · 16 communities (13 shown, 3 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7f0b6c40`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky architecture
- check_growth_features.py
- sharadar.py
- config.py
- __init__.py
- universe.py
- features.py
- step3_verdict.py
- fundamentals.py
- backtest.py
- Walk-Forward Results
- build_showcase.py
- AGENTS.md
- Pinky project history
- train.py
- Claude instructions (Pinky)

## God Nodes (most connected - your core abstractions)
1. `run_all()` - 19 edges
2. `Pinky project history` - 17 edges
3. `run_backtest()` - 16 edges
4. `backtest_prices()` - 15 edges
5. `_backtest_lines()` - 14 edges
6. `build_data()` - 14 edges
7. `main()` - 14 edges
8. `summarize_backtest()` - 13 edges
9. `acquired_share()` - 13 edges
10. `load_raw_ticker()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Step 2 notes (model fixes — done)` --references--> `cross_section_rank()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/preprocess.py
- `Gotchas (learned the hard way)` --references--> `first_filed()`  [INFERRED]
  project.md → pinky/fundamentals.py
- `Training (`pinky/train.py`, `pinky/walkforward.py`, `pinky/preprocess.py`)` --references--> `dev_rows()`  [INFERRED]
  docs/ARCHITECTURE.md → pinky/train.py
- `Decisions (full, as of 2026-10-03)` --references--> `dev_rows()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/train.py
- `Decisions` --references--> `dev_rows()`  [INFERRED]
  project.md → pinky/train.py

## Import Cycles
- None detected.

## Communities (16 total, 3 thin omitted)

### Community 0 - "Pinky architecture"
Cohesion: 0.04
Nodes (43): Backtest (`pinky/backtest.py`), Data (Sharadar Core US Equities Bundle), Dataset (`pinky/pit_dataset.py`), Goal, Legacy (not used by `--pit` runs), Locked decisions, Outputs (`artifacts/`, `models/`; never in git), Pinky architecture (+35 more)

### Community 1 - "check_growth_features.py"
Cohesion: 0.17
Nodes (26): datetime, pinky, feature_columns(), Numeric model inputs only (no ids, no labels)., check(), correlations(), coverage(), dataset_structure() (+18 more)

### Community 2 - "sharadar.py"
Cohesion: 0.09
Nodes (31): Decimal, io, json, os, api_key(), bulk_status(), download_bulk(), pull_all() (+23 more)

### Community 3 - "config.py"
Cohesion: 0.07
Nodes (44): dataclasses, pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe() (+36 more)

### Community 5 - "universe.py"
Cohesion: 0.08
Nodes (44): Index, numpy, build_pit_dataset(), load_pit_dataset(), _log_market_cap(), DataFrame, DatetimeIndex, Path (+36 more)

### Community 6 - "features.py"
Cohesion: 0.22
Nodes (16): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+8 more)

### Community 7 - "step3_verdict.py"
Cohesion: 0.18
Nodes (22): Ticker -> Sharadar sector (current classification) for every eligible stock., sector_map(), DataFrame, Monthly top-k picks (first test date of each month): share in the day's top…, winner_crash_rates(), ic_halves(), main(), mean_stat() (+14 more)

### Community 8 - "fundamentals.py"
Cohesion: 0.18
Nodes (25): add_accel(), add_yoy(), _asof_attach(), attach_growth_features(), _dates(), earnings_announcements(), first_filed(), growth_feature_frame() (+17 more)

### Community 10 - "backtest.py"
Cohesion: 0.06
Nodes (64): math, between_years(), _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores(), monthly_rebalance_dates() (+56 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.08
Nodes (24): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read (+16 more)

### Community 12 - "build_showcase.py"
Cohesion: 0.07
Nodes (47): acquired_share(), brier_score(), calibration_table(), _monthly_dates(), precision_at_k(), DataFrame, DatetimeIndex, ndarray (+39 more)

### Community 19 - "Pinky project history"
Cohesion: 0.10
Nodes (19): Bar to beat (v6_pit: Jan 2001 → Jan 2021; SPY +7.3%/yr, equal-weight universe +8.2%/yr), Batch 2 decisions (2026-10-09, Claude Opus 5.5), Data facts for Phase 2, First Claude chat (2026-10-05, Claude Opus 5.5), Four model fixes — v7_pit + ablations (2026-09-27), Honest baseline — v5_pit (2026-09-26), Key findings, Move to the Claude app (2026-10-04, user-approved) (+11 more)

### Community 21 - "train.py"
Cohesion: 0.05
Nodes (62): Training (`pinky/train.py`, `pinky/walkforward.py`, `pinky/preprocess.py`), Decisions (full, as of 2026-10-03), Repo layout (full, as of 2026-10-03), State log (snapshot 2026-10-03), Runbook (done 2026-10-03; reuse for the next batch), Step 3 notes (company data batch 1 — plan locked 2026-10-03), Step 3 training runbook (v8 growth features), joblib (+54 more)

## Knowledge Gaps
- **72 isolated node(s):** `Agent instructions (Pinky)`, `Claude app notes`, `How it works`, `What's in git and what isn't`, `Quick start (local)` (+67 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 232 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Pinky` connect `Pinky architecture` to `train.py`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `dev_rows()` connect `train.py` to `check_growth_features.py`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Why does `Gotchas (learned the hard way)` connect `Pinky architecture` to `fundamentals.py`, `config.py`, `train.py`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **What connects `Agent instructions (Pinky)`, `Claude app notes`, `How it works` to the rest of the system?**
  _72 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky architecture` be split into smaller, more focused modules?**
  _Cohesion score 0.041666666666666664 - nodes in this community are weakly interconnected._
- **Should `sharadar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0855614973262032 - nodes in this community are weakly interconnected._
- **Should `config.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06588235294117648 - nodes in this community are weakly interconnected._