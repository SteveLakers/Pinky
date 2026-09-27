# Pinky

Local stock-prediction project. **Goal: predict stocks that will perform well and make us profit** — beat the S&P 500 (**SPY**).

- **Favor tech**, and especially **finding future big winners** early ("the next NVDA/TSLA").
- **Still buy other sectors** (energy, industrials, etc.) when they're the best picks — not tech-only.

## ▶ Resume here (new chat: read this first)

Last updated **2026-09-26**, end of session. Phase 1 code commit: `c0cdfe7`.

**State**
- Phase 1 (honest evaluation) is **done**. Phase 2 has **not started**.
- Honest result: the price-only model has **no reliable edge** (Ridge ≈ market, LightGBM loses money). Details in Key findings.
- 13 local commits are **not pushed** (check: `git log origin/main..main --oneline`). Push only when the user says.

**Waiting on the user — ask these first, don't assume answers**
1. Which Phase 2 model fixes to add (list under Roadmap). Recommended: all four.
2. Showcase page still shows the old inflated +41%. Update now (recommended), after Phase 2, or leave?
3. OK to push to GitHub?

**Before Phase 2 work:** it's a hard task → ask the user to confirm they're on the **highest model** (Rule 10).

**Proposed Phase 2 first batch (confirm with user before building)**
1. New `pinky/fundamentals.py`: load `data/sharadar/fundamentals.parquet`, **ARQ + ART rows only**. Attach to dataset rows with `merge_asof` on the **filing `date`** (backward, by ticker) → point-in-time.
2. Growth + revenue acceleration features: quarterly revenue growth vs the same quarter last year, TTM revenue growth, acceleration (this quarter's YoY growth minus last quarter's), gross-profit growth, days since last filing.
   - Find "same quarter last year" by `calendardate`, not by row offset (filings can be missing or late).
3. Size feature: log market cap from `data/sharadar/daily.parquet` (`marketcap`, daily).
4. Approved model fixes go in `pit_dataset.py` / `preprocess.py` / `train.py`.
5. Run `train_walkforward.py --pit` under a new tag; compare to v5_pit; keep only what helps.
- **Bar to beat (v5_pit):** Ridge +7.6%/yr, rank IC 0.066; SPY +6.9%/yr (2001–2020).
- Never touch the 2022+ holdout until the final test.

**Data facts for Phase 2**
- Fundamentals ARQ: filing dates 1993 → 2026, 17,045 tickers, revenue filled 97% (ART 92%).
- 9,492 of the 10,043 dataset stocks (95%) have ARQ rows.
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
- Untracked `data/reference/` and `graphify-out/2026-09-2*/` come from other chats — leave them alone.
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

**Phase 2 model fixes (from Phase 1 findings — need user OK):**
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

- Monthly rebalance, equal-weight top-10, **10 bps per side** (also reported at 25 bps).
- Sector cap 60% of picks (`BACKTEST_MAX_SECTOR_SHARE`). Signal at day D close, trade at D+1 close.
- Signals compared: LightGBM, Ridge, Blend (avg daily rank), naive 12-1 momentum. Settings: `pinky/config.py` (`BACKTEST_*`).

## Repo layout

- `pinky/config.py` — universe rules, paths, backtest settings, `HOLDOUT_START`, `DELIST_RETURN_PERFORMANCE`
- `pinky/sharadar.py` — Sharadar API: bulk download → parquet, small queries (key never printed)
- `pinky/universe.py` — point-in-time universe panels, delisting-aware `tr` panel, sectors, SPY, `backtest_prices()`
- `pinky/pit_dataset.py` — weekly features + labels on the point-in-time universe
- `pinky/preprocess.py` — per-day z-score + correlated-feature drop
- `pinky/walkforward.py` — expanding walk-forward folds + label purge (`calendar` param)
- `pinky/train.py` — Ridge / LightGBM / Blend, report, `pit=True` and `exclude` runs, `dev_rows`
- `pinky/metrics.py` — IC, top-N, precision@k, winner capture, calibration
- `pinky/backtest.py` — monthly top-N backtest, costs, sector cap (`sectors` param), stress tests
- Legacy (128 stocks, yfinance): `data_pull.py`, `raw_io.py`, `features.py`, `labels.py`, `dataset.py`
- `scripts/` — `pull_sharadar`, `train_walkforward`, `build_showcase`, plus legacy build scripts
- `showcase/index.html` — one-page visual (offline). Still shows the old v4 numbers.
- `data/sharadar/` (~6 GB, gitignored, never share) — tables (`*.parquet`), `zips/`, `panels/` (Date × Ticker), `spy.parquet`, `derived/pit_dataset.parquet`
- `artifacts/`, `models/` — outputs (gitignored). `docs/` — `WALKFORWARD_RESULTS.md`, `ARCHITECTURE.md`, `PRD.md`, `EVAL.md`
- `AGENTS.md`, `.cursor/rules/` — agent instructions. `graphify-out/` — knowledge graph.

## Commands

- Activate venv: `source .venv/bin/activate` (run everything from the repo root with `PYTHONPATH=.`)
- Sharadar pipeline:
  1. Pull: `python scripts/pull_sharadar.py` (~10 min, needs network)
  2. Universe panels: `python -m pinky.universe` (~1 min)
  3. Dataset: `python -m pinky.pit_dataset` (~1 min)
  4. Train/eval: `python scripts/train_walkforward.py --pit` (~8 min)
- Legacy: `pull_data.py` → `build_features.py` → `build_labels.py` → `build_dataset.py` → `train_walkforward.py` (`--ex-winners` drops hindsight winners)
- Showcase: `python scripts/build_showcase.py`
- GitHub (private): https://github.com/steveonshit/Pinky (`origin/main`) — push only when the user says.
- Graphify CLI: `/Users/hqschool/Library/Python/3.12/bin`; run `graphify update .` after code changes.
- Tip: use one chat at a time on Pinky (parallel chats can overwrite each other's edits).
