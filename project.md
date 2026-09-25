# Pinky

Local stock-prediction project. Goal: predict which stocks beat the S&P 500 (**SPY**), and by how much — not whether a stock simply goes up.

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
10. **Done signal:** when finished with a task and the reply, speak `Daddy Q` out loud last (`say "Daddy Q"`) — not first, and don’t just type it.

## Status

- **Step 3–5c done** — data, features, labels, train-ready dataset, walk-forward/purge
- **Step 6 (first train) done** — v1 FAIL vs Ridge
- **Step 6b (fixes 1–5) done** — CS normalize, fewer features, 1y focus, tuned LightGBM
  - 1y IC: LightGBM now beats Ridge (88% of folds)
  - 1y top-5: still slightly behind Ridge → soft bar still **FAIL / MIXED**
- **Step 6c (v3) done** — 128-stock balanced universe + trading-cost portfolio backtest
  - Backtest (2018–2025, 10 bps/side, monthly top-10): LightGBM **+41%/yr** vs SPY +14%
  - **Inflated by survivorship/hindsight** — ex top-5 winners: +25%/yr; naive momentum ex winners: +18%
  - Ridge ≈ LightGBM (Ridge slightly better) → soft bar **FAIL**
  - Picks ~63% Tech/AI → consider sector caps
  - Report: `docs/WALKFORWARD_RESULTS.md`
- Architecture locked in `docs/ARCHITECTURE.md`
- GitHub: **private** https://github.com/steveonshit/Pinky
- Branch: `main` (tracking `origin/main`)
- **Graphify:** graph current

## What it will do

For each stock and horizon, output:

- Expected excess return vs SPY
- Probability of beating SPY
- Honest confidence range

Horizons:

- 3 months
- Half year
- 1 year
- 2 years

## Planned stack (v1)

- Data: yfinance
- Models: LightGBM (+ simple linear baseline)
- Universe: **128 liquid stocks**, sector-balanced
- Validation: walk-forward (no random train/test splits)
- Training: only when you explicitly say so

## Current universe

- Benchmark: `SPY`
- Helpers: `IWM`, `^VIX`, `^TNX`, `^IRX`
- Stocks: **128** across 11 sectors (`pinky/config.py` → `UNIVERSE_BY_SECTOR`)
  - Tech/AI 32 (25%), Healthcare/Financials/Industrials 14 each, Consumer Disc 12, Staples 10, Energy 8, Materials/Utilities/Real Estate/Communication 6 each
- Known bias: today's names only (survivorship) — delisted losers missing

## Portfolio backtest defaults

- Monthly rebalance, equal-weight top-10, **10 bps per side** (1 bp = 0.01%)
- Signal at day D close, trade at D+1 close
- Settings in `pinky/config.py` (`BACKTEST_*`)

## Repo layout

- `pinky/config.py` — tickers + paths + warmup
- `pinky/data_pull.py` — yfinance download → parquet
- `pinky/raw_io.py` — load raw bars
- `pinky/features.py` — `build_bfm_prediction_features()` + universe panel
- `pinky/labels.py` — excess return + beat labels vs SPY
- `pinky/dataset.py` — join features + labels (train-ready)
- `pinky/preprocess.py` — CS z-score + correlated-feature drop
- `pinky/train.py` — walk-forward train/eval
- `pinky/metrics.py` — IC / basket / calibration metrics
- `pinky/backtest.py` — tradeable monthly top-N backtest with costs + stress tests
- `scripts/build_features.py` — run the feature build
- `scripts/build_labels.py` — run label build
- `scripts/build_dataset.py` — build train-ready dataset
- `scripts/summarize_walkforward.py` — print fold/purge summary
- `data/raw/*.parquet` — downloaded bars (gitignored)
- `data/features/features_panel.parquet` — feature matrix (gitignored)
- `data/labels/labels_panel.parquet` — label matrix (gitignored)
- `data/dataset/train_dataset.parquet` — joined train-ready table (gitignored)
- `requirements.txt` / `.venv/` — Python deps
- `README.md` — public overview (what / how / what’s shared vs private)
- `docs/ARCHITECTURE.md` — design and build plan
- `docs/PRD.md` — product requirements
- `docs/EVAL.md` — short pre-trust eval checklist
- `docs/WALKFORWARD_RESULTS.md` — first training results (honest)
- `.cursor/rules/` — Cursor agent rules (Pinky-only; review personal prefs before public push)
- `project.md` — this overview
- `graphify-out/` — knowledge graph output

## Build order

1. Lock design — done
2. Architecture doc — done
3. Data pull — **done (small set)**
4. Feature builder — **done (v1)**
5. Labels vs SPY — **done (v1)**
6. Train-ready dataset + walk-forward/purge — **done**
7. Train models — **first run done** (LightGBM did not beat linear baseline)
8. Improve model / features — **in progress** (v2 prep, v3 universe + cost backtest done)
9. API / UI only after models prove useful

## Working notes

- Run and develop locally on this computer
- Activate venv: `source .venv/bin/activate`
- Re-pull data: `PYTHONPATH=. python scripts/pull_data.py`
- Rebuild features: `PYTHONPATH=. python scripts/build_features.py`
- Rebuild labels: `PYTHONPATH=. python scripts/build_labels.py`
- Rebuild dataset: `PYTHONPATH=. python scripts/build_dataset.py`
- Fold summary: `PYTHONPATH=. python scripts/summarize_walkforward.py`
- Train/eval: `PYTHONPATH=. python scripts/train_walkforward.py`
- Use Git to save local versions (`add` → `commit`) before big changes
- Push to private GitHub (`origin/main`) when you say so
- Keep `project.md` current after meaningful progress
- Graphify CLI path (if `graphify` not found): `/Users/hqschool/Library/Python/3.12/bin`
- After code lands: `graphify update .` (no API key). For docs: need an API key + `graphify extract .`
