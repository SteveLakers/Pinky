# Growth round 2 plan (DRAFT)

**Status:** drafted 2026-10-19 (Claude Opus 5.5). **User decisions 2026-10-19 (end of the batch 2 chat):** test the 4 columns **one by one, then all together**; the 2-year label later. Open points answered 2026-10-21 (60 runs, one test at a time, same locked rule; user chose to continue on Opus 5.5). Exact design: section "Design" at the bottom. Code built and checked 2026-10-21 (section Code checks). No runs yet: train only after the user says `run`.

## Why a round 2

- v8 growth: DROP (real − placebo +0.26 / +0.98%/yr; bar +1.0%).
- SHAP (2026-10-16): the models already give growth ~22% of the ranking weight, so "growth weighs too little" is not the problem.
- Data: the fastest 20% of growers have the worst median next year but the most big winners **and** the most crashes. Past growth is a lottery ticket. Round 2 should look for what **separates winners from crashers among growers**, not more growth columns.
- Batch 2 (2026-10-19): margins DROP in every test, so round 2's base = the plain baselines. The fast-grower table shows margin **change** doesn't separate winners (big winners flat at 11–14% across groups), but **being loss-making** does mark the lottery tickets (17% big winners and 18% crashes vs 11% / 9.5% for profitable fast growers). The separator must come from somewhere else: the market's reaction to the news (idea 1) is the strongest candidate.

## Candidate ideas (pick 2–3 before any results)

| # | Idea | Columns | Data | Notes |
|---|---|---|---|---|
| 1 | **Market's reaction to the report** | `ear_3d`: stock return minus SPY, trading days −1…+1 around the latest earnings announcement | events (code 22) + `tr` prices: have it | Classic signal (post-earnings drift). Usable only from day +2 (strictly after the window closes). Announcements start Aug 2004; before that, the filing date (weaker), so 2001–04 is thin → the 2001–08 half test is harder. Overlaps Roadmap 4. |
| 2 | **Sales surprise vs own trend** | `rev_sue`: this quarter's sales growth minus the mean of the previous 4 quarters, divided by their spread | ARQ: have it | No analyst estimates in Sharadar, so "surprise" = vs the company's own trend. Needs 8 quarters of history. |
| 3 | **Multi-year and steady growth** | `rev_cagr_3y` (12-month sales vs 3 years earlier), `rev_up_quarters` (of the last 8 quarters, how many grew vs a year ago) | ART / ARQ: have it | Steady growers vs one-off jumps. |
| 4 | **Rule of 40** | `rule40`: 12-month sales growth + operating margin | have it | SaaS rule of thumb. Only worth it if batch 2 shows margins matter. |
| 5 | **Longer label (2 years)** | none (changes the target) | have it | Not a feature test: a new model target. Dev rows lose a year; overlapping labels make it noisier. Later, separately. |

## Recommendation

- **One new group `growth2` with 4 columns: `ear_3d`, `rev_sue`, `rev_cagr_3y`, `rev_up_quarters`** (ideas 1–3). Few columns on purpose: extra columns cost A ~1%/yr even when real.
- Base = whatever batch 2 keeps for each version (baseline, margins, or growth + margins).
- Test it alone on that base: A and B × seeds 42 / 7 / 99 × real / placebo (`--placebo=growth2`) = **12 runs** (~30 min).
- Same locked keep rule as batch 2 (real − placebo ≥ +1.0%/yr overall and ≥ +0.5%/yr each half; real ≥ the base), plus a leak audit if the gap is > +3%/yr.
- Same checks as batches 1–2 before any run: made-up cases, independent recompute, leak-power test (fake early dates must look better), placebo sanity, old columns identical.
- Info after the runs: SHAP; the fast-grower table, split by `ear_3d` and `rev_sue`.

## Decisions for the user (asked 2026-10-19)

1. Ideas: 1a = 1 + 2 + 3 in one group (my pick) | 1b = only 1 (the reaction) | 1c = other mix.
2. Longer label (idea 5): 2a = later, separately (my pick) | 2b = now.

## User decisions (2026-10-19)

User: "1, can we do one by one, and than at last everything together, this way we can see which helps and which doesn't. 2a". So the Recommendation above (one group) is replaced by:
- **5 tests**, each its own feature group, all on the plain baselines (A `v9_pit`, B `v9_pit_no-rank_label`):
  1. `ear_3d` alone (price reaction to the latest earnings report)
  2. `rev_sue` alone (sales surprise vs own trend)
  3. `rev_cagr_3y` alone (3-year sales growth)
  4. `rev_up_quarters` alone (quarters of growth out of the last 8)
  5. all 4 together (placebo shuffles all 4 as one block: needs `--placebo` to take several groups, or a 5th group holding all 4)
