# Graph Report - Pinky  (2026-10-21)

## Corpus Check
- 48 files · ~64,752 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .csv 3, .mdc 1)

## Summary
- 695 nodes · 1660 edges · 31 communities (27 shown, 4 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c7326aae`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Growth round 2 plan (DRAFT)
- check_growth_features.py
- sharadar.py
- check_growth2_features.py
- __init__.py
- universe.py
- feature_columns
- step3_verdict.py
- fundamentals.py
- Pinky PRD (product requirements)
- check_review_fixes.py
- Walk-Forward Results
- train.py
- AGENTS.md
- product_numbers.py
- rewrite_summary
- score_group_table
- pandas
- walkforward.py
- Pinky project history
- Batch 2 plan: margin expansion
- Pinky evaluation rules
- dataset.py
- Pinky
- Claude instructions (Pinky)
- run_all
- shap_report.py
- Pinky
- Pinky architecture
- Step 3 training runbook (v8 growth features)

## God Nodes (most connected - your core abstractions)
1. `run_all()` - 23 edges
2. `benchmark_closeadj()` - 21 edges
3. `run_backtest()` - 20 edges
4. `dev_rows()` - 20 edges
5. `Pinky project history` - 19 edges
6. `feature_columns()` - 18 edges
7. `summarize_backtest()` - 17 edges
8. `pit_training_frame()` - 17 edges
9. `backtest_prices()` - 17 edges
10. `tradeable_panel()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Batch 2 code: margins (2026-10-16, Claude Opus 5.5)` --references--> `shuffle_within_date()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/fundamentals.py
- `Step 2 notes (model fixes — done)` --references--> `cross_section_rank()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/preprocess.py
- `Decisions (full, as of 2026-10-03)` --references--> `dev_rows()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/train.py
- `Decisions` --references--> `dev_rows()`  [INFERRED]
  project.md → pinky/train.py
- `Step 3 notes (company data batch 1 — plan locked 2026-10-03)` --references--> `pit_training_frame()`  [INFERRED]
  docs/STEP3_RUNBOOK.md → pinky/train.py

## Import Cycles
- None detected.

## Communities (31 total, 4 thin omitted)

### Community 0 - "Growth round 2 plan (DRAFT)"
Cohesion: 0.16
Nodes (13): Training (`pinky/train.py`, `pinky/walkforward.py`, `pinky/preprocess.py`), Candidate ideas (pick 2–3 before any results), Code checks (2026-10-21, before any run), Code review fixes (2026-10-21, before any round 2 run), Decisions for the user (asked 2026-10-19), Design (pinned 2026-10-21, before any code ran on results), Growth round 2 plan (DRAFT), Recommendation (+5 more)

### Community 1 - "check_growth_features.py"
Cohesion: 0.13
Nodes (40): datetime, pinky, check(), correlations(), coverage(), dataset_structure(), _day_ranks(), hand_checks() (+32 more)

### Community 2 - "sharadar.py"
Cohesion: 0.09
Nodes (30): Decimal, io, os, api_key(), bulk_status(), download_bulk(), _get(), pull_all() (+22 more)

### Community 3 - "check_growth2_features.py"
Cohesion: 0.19
Nodes (25): bisect, calendar, _back(), check(), correlations(), coverage_and_values(), dataset_structure(), hand_checks() (+17 more)

### Community 5 - "universe.py"
Cohesion: 0.07
Nodes (47): Backtest (`pinky/backtest.py`), Index, numpy, build_pit_dataset(), load_pit_dataset(), _log_market_cap(), DataFrame, DatetimeIndex (+39 more)

### Community 6 - "feature_columns"
Cohesion: 0.23
Nodes (14): feature_columns(), Numeric model inputs only (no ids, no labels)., cross_section_rank(), cross_section_zscore(), drop_correlated_features(), prepare_fold_frames(), DataFrame, ranking_feature_cols() (+6 more)

### Community 7 - "step3_verdict.py"
Cohesion: 0.14
Nodes (30): has_run(), main(), needed_runs(), Verdict for a company-data batch (batch 2 on): does each feature set earn its…, seeded(), backtest_id(), ic_halves(), main() (+22 more)

### Community 8 - "fundamentals.py"
Cohesion: 0.10
Nodes (54): add_accel(), add_change(), add_reaction(), add_sue(), add_up_quarters(), add_yoy(), _asof_attach(), attach_growth2_features() (+46 more)

### Community 9 - "Pinky PRD (product requirements)"
Cohesion: 0.20
Nodes (10): 1. Problem, 2. Goal, 3. User, 4. Constraints, 5. Requirements, 6. Out of scope, 7. Success, 8. Risks (+2 more)

### Community 10 - "check_review_fixes.py"
Cohesion: 0.06
Nodes (76): math, between_years(), _cagr(), _daily_drawdown(), default_prices(), load_price_panel(), _max_drawdown(), momentum_scores() (+68 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.08
Nodes (25): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read (+17 more)

### Community 12 - "train.py"
Cohesion: 0.13
Nodes (23): lightgbm, brier_score(), calibration_table(), ndarray, Reliability-style bins: predicted prob vs realized frequency., Mean realized beat-rate among top predicted names each day., Equal-weight all-names excess each day, then average., _safe_spearman() (+15 more)

### Community 14 - "product_numbers.py"
Cohesion: 0.09
Nodes (35): acquired_share(), _monthly_dates(), precision_at_k(), DataFrame, DatetimeIndex, Series, Evaluation metrics for walk-forward reports (honest, no fake scores)., Share of the monthly top picks whose company is acquired within `days` of the… (+27 more)

### Community 15 - "rewrite_summary"
Cohesion: 0.21
Nodes (12): _pit_universe_desc(), Path, Series, _ranking_lines(), Every fold's models → models/<run>/<horizon>/fold_NN/, plus folds.json (fold…, Does the model find the future top decile / the year's biggest winners?, Files a report rebuild overwrites (summary, stats, monthly returns, score…, Re-score a pit run from its saved metrics + predictions (no retraining). Uses… (+4 more)

### Community 16 - "score_group_table"
Cohesion: 0.33
Nodes (6): State log (snapshot 2026-10-03), What each score group did next: shows where a model's ranking skill sits. Every…, score_group_table(), _fmt_pct(), Where the ranking skill sits: what each score group did next., _score_group_lines()

### Community 17 - "pandas"
Cohesion: 0.05
Nodes (64): pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe(), DataFrame (+56 more)

### Community 18 - "walkforward.py"
Cohesion: 0.21
Nodes (15): dataclasses, iter_walk_forward_folds(), purge_train(), DataFrame, DatetimeIndex, Timestamp, Walk-forward folds + label-window purge. - Expanding train window, fixed-length…, Small table describing folds (no model training). (+7 more)

### Community 19 - "Pinky project history"
Cohesion: 0.08
Nodes (25): Bar to beat (v6_pit: Jan 2001 → Jan 2021; SPY +7.3%/yr, equal-weight universe +8.2%/yr), Batch 2 code: margins (2026-10-16, Claude Opus 5.5), Batch 2 decisions (2026-10-09, Claude Opus 5.5), Batch 2 results: margins (2026-10-19, Claude Opus 5.5), Claude and plugin setup (moved from project.md 2026-10-12, unchanged), Data facts for Phase 2, Decisions (full, as of 2026-10-03), First Claude chat (2026-10-05, Claude Opus 5.5) (+17 more)

### Community 20 - "Batch 2 plan: margin expansion"
Cohesion: 0.20
Nodes (9): After the runs (info only, not gates), Batch 2 plan: margin expansion, Code (before any run), Code checks (2026-10-16), Features (new opt-in group `margins`, 4 columns), Goal, Keep rule (locked; user-approved 2026-10-09), Runbook (only after the user says `run`) (+1 more)

### Community 21 - "Pinky evaluation rules"
Cohesion: 0.25
Nodes (8): Honesty rules (every run), How big is noise?, Keep rule for new data (locked 2026-10-03), Pinky evaluation rules, Scoreboard (shown every time; never decides), Stop and audit if, What every report shows, What success means

### Community 23 - "dataset.py"
Cohesion: 0.21
Nodes (12): build_train_dataset(), label_columns(), load_dataset(), DataFrame, Path, Train-ready dataset: join features (X) + labels (y) on Date + Ticker., Label column names for one horizon or all., Inner-join features and labels on Date + Ticker. Does not invent rows. Rows… (+4 more)

### Community 24 - "Pinky"
Cohesion: 0.40
Nodes (5): Disclaimer, How it works, Pinky, Quick start (local), What's in git and what isn't

### Community 26 - "run_all"
Cohesion: 0.17
Nodes (16): Moved from project.md (2026-10-21 trim, user-approved), Repo layout (full, as of 2026-10-03), dev_rows(), pit_tag(), pit_training_frame(), placebo_group(), _prep_desc(), DatetimeIndex (+8 more)

### Community 27 - "shap_report.py"
Cohesion: 0.21
Nodes (12): joblib, json, explain_fold(), explain_runs(), family_of(), DataFrame, ndarray, Per run x fold x input/family numbers; runs that share inputs share one rebuild. (+4 more)

### Community 28 - "Pinky"
Cohesion: 0.20
Nodes (10): Backtest defaults, Decisions, Gotchas (learned the hard way), Key findings (summary), Pinky, Repo layout, ▶ Resume here (new chat: read this first), Roadmap (+2 more)

### Community 29 - "Pinky architecture"
Cohesion: 0.22
Nodes (9): Data (Sharadar Core US Equities Bundle), Dataset (`pinky/pit_dataset.py`), Goal, Legacy (not used by `--pit` runs), Locked decisions, Outputs (`artifacts/`, `models/`; never in git), Pinky architecture, Pipeline (+1 more)

### Community 30 - "Step 3 training runbook (v8 growth features)"
Cohesion: 0.50
Nodes (3): Runbook (done 2026-10-03; reuse for the next batch), Step 3 notes (company data batch 1 — plan locked 2026-10-03), Step 3 training runbook (v8 growth features)

## Knowledge Gaps
- **88 isolated node(s):** `Agent instructions (Pinky)`, `Claude app notes`, `How it works`, `What's in git and what isn't`, `Quick start (local)` (+83 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 297 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `dev_rows()` connect `run_all` to `Growth round 2 plan (DRAFT)`, `check_growth_features.py`, `check_growth2_features.py`, `universe.py`, `train.py`, `Pinky project history`, `shap_report.py`, `Pinky`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Why does `Pinky` connect `Pinky` to `Growth round 2 plan (DRAFT)`, `README.md`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `Pinky architecture` connect `Pinky architecture` to `Growth round 2 plan (DRAFT)`, `universe.py`, `README.md`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `run_all()` (e.g. with `Moved from project.md (2026-10-21 trim, user-approved)` and `Gotchas (learned the hard way)`) actually correct?**
  _`run_all()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Agent instructions (Pinky)`, `Claude app notes`, `How it works` to the rest of the system?**
  _88 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `check_growth_features.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1322849213691027 - nodes in this community are weakly interconnected._
- **Should `sharadar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08712121212121213 - nodes in this community are weakly interconnected._