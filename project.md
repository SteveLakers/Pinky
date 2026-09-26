# Pinky

Local stock-prediction project. **Goal: predict stocks that will perform well and make us profit** — beat the S&P 500 (**SPY**).

- **Favor tech**, and especially **finding future big winners** early ("the next NVDA/TSLA").
- **Still buy other sectors** (energy, industrials, etc.) when they're the best picks — not tech-only.

## Rules (always on)

These rules apply at all times, no exceptions, unless you explicitly say otherwise.
Mirrored in `.cursor/rules/` so Cursor loads them every Pinky chat.

1. **Never lie.** Be honest. Never fake data, results, or information.
2. **Double-check before answering.** Verify claims before responding.
3. **Be concise.** Straight to the point. No filler. Make the point ASAP so it’s easy to understand.
4. **No exceptions** to these rules unless you say otherwise.
5. **Auto-update `project.md`.** Especially after finishing a big feature or update; also refresh it periodically as the project changes.
6. **Challenge bad ideas.** If you’re wrong, or if there’s a better solution, say so.
7. **Stress-test your thinking.** Always consider whether what you’re doing or saying is the best approach. If not, say so. You won’t be mad.
8. **Actively hunt for mistakes.** Continuously check statements, assumptions, plans, and requests for errors, gaps, or weaker approaches. When found, tell you right away — no waiting, soft-pedaling, or silence.
9. **Every new chat:** agent must read `project.md` first.
10. **HIGHEST MODELS — top priority, all agents.** Go very heavy on higher/highest models for reasoning, planning, decisions, and thinking. Token cost doesn't matter to the user. Never downgrade to save cost (`.cursor/rules/strong-models.mdc`).
    - User runs Cursor on **Auto**; agents can't change the main model → **before a hard task, or if a task turns hard mid-way: STOP, ask the user to switch to the highest model, and wait** before doing the work (unless the user says continue).
    - Hard sub-work → subagents on the strongest model; copy this rule into every subagent prompt.
11. **Communication:** simple, plain sentences; bullet points; **ask before large decisions/changes** (`.cursor/rules/communication.mdc`).
12. **Graphify first:** run `graphify query/explain/path` before exploring code; `graphify update .` after code changes (`.cursor/rules/graphify.mdc`).

## Where we are (2026-09-26)

