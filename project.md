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

- **Step 3 (data pull) done** — expanded liquid universe in `data/raw/`
- **Step 4 (feature builder) done** — `data/features/features_panel.parquet` (~156k rows, 58 tickers)
- **Step 5 (labels vs SPY) done** — `data/labels/labels_panel.parquet`
  - Horizons: 3m/63d, 6m/126d, 1y/252d, 2y/504d
  - Expanded-universe beat rates ~52–55% (was ~60–78% on old mega-10 — bias reduced)
- **Training:** not started (wait for explicit go)
- Architecture locked in `docs/ARCHITECTURE.md`
- GitHub: **private** repo at https://github.com/steveonshit/Pinky (invite collaborator next)
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
- Universe: **58 liquid stocks** now; expand further later if needed
- Validation: walk-forward (no random train/test splits)
- Training: only when you explicitly say so

## Current universe

- Benchmark: `SPY`
- Helpers: `IWM`, `^VIX`, `^TNX`, `^IRX`
- Stocks: **58** liquid names across tech, consumer, healthcare, financials, industrials, energy (`pinky/config.py` → `UNIVERSE_STOCKS`)
- Still short of full NASDAQ-100; good enough for first honest training later

## Repo layout

- `pinky/config.py` — tickers + paths + warmup
- `pinky/data_pull.py` — yfinance download → parquet
- `pinky/raw_io.py` — load raw bars
- `pinky/features.py` — `build_bfm_prediction_features()` + universe panel
- `pinky/labels.py` — excess return + beat labels vs SPY
- `scripts/pull_data.py` — run the pull
- `scripts/build_features.py` — run the feature build
- `scripts/build_labels.py` — run label build
- `data/raw/*.parquet` — downloaded bars (gitignored)
- `data/features/features_panel.parquet` — feature matrix (gitignored)
- `data/labels/labels_panel.parquet` — label matrix (gitignored)
- `requirements.txt` / `.venv/` — Python deps
- `README.md` — public overview (what / how / what’s shared vs private)
- `docs/ARCHITECTURE.md` — design and build plan
- `docs/PRD.md` — product requirements
- `docs/EVAL.md` — short pre-trust eval checklist
- `.cursor/rules/` — Cursor agent rules (Pinky-only; review personal prefs before public push)
- `project.md` — this overview
- `graphify-out/` — knowledge graph output

## Build order

1. Lock design — done
2. Architecture doc — done
3. Data pull — **done (small set)**
4. Feature builder — **done (v1)**
5. Labels vs SPY — **done (v1)**
6. Train models — next
7. Walk-forward evaluation
8. API / UI only after models prove useful

## Working notes

- Run and develop locally on this computer
- Activate venv: `source .venv/bin/activate`
- Re-pull data: `PYTHONPATH=. python scripts/pull_data.py`
- Rebuild features: `PYTHONPATH=. python scripts/build_features.py`
- Rebuild labels: `PYTHONPATH=. python scripts/build_labels.py`
- Use Git to save local versions (`add` → `commit`) before big changes
- Push to GitHub only if/when we connect a remote
- Keep `project.md` current after meaningful progress
- Graphify CLI path (if `graphify` not found): `/Users/hqschool/Library/Python/3.12/bin`
- After code lands: `graphify update .` (no API key). For docs: need an API key + `graphify extract .`
