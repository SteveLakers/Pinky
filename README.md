# Pinky

Local research project: can a model pick US stocks that beat the S&P 500 (**SPY**)?

- **Goal:** find stocks that beat SPY over the next year. Lean toward tech and toward finding future big winners early, but buy any sector when it's the best pick.
- **Realistic target:** beat SPY by a few % a year, reliably. No leverage.
- **Status:** not there yet. On an honest 2001–2020 backtest, the best version roughly matches SPY. Current numbers, decisions and next steps: [`project.md`](project.md).

## How it works

```text
Sharadar data (US stocks since 1998, dead companies included)
        ↓
Daily point-in-time universe: stocks you could really have bought that day
(price ≥ $5, ≥ $5M traded per day, NYSE / NASDAQ / NYSE American)
        ↓
Delisting-aware returns: a stock that leaves is sold into SPY;
bankruptcies also take a −30% hit
        ↓
Weekly dataset: price features (+ size, + company data when tested);
label = return vs SPY over the next year
        ↓
Walk-forward training: train on the past, test the next year, purge overlaps
Models: Ridge, LightGBM, and a blend of the two
        ↓
Monthly portfolio backtest after trading costs, vs SPY and the equal-weight universe
```

- **No cheating with time:** every input uses only data public on that date (company numbers only after their earnings announcement or SEC filing). 2022 onward is locked as a final exam and used once, at the very end.
- **New data must earn its place:** it has to beat a placebo (the same numbers shuffled between stocks) under a rule fixed before seeing results.

Details: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) (design), [`docs/EVAL.md`](docs/EVAL.md) (how results are judged), [`docs/PRD.md`](docs/PRD.md) (requirements), [`docs/WALKFORWARD_RESULTS.md`](docs/WALKFORWARD_RESULTS.md) (results by version).

## What's in git and what isn't

| In git | Never in git |
|---|---|
| Code, scripts, docs | Sharadar data (`data/`; the license forbids sharing it) |
| Method and results write-ups | Trained models (`models/`) and run outputs (`artifacts/`) |
| | API keys (`.env`) |

## Quick start (local)

Needs a Sharadar Core US Equities Bundle subscription. Put the key in `.env` as `SHARADAR_API_KEY=...` (git ignores it).

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python scripts/pull_sharadar.py      # download data (~10 min)
PYTHONPATH=. python -m pinky.universe             # daily universe + returns (~1 min)
PYTHONPATH=. python -m pinky.pit_dataset          # weekly dataset (~1 min)
PYTHONPATH=. python scripts/train_walkforward.py --pit   # train + report (~8 min)
```

The report lands in `artifacts/walkforward_summary_<run>.md`. Run options and checks: [`project.md`](project.md) → Commands.

The yfinance files (`pinky/data_pull.py`, `raw_io.py`, `features.py`, `labels.py`) are the old prototype on 128 of today's big stocks, kept only to reproduce early results.

## Disclaimer

Educational research prototype. Not financial advice, not a trading product.
