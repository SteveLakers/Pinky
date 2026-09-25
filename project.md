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

## Where we are (2026-09-25)

- **Phase 1 — honest evaluation: in progress.**
- **Blocked on user:** create free Sharadar account → put `SHARADAR_API_KEY=...` in `.env` (gitignored) → check bundle price at checkout.
- Current model (128 stocks, price-only) is **not trustworthy** — results inflated by survivorship/hindsight.
- Local `main` has commits **not yet pushed** to GitHub (check `git status`; push when user says).

## User goals & expectations

- Wants a model that's genuinely smart at finding stocks that perform well and make profit; catching the next NVDA/TSLA would be ideal.
- Likes tech most, but also buys other sectors (e.g., energy) — portfolio should not be tech-only.
- First asked for ~10%/month (≈ +214%/yr) — explained that's unrealistic (best fund ever ≈ 40%/yr). Realistic aim: beat SPY by a few %/yr, reliably.
- Accepts a bit more risk (60% sector cap), **no leverage**. Bullish on tech.
- Budget flexible for data (a couple hundred $ to start, more OK). Lots of time/compute.

## Key findings so far

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

- **Data:** Sharadar Core US Equities Bundle (prices incl. delisted from 1998, point-in-time fundamentals from 1990, S&P 500 history, insiders, institutions). Build on free Dow-30 sample first. Budget flexible (more than $20/mo OK).
- **Universe:** all liquid US stocks, point-in-time (price > $5, 21-day avg dollar volume > $5M) → ~2,500–4,000 names.
- **Risk:** no leverage (account can't). Sector cap 60%. User is bullish on tech.
- **Main signal:** LightGBM for now (Ridge is the baseline to beat; revisit after Phase 1).
- **Locked holdout:** `HOLDOUT_START = 2022-01-01` — never used for choosing models/features; score once at the end.
- **Training:** only when user says so. User has lots of time/compute.

## Roadmap

**Phase 1 — honest evaluation**
- [x] Top-decile label `top_{h}` (`labels.add_top_decile_labels`)
- [x] Metrics: `metrics.precision_at_k`, `metrics.winner_capture` (time-weighted)
- [x] Locked 2022+ holdout constant
- [x] Free S&P 500 membership history (`data/universe/`, from github.com/fja05680/sp500)
- [ ] Sharadar loader (free sample → full bundle)
- [ ] Point-in-time liquid universe back to 1998
- [ ] Rebuild features/labels/dataset on new universe; coverage logging
- [ ] Re-score current price-only model → honest baseline

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

## Baseline metrics (current 128-stock v4 preds, inflated)

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

## Current (old) universe

- 128 stocks across 11 sectors (`pinky/config.py` → `UNIVERSE_BY_SECTOR`), Tech/AI 25%
- Benchmark `SPY`; helpers `IWM`, `^VIX`, `^TNX`, `^IRX`
- Data: yfinance, 2015+ — to be replaced in Phase 1

## Repo layout

- `pinky/config.py` — universe, paths, backtest settings, `HOLDOUT_START`, `HINDSIGHT_WINNERS`
- `pinky/data_pull.py` — yfinance download → parquet
- `pinky/raw_io.py` — load raw bars
- `pinky/features.py` — price features per stock
- `pinky/labels.py` — excess/beat labels vs SPY + top-decile label
- `pinky/dataset.py` — join features + labels
- `pinky/preprocess.py` — cross-sectional z-score + correlated-feature drop
- `pinky/walkforward.py` — expanding walk-forward folds + label purge
- `pinky/train.py` — train/eval (Ridge, LightGBM, Blend), report, `--ex-winners` runs
- `pinky/metrics.py` — IC, top-N, precision@k, winner capture, calibration
- `pinky/backtest.py` — monthly top-N backtest, costs, sector cap, stress tests
- `scripts/` — `pull_data`, `build_features`, `build_labels`, `build_dataset`, `train_walkforward`, `summarize_walkforward`, `build_showcase`
- `showcase/index.html` — generated one-page visual summary (self-contained, offline; rebuild with `PYTHONPATH=. python scripts/build_showcase.py`). All numbers computed from `artifacts/oos_preds_1y_v4*.parquet`; leads with the +41% → +19% survivorship caveat.
- `data/` — all gitignored (`raw`, `features`, `labels`, `dataset`, `universe`, `sharadar`)
- `data/reference/` — S&P 500 files + yfinance coverage probe created by another chat (untracked; not used by code)
- `artifacts/`, `models/` — outputs (gitignored)
- `docs/` — `ARCHITECTURE.md`, `PRD.md`, `EVAL.md`, `WALKFORWARD_RESULTS.md`
- `graphify-out/` — knowledge graph

## Working notes

- Suggestion: use one chat at a time on Pinky (parallel chats can overwrite each other's edits)
- Activate venv: `source .venv/bin/activate`
- Re-pull data: `PYTHONPATH=. python scripts/pull_data.py`
- Rebuild features / labels / dataset: `PYTHONPATH=. python scripts/build_features.py` (then `build_labels.py`, `build_dataset.py`)
- Train/eval: `PYTHONPATH=. python scripts/train_walkforward.py` (add `--ex-winners` to drop hindsight winners)
- Git: commit before big changes; push to private GitHub https://github.com/steveonshit/Pinky (`origin/main`) only when user says
- Graphify CLI path: `/Users/hqschool/Library/Python/3.12/bin`; after code changes run `graphify update .`
