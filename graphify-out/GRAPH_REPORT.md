# Graph Report - Pinky  (2026-10-05)

## Corpus Check
- 37 files · ~40,551 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .csv 3, .mdc 1)

## Summary
- 505 nodes · 1055 edges · 26 communities (23 shown, 3 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8330f573`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pinky PRD (Product Requirements Document)
- check_growth_features.py
- sharadar.py
- preprocess.py
- __init__.py
- walkforward.py
- features.py
- Pinky Architecture Plan
- fundamentals.py
- config.py
- build_showcase.py
- Walk-Forward Results
- metrics.py
- AGENTS.md
- step3_verdict.py
- Pinky Eval Checklist (v1)
- Pinky
- 5. In scope (v1)
- Metrics to report
- Pinky project history
- train.py
- run_horizon
- run_all
- score_group_table
- pit_training_frame
- Claude instructions (Pinky)

## God Nodes (most connected - your core abstractions)
1. `run_all()` - 17 edges
2. `run_backtest()` - 14 edges
3. `_backtest_lines()` - 14 edges
4. `build_data()` - 14 edges
5. `Pinky PRD (Product Requirements Document)` - 14 edges
6. `load_raw_ticker()` - 13 edges
7. `backtest_prices()` - 13 edges
8. `main()` - 13 edges
9. `Pinky project history` - 13 edges
10. `feature_columns()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Feature pipeline` --references--> `build_bfm_prediction_features()`  [INFERRED]
  docs/ARCHITECTURE.md → pinky/features.py
- `Step 2 notes (model fixes — done)` --references--> `cross_section_rank()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/preprocess.py
- `Step 3 notes (company data batch 1 — plan locked 2026-10-03)` --references--> `pit_training_frame()`  [INFERRED]
  docs/STEP3_RUNBOOK.md → pinky/train.py
- `Backtest defaults` --references--> `with_cost()`  [INFERRED]
  project.md → pinky/backtest.py
- `Gotchas (learned the hard way)` --references--> `first_filed()`  [INFERRED]
  project.md → pinky/fundamentals.py

## Import Cycles
- None detected.

## Communities (26 total, 3 thin omitted)

### Community 0 - "Pinky PRD (Product Requirements Document)"
Cohesion: 0.15
Nodes (13): 10. Milestones, 11. Risks, 12. Open decisions, 13. Related docs, 1. Problem, 2. Product goal, 3. Who it’s for, 4. What success looks like (+5 more)

### Community 1 - "check_growth_features.py"
Cohesion: 0.17
Nodes (26): datetime, pinky, feature_columns(), Numeric model inputs only (no ids, no labels)., check(), correlations(), coverage(), dataset_structure() (+18 more)

### Community 2 - "sharadar.py"
Cohesion: 0.12
Nodes (22): io, os, api_key(), bulk_status(), download_bulk(), pull_all(), DataFrame, Path (+14 more)

### Community 3 - "preprocess.py"
Cohesion: 0.26
Nodes (12): cross_section_rank(), cross_section_zscore(), drop_correlated_features(), prepare_fold_frames(), DataFrame, ranking_feature_cols(), Feature prep for ranking models. 1) Cross-sectional z-score or percentile rank…, Stock-differentiating features only (exclude pure macro/regime). (+4 more)

### Community 5 - "walkforward.py"
Cohesion: 0.11
Nodes (24): dataclasses, iter_walk_forward_folds(), purge_train(), DataFrame, DatetimeIndex, Timestamp, Walk-forward folds + label-window purge. - Expanding train window, fixed-length…, Small table describing folds (no model training). (+16 more)

### Community 6 - "features.py"
Cohesion: 0.09
Nodes (37): build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path, Series, Build tabular prediction features (v1). Architecture name:… (+29 more)

### Community 7 - "Pinky Architecture Plan"
Cohesion: 0.18
Nodes (11): Build order, Explicit non-goals (for now), Feature pipeline, Goal, Labels (truth the model learns), Locked decisions, Models, Pinky Architecture Plan (+3 more)

### Community 8 - "fundamentals.py"
Cohesion: 0.14
Nodes (28): Runbook (done 2026-10-03; reuse for the next batch), Step 3 notes (company data batch 1 — plan locked 2026-10-03), Step 3 training runbook (v8 growth features), add_accel(), add_yoy(), _asof_attach(), attach_growth_features(), _dates() (+20 more)

### Community 9 - "config.py"
Cohesion: 0.06
Nodes (45): pandas, pathlib, all_tickers(), Universe + path config for Pinky., Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe(), DataFrame (+37 more)

