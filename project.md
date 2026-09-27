# Pinky

Local stock-prediction project. **Goal: predict stocks that will perform well and make us profit** — beat the S&P 500 (**SPY**).

- **Favor tech**, and especially **finding future big winners** early ("the next NVDA/TSLA").
- **Still buy other sectors** (energy, industrials, etc.) when they're the best picks — not tech-only.

## ▶ Resume here (new chat: read this first)

Last updated **2026-09-27**. Phase 1 code: `c0cdfe7`. Phase 2 step 1 (v6_pit): `5be6e83`. Showcase + report checks: `cf84035`. Step 2 (v7): see `git log`.

**State**
- Phase 1 (honest evaluation): **done**.
- Phase 2 **step 1 — new yardstick (v6_pit): done.** Same price-only models; 2020 now tested; holding buffer; top-50 / top 10% portfolios. Still **no reliable edge** (see Key findings).
- **Showcase updated to v6_pit: done** (2026-09-27). Leads with the honest result; every number is computed from saved artifacts; text checked against the data.
- **Every report now includes both checks the user asked for:** share of top picks acquired within 6 months (top-10 and top 10%, vs base rate) and results before/after 2009 vs SPY (`REPORT_SPLIT_YEAR` in `config.py`).
- **Phase 2 step 2 — four model fixes (v7_pit): done**, plus one ablation per fix and a control (all off = v6). Results in Key findings and `docs/WALKFORWARD_RESULTS.md`. Short version: IC doubles, crashes drop, **still no edge over SPY**; no run passes the bar. The **rank label** turns models into calm, low-volatility pickers (few big winners), which clashes with the goal.
- **Waiting on the user:** which return target step 3 builds on (rank label = calm picks, better IC; raw target = winner-hunting LightGBM), and whether to rebuild the showcase now or after step 3.
- **Next:** step 3 — company data batch 1 → compare to step 2. After each step: rebuild the showcase (set `RUN` in `scripts/build_showcase.py`) and re-read its text. Static lines: the footer's "Stocks need a year of price history" must go once the showcase shows a run with the `young` fix.
- Local commits are **not pushed** (check: `git log origin/main..main --oneline`). User said: don't push yet.

**User decisions (2026-09-26)**
- Phase 2 model fixes: **all four approved** (list under Roadmap).
- Evaluation fixes approved and done in v6_pit: holding buffer, 2020 test block, top-50 / top 10% reports.
- User wants **company data features**, not just price — that is the core of Phase 2.
- Build **step by step** so we can tell what helps. Showcase update **after step 1** (done). GitHub: **don't push yet**.
- Add to every future report (2026-09-27): takeover share of top picks, and 2009–2020 vs SPY (done in `train.py`).
- User confirmed the highest model for Phase 2 (2026-09-26). New chats: ask again before hard work (Rule 10).

**Step 2 notes (model fixes — done)**
- `train.MODEL_FIXES` = `rank_label`, `rank_features`, `young`, `size`; pit runs use all unless `--without=a,b` (run tagged `no-<fix>`). Legacy runs use none.
- Dataset (`pit_dataset.py`) now keeps stocks with ≥ ~1 month of prices (`SHORT_FEATURES`), adds `history_1y` and `log_mcap` (Sharadar DAILY; verified point-in-time). v6 dataset backup: `data/sharadar/derived/pit_dataset_v6.parquet`.
- Rank features run once before the walk-forward (`preprocess.cross_section_rank`; per-day only, so no leak). Each run saves `artifacts/run_config_<run>.json` (fixes, stock count) for `--report-only`.

**Step 3 notes (company data batch 1)**
1. New `pinky/fundamentals.py`: load `data/sharadar/fundamentals.parquet`, **ARQ + ART rows only**. Attach to dataset rows with `merge_asof` on the **filing `date`** (backward, by ticker) → point-in-time.
2. Growth + revenue acceleration features: quarterly revenue growth vs the same quarter last year, TTM revenue growth, acceleration (this quarter's YoY growth minus last quarter's), gross-profit growth, days since last filing.
   - Find "same quarter last year" by `calendardate`, not by row offset (filings can be missing or late).
3. Run `train_walkforward.py --pit` under a new version; compare to the previous step; keep only what helps.

