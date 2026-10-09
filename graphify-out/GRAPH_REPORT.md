# Graph Report - Pinky  (2026-10-07)

## Corpus Check
- 39 files · ~43,633 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .csv 3, .mdc 1)

## Summary
- 514 nodes · 1103 edges · 18 communities (15 shown, 3 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6cf5608d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky architecture
- check_growth_features.py
- sharadar.py
- data_pull.py
- __init__.py
- walkforward.py
- features.py
- config.py
- fundamentals.py
- load_dataset
- build_showcase.py
- Walk-Forward Results
- product_numbers.py
- AGENTS.md
- Pinky
- Pinky project history
- train.py
- Claude instructions (Pinky)

## God Nodes (most connected - your core abstractions)
1. `run_all()` - 17 edges
2. `run_backtest()` - 16 edges
3. `Pinky project history` - 16 edges
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

## Communities (18 total, 3 thin omitted)

### Community 0 - "Pinky architecture"
Cohesion: 0.05
Nodes (33): Backtest (`pinky/backtest.py`), Data (Sharadar Core US Equities Bundle), Dataset (`pinky/pit_dataset.py`), Goal, Legacy (not used by `--pit` runs), Locked decisions, Outputs (`artifacts/`, `models/`; never in git), Pinky architecture (+25 more)

### Community 1 - "check_growth_features.py"
Cohesion: 0.15
Nodes (29): datetime, pinky, feature_columns(), Numeric model inputs only (no ids, no labels)., benchmark_closeadj(), SPY adjusted close from Sharadar funds (cached)., check(), correlations() (+21 more)

### Community 2 - "sharadar.py"
Cohesion: 0.07
Nodes (36): Decimal, Index, io, json, os, api_key(), bulk_status(), download_bulk() (+28 more)

### Community 3 - "data_pull.py"
Cohesion: 0.16
Nodes (16): all_tickers(), Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe(), DataFrame, Path, Download daily OHLCV via yfinance and save to data/raw/., Turn ^VIX into VIX-index style names for files. (+8 more)

### Community 5 - "walkforward.py"
Cohesion: 0.25
Nodes (14): dataclasses, iter_walk_forward_folds(), purge_train(), DataFrame, DatetimeIndex, Timestamp, Walk-forward folds + label-window purge. - Expanding train window, fixed-length…, Small table describing folds (no model training). (+6 more)

### Community 6 - "features.py"
Cohesion: 0.09
Nodes (37): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+29 more)

### Community 7 - "config.py"
Cohesion: 0.22
Nodes (9): pandas, pathlib, Universe + path config for Pinky., label_columns(), Train-ready dataset: join features (X) + labels (y) on Date + Ticker., Label column names for one horizon or all., Labels vs SPY (architecture-locked). For each stock + date + horizon:…, Load saved raw parquet bars. (+1 more)

### Community 8 - "fundamentals.py"
Cohesion: 0.11
Nodes (37): add_accel(), add_yoy(), _asof_attach(), attach_growth_features(), _dates(), earnings_announcements(), first_filed(), growth_feature_frame() (+29 more)

### Community 9 - "load_dataset"
Cohesion: 0.27
Nodes (9): build_train_dataset(), load_dataset(), DataFrame, Path, Inner-join features and labels on Date + Ticker. Does not invent rows. Rows…, Write train-ready panel to parquet., Load saved train-ready dataset., save_dataset() (+1 more)

### Community 10 - "build_showcase.py"
Cohesion: 0.05
Nodes (84): math, between_years(), _cagr(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores(), monthly_rebalance_dates() (+76 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.08
Nodes (24): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read (+16 more)

### Community 12 - "product_numbers.py"
Cohesion: 0.07
Nodes (49): numpy, acquired_share(), brier_score(), calibration_table(), daily_rank_ic(), _monthly_dates(), precision_at_k(), DataFrame (+41 more)

### Community 17 - "Pinky"
Cohesion: 0.20
Nodes (10): Backtest defaults, Commands, Gotchas (learned the hard way), Key findings (summary), Pinky, Repo layout, ▶ Resume here (new chat: read this first), Roadmap (+2 more)

### Community 19 - "Pinky project history"
Cohesion: 0.11
Nodes (18): Bar to beat (v6_pit: Jan 2001 → Jan 2021; SPY +7.3%/yr, equal-weight universe +8.2%/yr), Data facts for Phase 2, First Claude chat (2026-10-05, Claude Opus 5.5), Four model fixes — v7_pit + ablations (2026-09-27), Honest baseline — v5_pit (2026-09-26), Key findings, Move to the Claude app (2026-10-04, user-approved), New yardstick — v6_pit (2026-09-26) (+10 more)

### Community 21 - "train.py"
Cohesion: 0.06
Nodes (57): Training (`pinky/train.py`, `pinky/walkforward.py`, `pinky/preprocess.py`), Decisions (full, as of 2026-10-03), Repo layout (full, as of 2026-10-03), State log (snapshot 2026-10-03), Runbook (done 2026-10-03; reuse for the next batch), Step 3 notes (company data batch 1 — plan locked 2026-10-03), Step 3 training runbook (v8 growth features), joblib (+49 more)

## Knowledge Gaps
- **71 isolated node(s):** `Agent instructions (Pinky)`, `Claude app notes`, `How it works`, `What's in git and what isn't`, `Quick start (local)` (+66 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 229 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Pinky` connect `Pinky` to `Pinky architecture`, `train.py`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Why does `dev_rows()` connect `train.py` to `check_growth_features.py`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Why does `Gotchas (learned the hard way)` connect `Pinky` to `fundamentals.py`, `walkforward.py`, `train.py`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **What connects `Agent instructions (Pinky)`, `Claude app notes`, `How it works` to the rest of the system?**
  _71 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pinky architecture` be split into smaller, more focused modules?**
  _Cohesion score 0.05263157894736842 - nodes in this community are weakly interconnected._
- **Should `check_growth_features.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14795008912655971 - nodes in this community are weakly interconnected._
- **Should `sharadar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07422402159244265 - nodes in this community are weakly interconnected._