# Pinky architecture

Last updated: 2026-10-05. Current state, decisions and next steps: `project.md`. Results by version: `docs/WALKFORWARD_RESULTS.md`.

## Goal

Rank every liquid US stock by how much it should beat SPY over the next year, and test whether buying the top of that list beats SPY after trading costs.

## Pipeline

| Step | Code | Output |
|---|---|---|
| 1. Download | `scripts/pull_sharadar.py` → `pinky/sharadar.py` | `data/sharadar/*.parquet` (7 tables) |
| 2. Universe + returns | `python -m pinky.universe` | `data/sharadar/panels/*.parquet` (Date × Ticker) |
| 3. Dataset | `python -m pinky.pit_dataset` (+ `pinky/fundamentals.py`) | `data/sharadar/derived/pit_dataset.parquet` |
| 4. Train + evaluate | `scripts/train_walkforward.py --pit` → `pinky/train.py` | `artifacts/*_<run>.*`, `models/<run>/1y/fold_NN/` |
| 5. Compare / judge | `scripts/compare_runs.py`, `scripts/step3_verdict.py` | tables, `artifacts/step3_verdict.md` |
| 6. Explain | `scripts/residual_edge.py` (residual-edge skill), `scripts/shap_report.py` | `artifacts/residual_edge/`, `artifacts/shap/` |

## Data (Sharadar Core US Equities Bundle)

- Tables: `tickers`, `stocks` (daily prices), `fundamentals` (SF1), `sp500`, `actions`, `daily` (market cap and ratios), `events`. SPY comes from `funds`.
- The key lives in `.env` and is never printed. License: the data never leaves this Mac.
- Company numbers: as-reported dimensions only (ARQ, ART). Never MR*: those rows are dated at quarter end and leak about 2.5 months.

## Universe (`pinky/universe.py`)

A stock is in the universe on day D only if, using data up to D:
- it is a common stock, ADR or Canadian common stock (no preferreds, secondary classes or SPACs) listed on NYSE, NASDAQ or NYSE American;
- its unadjusted close is at least $5 and its 21-day average dollar volume at least $5M.

That gives about 1,200–2,850 stocks a day and 11,561 distinct stocks (1998–2026). Delisted companies are included for the days they traded.

**Returns (`tr` panel):** the adjusted close while listed. After a delisting the exit value is reinvested in SPY; bankruptcy, liquidation and regulatory delistings first take −30% on the last price. All forward returns and backtests use `tr`, never raw prices.

## Dataset (`pinky/pit_dataset.py`)

- One row per stock per week (every 5th trading day) from 1999. A stock needs about 1 month of prices.
- **Features** (model inputs):
  - 13 price features: returns over 1, 5 and 21 days; volatility over 21 and 63 days; volume vs its 21-day average; RSI-14; distance from the 50- and 200-day averages; momentum over 63, 126 and 252 days, and 12-1 momentum.
  - `history_1y` (how much of a year of prices the stock has; 1 = a full year) and `log_mcap` (size).
  - 6 growth features (`pinky/fundamentals.py`): `rev_yoy_q`, `rev_accel`, `gp_yoy_q`, `rev_yoy_ttm`, `days_since_news`, `has_growth`. Each number is used only on dates strictly after its news date (the earnings announcement, else the SEC filing). Tested in v8 and dropped; still in the dataset.
  - 4 margin features (batch 2, same date rules): `gm_ttm`, `om_ttm` (gross / operating margin, last 12 months), `gm_chg_q`, `om_chg_q` (change vs the same quarter a year ago, in margin points). Revenue ≤ 0 → missing.
- **Labels** for 3m, 6m, 1y and 2y (1y is the main target): `excess_*` (stock return − SPY return), `beat_*`, `stock_fwd_*`, `spy_fwd_*`, `top_*` (top 10% of that date).
- Any column whose name doesn't start with a prefix in `dataset.LABEL_PREFIXES` is treated as a model input, so a new label must get a prefix there.

