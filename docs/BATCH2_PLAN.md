# Batch 2 plan: margin expansion

**Status:** user approved both parts (24 runs) on 2026-10-16. Code built and checked 2026-10-16 (Claude Opus 5.5, user chose to continue on it): `check_margin_features.py` 50/50, `check_growth_features.py` 59/59, v9 training frames proven identical. **Not trained yet:** train only after the user says `run` (commands: Runbook below).

## Goal

Does margin data improve the picks? Two parts:
1. **Margins alone** (Roadmap 2).
2. **Growth + margins:** do margins separate the fast growers that win from those that crash? (Lead from 2026-10-16: the fastest 20% of sales growers have the worst median next year but the most big winners and the most crashes; `docs/PROJECT_HISTORY.md` → Residual edge + SHAP.)

## Features (new opt-in group `margins`, 4 columns)

All from SF1 **ARQ / ART only** (already downloaded in `data/sharadar/fundamentals.parquet`; no new data), using growth's news-date rules in `pinky/fundamentals.py`: news date = earnings announcement or SEC filing, first-filed report, filings < 10 days after period end skipped, `merge_asof(allow_exact_matches=False)` (used only after the news date), stale quarter > 365 days / TTM > 550 days → missing.

| Column | Meaning |
|---|---|
| `gm_ttm` | gross margin, last 12 months (`gp / revenue`, ART) |
| `gm_chg_q` | gross margin change vs the same quarter a year ago (ARQ, percentage points) |
| `om_ttm` | operating margin, last 12 months (`opinc / revenue`, ART) |
| `om_chg_q` | operating margin change vs the same quarter a year ago (ARQ) |

Revenue ≤ 0 → missing. Only 4 columns on purpose: extra columns cost A ~1%/yr even with real data.

## Code (before any run)

1. `pinky/fundamentals.py`: the 4 features + a generic within-date shuffle for any feature group (placebo).
2. `pinky/pit_dataset.py`: attach them. Back up `pit_dataset.parquet` as `pit_dataset_v9.parquet` first; after the rebuild, prove every old column is identical (data check, no retraining), so the v9 baselines stay valid.
3. `pinky/train.py`: `FEATURE_GROUPS += ("margins",)`; `--placebo=<group>` shuffles only that group. Defaults don't change, so `VERSION` stays v9 and plain runs stay identical.
4. `scripts/check_margin_features.py`: date / leak checks like `check_growth_features.py` (dates, ARQ/ART only, staleness, leak-power test with fake early dates, placebo independence).
5. Verdict script for the rule below (generalize `scripts/step3_verdict.py`).

## Runs (24; 6 at a time, ~15 min per batch; train only after the user says `run`)

- **Part 1, margins (12):** A and B × seeds 42 / 7 / 99 × real (`--with=margins`) / placebo (`--with=margins --placebo=margins`).
- **Part 2, growth + margins (12):** A and B × 3 seeds × real (`--with=growth,margins`) / placebo margins (`--with=growth,margins --placebo=margins`).
- Baselines already exist: `v9_pit` (+ `_s7`, `_s99`), `v9_pit_no-rank_label` (+ seeds).

## Keep rule (locked; user-approved 2026-10-09)

LightGBM top 10% + buffer, net of 10 bps, 2001–2020, mean of 3 seeds, A and B separately. KEEP only if both:
1. real − placebo ≥ +1.0%/yr overall and ≥ +0.5%/yr in 2001–08 and in 2009–20;
2. real ≥ the baseline: A +7.14%/yr, B +6.10%/yr.

Part 2 KEEP = growth comes back, together with margins. Gap > +3%/yr vs placebo → leak audit before believing it. No feature changes after results; 2022+ holdout untouched. Four tests make one lucky KEEP possible; the holdout is the final check. Expect modest results: DROP is a valid answer.

## After the runs (info only, not gates)

- Residual edge + SHAP on the new runs (`scripts/residual_edge.py`, `scripts/shap_report.py`).
- Fast-grower table by margin change: among the fastest 20% growers, next-year median, big winners and crashes by margin-change group.

## Code checks (2026-10-16)

