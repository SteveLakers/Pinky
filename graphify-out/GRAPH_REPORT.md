# Graph Report - Pinky  (2026-10-06)

## Corpus Check
- 38 files · ~42,422 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .csv 3, .mdc 1)

## Summary
- 504 nodes · 1086 edges · 22 communities (18 shown, 4 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 17 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5a42971f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky PRD (product requirements)
- check_growth_features.py
- sharadar.py
- build_showcase.py
- __init__.py
- dataset.py
- config.py
- Pinky architecture
- fundamentals.py
- step3_verdict.py
- train.py
- Walk-Forward Results
- product_numbers.py
- AGENTS.md
- universe.py
- Pinky
- Pinky
- Pinky evaluation rules
- Pinky project history
- dev_rows
- Claude instructions (Pinky)

## God Nodes (most connected - your core abstractions)
1. `run_all()` - 17 edges
2. `run_backtest()` - 16 edges
3. `backtest_prices()` - 15 edges
4. `Pinky project history` - 15 edges
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
- `Repo layout (full, as of 2026-10-03)` --references--> `dev_rows()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/train.py

## Import Cycles
- None detected.

## Communities (22 total, 4 thin omitted)

### Community 0 - "Pinky PRD (product requirements)"
Cohesion: 0.20
Nodes (10): 1. Problem, 2. Goal, 3. User, 4. Constraints, 5. Requirements, 6. Out of scope, 7. Success, 8. Risks (+2 more)

### Community 1 - "check_growth_features.py"
Cohesion: 0.18
Nodes (24): datetime, pinky, check(), correlations(), coverage(), dataset_structure(), _day_ranks(), hand_checks() (+16 more)

### Community 2 - "sharadar.py"
Cohesion: 0.12
Nodes (22): io, os, api_key(), bulk_status(), download_bulk(), pull_all(), DataFrame, Path (+14 more)

### Community 3 - "build_showcase.py"
Cohesion: 0.16
Nodes (20): Ticker -> Sharadar sector (current classification) for every eligible stock., sector_map(), build_data(), buyout_split(), equity_curve(), main(), make_curve(), max_drawdown() (+12 more)

### Community 5 - "dataset.py"
Cohesion: 0.08
Nodes (41): dataclasses, build_train_dataset(), feature_columns(), label_columns(), load_dataset(), DataFrame, Path, Train-ready dataset: join features (X) + labels (y) on Date + Ticker. (+33 more)

### Community 6 - "config.py"
Cohesion: 0.06
Nodes (58): pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe(), DataFrame (+50 more)

### Community 7 - "Pinky architecture"
Cohesion: 0.20
Nodes (10): Backtest (`pinky/backtest.py`), Data (Sharadar Core US Equities Bundle), Dataset (`pinky/pit_dataset.py`), Goal, Legacy (not used by `--pit` runs), Locked decisions, Outputs (`artifacts/`, `models/`; never in git), Pinky architecture (+2 more)

### Community 8 - "fundamentals.py"
Cohesion: 0.12
Nodes (33): Repo layout (full, as of 2026-10-03), Runbook (done 2026-10-03; reuse for the next batch), Step 3 notes (company data batch 1 — plan locked 2026-10-03), Step 3 training runbook (v8 growth features), add_accel(), add_yoy(), _asof_attach(), attach_growth_features() (+25 more)

### Community 9 - "step3_verdict.py"
Cohesion: 0.25
Nodes (17): ic_halves(), main(), mean_stat(), monthly_gap(), needed_runs(), nw_se(), pct(), periods() (+9 more)

### Community 10 - "train.py"
Cohesion: 0.06
Nodes (68): joblib, lightgbm, math, between_years(), _cagr(), default_prices(), load_price_panel(), _max_drawdown() (+60 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.08
Nodes (24): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read (+16 more)

### Community 12 - "product_numbers.py"
Cohesion: 0.07
Nodes (46): State log (snapshot 2026-10-03), json, acquired_share(), brier_score(), calibration_table(), _monthly_dates(), precision_at_k(), DataFrame (+38 more)

### Community 14 - "universe.py"
Cohesion: 0.10
Nodes (34): Index, numpy, build_pit_dataset(), load_pit_dataset(), _log_market_cap(), DataFrame, DatetimeIndex, Path (+26 more)

### Community 16 - "Pinky"
Cohesion: 0.40
Nodes (5): Disclaimer, How it works, Pinky, Quick start (local), What's in git and what isn't

### Community 17 - "Pinky"
Cohesion: 0.20
Nodes (10): Backtest defaults, Commands, Gotchas (learned the hard way), Key findings (summary), Pinky, Repo layout, ▶ Resume here (new chat: read this first), Roadmap (+2 more)

### Community 18 - "Pinky evaluation rules"
Cohesion: 0.25
Nodes (8): Honesty rules (every run), How big is noise?, Keep rule for new data (locked 2026-10-03), Pinky evaluation rules, Scoreboard (shown every time; never decides), Stop and audit if, What every report shows, What success means

### Community 19 - "Pinky project history"
Cohesion: 0.11
Nodes (17): Bar to beat (v6_pit: Jan 2001 → Jan 2021; SPY +7.3%/yr, equal-weight universe +8.2%/yr), Data facts for Phase 2, First Claude chat (2026-10-05, Claude Opus 5.5), Four model fixes — v7_pit + ablations (2026-09-27), Honest baseline — v5_pit (2026-09-26), Key findings, Move to the Claude app (2026-10-04, user-approved), New yardstick — v6_pit (2026-09-26) (+9 more)

### Community 21 - "dev_rows"
Cohesion: 0.33
Nodes (6): Training (`pinky/train.py`, `pinky/walkforward.py`, `pinky/preprocess.py`), Decisions (full, as of 2026-10-03), dev_rows(), DatetimeIndex, Rows whose label window ends before HOLDOUT_START, so the holdout stays unseen., Decisions

## Knowledge Gaps
- **70 isolated node(s):** `Agent instructions (Pinky)`, `Claude app notes`, `How it works`, `What's in git and what isn't`, `Quick start (local)` (+65 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 228 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Pinky` connect `Pinky` to `dev_rows`, `README.md`?**
  _High betweenness centrality (0.175) - this node is a cross-community bridge._
- **Why does `dev_rows()` connect `dev_rows` to `fundamentals.py`, `check_growth_features.py`, `train.py`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `Gotchas (learned the hard way)` connect `Pinky` to `fundamentals.py`, `train.py`, `dataset.py`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **What connects `Agent instructions (Pinky)`, `Claude app notes`, `How it works` to the rest of the system?**
  _70 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `sharadar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11956521739130435 - nodes in this community are weakly interconnected._
- **Should `dataset.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0782608695652174 - nodes in this community are weakly interconnected._
- **Should `config.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05827505827505827 - nodes in this community are weakly interconnected._