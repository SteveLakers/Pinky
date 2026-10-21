# Graph Report - Pinky  (2026-10-21)

## Corpus Check
- 49 files · ~66,758 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .csv 3, .mdc 1)

## Summary
- 712 nodes · 1708 edges · 33 communities (30 shown, 3 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 39 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3ddb96e0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Growth round 2 plan (DRAFT)
- check_growth2_features.py
- sharadar.py
- data_pull.py
- __init__.py
- universe.py
- preprocess.py
- step3_verdict.py
- fundamentals.py
- Pinky PRD (product requirements)
- check_review_fixes.py
- Walk-Forward Results
- metrics.py
- AGENTS.md
- compare_runs.py
- rewrite_summary
- score_group_table
- features.py
- dataset.py
- dev_rows
- Batch 2 plan: margin expansion
- Pinky evaluation rules
- README.md
- run_horizon
- Key findings
- Claude instructions (Pinky)
- train.py
- shap_report.py
- Pinky
- Pinky architecture
- Step 3 training runbook (v8 growth features)
- Batch 2 decisions (2026-10-09, Claude Opus 5.5)
- train_walkforward.py

## God Nodes (most connected - your core abstractions)
1. `run_all()` - 23 edges
2. `benchmark_closeadj()` - 21 edges
3. `run_backtest()` - 20 edges
4. `dev_rows()` - 20 edges
5. `Pinky project history` - 19 edges
6. `summarize_backtest()` - 18 edges
7. `feature_columns()` - 18 edges
8. `pit_training_frame()` - 17 edges
9. `backtest_prices()` - 17 edges
10. `tradeable_panel()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `2. High: reported maximum drawdown understates daily losses` --references--> `summarize_backtest()`  [INFERRED]
  docs/CODE_REVIEW_2026-10-21.md → pinky/backtest.py
- `Batch 2 code: margins (2026-10-16, Claude Opus 5.5)` --references--> `shuffle_within_date()`  [INFERRED]
  docs/PROJECT_HISTORY.md → pinky/fundamentals.py
- `Decisions` --references--> `dev_rows()`  [INFERRED]
  project.md → pinky/train.py
- `Step 3 notes (company data batch 1 — plan locked 2026-10-03)` --references--> `pit_training_frame()`  [INFERRED]
  docs/STEP3_RUNBOOK.md → pinky/train.py
- `1. High: synthetic delisting prices are accepted as new trade fills` --references--> `total_return_panel()`  [INFERRED]
  docs/CODE_REVIEW_2026-10-21.md → pinky/universe.py

## Import Cycles
- None detected.

## Communities (33 total, 3 thin omitted)

### Community 0 - "Growth round 2 plan (DRAFT)"
Cohesion: 0.16
Nodes (13): Training (`pinky/train.py`, `pinky/walkforward.py`, `pinky/preprocess.py`), Candidate ideas (pick 2–3 before any results), Code checks (2026-10-21, before any run), Code review fixes (2026-10-21, before any round 2 run), Decisions for the user (asked 2026-10-19), Design (pinned 2026-10-21, before any code ran on results), Growth round 2 plan (DRAFT), Recommendation (+5 more)

### Community 1 - "check_growth2_features.py"
Cohesion: 0.08
Nodes (74): bisect, calendar, datetime, pinky, feature_columns(), Numeric model inputs only (no ids, no labels)., pit_training_frame(), Pit dataset → model frame for the given fixes (placebo shuffle before ranking). (+66 more)

### Community 2 - "sharadar.py"
Cohesion: 0.08
Nodes (32): 1. High: synthetic delisting prices are accepted as new trade fills, 2. High: reported maximum drawdown understates daily losses, 3. Medium: RSI drops valid stocks after uninterrupted rises or flat prices, 4. Medium: malformed PIT flags silently launch the legacy path, 5. Medium: an API error can expose the API key, Code review — 2026-10-21, Findings, in priority order, Verification and limits (+24 more)

### Community 3 - "data_pull.py"
Cohesion: 0.16
Nodes (16): all_tickers(), Unique tickers to download (stocks + benchmark + helpers)., download_ticker(), pull_universe(), DataFrame, Path, Download daily OHLCV via yfinance and save to data/raw/., Turn ^VIX into VIX-index style names for files. (+8 more)

### Community 5 - "universe.py"
Cohesion: 0.06
Nodes (60): Index, numpy, pandas, pathlib, Universe + path config for Pinky., build_pit_dataset(), load_pit_dataset(), _log_market_cap() (+52 more)

### Community 6 - "preprocess.py"
Cohesion: 0.23
Nodes (13): Step 2 notes (model fixes — done), cross_section_rank(), cross_section_zscore(), drop_correlated_features(), prepare_fold_frames(), DataFrame, ranking_feature_cols(), Feature prep for ranking models. 1) Cross-sectional z-score or percentile rank… (+5 more)

### Community 7 - "step3_verdict.py"
Cohesion: 0.09
Nodes (43): Decimal, json, re, has_run(), main(), needed_runs(), Verdict for a company-data batch (batch 2 on): does each feature set earn its…, seeded() (+35 more)

### Community 8 - "fundamentals.py"
Cohesion: 0.10
Nodes (55): Risks requiring further evidence, add_accel(), add_change(), add_reaction(), add_sue(), add_up_quarters(), add_yoy(), _asof_attach() (+47 more)

### Community 9 - "Pinky PRD (product requirements)"
Cohesion: 0.20
Nodes (10): 1. Problem, 2. Goal, 3. User, 4. Constraints, 5. Requirements, 6. Out of scope, 7. Success, 8. Risks (+2 more)

### Community 10 - "check_review_fixes.py"
Cohesion: 0.06
Nodes (73): math, between_years(), _cagr(), _daily_drawdown(), _max_drawdown(), momentum_scores(), monthly_rebalance_dates(), _next_day() (+65 more)

### Community 11 - "Walk-Forward Results"
Cohesion: 0.08
Nodes (25): Data checks done, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read, Honest read (+17 more)

### Community 12 - "metrics.py"
Cohesion: 0.19
Nodes (15): brier_score(), calibration_table(), DataFrame, ndarray, Evaluation metrics for walk-forward reports (honest, no fake scores)., Reliability-style bins: predicted prob vs realized frequency., Mean realized beat-rate among top predicted names each day., Mean equal-weight excess of top-N predicted names each day. (+7 more)

### Community 14 - "compare_runs.py"
Cohesion: 0.15
Nodes (18): acquired_share(), _monthly_dates(), precision_at_k(), DatetimeIndex, Series, Share of the monthly top picks whose company is acquired within `days` of the…, First available date of each month (limits overlap from year-long labels)., Share of the model's top-k picks that end up in the future top decile. `frac`… (+10 more)

### Community 15 - "rewrite_summary"
Cohesion: 0.23
Nodes (12): 6. Medium: report regeneration can silently change an old experiment, default_prices(), _pit_universe_desc(), Path, Series, _ranking_lines(), Does the model find the future top decile / the year's biggest winners?, Files a report rebuild overwrites (summary, stats, monthly returns, score… (+4 more)

### Community 16 - "score_group_table"
Cohesion: 0.33
Nodes (6): State log (snapshot 2026-10-03), What each score group did next: shows where a model's ranking skill sits. Every…, score_group_table(), _fmt_pct(), Where the ranking skill sits: what each score group did next., _score_group_lines()

### Community 17 - "features.py"
Cohesion: 0.09
Nodes (40): load_price_panel(), Date x ticker adjusted close. Missing tickers are skipped (reported)., build_bfm_prediction_features(), build_universe_features(), _helper_frame(), _pct_change(), DataFrame, Path (+32 more)

### Community 18 - "dataset.py"
Cohesion: 0.11
Nodes (27): dataclasses, build_train_dataset(), label_columns(), load_dataset(), DataFrame, Path, Train-ready dataset: join features (X) + labels (y) on Date + Ticker., Label column names for one horizon or all. (+19 more)

### Community 19 - "dev_rows"
Cohesion: 0.12
Nodes (17): Bar to beat (v6_pit: Jan 2001 → Jan 2021; SPY +7.3%/yr, equal-weight universe +8.2%/yr), Claude and plugin setup (moved from project.md 2026-10-12, unchanged), Data facts for Phase 2, Decisions (full, as of 2026-10-03), First Claude chat (2026-10-05, Claude Opus 5.5), Move to the Claude app (2026-10-04, user-approved), Moved from project.md (2026-10-21 trim, user-approved), Other notes moved from project.md (2026-10-03) (+9 more)

### Community 20 - "Batch 2 plan: margin expansion"
Cohesion: 0.20
Nodes (9): After the runs (info only, not gates), Batch 2 plan: margin expansion, Code (before any run), Code checks (2026-10-16), Features (new opt-in group `margins`, 4 columns), Goal, Keep rule (locked; user-approved 2026-10-09), Runbook (only after the user says `run`) (+1 more)

### Community 21 - "Pinky evaluation rules"
Cohesion: 0.25
Nodes (8): Honesty rules (every run), How big is noise?, Keep rule for new data (locked 2026-10-03), Pinky evaluation rules, Scoreboard (shown every time; never decides), Stop and audit if, What every report shows, What success means

### Community 22 - "README.md"
Cohesion: 0.20
Nodes (5): Disclaimer, How it works, Pinky, Quick start (local), What's in git and what isn't

### Community 23 - "run_horizon"
Cohesion: 0.32
Nodes (8): _fit_beat_models(), _fit_return_models(), DataFrame, DatetimeIndex, Train/eval all folds for one horizon with CS prep + tuned LightGBM. Returns…, run_horizon(), _xy_beat(), _xy_return()

### Community 24 - "Key findings"
Cohesion: 0.33
Nodes (6): Four model fixes — v7_pit + ablations (2026-09-27), Honest baseline — v5_pit (2026-09-26), Key findings, New yardstick — v6_pit (2026-09-26), Old 128-stock results (inflated by survivorship + hindsight), Step 3 — growth features (v8) (2026-10-03)

### Community 26 - "train.py"
Cohesion: 0.15
Nodes (17): lightgbm, backtest_settings(), pit_tag(), placebo_group(), _prep_desc(), Walk-forward training + evaluation (LightGBM + Ridge baseline). v2 prep: -…, Every fold's models → models/<run>/<horizon>/fold_NN/, plus folds.json (fold…, The feature group a run shuffles: True (v8 / early v9 configs) = growth; False… (+9 more)

### Community 27 - "shap_report.py"
Cohesion: 0.23
Nodes (11): joblib, explain_fold(), explain_runs(), family_of(), DataFrame, ndarray, Per run x fold x input/family numbers; runs that share inputs share one rebuild., SHAP: which inputs drive the LightGBM return model's scores, fold by fold (=… (+3 more)

### Community 28 - "Pinky"
Cohesion: 0.20
Nodes (10): Backtest defaults, Decisions, Gotchas (learned the hard way), Key findings (summary), Pinky, Repo layout, ▶ Resume here (new chat: read this first), Roadmap (+2 more)

### Community 29 - "Pinky architecture"
Cohesion: 0.20
Nodes (10): Backtest (`pinky/backtest.py`), Data (Sharadar Core US Equities Bundle), Dataset (`pinky/pit_dataset.py`), Goal, Legacy (not used by `--pit` runs), Locked decisions, Outputs (`artifacts/`, `models/`; never in git), Pinky architecture (+2 more)

### Community 30 - "Step 3 training runbook (v8 growth features)"
Cohesion: 0.50
Nodes (3): Runbook (done 2026-10-03; reuse for the next batch), Step 3 notes (company data batch 1 — plan locked 2026-10-03), Step 3 training runbook (v8 growth features)

### Community 31 - "Batch 2 decisions (2026-10-09, Claude Opus 5.5)"
Cohesion: 0.40
Nodes (5): Batch 2 code: margins (2026-10-16, Claude Opus 5.5), Batch 2 decisions (2026-10-09, Claude Opus 5.5), Batch 2 results: margins (2026-10-19, Claude Opus 5.5), Residual edge + SHAP on the baselines (2026-10-16, Claude Opus 5.5 Max), Step 2: code prep + baseline runs (2026-10-12, Claude Opus 5.5 Max)

### Community 32 - "train_walkforward.py"
Cohesion: 0.40
Nodes (3): parse_args(), CLI: walk-forward train + evaluate (default focus: 1y). Usage: python…, Exact flags only: a misspelled or malformed option (e.g. `--pit=true`) stops…

## Knowledge Gaps
- **91 isolated node(s):** `Agent instructions (Pinky)`, `Claude app notes`, `How it works`, `What's in git and what isn't`, `Quick start (local)` (+86 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 302 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `dev_rows()` connect `dev_rows` to `Growth round 2 plan (DRAFT)`, `check_growth2_features.py`, `universe.py`, `run_horizon`, `train.py`, `shap_report.py`, `Pinky`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Why does `Pinky` connect `Pinky` to `Growth round 2 plan (DRAFT)`, `README.md`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `Pinky architecture` connect `Pinky architecture` to `Growth round 2 plan (DRAFT)`, `README.md`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `run_all()` (e.g. with `Moved from project.md (2026-10-21 trim, user-approved)` and `Gotchas (learned the hard way)`) actually correct?**
  _`run_all()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Agent instructions (Pinky)`, `Claude app notes`, `How it works` to the rest of the system?**
  _91 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `check_growth2_features.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07630522088353414 - nodes in this community are weakly interconnected._
- **Should `sharadar.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07563025210084033 - nodes in this community are weakly interconnected._