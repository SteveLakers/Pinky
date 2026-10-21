# Code review — 2026-10-21

Scope: the established Sharadar/PIT data, training, evaluation and experiment-analysis paths. Base commit `780deef`, plus the working files inspected during this session. Another process began editing growth round 2 during the review; that unfinished feature is outside this report's coverage. No pipeline code, saved experiment results, models, showcase or product files were changed by this review. No training or network requests were run. Only development-period results were analyzed.

## Findings, in priority order

### 1. High: synthetic delisting prices are accepted as new trade fills

- Code: `pinky/backtest.py:156` checks the passed price panel for an entry price; `pinky/universe.py:175` passes `tr`, whose post-delisting values are synthetic reinvestment in SPY (`total_return_panel`). A nonmissing `tr` value does not prove the stock can be bought.
- Observed in saved baseline A, seed 42, LightGBM, Top-10 + buffer: a **new** ABNK1 position on **2005-12-05**. The raw price panel and ticker metadata end on **2005-12-02**; actions on that date include acquisition and delisting. There is no later raw stock price, but the synthetic total-return series continues.
- Reconstructed A's 240 monthly selections using the existing cap and buffer. Their gross returns match saved returns to a maximum absolute error of `1.97e-7`, so this reproduces the saved selection path rather than an unrelated example.
- The top-10% buffered portfolios also have new positions without a raw entry-day close: A seed 42 has **3**, B seed 42 has **2**. Those counts alone do not establish the cause for every missing quote. Previously held positions without raw quotes were excluded from these counts.
- Recommended repair: use actual tradeability/quotes to govern new fills and give unfilled orders an explicit policy. Keep synthetic total-return values for label calculation and accounting for existing holdings after a delisting. Measure the performance change before revising any experiment verdict.

### 2. High: reported maximum drawdown understates daily losses

- Code: `pinky/backtest.py:231` computes drawdown from the holding-period returns passed by `summarize_backtest` at line 254. Prices inside each holding period are discarded.
- Saved **A seed 42, LightGBM, Top-10 + buffer** reports **−35.16%** maximum drawdown. Reconstructing daily portfolio value from the same holdings, equal weights at rebalance, drift between rebalances and saved entry costs gives **−46.13%**. All 240 period-end gross returns reconcile within `1.97e-7`.
- Separate arithmetic bug in the same helper: `[-0.20, +0.10]` returns a drawdown of **0%**, because the initial wealth of 1 is absent from the peak calculation. The correct result is **−20%**.
- A small price path falling 50% and recovering before the next rebalance also reports 0% under the current holding-period calculation.
- Recommended repair: calculate maximum drawdown from daily portfolio equity, including initial capital and costs. If retaining the existing statistic, label it explicitly as drawdown sampled at rebalance dates and fix its initial-capital calculation.

### 3. Medium: RSI drops valid stocks after uninterrupted rises or flat prices

- Code: `pinky/pit_dataset.py:51` converts zero average losses to missing; line 134 then drops rows missing RSI along with genuinely immature histories.
- Reproduction: an increasing 65-business-day price series with complete volume produces missing RSI and **zero retained rows** under the dataset's short-feature rule. On its final row, RSI is the only missing short feature. An equivalent decreasing series produces RSI 0.
- Recommended repair: return RSI 100 when gains are positive and losses are zero; define the all-flat case explicitly. Preserve missing values for genuinely incomplete histories. Add a focused regression check before rebuilding the dataset.
- The number of affected real dataset rows and effect on returns were not measured. Fixing this changes the dataset, so the old baselines cannot simply be assumed identical afterward.

### 4. Medium: malformed PIT flags silently launch the legacy path

- Code: `scripts/train_walkforward.py:30` requires an exact `--pit`, but line 40 accepts any argument starting with a recognized prefix.
- Reproduction: invoking the CLI through `runpy` with `--pit=true`, with training replaced by a mock, calls `run_all(pit=False)` without an unknown-option error. No model was trained by this check.
- Recommended repair: parse flags with `argparse` or exact matching and reject malformed flags before loading data or starting training. Apply the same validation to the other boolean options.

### 5. Medium: an API error can expose the API key

- Code: `pinky/sharadar.py:72` puts the key in URL parameters; line 74 calls `raise_for_status()` without scrubbing the resulting error.
- Reproduction: a real `requests.Response` with status 401 and a URL containing a **fake** token causes `bulk_status()` to raise an exception containing that token. There was no real API request and no real key was read or printed for this check.
- Recommended repair: sanitize HTTP and transport exceptions at the shared request boundary, including exception chaining/tracebacks. Do not rely solely on scrubbing HTTP response bodies. No claim is made that a real credential has already leaked.

### 6. Medium: report regeneration can silently change an old experiment

- Code: `pinky/train.py:763` reloads current prices, sectors and acquisition data for `rewrite_summary`; `_backtest_lines` uses current portfolio settings. `_write_summary` overwrites the original run's backtest stats and monthly returns at lines 724–725.
- Saved run configs contain only version, feature fixes, stock count, seed and placebo. They omit code/data fingerprints, package versions, exclusions, portfolio settings and preprocessing settings. Confirmed against both baseline configs.
- Consequence: changing backtest settings or refreshing data, then running `--report-only`, can replace the measurements used by a later batch verdict under the original experiment name.
- Recommended improvement: freeze the full experiment/evaluation configuration and input fingerprints; verify them before regeneration, or write a separately named evaluation. Preserve the original measured results.

## Risks requiring further evidence

- **Fundamental availability:** `earnings_announcements` retains only ticker and event date. `with_news_dates` infers the quarter from its period end and assigns filing-derived values to the earlier event date. The checks establish consistency with that inferred date, but do not prove that every revenue, gross-profit and operating-income value was actually released then. This is an availability assumption, not a demonstrated leak in a particular company. Verify against source releases or run a filing-date sensitivity check before relying on it.
- **Historical metadata:** `eligible_tickers` applies a single securities-master exchange/category/SIC classification to the whole history; `sector_map` explicitly uses current classification. Price and liquidity filters are daily, but these other classifications are not historically versioned. The size of any resulting bias was not measured.

## Verification and limits

- Existing growth synthetic checks: **22 passed**, 0 failed. Existing margin synthetic checks: **14 passed**, 0 failed. Only their synthetic-case functions were invoked, not the full data-check scripts.
- Additional focused probes reproduced RSI omission, CLI fallback, initial-loss drawdown, hidden intraperiod crash and unsanitized HTTP error behavior.
- Reconstructed baseline holdings and daily equity using local data; verified saved period-return agreement and raw entry-price availability. Seed 42 only; daily drawdown quantified for A's top-10 buffered LightGBM portfolio only.
- This is not a claim that the entire repository is correct. Full training, full real-data feature checks, holdout evaluation, deployment and product QA were not performed.
- Recommended order: correct execution and risk measurement, add focused checks for the confirmed defects, then decide which dataset/baseline reruns to authorize. Do not infer that fixing these issues will create predictive edge.
