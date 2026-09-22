# Pinky

Local research system that predicts **relative** stock performance vs the S&P 500 (**SPY**) — not whether a stock simply “goes up.”

> Rising markets can lift almost everything. Pinky focuses on a harder question: **will this name beat SPY, and by how much?**

## What it does

For a liquid stock and time horizon, Pinky aims to output:

1. Expected **excess return vs SPY**
2. **Probability** of beating SPY
3. An **honest confidence range** (no fake certainty)

Horizons (v1): **3m / 6m / 1y / 2y**

## How it works (high level)

```text
Market data (yfinance)
        ↓
Features (technicals, relative strength, macro, regime)
        ↓
Labels vs SPY (excess return + beat/lose)
        ↓
Walk-forward training + purge (no random-split cheating)
        ↓
Models: LightGBM (+ linear baseline)
        ↓
Evaluation → only then prediction UI
```

Details live in:

- [`docs/PRD.md`](docs/PRD.md) — product requirements
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — design
- [`docs/EVAL.md`](docs/EVAL.md) — how we judge quality

## What’s public vs private

| Shared on GitHub | Kept off GitHub |
|------------------|-----------------|
| Product docs & architecture | Downloaded price files (`.parquet`) |
| Pipeline code & scripts | Trained model weights / artifacts |
| Eval checklist | API keys / `.env` |
| High-level method | Anything you’d call “edge” configs later |

Rebuild local data anytime with the scripts below. Models are not published until/unless we choose to.

## Current status

- ✅ Data pull (liquid multi-sector universe)
- ✅ Feature builder (v1)
- ✅ Labels vs SPY (4 horizons)
- ⏳ Train-ready join + walk-forward/purge
- ⏳ Training (only when explicitly started)
- ⏳ Eval report / UI after models prove useful

## Quick start (local)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

PYTHONPATH=. python scripts/pull_data.py
PYTHONPATH=. python scripts/build_features.py
PYTHONPATH=. python scripts/build_labels.py
```

## Design principles

- Beat **SPY**, don’t predict raw direction
- **Walk-forward + purge** validation only
- Never fake data or metrics
- No polished UI before model quality is proven

## Disclaimer

This is an educational / research prototype. Not financial advice. Not a trading product.
