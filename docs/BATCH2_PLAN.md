# Batch 2 plan: margin expansion (DRAFT)

**Status:** drafted 2026-10-16 (Claude Opus 5.5). **Not approved yet:** show the user a short summary and get their OK before writing code or training. Nothing is built or run.

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

## Ask the user

- OK with the 4 features and 24 runs? (Smaller option: Part 1 only, 12 runs.)