- Each test: A and B × seeds 42 / 7 / 99 × real / placebo = 12 runs → **60 runs** (~2.5 h, 10 batches of 6).
- 2-year label: later, as a separate test.

**Open points (asked 2026-10-21; user: "continue on opus 5.5 1a 2a", tests one at a time):**
- 60 runs: yes (1a). Run **one test at a time** (12 runs each), result shown after each, in the fixed order 1 → 5. All 5 run whatever the early results say (no stopping after a KEEP or a DROP).
- Same locked rule for every test (2a): real − placebo ≥ +1.0%/yr and ≥ +0.5%/yr each half; real ≥ baseline. If several KEEP for a version, the highest real mean wins (batch 2's tie-break).
- Caveats (told the user): 5 tests × 2 versions = 10 chances, so one lucky KEEP is plausible; only the 2022+ holdout settles it. A single column rarely moves a portfolio +1%/yr, so DROP on the singles is likely even if one of them carries real information (its IC and SHAP share are reported as info). A column tested alone can miss value it only adds with the others: test 5 covers that.

## Design (pinned 2026-10-21, before any code ran on results)

Same date rules as growth and margins (`pinky/fundamentals.py`): ARQ / ART only, news date = earnings announcement (code 22) or SEC filing, first-filed report, filings < 10 days after period end skipped, used only strictly after the news date, a late catch-up filing never replaces a newer quarter, stale quarter > 365 days / TTM > 550 days → missing. Missing values become the day's middle rank (as for growth).

| Test | Group | Column | Definition |
|---|---|---|---|
| 1 | `ear` | `ear_3d` | Stock return (`tr`, delisting-aware) minus SPY over trading days −1…+1 around the latest quarter's news date: day 0 = first trading day on or after the news date; return from the close of day −2 to the close of day +1. Used only on rows **after day +1** (so from day +2). Missing if the stock has no price at either end. Before Aug 2004 the news date is the filing date (weaker). |
| 2 | `sue` | `rev_sue` | (this quarter's `rev_yoy_q` − mean of the previous 4 quarters' `rev_yoy_q`) / max(their sample std, 0.01). All 4 previous quarters must exist and be public by this quarter's news date. |
| 3 | `cagr` | `rev_cagr_3y` | (12-month revenue / 12-month revenue 3 years earlier)^(1/3) − 1 (ART); both > 0, the earlier report public first. |
| 4 | `steady` | `rev_up_quarters` | Of this and the previous 7 quarters, how many had `rev_yoy_q` > 0 (0–8). All 8 must be known and public by this quarter's news date. |
| 5 | `growth2` | all 4 | Can't be combined with groups 1–4 (same columns). |

- Each test: `--with=<group>` (real) and `--with=<group> --placebo=<group>` (that group shuffled within each date), A and B, seeds 42 / 7 / 99.
- Run names: `v9_pit_with-ear`, `v9_pit_with-ear_placebo-ear` (+ `_s7`, `_s99`); B: `v9_pit_no-rank_label_with-ear…`. Same pattern for `sue`, `cagr`, `steady`, `growth2`.
- Verdict: `scripts/batch_verdict.py 3` judges every test whose 12 runs exist; the final pick and A vs B only once all 5 are in.
- Checks before any run (`scripts/check_growth2_features.py`): made-up cases, dataset vs the batch 2 backup (old columns identical, exactly 4 added), old training frames unchanged, date rules on real data, independent slow recompute, hand checks, coverage, correlations, leak-power test (fake early dates must look better), placebo sanity.

## Code checks (2026-10-21, before any run)

- Built (Claude Opus 5.5): `pinky/fundamentals.py` (4 columns, groups `ear` / `sue` / `cagr` / `steady` / `growth2`), `pinky/pit_dataset.py` (attached after margins), `pinky/train.py` (groups; columns of off groups dropped unless an on group uses them; groups sharing columns can't be on together), `scripts/check_growth2_features.py`, `scripts/batch_verdict.py 3`, SHAP labels.
- `check_growth2_features.py` **85/85**; `check_growth_features.py` 59/59; `check_margin_features.py` 50/50 (their dataset checks now allow the round 2 columns after margins). Log: `artifacts/logs/check_growth2_features.log`.
- Dataset rebuilt (41 s); backup of the batch 2 dataset: `data/sharadar/derived/pit_dataset_batch2.parquet`. Same 2,932,585 rows in the same order, all old columns identical, exactly the 4 round 2 columns added.
- With the round 2 groups off, the model frames (plain, growth, growth placebo, margins + margin placebo, growth + margins) equal those from the backup → v9 baselines and batch 2 runs stay valid. Each group adds only its own columns; its placebo moves only them (|rank corr| real vs placebo < 0.01).
- Date rules: reaction known on the trading day after day 0, always strictly after the news date (median 1 day; the 20,909 reports with a bigger gap were published before the price data starts in 1998 and have no reaction value); every value used only strictly after it was known; no quarterly value > 365 days or TTM > 550 days old; never backwards. 2,686 sampled rows (304 stocks) match a plain-Python re-implementation.
- Hand checks: NVDA Q3 FY17 (news 2016-11-10, reaction +22.5% vs SPY) shows on the first row after 2016-11-11, not before; AAPL Q4 FY16 (news 2016-10-25, −0.8%) from 2016-10-28.
- Coverage: `ear_3d` 90–97% of rows every year; the sales columns 74–88% from 2002 on, thinner before (2001: `rev_cagr_3y` 48%, `rev_up_quarters` 67%; they need 3 years of history), so 2001–02 rows lean on the middle-rank fill.
- Correlations (per-date ranks): `rev_cagr_3y` / `rev_up_quarters` 0.62; strongest links to older inputs: `rev_sue`–`rev_accel` 0.69, `ear_3d`–`mom_63` 0.36; all below the 0.92 drop threshold.
- **Leak-power test** (dev rows 2005+, 3-month return vs SPY), rank IC real dates | fake early dates (quarter end + 1 day) | placebo: `ear_3d` +0.0073 | +0.1545 | −0.0002; `rev_sue` +0.0047 | +0.0288 | +0.0001; `rev_cagr_3y` −0.0014 | +0.0002 | +0.0003; `rev_up_quarters` +0.0182 | +0.0210 | −0.0002. A leak would show; ours doesn't. With honest dates only `rev_up_quarters` ranks 3-month returns a little; expect small gains, if any.
- Not covered: the review's "fundamental availability" risk (values from the filing dated at the earlier announcement) applies to all fundamentals since v8; it doesn't touch `ear_3d`, which uses prices only.

## Runbook (only after the user says `run`; one test at a time)

Follow `docs/STEP3_RUNBOOK.md` steps 0–7 with these changes:
- **Pre-flight:** `PYTHONPATH=. python -c "import pyarrow.parquet as pq; print('round 2 ok' if 'ear_3d' in pq.read_schema('data/sharadar/derived/pit_dataset.parquet').names else 'OLD DATASET: STOP')"`; optional `PYTHONPATH=.:scripts python scripts/check_growth2_features.py | tail -1` (expect all checks passed). No model copy, no control run (old frames proven identical instead).
- **One test = 12 runs = 2 batches of 6** (A, then B; ~15 min each). Order: `ear`, `sue`, `cagr`, `steady`, `growth2`. After each test: verdict, short result to the user, then the next test (all 5 run whatever the results).
- **Launch** (group `g`): each batch is one background command (Claude: `run_in_background: true`, `timeout: 7200000`) starting with the runbook's 2 setup lines (`cd … && source .venv/bin/activate && mkdir -p artifacts/logs` and the `launch()` function). Then:
  - A: `launch v9_pit_with-$g --with=$g`, `launch v9_pit_with-${g}_s7 --with=$g --seed=7`, `launch v9_pit_with-${g}_s99 --with=$g --seed=99`, `launch v9_pit_with-${g}_placebo-$g --with=$g --placebo=$g` (+ `_s7` / `_s99` with `--seed=7` / `--seed=99`), then `wait`.
  - B: the same six with `--without=rank_label` and names `v9_pit_no-rank_label_with-$g…`.
  - Seed suffix goes last: e.g. `v9_pit_no-rank_label_with-steady_placebo-steady_s7`.
- **Watch / check:** runbook steps 3–4 with `train_v9_*with-$g*` logs; expect 12 stats files `artifacts/backtest_stats_1y_v9_*with-${g}*.csv` per test, every log `EXIT 0`, names match, configs show the right `fixes` / `placebo` / `seed`; each log's `[seed]` line says `placebo: <g> shuffled within each date` or `off`.
- **Verdict:** `PYTHONPATH=.:scripts python scripts/batch_verdict.py 3` (writes `artifacts/batch3_verdict.md`): judges every test whose 12 runs exist, lists the rest as not run yet; final pick + A vs B once all 5 are in. It applies the locked rule; don't re-judge by hand. ON HOLD → audit first.
- **Then (info, not gates):** per test, the new column's IC and SHAP share; after all 5, residual edge + SHAP on the finals and the fast-grower table split by `ear_3d` and `rev_sue`.