### Community 10 - "build_showcase.py"
Cohesion: 0.08
Nodes (49): json, math, between_years(), _cagr(), default_prices(), load_price_panel(), _max_drawdown(), monthly_rebalance_dates() (+41 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.08
Nodes (24): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read (+16 more)

### Community 12 - "metrics.py"
Cohesion: 0.11
Nodes (25): numpy, acquired_share(), brier_score(), calibration_table(), daily_rank_ic(), _monthly_dates(), DataFrame, DatetimeIndex (+17 more)

### Community 14 - "step3_verdict.py"
Cohesion: 0.07
Nodes (52): Index, precision_at_k(), Share of the model's top-k picks that end up in the future top decile. `frac`…, load(), acquisition_dates(), backtest_prices(), benchmark_closeadj(), build_panels() (+44 more)

### Community 15 - "Pinky Eval Checklist (v1)"
Cohesion: 0.25
Nodes (4): Fail conditions (do not ship / do not trust), Must-pass rules, Pass bar (first useful prototype), Pinky Eval Checklist (v1)

### Community 16 - "Pinky"
Cohesion: 0.25
Nodes (8): Current status, Design principles, Disclaimer, How it works (high level), Pinky, Quick start (local), What it does, What’s public vs private

### Community 17 - "5. In scope (v1)"
Cohesion: 0.29
Nodes (7): 5. In scope (v1), Data, Delivery (v1), Features, Labels, Models, Validation

### Community 18 - "Metrics to report"
Cohesion: 0.40
Nodes (5): Basket vs SPY, Honesty checks, Metrics to report, Probability calibration (beat model), Ranking quality

### Community 19 - "Pinky project history"
Cohesion: 0.12
Nodes (15): Bar to beat (v6_pit: Jan 2001 → Jan 2021; SPY +7.3%/yr, equal-weight universe +8.2%/yr), Data facts for Phase 2, Four model fixes — v7_pit + ablations (2026-09-27), Honest baseline — v5_pit (2026-09-26), Key findings, Move to the Claude app (2026-10-04, user-approved), New yardstick — v6_pit (2026-09-26), Old 128-stock results (inflated by survivorship + hindsight) (+7 more)

### Community 20 - "train.py"
Cohesion: 0.18
Nodes (13): joblib, lightgbm, momentum_scores(), Naive baseline: score = trailing 12m return (skip last month), same dates/names…, Mean daily rank IC computed inside each sector (does the model rank within a…, within_sector_ic(), _backtest_lines(), _fmt_pct() (+5 more)

### Community 21 - "run_horizon"
Cohesion: 0.21
Nodes (13): Decisions (full, as of 2026-10-03), dev_rows(), _eval_prepared(), _fit_beat_models(), _fit_return_models(), DataFrame, DatetimeIndex, Rows whose label window ends before HOLDOUT_START, so the holdout stays unseen. (+5 more)

### Community 22 - "run_all"
Cohesion: 0.21
Nodes (12): _pit_universe_desc(), _prep_desc(), Path, Series, _ranking_lines(), Does the model find the future top decile / the year's biggest winners?, Rebuild a pit run's report from its saved metrics + predictions (no retraining)., Run walk-forward training. Default focus: 1y. `exclude` drops tickers from… (+4 more)

### Community 23 - "score_group_table"
Cohesion: 0.40
Nodes (5): State log (snapshot 2026-10-03), What each score group did next: shows where a model's ranking skill sits. Every…, score_group_table(), Where the ranking skill sits: what each score group did next., _score_group_lines()

### Community 24 - "pit_training_frame"
Cohesion: 0.50
Nodes (5): Repo layout (full, as of 2026-10-03), Placebo: give each row another same-date row's six growth values (block kept…, shuffle_growth_within_date(), pit_training_frame(), Pit dataset → model frame for the given fixes (placebo shuffle before ranking).

## Knowledge Gaps
- **79 isolated node(s):** `Agent instructions (Pinky)`, `Claude app notes`, `What it does`, `How it works (high level)`, `What’s public vs private` (+74 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 236 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_bfm_prediction_features()` connect `features.py` to `Pinky Architecture Plan`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Why does `Pinky Architecture Plan` connect `Pinky Architecture Plan` to `Pinky Eval Checklist (v1)`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `Feature pipeline` connect `Pinky Architecture Plan` to `features.py`?**
  _High betweenness centrality (0.169) - this node is a cross-community bridge._
- **What connects `Agent instructions (Pinky)`, `Claude app notes`, `What it does` to the rest of the system?**
  _79 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `sharadar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11956521739130435 - nodes in this community are weakly interconnected._
- **Should `walkforward.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._
- **Should `features.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08846153846153847 - nodes in this community are weakly interconnected._