- Dataset rebuilt; backup `data/sharadar/derived/pit_dataset_v9.parquet`. Same 2,932,585 rows in the same order, all 43 old columns identical, exactly the 4 margin columns added.
- With margins off, the model frames (A / B plain, growth real, growth placebo seed 42) from the new dataset equal those from the backup → the v9 baselines stay valid; old run names unchanged (bare `--placebo` keeps the tag `placebo`).
- Margin placebo moves only margin values (growth and all other columns identical; 99.5% of rows get another stock's block).
- Date rules: every value used only strictly after its news date; no quarterly value > 365 days or TTM > 550 days old; never backwards. 2,760 sampled rows (304 stocks) match a plain-Python re-implementation exactly. Hand checks: NVDA Q3 FY17 (op. margin +13.1 pts) appears 2016-11-11; AAPL Q4 FY16 (release 2016-10-25) appears on the next weekly row, 2016-10-28.
- Coverage: 90–97% of rows from 2001 (TTM margins), 85–90% (changes). 10.8% of rows have gross margin exactly 100% (no cost of revenue reported, e.g. banks); kept as is (plan: revenue ≤ 0 is the only rule). Extremes don't matter: A and B rank inputs within each date.
- Correlations (per-date ranks): `gm_chg_q` / `om_chg_q` 0.54; strongest link to an older input `gp_yoy_q` ~0.5; all far below the 0.92 drop threshold.
- **Leak-power test** (dev rows 2005+, 3-month return vs SPY): `om_chg_q` IC real dates −0.0049, fake early dates (quarter end + 1 day) +0.0273, placebo +0.0002 (`gm_chg_q`: −0.0014 / +0.0227; `om_ttm`: +0.0098 / +0.0167; `gm_ttm`: −0.0053 / −0.0036). A leak would show; ours doesn't. With honest dates the margin changes barely rank 3-month returns → expect small gains, if any.
- Verdict script `scripts/batch_verdict.py 2` (reuses `step3_verdict.py`): smoke-tested on existing runs; baselines read back as +7.14% / +6.10%.

## Runbook (only after the user says `run`)

Follow `docs/STEP3_RUNBOOK.md` steps 0–7 with these changes:
- **Pre-flight:** `PYTHONPATH=. python -c "import pyarrow.parquet as pq; print('margins ok' if 'gm_ttm' in pq.read_schema('data/sharadar/derived/pit_dataset.parquet').names else 'OLD DATASET: STOP')"`; optional `PYTHONPATH=. python scripts/check_margin_features.py | tail -1` (~3 min, expect `50/50 checks passed`). No model copy, no control run (inputs proven identical instead).
- **Launch:** 4 batches of 6, one after another (~15 min each). Each block is one background command (Claude: `run_in_background: true`, `timeout: 7200000`) and starts with the same 2 setup lines as the runbook (`cd … && source .venv/bin/activate && mkdir -p artifacts/logs` and the `launch()` function). Then:
  - Batch 1 (Part 1, A): `launch v9_pit_with-margins --with=margins`, `… _s7 --with=margins --seed=7`, `… _s99 --with=margins --seed=99`, `launch v9_pit_with-margins_placebo-margins --with=margins --placebo=margins` (+ `_s7` / `_s99` with `--seed=7` / `--seed=99`), then `wait`.
  - Batch 2 (Part 1, B): the same six with `--without=rank_label` and names `v9_pit_no-rank_label_with-margins…`.
  - Batch 3 (Part 2, A): `--with=growth,margins` (names `v9_pit_with-growth_with-margins…`; placebo `--placebo=margins` → `…_placebo-margins…`).
  - Batch 4 (Part 2, B): batch 3 with `--without=rank_label` (names `v9_pit_no-rank_label_with-growth_with-margins…`).
  - Seed suffix goes last: e.g. `v9_pit_no-rank_label_with-growth_with-margins_placebo-margins_s7`.
- **Watch / check:** runbook steps 3–4 with `train_v9_*margins*` logs; expect 24 stats files `artifacts/backtest_stats_1y_v9_*margins*.csv`, every log `EXIT 0`, names match, configs show the right `fixes` / `placebo` / `seed`. Each log's `[seed]` line says `placebo: margins shuffled within each date` or `off`.
- **Verdict:** `PYTHONPATH=. python scripts/batch_verdict.py 2` (writes `artifacts/batch2_verdict.md`). It applies the locked rule; don't re-judge by hand. ON HOLD → audit first.
- **Then (info, not gates):** residual edge + SHAP on the final runs (`scripts/residual_edge.py`, `scripts/shap_report.py`); the fast-grower table (not built yet: write it after the verdict, design fixed above).