- **Phase 1 — honest evaluation: done (dev window 2001–2020).**
- Sharadar bundle active; full history pulled to `data/sharadar/` (never commit — license).
- **Honest baseline: the price-only model has no reliable edge on the realistic universe.** Ridge ≈ market; LightGBM loses money (picks volatile "lottery tickets"). See Key findings.
- Old +41% / +19% results were inflated by survivorship + hindsight (128 of today's big names).
- **Next: Phase 2** — company data, growth + revenue acceleration first.
- `showcase/index.html` still shows the **old 128-stock numbers** — needs an update decision.
- Local `main` has commits **not yet pushed** to GitHub (push only when user says).

### Open items

- [ ] Push unpushed commits to GitHub (awaiting OK)
- [ ] Showcase: update to honest v5 numbers? (ask user)
- [ ] Optional: host showcase online (e.g., Vercel) — would be public; needs user OK on content
- [ ] Phase 2 is a hard design task → **user on the highest model before starting**
- [ ] Approve the Phase 2 model fixes (see Roadmap)

## User goals & expectations

- Wants a model that's genuinely smart at finding stocks that perform well and make profit; catching the next NVDA/TSLA would be ideal.
- Likes tech most, but also buys other sectors (e.g., energy) — portfolio should not be tech-only.
- First asked for ~10%/month (≈ +214%/yr) — explained that's unrealistic (best fund ever ≈ 40%/yr). Realistic aim: beat SPY by a few %/yr, reliably.
- Accepts a bit more risk (60% sector cap), **no leverage**. Bullish on tech.
- Budget flexible for data (a couple hundred $ to start, more OK). Lots of time/compute.

## Key findings so far

### Honest baseline — v5_pit (2026-09-26)

Point-in-time liquid US universe, delisted stocks included, 1y signal, monthly top-10, 10 bps, **Jan 2001 → Feb 2020** (19 walk-forward test years; 2022+ holdout untouched).

| Signal | CAGR | Max DD | Precision@10 | Winner capture |
|---|---|---|---|---|
| SPY | +6.9% | −52% | — | — |
| Equal-weight whole universe | +7.5% | — | 0.10 (random) | 0.005 (random) |
| Ridge | +7.6% | −47% | 0.08 | 0.019 |
| Blend | +0.6% | −68% | 0.10 | 0.028 |
| LightGBM | **−8.0%** | −87% | 0.15 | 0.027 |
| Naive 12-1 momentum | −1.4% | −84% | 0.17 | 0.048 |

- 60% sector cap barely changes anything here (picks already spread out).
- LightGBM's picks: 1.5× random chance of a top-10% winner, but 2.6× the normal chance of losing >50% vs SPY. **Price data predicts how much a stock moves, not which way.**
- Ridge picks calm, rising stocks → about market return, smaller drawdowns.
- Different window than the old tests below (2001–2020 vs 2018–2025) — not directly comparable.
- Report: `artifacts/walkforward_summary_v5_pit.md`; history: `docs/WALKFORWARD_RESULTS.md`.

### Old 128-stock results (inflated — kept for reference)

| Test (1y signal, monthly top-10, 10 bps, 2018–Oct 2025) | CAGR |
|---|---|
| SPY | +14% |
| LightGBM, 60% sector cap, 128 stocks | +41% |
| Same, **NVDA/SMCI/TSLA/PLTR/AVGO removed from train + test** | **+19%** |
| Ridge (uncapped), same 5 removed | +26% |
| Naive 12-1 momentum, same 5 removed | +18% |
| Equal-weight all 123 remaining | +16% |

- Most of the +41% came from 5 hindsight winners. Real edge is small.
- Ridge beats LightGBM once winners are removed.
- Max drawdown worse than SPY for all models (−31% to −35% vs −23%).
- Only ~8 independent years of data (2016+, overlapping 1y labels) → not enough to learn subtle patterns.
- Features are price-only → can only see winners after they're obvious.
- Honest target for a good model: **~2–5%/yr over SPY**, not +41%. ~30–40% chance the honest edge is ~zero.
- Full history: `docs/WALKFORWARD_RESULTS.md` (v1 → v4 ex5).

## Decisions

- **Data:** Sharadar Core US Equities Bundle — active. Direct API, bulk tables (prices incl. delisted from 1998, fundamentals, S&P 500 history, corporate actions, daily valuation metrics, events). Key in `.env` (gitignored, never print it).
- **Fundamentals:** only As-Reported dimensions **ARQ / ART / ARY** — dated by SEC filing date (point-in-time). MR* rows are dated at quarter-end → ~2.5 months of future leak. Never use MR*.
- **Universe (`pinky/universe.py`):** each day, stocks with price ≥ $5 and 21-day avg dollar volume ≥ $5M (nominal $). Common stock + ADRs + Canadian; no preferreds, no secondary share classes, no SPACs (SIC 6770); NYSE / NASDAQ / NYSE American only. Result: **1,200–2,850 stocks per day, 11,561 distinct** (1998–2026). Fewer than the ~2,500–4,000 first estimated because $5M is not inflation-adjusted.
- **Delistings:** exit value is reinvested in SPY. Bankruptcy / liquidation / regulatory delistings also take **−30%** on the last price (Shumway 1997). No stock silently drops out.
- **Dataset rows:** weekly (every 5th trading day); folds use the daily calendar. Stocks need 1y of price history to be scored (same as before — hides new IPOs for a year; fix in Phase 2).
- **Sectors:** new universe uses Sharadar sectors (current classification) for the cap. The custom "Tech/AI" bucket only applies to the old 128-stock universe.
- **Risk:** no leverage (account can't). Sector cap 60%. User is bullish on tech.
- **Main signal:** undecided. On the honest data Ridge ≈ market and LightGBM loses money. Revisit in Phase 2.
- **Locked holdout:** `HOLDOUT_START = 2022-01-01`. Dev runs only use rows whose label ends before it (`train.dev_rows`). Score the holdout once, at the very end.
- **Training:** only when user says so. User has lots of time/compute.

## Roadmap

**Phase 1 — honest evaluation**
- [x] Top-decile label `top_{h}` (`labels.add_top_decile_labels`)
- [x] Metrics: `metrics.precision_at_k`, `metrics.winner_capture` (time-weighted)
- [x] Locked 2022+ holdout constant
- [x] Free S&P 500 membership history (`data/universe/`, from github.com/fja05680/sp500)
- [x] Sharadar loader + full bulk pull (`pinky/sharadar.py`)
- [x] Point-in-time liquid universe back to 1998 (`pinky/universe.py`)
- [x] Rebuild features/labels/dataset on new universe (`pinky/pit_dataset.py`)
- [x] Re-score current price-only model → honest baseline (v5_pit)

**Phase 2 model fixes (proposed from Phase 1 findings — need user OK):**
- Train on each day's **return rank** instead of raw return (a few +5,000% stocks pull LightGBM toward lottery tickets).
- Scale features by **daily rank** instead of z-score (one bad tick can squash a whole day).
- Let stocks **without 1y of history** be scored (so a new PLTR isn't invisible for a year).
- Add **size** (market cap) as a feature.

**Phase 2 — company data (what to look at)**, added in batches, keep only what beats baseline:
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

## Baseline metrics

Honest (v5_pit): see Key findings table (precision@10, winner capture).

Old 128-stock v4 preds (inflated):

| | LightGBM | Ridge | Random |
|---|---|---|---|
| precision@10 (picks that end up top-10%) | 0.32 | 0.34 | 0.10 |
| Winner capture (time holding year's top-20) | 0.25 | 0.25 | 0.08 |

Random = mean of 20 random-score runs (matches theory: 0.10 and 10/128 ≈ 0.08).

## Portfolio backtest defaults

- Monthly rebalance, equal-weight top-10, **10 bps per side** (1 bp = 0.01%)
- Sector cap: max **60%** of picks per sector (`BACKTEST_MAX_SECTOR_SHARE`)
- Signal at day D close, trade at D+1 close
- Signals compared: LightGBM, Ridge, Blend (avg daily rank), naive momentum
- Settings in `pinky/config.py` (`BACKTEST_*`)

## Old (legacy) universe

- 128 stocks across 11 sectors (`pinky/config.py` → `UNIVERSE_BY_SECTOR`), Tech/AI 25%
- Benchmark `SPY`; helpers `IWM`, `^VIX`, `^TNX`, `^IRX`
- Data: yfinance, 2015+ — replaced by the Sharadar point-in-time universe (still runnable without `--pit`)

## Repo layout

- `pinky/config.py` — universe rules, paths, backtest settings, `HOLDOUT_START`, `HINDSIGHT_WINNERS`
- `pinky/sharadar.py` — Sharadar API: bulk download → parquet, small queries (key never printed)
- `pinky/universe.py` — point-in-time universe panels + delisting-aware total-return panel (`tr`), sectors, SPY
- `pinky/pit_dataset.py` — weekly features + labels on the point-in-time universe
- `pinky/data_pull.py` — yfinance download → parquet (legacy)
- `pinky/raw_io.py` — load raw bars
- `pinky/features.py` — price features per stock
- `pinky/labels.py` — excess/beat labels vs SPY + top-decile label
- `pinky/dataset.py` — join features + labels
- `pinky/preprocess.py` — cross-sectional z-score + correlated-feature drop
- `pinky/walkforward.py` — expanding walk-forward folds + label purge
- `pinky/train.py` — train/eval (Ridge, LightGBM, Blend), report, `--ex-winners` and `--pit` runs
- `pinky/metrics.py` — IC, top-N, precision@k, winner capture, calibration
- `pinky/backtest.py` — monthly top-N backtest, costs, sector cap, stress tests
- `scripts/` — `pull_sharadar`, `pull_data`, `build_features`, `build_labels`, `build_dataset`, `train_walkforward`, `summarize_walkforward`, `build_showcase`
- `showcase/index.html` — generated one-page visual summary (self-contained, offline; rebuild with `PYTHONPATH=. python scripts/build_showcase.py`). All numbers computed from `artifacts/oos_preds_1y_v4*.parquet`; leads with the +41% → +19% survivorship caveat.
- `data/` — all gitignored (`raw`, `features`, `labels`, `dataset`, `universe`, `sharadar`)
- `data/sharadar/` — vendor tables (`*.parquet`), `zips/` (raw downloads), `panels/` (Date × Ticker), `derived/pit_dataset.parquet`. ~6 GB. Never commit or share.
- `data/reference/` — S&P 500 files + yfinance coverage probe created by another chat (untracked; not used by code)
- `artifacts/`, `models/` — outputs (gitignored)
- `docs/` — `ARCHITECTURE.md`, `PRD.md`, `EVAL.md`, `WALKFORWARD_RESULTS.md`
- `AGENTS.md` — short instructions for any agent tool (read project.md, highest models, stop-and-ask rule)
- `.cursor/rules/` — `pinky-rules`, `communication`, `graphify`, `read-project-md`, `strong-models`
- `graphify-out/` — knowledge graph

## Working notes

- Suggestion: use one chat at a time on Pinky (parallel chats can overwrite each other's edits)
- Activate venv: `source .venv/bin/activate`
- **Sharadar pipeline (current):**
  1. Pull: `PYTHONPATH=. python scripts/pull_sharadar.py` (all tables; ~10 min, needs network)
  2. Universe panels: `PYTHONPATH=. python -m pinky.universe` (~1 min)
  3. Dataset: `PYTHONPATH=. python -m pinky.pit_dataset` (~1 min)
  4. Train/eval: `PYTHONPATH=. python scripts/train_walkforward.py --pit` (~8 min)
- Legacy (128 stocks, yfinance): `pull_data.py` → `build_features.py` → `build_labels.py` → `build_dataset.py` → `train_walkforward.py` (add `--ex-winners` to drop hindsight winners)
- Rebuild showcase: `PYTHONPATH=. python scripts/build_showcase.py` (after new results)
- Git: commit before big changes; push to private GitHub https://github.com/steveonshit/Pinky (`origin/main`) only when user says
- Graphify CLI path: `/Users/hqschool/Library/Python/3.12/bin`; after code changes run `graphify update .`