## Training (`pinky/train.py`, `pinky/walkforward.py`, `pinky/preprocess.py`)

- **Walk-forward:** train on everything before a test year, test that year, move one year on. Test years 2001–2020 (20 folds; the last one may be shorter, down to 63 trading days, so 2020 is tested). Day counts use the daily trading calendar.
- **Purge:** train rows whose 1-year label reaches into the test year are dropped.
- **Locked holdout:** only rows whose label ends before 2022-01-01 are used (`dev_rows`).
- **Prep:** features become per-day percentile ranks (z-scores without `rank_features`); features correlated above 0.92 on the train set are dropped.
- **Models per fold:**
  - Return models: Ridge (the baseline) and LightGBM (120 trees, depth 4, 15 leaves, half the columns per tree, no row sampling). Target: each day's return rank (version A) or the raw excess return (version B).
  - Blend: the average of the two models' daily ranks.
  - Beat-SPY classifiers (logistic regression, LightGBM): reported only, not used for picks.
- **Switches** (`MODEL_FIXES`, all on with `--pit`; turn some off with `--without=`): `rank_label`, `rank_features`, `young`, `size`. **Company data under test** (`FEATURE_GROUPS`, off unless `--with=`; since v9): `growth`, `margins`. Also `--placebo=<group>` (that group's values shuffled between stocks within each date; bare `--placebo` = growth) and `--seed=N`.
- Run names come from the options (for example `v9_pit_no-rank_label_s7`, `v9_pit_with-growth_placebo`, `v9_pit_with-growth_with-margins_placebo-margins`), not from log file names. v9's plain `v9_pit` = v8's `v8_pit_no-growth` (same predictions).

## Backtest (`pinky/backtest.py`)

- Signal on the first test date of each month (every test date with `rebalance="weekly"`); trade at the next day's close; equal weight.
- Costs: 10 bps per side on real turnover; the same trades are re-priced at 25 bps.
- Sector cap: at most 60% of the picks from one sector (Sharadar sectors).
- Holding buffer: a holding is kept while it ranks in the top 3× N.
- Portfolios: top-10, top-50 and the top 10% of each date's stocks, each with and without the buffer, plus a "v5 rules" top-10 (no cap, no buffer) for comparison with old runs. Main comparison rows: **top-10 + buffer** and **top 10% + buffer**.
- Signals: LightGBM, Ridge, Blend and naive 12-1 momentum, compared with SPY and the equal-weight universe over 2001–2020 and split at 2009.

## Outputs (`artifacts/`, `models/`; never in git)

Per run: `walkforward_summary_<run>.md` (the report), `walkforward_metrics_<run>.csv`, `oos_preds_1y_<run>.parquet`, `backtest_stats_1y_<run>.csv`, `backtest_periods_1y_<run>.csv` (monthly returns), `score_groups_1y_<run>.csv` and `run_config_<run>.json`; the log is `artifacts/logs/train_<run>.log`. `models/<run>/1y/fold_NN/` keeps every fold's models, with `folds.json` (fold dates) next to them (since v9; older runs: `models/1y_<tag>/`, last fold only, shared across versions). `--report-only=<run>` rebuilds a report without retraining.

## Locked decisions

- Benchmark SPY; main horizon 1 year; monthly trading; no leverage; 60% sector cap.
- Point-in-time data only; the 2022+ holdout is scored once, at the very end.
- New data is kept only if it beats a placebo under a rule fixed before results (`docs/EVAL.md`).

## Legacy (not used by `--pit` runs)

The first prototype used yfinance prices for up to 128 of today's big stocks (2026-09-21 → 09-25): `pinky/data_pull.py`, `raw_io.py`, `features.py`, `labels.py`, the build functions in `dataset.py`, and `scripts/pull_data.py`, `build_features.py`, `build_labels.py`, `build_dataset.py`, `summarize_walkforward.py`. Its results were inflated by survivorship and hindsight (`docs/WALKFORWARD_RESULTS.md`).