**Bar to beat (v6_pit: Jan 2001 → Jan 2021; SPY +7.3%/yr, equal-weight universe +8.2%/yr)**
- Ridge rank IC **0.052**; Ridge top 10% + buffer **+8.7%/yr** (+7.8% at 25 bps); Ridge top-10 + buffer +8.3%/yr.
- Also check: 2009–2020 vs SPY (Ridge trails: +12.6% vs +14.5%/yr) and the takeover share of top picks (Ridge top-10: 25%; base rate 2.2%).
- Per-portfolio numbers: `artifacts/backtest_stats_1y_v6_pit.csv`. Side by side: `PYTHONPATH=. python scripts/compare_runs.py v6_pit v7_pit`.
- v7_pit (step 2) passes the IC part (0.056–0.063) but not the portfolio part (best top 10% + buffer: LightGBM +7.2%). Top-10 CAGRs are noisy by a few %/yr: judge on IC and top 10% first.
- Never touch the 2022+ holdout until the final test.

**Data facts for Phase 2**
- Fundamentals ARQ: filing dates 1993 → 2026, 17,045 tickers, revenue filled 97% (ART 92%).
- 9,492 of the 10,043 v6 dataset stocks (95%) have ARQ rows. The v7 dataset has 10,902 stocks (young stocks added).
- `daily.parquet` columns: `marketcap`, `ev`, `evebit`, `evebitda`, `pb`, `pe`, `ps`.
- Not downloaded yet: Sharadar `metrics` table (access confirmed, ~1.4 MB).

**When you finish a chunk of work:** update this Resume section so the next chat can pick up.

## Gotchas (learned the hard way)

- Sharadar CSVs must be parsed with `sharadar.CSV_KW` (`keep_default_na=False`). Otherwise the ticker "NA" becomes blank.
- `fiscalperiod` is text ("2009-Q4"), not a date.
- Fundamentals: use **AR\*** dimensions only (dated by SEC filing date). **MR\*** rows are dated at quarter-end → ~2.5 months of future leak.
- Any dataset column that doesn't start with a prefix in `dataset.LABEL_PREFIXES` is treated as a **model input**. New label columns must get a prefix there, or they leak.
- Rows are weekly → always pass the daily `calendar` to `iter_walk_forward_folds`. Otherwise "252 days" silently becomes 252 weeks.
- Forward returns and backtests must use the `tr` panel (delisting-aware), never raw `closeadj`.
- pandas `to_numpy()` can return a read-only array → use `np.array(..., copy=True)` before writing into it.
- Filtered Sharadar API queries return only the last year unless you pass `from_=`.
- Sharadar tickers are unique (reused symbols get a suffix, e.g. `CNO1`).
- ~195 of 2.8M rows show one-day jumps > 100% on tiny stocks (likely split glitches); left in for the baseline.
- Size: panels are 7,227 days × 17,340 stocks. Dataset build peaks ~14 GB RAM (machine: 48 GB, 18 cores, 1.3 TB free).
- Untracked `data/reference/` comes from another chat — leave it alone.
- `graphify update` backs up the previous graph into a dated folder (`graphify-out/YYYY-MM-DD/`, untracked). Don't commit them.
- API key safety: never print `.env`. Before a commit, check the staged diff with a count-only `grep -c -F` for the key.

## Rules (always on)

Apply at all times unless the user says otherwise. Mirrored in `.cursor/rules/`.

1. **Never lie.** Never fake data, results, or information.
2. **Double-check before answering.**
3. **Be concise.** Straight to the point, no filler.
4. **No exceptions** unless the user says so.
5. **Auto-update `project.md`** after big features/updates, and as the project changes.
6. **Challenge bad ideas.** If the user is wrong or a better way exists, say so.
7. **Stress-test the approach.** If it isn't the best, say so. The user won't be mad.
8. **Hunt for mistakes** in statements, plans, and requests. Report them right away.
9. **Every new chat:** read `project.md` first.
10. **HIGHEST MODELS — top priority, all agents.** Go heavy on the highest models for reasoning, planning, decisions, and thinking. Token cost doesn't matter. Never downgrade to save cost (`.cursor/rules/strong-models.mdc`).
    - User runs Cursor on **Auto**; agents can't change the main model → **before a hard task, or if a task turns hard mid-way: STOP, ask the user to switch to the highest model, and wait** (unless the user says continue).
    - Hard sub-work → subagents on the strongest model; copy this rule into every subagent prompt.
11. **Communication:** simple sentences, bullet points, **ask before large decisions/changes**.
12. **Graphify first:** `graphify query/explain/path` before exploring code; `graphify update .` after code changes.

Also: **no push** until the user says; **training only when the user says**.

## User goals & expectations

