# Pinky Architecture Plan

Last updated: 2026-09-10

## Goal

- Predict relative stock performance vs the S&P 500 (**SPY**).
- Support four horizons:
  - 3 months (~63 trading days)
  - half year (~126 trading days)
  - 1 year (~252 trading days)
  - 2 years (~504 trading days)
- For each horizon, output:
  - expected excess return vs SPY
  - probability of beating SPY
  - honest confidence range

## Locked decisions

- **Benchmark:** SPY (not IWM)
- **Universe (v1):** major liquid stocks, start with NASDAQ-100 style names
- **Model type (planned):** LightGBM for both heads, plus a simple linear baseline
- **Data (v1 prototype):** yfinance; upgrade later if results look real

## What we predict

- Do **not** predict “will this stock go up?”
- Predict “will this stock beat SPY, and by how much?”
- Why: rising markets can lift almost everything; relative skill is the useful signal

## Labels (truth the model learns)

For each stock + date + horizon:

- **Return label:** stock return − SPY return
- **Beat label:** 1 if stock beat SPY, else 0

## Models

Per horizon, train two models:

- `return_model` → expected excess return vs SPY
- `beat_spy_model` → P(beat SPY)

That means 4 horizons × 2 models = 8 models in v1.

## Feature pipeline

1. Pull history for the stock + helpers:
   - SPY (benchmark + market context)
   - IWM (kept as a relative-strength / size feature, not the beat target)
   - VIX, TNX, IRX (macro / rates / fear)
2. Run `build_bfm_prediction_features()`
3. Output feature vector **X** (tabular numeric features)

Feature groups (v1):

- stock technicals
- relative strength vs SPY / IWM
- macro environment
- multi-period momentum
- market regime (bull / high-vol)

Same feature builder for all horizons at first. Tune later if needed.

## Prediction flow

1. Build latest feature vector **X**
2. Run the horizon’s return + beat models
3. Combine with recent SPY context
4. Show expected excess return, P(beat SPY), and confidence range

## Validation rules (non-negotiable)

- No random train/test splits
- Use walk-forward validation
- Purge overlapping label windows
- Judge success by:
  - rank quality
  - top predicted basket vs SPY
  - probability calibration
- Do **not** trust inflated accuracy from overlapping samples

## Build order

1. Lock design (done for current decisions)
2. Architecture doc (this file)
3. Data pull for liquid majors + benchmarks
4. Feature builder
5. Labels for 4 horizons vs SPY
6. Train LightGBM pairs + linear baseline
7. Walk-forward evaluation report
8. Prediction API / UI only after models prove useful

## Explicit non-goals (for now)

- Predicting exact future prices
- Trading every tiny illiquid ticker
- Shipping a polished UI before model quality is proven
