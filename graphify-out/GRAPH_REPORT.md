# Graph Report - Pinky  (2026-10-21)

## Corpus Check
- 47 files · ~62,184 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .csv 3, .mdc 1)

## Summary
- 656 nodes · 1534 edges · 27 communities (23 shown, 4 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 26 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `780deef2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Growth round 2 plan (DRAFT)
- check_growth_features.py
- sharadar.py
- check_growth2_features.py
- __init__.py
- shap_report.py
- build_showcase.py
- step3_verdict.py
- fundamentals.py
- Pinky PRD (product requirements)
- backtest.py
- Walk-Forward Results
- metrics.py
- AGENTS.md
- universe.py
- train.py
- compare_runs.py
- pandas
- feature_columns
- Pinky project history
- Batch 2 plan: margin expansion
- Pinky evaluation rules
- Pinky architecture
- Pinky
- Claude instructions (Pinky)
- Pinky

## God Nodes (most connected - your core abstractions)
1. `run_all()` - 21 edges
2. `benchmark_closeadj()` - 21 edges
3. `dev_rows()` - 20 edges
4. `Pinky project history` - 19 edges
5. `feature_columns()` - 18 edges
6. `pit_training_frame()` - 17 edges
7. `run_backtest()` - 16 edges
8. `backtest_prices()` - 15 edges
9. `_backtest_lines()` - 14 edges
10. `iter_walk_forward_folds()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Batch 2 code: margins (2026-10-16, Claude Opus 5.5)` --references--> `shuffle_within_date()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/fundamentals.py
- `Step 2 notes (model fixes — done)` --references--> `cross_section_rank()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/preprocess.py
- `Decisions` --references--> `dev_rows()`  [INFERRED]
  project.md → pinky/train.py
- `Gotchas (learned the hard way)` --references--> `first_filed()`  [INFERRED]
  project.md → pinky/fundamentals.py
- `Repo layout (full, as of 2026-10-03)` --references--> `shuffle_growth_within_date()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/fundamentals.py

## Import Cycles
- None detected.

## Communities (27 total, 4 thin omitted)

### Community 0 - "Growth round 2 plan (DRAFT)"
Cohesion: 0.18
Nodes (12): Training (`pinky/train.py`, `pinky/walkforward.py`, `pinky/preprocess.py`), Candidate ideas (pick 2–3 before any results), Code checks (2026-10-21, before any run), Decisions for the user (asked 2026-10-19), Design (pinned 2026-10-21, before any code ran on results), Growth round 2 plan (DRAFT), Recommendation, Runbook (only after the user says `run`; one test at a time) (+4 more)

### Community 1 - "check_growth_features.py"
Cohesion: 0.11
Nodes (46): datetime, Runbook (done 2026-10-03; reuse for the next batch), Step 3 notes (company data batch 1 — plan locked 2026-10-03), Step 3 training runbook (v8 growth features), pinky, pit_training_frame(), Pit dataset → model frame for the given fixes (placebo shuffle before ranking)., check() (+38 more)

### Community 2 - "sharadar.py"
Cohesion: 0.08
Nodes (34): Decimal, Index, io, os, api_key(), bulk_status(), download_bulk(), load() (+26 more)

### Community 3 - "check_growth2_features.py"
Cohesion: 0.19
Nodes (25): bisect, calendar, _back(), check(), correlations(), coverage_and_values(), dataset_structure(), hand_checks() (+17 more)

### Community 5 - "shap_report.py"
Cohesion: 0.10
Nodes (30): Decisions (full, as of 2026-10-03), Moved from project.md (2026-10-21 trim, user-approved), Repo layout (full, as of 2026-10-03), joblib, numpy, load_pit_dataset(), dev_rows(), Rows whose label window ends before HOLDOUT_START, so the holdout stays unseen. (+22 more)

### Community 6 - "build_showcase.py"
Cohesion: 0.11
Nodes (33): between_years(), default_prices(), load_price_panel(), momentum_scores(), pick_sector_share(), DataFrame, Holding periods that start in [first, last] (either end open)., Same trades re-priced at another cost level (picks and turnover don't depend on… (+25 more)

### Community 7 - "step3_verdict.py"
Cohesion: 0.14
Nodes (29): has_run(), main(), needed_runs(), Verdict for a company-data batch (batch 2 on): does each feature set earn its…, seeded(), build_input(), monthly_returns(), DataFrame (+21 more)

### Community 8 - "fundamentals.py"
Cohesion: 0.08
Nodes (65): add_accel(), add_change(), add_reaction(), add_sue(), add_up_quarters(), add_yoy(), _asof_attach(), attach_growth2_features() (+57 more)

### Community 9 - "Pinky PRD (product requirements)"
Cohesion: 0.20
Nodes (10): 1. Problem, 2. Goal, 3. User, 4. Constraints, 5. Requirements, 6. Out of scope, 7. Success, 8. Risks (+2 more)

### Community 10 - "backtest.py"
Cohesion: 0.18
Nodes (19): math, _cagr(), _max_drawdown(), monthly_rebalance_dates(), _next_day(), _period_end(), pick_top(), DatetimeIndex (+11 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.08
Nodes (25): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read (+17 more)

### Community 12 - "metrics.py"
Cohesion: 0.12
Nodes (24): acquired_share(), brier_score(), calibration_table(), daily_rank_ic(), _monthly_dates(), DataFrame, DatetimeIndex, ndarray (+16 more)

### Community 14 - "universe.py"
Cohesion: 0.13
Nodes (26): backtest_prices(), build_panels(), eligible_tickers(), load_panel(), DataFrame, Point-in-time liquid US stock universe from Sharadar (survivorship-free). A…, Delisting-aware total-return index (Date x Ticker). - While listed: adjusted…, Delisting-aware total-return panel plus a SPY column, for… (+18 more)

### Community 15 - "train.py"
Cohesion: 0.09
Nodes (39): State log (snapshot 2026-10-03), json, lightgbm, What each score group did next: shows where a model's ranking skill sits. Every…, score_group_table(), _eval_prepared(), _fit_beat_models(), _fit_return_models() (+31 more)

### Community 16 - "compare_runs.py"
Cohesion: 0.22
Nodes (12): precision_at_k(), Share of the model's top-k picks that end up in the future top decile. `frac`…, acquisition_dates(), Ticker -> completion date of its acquisition (Sharadar `acquisitionby`; first…, main(), _pct(), DataFrame, Series (+4 more)

### Community 17 - "pandas"
Cohesion: 0.06
Nodes (57): pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe(), DataFrame (+49 more)

### Community 18 - "feature_columns"
Cohesion: 0.08
Nodes (41): dataclasses, build_train_dataset(), feature_columns(), label_columns(), load_dataset(), DataFrame, Path, Train-ready dataset: join features (X) + labels (y) on Date + Ticker. (+33 more)

### Community 19 - "Pinky project history"
Cohesion: 0.08
Nodes (24): Bar to beat (v6_pit: Jan 2001 → Jan 2021; SPY +7.3%/yr, equal-weight universe +8.2%/yr), Batch 2 code: margins (2026-10-16, Claude Opus 5.5), Batch 2 decisions (2026-10-09, Claude Opus 5.5), Batch 2 results: margins (2026-10-19, Claude Opus 5.5), Claude and plugin setup (moved from project.md 2026-10-12, unchanged), Data facts for Phase 2, First Claude chat (2026-10-05, Claude Opus 5.5), Four model fixes — v7_pit + ablations (2026-09-27) (+16 more)

### Community 20 - "Batch 2 plan: margin expansion"
Cohesion: 0.20
Nodes (9): After the runs (info only, not gates), Batch 2 plan: margin expansion, Code (before any run), Code checks (2026-10-16), Features (new opt-in group `margins`, 4 columns), Goal, Keep rule (locked; user-approved 2026-10-09), Runbook (only after the user says `run`) (+1 more)

### Community 21 - "Pinky evaluation rules"
Cohesion: 0.25
Nodes (8): Honesty rules (every run), How big is noise?, Keep rule for new data (locked 2026-10-03), Pinky evaluation rules, Scoreboard (shown every time; never decides), Stop and audit if, What every report shows, What success means

### Community 23 - "Pinky architecture"
Cohesion: 0.20
Nodes (10): Backtest (`pinky/backtest.py`), Data (Sharadar Core US Equities Bundle), Dataset (`pinky/pit_dataset.py`), Goal, Legacy (not used by `--pit` runs), Locked decisions, Outputs (`artifacts/`, `models/`; never in git), Pinky architecture (+2 more)

### Community 24 - "Pinky"
Cohesion: 0.40
Nodes (5): Disclaimer, How it works, Pinky, Quick start (local), What's in git and what isn't

### Community 26 - "Pinky"
Cohesion: 0.20
Nodes (10): Backtest defaults, Decisions, Gotchas (learned the hard way), Key findings (summary), Pinky, Repo layout, ▶ Resume here (new chat: read this first), Roadmap (+2 more)

## Knowledge Gaps
- **88 isolated node(s):** `Agent instructions (Pinky)`, `Claude app notes`, `How it works`, `What's in git and what isn't`, `Quick start (local)` (+83 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 279 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `dev_rows()` connect `shap_report.py` to `Growth round 2 plan (DRAFT)`, `check_growth_features.py`, `check_growth2_features.py`, `train.py`, `Pinky`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `Pinky` connect `Pinky` to `Growth round 2 plan (DRAFT)`, `README.md`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Why does `Gotchas (learned the hard way)` connect `Pinky` to `fundamentals.py`, `feature_columns`, `train.py`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `run_all()` (e.g. with `Moved from project.md (2026-10-21 trim, user-approved)` and `Gotchas (learned the hard way)`) actually correct?**
  _`run_all()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `dev_rows()` (e.g. with `Training (`pinky/train.py`, `pinky/walkforward.py`, `pinky/preprocess.py`)` and `Decisions (full, as of 2026-10-03)`) actually correct?**
  _`dev_rows()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Agent instructions (Pinky)`, `Claude app notes`, `How it works` to the rest of the system?**
  _88 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `check_growth_features.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10552061495457722 - nodes in this community are weakly interconnected._