- Wants a model that's genuinely smart at finding stocks that perform well; catching the next NVDA/TSLA would be ideal.
- Likes tech most, but also buys other sectors (e.g., energy) — not tech-only.
- First asked for ~10%/month — explained that's unrealistic. Realistic aim: beat SPY by a few %/yr, reliably.
- Accepts a bit more risk (60% sector cap), **no leverage** (account can't). Bullish on tech.
- Data budget flexible (paying for Sharadar). Lots of time and compute.

## Key findings

### Four model fixes — v7_pit + ablations (2026-09-27)

Same price features; same yardstick. SPY +7.3%/yr (2009–2020 +14.5%). Control (all fixes off) reproduces v6_pit.

| | v6_pit | v7_pit | v7 without rank label |
|---|---|---|---|
| Rank IC Ridge / LightGBM | 0.052 / 0.015 | 0.056 / 0.063 | 0.024 / 0.031 |
| Top 10% + buffer, LightGBM (2009–2020) | +4.3% (+8.9%) | +7.2% (+13.5%) | +5.8% (+11.6%) |
| Top 10% + buffer, Ridge (2009–2020) | **+8.7%** (+12.6%) | +6.8% (+11.8%) | +5.2% (+10.4%) |
| LightGBM top-10: big winners / crashes (random 10% / ~7%) | 14.7% / 18.5% | 3.9% / 2.3% | 13.4% / 8.0% |

- **Still no edge over SPY; no run passes the bar.** Best broad portfolio: LightGBM top 10% + buffer +7.2% vs SPY +7.3%.
- **Rank label = the big lever:** IC ~doubles, but picks become calm low-volatility stocks (median vol 14–16% vs 33%) that rarely crash **and rarely win big** — against the goal.
- **Without the rank label**, LightGBM is the best winner-finder so far (13.4% big winners, crashes 18.5% → 8.0%).
- Rank features beat z-scores on robustness: z-scores bring back takeover targets (41% of Ridge's top-10). Young stocks: small IC gain. Size: helps LightGBM.
- Full table + ablations: `docs/WALKFORWARD_RESULTS.md`.

### New yardstick — v6_pit (2026-09-26)

Same price-only models as v5_pit. 2020 now tested (20 folds, backtest Jan 2001 → Jan 2021), holding buffer, wider portfolios. SPY +7.3%/yr, equal-weight universe +8.2%/yr.

| CAGR net of 10 bps (25 bps) | LightGBM | Ridge | Momentum 12-1 |
|---|---|---|---|
| Top-10 + buffer | −6.2% (−8.5%) | +8.3% (+5.9%) | −1.6% (−2.7%) |
| Top-50 + buffer | +2.0% (+0.2%) | +7.7% (+5.9%) | +3.6% (+2.6%) |
| Top 10% + buffer | +4.3% (+3.1%) | **+8.7% (+7.8%)** | +7.0% (+6.2%) |

- **Still no reliable edge.** Ridge's lead is all from 2001–2008. **2009–2020: Ridge (top 10% + buffer) +12.6%/yr vs SPY +14.5%.**
- **Ridge's top-10 are mostly takeover targets:** 25% get acquired within 6 months (base rate 2.2%). Calm, steady "pending deal" stocks = accidental merger arbitrage, not winner-finding.
  - Those bought-out picks: median 63-day volatility 5.5% (other picks 25.5%), 0% crash (other picks 11%), mean 1y excess vs SPY only +0.2%. Safe, but no edge.
- **2020 broke every model:** rank IC −0.17 to −0.22 that year. Mean Ridge IC 0.066 → 0.052.
- **Buffer:** big help for top 10% (turnover 103% → 45%/month); little help for top-10, because top picks fall to a median rank of ~168 within a month (the signal jumps around).
- Ridge finds fewer big winners than random (precision 0.06–0.08 vs 0.10). Momentum finds the most (0.15–0.17) but concentrated momentum crashes (−84% to −91% drawdowns).
- Full report: `artifacts/walkforward_summary_v6_pit.md`. History: `docs/WALKFORWARD_RESULTS.md`.

### Honest baseline — v5_pit (2026-09-26)

Point-in-time liquid US universe, delisted stocks included, 1y signal, monthly top-10, 10 bps, **Jan 2001 → Feb 2020** (19 test years; 2022+ holdout untouched).

| Signal | CAGR | Max DD | Precision@10 | Winner capture |
|---|---|---|---|---|
| SPY | +6.9% | −52% | — | — |
| Equal-weight whole universe | +7.5% | — | 0.10 (random) | 0.005 (random) |
| Ridge | +7.6% | −47% | 0.08 | 0.019 |
| Blend | +0.6% | −68% | 0.10 | 0.028 |
| LightGBM | **−8.0%** | −87% | 0.15 | 0.027 |
| Naive 12-1 momentum | −1.4% | −84% | 0.17 | 0.048 |

- LightGBM picks volatile "lottery tickets": 1.5× random chance of a top-10% winner, but 2.6× the normal chance of losing > 50% vs SPY. **Price data predicts how much a stock moves, not which way.**
- Ridge picks calm, rising stocks → about market return, smaller drawdowns.
- The 60% sector cap barely matters here (picks are already spread out).
- Full report: `artifacts/walkforward_summary_v5_pit.md`. History: `docs/WALKFORWARD_RESULTS.md`.

### Old 128-stock results (inflated by survivorship + hindsight)

- 2018–2025: LightGBM +41%/yr vs SPY +14%. With NVDA/SMCI/TSLA/PLTR/AVGO removed: +19%. Precision@10 0.32–0.34.
- Details in `docs/WALKFORWARD_RESULTS.md` (v1 → v4 ex5).

## Decisions

- **Data:** Sharadar Core US Equities Bundle — active. Direct API + bulk tables. Key in `.env` (gitignored, never print). License: never share or commit the data.
- **Universe (`pinky/universe.py`):** each day, price ≥ $5 and 21-day avg dollar volume ≥ $5M (nominal $). Common stock + ADRs + Canadian; no preferreds, secondary share classes, or SPACs (SIC 6770); NYSE / NASDAQ / NYSE American only. → **1,200–2,850 stocks/day, 11,561 distinct** (1998–2026).
- **Delistings:** exit value reinvested in SPY. Bankruptcy / liquidation / regulatory delistings also take **−30%** on the last price (Shumway 1997).
- **Dataset rows:** weekly (every 5th trading day); folds use the daily calendar. Stocks need 1y of price history to be scored (hides new IPOs for a year — Phase 2 fix).
- **Sectors:** Sharadar sectors (current classification) for the cap. The custom "Tech/AI" bucket only applies to the old 128-stock universe.
- **Risk:** no leverage. Sector cap 60%.
- **Main signal:** undecided. Revisit in Phase 2.
- **Locked holdout:** `HOLDOUT_START = 2022-01-01`. Dev runs only use rows whose label ends before it (`train.dev_rows`). Score the holdout once, at the very end.

## Roadmap

**Phase 1 — honest evaluation: done.** Sharadar pull, point-in-time universe, delisting-aware labels, weekly dataset, top-decile label, precision@10 + winner capture, locked holdout, honest re-score (v5_pit).

**Phase 2 step 1 — evaluation fixes: done (v6_pit).** Holding buffer, 2020 test block, top-50 / top 10% reports.

**Phase 2 model fixes (from Phase 1 findings — all four approved 2026-09-26):**
- Train on each day's **return rank** instead of raw return (a few +5,000% stocks pull LightGBM toward lottery tickets).
- Scale features by **daily rank** instead of z-score (one bad tick can squash a whole day).
- Let stocks **without 1y of history** be scored (so a new PLTR isn't invisible for a year).
- Add **size** (market cap) as a feature.

**Phase 2 — company data**, added in batches; keep only what beats the baseline:
1. **Growth + revenue acceleration** ← first
2. Margin expansion
3. Price strength (momentum, 52-week-high proximity, vs sector)
4. Earnings reactions / surprises
5. Reinvestment (R&D/revenue, ROIC)
6. Quality / safety (debt, cash burn, accruals, dilution)
7. Insiders + institutions
8. Industry tailwind
9. Valuation (context only — don't screen out growth)
10. Analyst revisions (expensive; later)

**Phase 3 — only if Phase 2 works:** position sizing, monthly picks report, live paper-trading log.

## Backtest defaults

- Monthly rebalance, equal weight, **10 bps per side** (25 bps re-prices the same trades via `backtest.with_cost`).
- Portfolios: top-10, top-50, top 10% of each date's stocks; each with and without the **holding buffer** (keep a holding while it ranks in the top 3× N, `BACKTEST_BUFFER_MULT`). Main comparison rows: **top-10 + buffer** and **top 10% + buffer**.
- Sector cap 60% of picks (`BACKTEST_MAX_SECTOR_SHARE`) on all rows except "v5 rules". Signal at day D close, trade at D+1 close.
- Walk-forward: 1-year test folds; the last fold may be shorter (≥ 63 days, `WF_MIN_LAST_TEST_DAYS`) so 2020 is tested.
- Signals compared: LightGBM, Ridge, Blend (avg daily rank), naive 12-1 momentum. Settings: `pinky/config.py` (`BACKTEST_*`, `WF_*`).

## Repo layout

- `pinky/config.py` — universe rules, paths, backtest settings, `HOLDOUT_START`, `DELIST_RETURN_PERFORMANCE`
- `pinky/sharadar.py` — Sharadar API: bulk download → parquet, small queries (key never printed)
- `pinky/universe.py` — point-in-time universe panels, delisting-aware `tr` panel, sectors, SPY, `backtest_prices()`
- `pinky/pit_dataset.py` — weekly features + labels on the point-in-time universe (13 price features + `history_1y` + `log_mcap`)
- `pinky/preprocess.py` — per-day z-score or percentile rank + correlated-feature drop
- `pinky/walkforward.py` — expanding walk-forward folds + label purge (`calendar` param)
- `pinky/train.py` — Ridge / LightGBM / Blend, report, `pit=True` and `exclude` runs, `dev_rows`
- `pinky/metrics.py` — IC, top-N, precision@k, winner capture, calibration
- `pinky/backtest.py` — monthly top-N / top-fraction backtest, costs, sector cap (`sectors` param), holding buffer, stress tests
- Legacy (128 stocks, yfinance): `data_pull.py`, `raw_io.py`, `features.py`, `labels.py`, `dataset.py`
- `scripts/` — `pull_sharadar`, `train_walkforward`, `compare_runs`, `build_showcase`, plus legacy build scripts
- `showcase/index.html` — one-page visual (offline), built from v6_pit artifacts by `scripts/build_showcase.py`.
- `data/sharadar/` (~6 GB, gitignored, never share) — tables (`*.parquet`), `zips/`, `panels/` (Date × Ticker), `spy.parquet`, `derived/pit_dataset.parquet`
- `artifacts/`, `models/` — outputs (gitignored). Per run: `walkforward_summary_<run>.md`, `walkforward_metrics_<run>.csv`, `oos_preds_1y_<run>.parquet`, `backtest_stats_1y_<run>.csv`, `run_config_<run>.json`. `models/1y_<tag>/` holds last-fold models per tag (`1y_pit` = latest full pit run, overwritten; ablations get `1y_pit_no-<fix>`).
- `docs/` — `WALKFORWARD_RESULTS.md`, `ARCHITECTURE.md`, `PRD.md`, `EVAL.md`
- `AGENTS.md`, `.cursor/rules/` — agent instructions. `graphify-out/` — knowledge graph.

## Commands

- Activate venv: `source .venv/bin/activate` (run everything from the repo root with `PYTHONPATH=.`)
- Sharadar pipeline:
  1. Pull: `python scripts/pull_sharadar.py` (~10 min, needs network)
  2. Universe panels: `python -m pinky.universe` (~1 min)
  3. Dataset: `python -m pinky.pit_dataset` (~1 min)
  4. Train/eval: `python scripts/train_walkforward.py --pit` (~8 min alone; output name = `train.VERSION` + `_pit`, currently `v7_pit`)
  - Ablations: `--without=rank_label,size` (see `train.MODEL_FIXES`). Several runs fit in parallel: `OMP_NUM_THREADS=3` each, 6 runs ≈ 13 min (18 cores, 51 GB RAM).
  - stdout is buffered when redirected to a file → use `python -u` to watch fold progress in a log.
  - Rebuild a report without retraining: `python scripts/train_walkforward.py --report-only=v7_pit` (uses the saved metrics CSV + preds parquet).
  - Compare runs: `python scripts/compare_runs.py v6_pit v7_pit ...`
- Legacy: `pull_data.py` → `build_features.py` → `build_labels.py` → `build_dataset.py` → `train_walkforward.py` (`--ex-winners` drops hindsight winners)
- Showcase: `python scripts/build_showcase.py` (~1 min; run name = `RUN` at the top). To view it in the IDE browser, serve it: `cd showcase && python3 -m http.server 8765` (`file://` is blocked).
- GitHub (private): https://github.com/steveonshit/Pinky (`origin/main`) — push only when the user says.
- Graphify CLI: `/Users/hqschool/Library/Python/3.12/bin`; run `graphify update .` after code changes.
- Tip: use one chat at a time on Pinky (parallel chats can overwrite each other's edits).
